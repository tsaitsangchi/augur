"""augur FinMind API client — 從 FinMind 抓任一 dataset，含節流 / 退避 / 重試。

這支在做什麼（白話）：
- 對 FinMind v4 `data` API 的薄 client：給 dataset 名 + 參數（data_id/start_date/end_date…），
  回傳 `list[dict]`（API 原樣列，欄名/大小寫逐字照 API，#2；不改值、不補值，#1）。
- token 從 `config.FINMIND_TOKEN` 取（不寫死，§一.5）。
- 扛真實世界的不穩定（#7 韌性）：逾時 / 連線錯誤 / 額度限流（402/429）→ 指數退避重試；
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
        try:
            resp = requests.get(API_URL, params=query, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise FinMindError(f"{dataset}: 連線失敗（重試 {max_retries} 次後）{type(e).__name__}") from e

        if resp.status_code in (402, 429):   # 額度/限流 → 退避重試
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise FinMindError(f"{dataset}: 額度/限流 HTTP {resp.status_code}（重試 {max_retries} 次仍失敗）")

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
    query = {"dataset": _PROBE_INVALID, "token": config.FINMIND_TOKEN}
    resp = requests.get(API_URL, params=query, timeout=timeout)
    body = resp.json()
    detail = body.get("detail")
    if isinstance(detail, list) and detail:
        expected = detail[0].get("ctx", {}).get("expected", "")
        return _DATASET_RE.findall(expected)
    return []
