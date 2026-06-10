"""augur FinMind API client — 從 FinMind 抓任一 dataset，含節流 / 退避 / 重試。

這支在做什麼（白話）：
- 對 FinMind v4 `data` API 的薄 client：給 dataset 名 + 參數（data_id/start_date/end_date…），
  回傳 `list[dict]`（API 原樣列，欄名/大小寫逐字照 API，#2；不改值、不補值，#1）。
- token 從 `config.FINMIND_TOKEN` 取（不寫死，§一.5）。
- 扛真實世界的不穩定（#7 韌性）：**主動限速**（每請求最小間隔，平滑 burst、整體壓在 FinMind ~6000/hr IP 線下，
  防 403 ip banned）＋ 逾時 / 連線 / 額度限流 / IP 封鎖（402/429/403）→ 依回應 `retry_after` 或指數退避重試；
  參數錯 / token 錯等應用層錯誤 → 立即拋 `FinMindError`（重試也沒用）。
- `list_datasets()`：送一個無效 dataset → FinMind 回 422，其 enum 列出全部合法 dataset 名
  → 支援 #3「`--all` 動態列舉、無 hardcoded 清單」。

邊界：**只抓資料**（不建表、不寫 DB——那是 ingest.py + generic_schema）；不算特徵、不選股；
**不決定抓不抓 intraday**（日為最小單位 #4 之守門在 ingest.py，不在這層）。

守 #7（節流/退避/重試韌性）· #3（dataset 動態列舉、無 hardcoded 清單）· #2（欄名/大小寫照 API）· #1（回 API 原值，不捏造）。
"""
from __future__ import annotations

import re
import time

import requests

from augur.core import config

API_URL = "https://api.finmindtrade.com/api/v4/data"
_PROBE_INVALID = "__augur_probe_invalid__"   # 送無效 dataset → 422 列出全部合法 dataset
_DATASET_RE = re.compile(r"'([A-Za-z0-9]+)'")

# ── 主動限速（#7;§一.9 經驗:2026-06-09 全史 burst 觸發 403 ip banned）──
# 每請求最小間隔 → 平滑 burst、整體壓在 FinMind ~6000/hr IP 線下;全部 fetch（驗證與全史）同走此門,
# 一律被限速 → 無論怎麼啟動都 burst 不起來（把「驗證時手動 sleep 間隔」內建進程式）。
MIN_INTERVAL = 1.0      # 秒/請求(~3600/hr;入憲 #17 operational 值:0.7s 曾 re-ban、2.0s 過保守 → 1.0s 為速度×安全平衡)
MAX_COOLDOWN = 1800     # honor retry_after 之上限(秒)
_last_request = [0.0]   # 上次請求 monotonic 時點(list 供函式內改寫)


def _pace():
    """主動限速:確保距上次請求 ≥ MIN_INTERVAL 秒(平滑 burst,防 IP 限速封鎖)。"""
    wait = MIN_INTERVAL - (time.monotonic() - _last_request[0])
    if wait > 0:
        time.sleep(wait)
    _last_request[0] = time.monotonic()


class FinMindError(RuntimeError):
    """FinMind API 應用層/連線錯誤（呼叫端可據此決定跳過/重排/中止）。"""


def fetch(dataset, *, timeout=60, max_retries=4, base_backoff=2.0, **params):
    """抓一個 FinMind dataset → `list[dict]`（無資料則 `[]`）。

    params 例：`data_id='2330', start_date='2025-01-01', end_date='2026-06-09'`。
    402/429（額度/限流）與逾時/連線錯誤 → 指數退避重試；應用層錯誤（參數/token）→ 立即拋。
    """
    query = {**params, "dataset": dataset, "token": config.FINMIND_TOKEN}
    backoff = base_backoff
    for attempt in range(max_retries + 1):
        _pace()                                   # 主動限速:每筆 fetch 先間隔(防 burst 被封)
        try:
            resp = requests.get(API_URL, params=query, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise FinMindError(f"{dataset}: 連線失敗（重試 {max_retries} 次後）{type(e).__name__}") from e

        if resp.status_code in (402, 429, 403):   # 額度/限流/IP 封鎖 → 依 retry_after 或退避重試
            if attempt < max_retries:
                ra = None
                try:
                    ra = resp.json().get("retry_after")   # FinMind 限速回應常附 retry_after(秒)
                except ValueError:
                    pass
                time.sleep(min(float(ra), MAX_COOLDOWN) if ra else backoff)
                backoff *= 2
                continue
            raise FinMindError(f"{dataset}: 限流/封鎖 HTTP {resp.status_code}（重試 {max_retries} 次仍失敗）")

        try:
            body = resp.json()
        except ValueError as e:
            raise FinMindError(f"{dataset}: 非 JSON 回應 (HTTP {resp.status_code})") from e

        if body.get("status") == 200:
            return body.get("data", [])
        # 應用層錯誤（如「Token is illegal」「parameter data_id can't be none」）→ 重試無益，直接拋
        raise FinMindError(f"{dataset}: status={body.get('status')} msg={body.get('msg')}")

    raise FinMindError(f"{dataset}: 重試耗盡")   # 理論上到不了（迴圈內已處理）


def list_datasets(*, timeout=60):
    """回傳 FinMind 全部合法 dataset 名（送無效 dataset → 解析 422 enum）；支援 #3 動態列舉。"""
    _pace()
    query = {"dataset": _PROBE_INVALID, "token": config.FINMIND_TOKEN}
    resp = requests.get(API_URL, params=query, timeout=timeout)
    body = resp.json()
    detail = body.get("detail")
    if isinstance(detail, list) and detail:
        expected = detail[0].get("ctx", {}).get("expected", "")
        return _DATASET_RE.findall(expected)
    return []
