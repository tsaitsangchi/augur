"""augur FinMind API client — 從 FinMind 抓任一 dataset，含節流 / 退避 / 重試。

這支在做什麼（白話）：
- 對 FinMind v4 `data` API 的薄 client：給 dataset 名 + 參數（data_id/start_date/end_date…），
  回傳 `list[dict]`（API 原樣列，欄名/大小寫逐字照 API，#2；不改值、不補值，#1）。
- token 從 `config.FINMIND_TOKEN` 取（不寫死，§一.5）。
- 扛真實世界的不穩定（#17 韌性）：**主動限速**（每請求最小間隔，平滑 burst、整體壓在 FinMind ~6000/hr IP 線下，
  防 403 ip banned）＋ 逾時 / 連線 / 額度限流 / IP 封鎖 / 伺服器暫時錯誤（402/429/403/5xx）→ 依回應 `retry_after` 或指數退避重試；
  參數錯 / token 錯等應用層錯誤 → 立即拋 `FinMindError`（重試也沒用）。
- `list_datasets()`：送一個無效 dataset → FinMind 回 422，其 enum 列出全部合法 dataset 名
  → 支援 #3「`--all` 動態列舉、無 hardcoded 清單」。

邊界：**只抓資料**（不建表、不寫 DB——那是 ingest.py + generic_schema）；不算特徵、不選股；
**不決定抓不抓 intraday**（日為最小單位 #4 之守門在 ingest.py，不在這層）。

守 #17（節流/退避/重試韌性：主動限速三層防護）· #3（dataset 動態列舉、無 hardcoded 清單）· #2（欄名/大小寫照 API）· #1（回 API 原值，不捏造）。
"""
from __future__ import annotations

import re
import threading
import time

import requests

from augur.core import config

API_URL = "https://api.finmindtrade.com/api/v4/data"
DATALIST_URL = "https://api.finmindtrade.com/api/v4/datalist"   # /datalist:列某 dataset 之 data_id 全集(#18 維度 id 權威來源)
TRANSLATION_URL = "https://api.finmindtrade.com/api/v4/translation"   # /translation:欄位中文對照(schema comment 權威來源)
_PROBE_INVALID = "__augur_probe_invalid__"   # 送無效 dataset → 422 列出全部合法 dataset
_DATASET_RE = re.compile(r"'([A-Za-z0-9]+)'")

# ── 主動限速（#17;§一.9 經驗:2026-06-09 全史 burst 觸發 403 ip banned）──
# 每請求最小間隔 → 平滑 burst、整體壓在 FinMind ~6000/hr IP 線下;全部 fetch（驗證與全史）同走此門,
# 一律被限速 → 無論怎麼啟動都 burst 不起來（把「驗證時手動 sleep 間隔」內建進程式）。
MIN_INTERVAL = 0.7      # operational(#17/#19):2026-06-12 實證 FinMind 對「sustained 負載」throttle —— burst/短測快(~1.39/s)、但 sustained 跑(數分鐘)降到 ~0.2/s(bimodal latency)。
                        # 試過 0.6s(soft-throttle 5-18s)、0.75s(sustained 仍 ~0.2/s);結論:binding 是 sustained-throttle 非 pace,過度試探會深化 throttle → 現操作值 0.7（#27 試錯逼近最佳奇異點、見訊號即停、勿過度試探深化）。
MAX_COOLDOWN = 1800     # honor retry_after 之上限(秒)
QUOTA_COOLDOWN = 1800   # 403 額度耗盡/IP 限流之固定冷卻(秒;用戶決策 2026-06-12 #24):撞 403 直接等額度 hourly 重置,不短退避反覆撞(防惡化成 sustained ban,handoff §4.B 教訓)

# ── 主動額度閘(#24 用戶方向 2026-06-12:撞 403 前先停)──
# 實證:FinMind 額度為 rolling 視窗(零 call 期間錶仍連續下退)、計數含未知成分(probe 403 時錶讀 5507<6000)
# → 不本地計數、閉環問權威錶 /user_info(實證:403 期間可讀、且讀錶不自計額度)。
USERINFO_URL = "https://api.web.finmindtrade.com/v2/user_info"
QUOTA_HEADROOM = 200    # 暫停閾值 = api_request_limit − 此頭寸(兩次讀錶間 worker 競態 + 人工診斷 probe 的緩衝)
QUOTA_METER_EVERY = 120 # 每 N 次 data call 讀一次錶(< HEADROOM → 兩次讀錶間衝不過上限)
QUOTA_POLL = 150        # 暫停期間每隔幾秒再讀錶(rolling 視窗連續退 → 退夠即自動續,不固定睡死)
_quota_state = {"calls": 0, "t": 0.0}
_quota_lock = threading.Lock()
# 暫時性錯誤(重試有意義):額度/限流/IP封鎖(402/429/403) + gateway 伺服器暫時故障(500/502/503/504)
_RETRY_STATUS = (402, 429, 403, 500, 502, 503, 504)
_next_slot = [0.0]      # 下一可發請求之 monotonic 時點(list 供函式內改寫)
_pace_lock = threading.Lock()   # thread-safe:多執行緒並發 fetch 時,start 仍序列化於 ≥MIN_INTERVAL


def _pace():
    """主動限速:確保請求 start 間隔 ≥ MIN_INTERVAL 秒(平滑 burst,防 IP 封鎖)。

    thread-safe:鎖內「預約」下一時槽(各執行緒 start 仍 ≥MIN_INTERVAL 間隔、IP 對外速率不變),
    sleep 在鎖外 → 並發時各請求之回應等待重疊、但 start rate 維持單流安全值(#17/#24)。
    """
    with _pace_lock:
        now = time.monotonic()
        slot = max(now, _next_slot[0])      # 我的發送時槽
        _next_slot[0] = slot + MIN_INTERVAL  # 預約下一時槽(下個執行緒至少再隔 MIN_INTERVAL)
    wait = slot - now
    if wait > 0:
        time.sleep(wait)


class FinMindError(RuntimeError):
    """FinMind API 應用層/連線錯誤（呼叫端可據此決定跳過/重排/中止）。"""


def _user_quota(timeout=15):
    """權威額度錶:/user_info → (user_count, api_request_limit)。讀失敗拋例外(呼叫端寬容)。"""
    resp = requests.get(USERINFO_URL, headers={"Authorization": f"Bearer {config.FINMIND_TOKEN}"}, timeout=timeout)
    j = resp.json()
    return int(j["user_count"]), int(j.get("api_request_limit") or 6000)


def _quota_gate():
    """[2026-06-17 Mac 本地操作、未 commit] Mac token user_count 黑箱失準(零 call 卻卡/自漲、與真實
    call 不符;IP 健康實測能抓為證)→ **禁用 user_count 預防暫停閘**,純靠 `_pace` 限速 + 撞真 403 之
    `QUOTA_COOLDOWN` 冷卻(WSL 經驗「錶有雜訊→以 DB 列數成長為真在抓訊號」)。仍週期讀錶 log 供監控、不暫停。
    **錶可靠之機台應 git restore 還原此閘**(原為主動額度閘:錶≥limit−HEADROOM 持鎖暫停、退半續)。"""
    with _quota_lock:
        _quota_state["calls"] += 1
        if _quota_state["calls"] < QUOTA_METER_EVERY and time.monotonic() - _quota_state["t"] < 120:
            return
        _quota_state["calls"] = 0
        _quota_state["t"] = time.monotonic()
        try:
            count, limit = _user_quota()
            print(f"[finmind] 額度錶 {count}/{limit}(閘已禁用、純靠 _pace+403;IP 健康)", flush=True)
        except Exception:
            pass


def _protected_get(url, query, label, *, timeout, max_retries, base_backoff):
    """三層防護（quota_gate→pace）下對 url 發 GET，含 402/429/5xx 退避、403 固定冷卻、逾時/連線重試 → 回 body dict。

    `fetch`（/data）與 `fetch_dedicated`（專屬 endpoint）共用此核心 → **同一限速防護**（#24「驗證與全史走同一 fetch、同一防護」）。
    """
    backoff = base_backoff
    for attempt in range(max_retries + 1):
        _quota_gate()                             # 主動額度閘:錶快滿先停(撞 403 前),退夠自動續
        _pace()                                   # 主動限速:每筆先間隔(防 burst 被封)
        try:
            resp = requests.get(url, params=query, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise FinMindError(f"{label}: 連線失敗（重試 {max_retries} 次後）{type(e).__name__}") from e

        if resp.status_code in _RETRY_STATUS:   # 額度/限流/IP封鎖/伺服器暫時錯誤 → 依 retry_after 或退避重試
            if attempt < max_retries:
                ra = None
                try:
                    ra = resp.json().get("retry_after")   # FinMind 限速回應常附 retry_after(秒)
                except ValueError:
                    pass
                if resp.status_code == 403:               # 額度耗盡/IP 限流:固定冷卻等 hourly 重置/IP 平息(不短退避反覆撞 → 防惡化成 sustained ban,handoff §4.B)
                    time.sleep(max(QUOTA_COOLDOWN, float(ra) if ra else 0))
                else:                                     # 429/5xx 暫時錯誤:honor retry_after 或指數退避
                    time.sleep(min(float(ra), MAX_COOLDOWN) if ra else backoff)
                    backoff *= 2
                continue
            raise FinMindError(f"{label}: 限流/封鎖/伺服器錯誤 HTTP {resp.status_code}（重試 {max_retries} 次仍失敗）")

        try:
            return resp.json()
        except ValueError as e:
            raise FinMindError(f"{label}: 非 JSON 回應 (HTTP {resp.status_code})") from e

    raise FinMindError(f"{label}: 重試耗盡")   # 理論上到不了（迴圈內已處理）


def fetch(dataset, *, timeout=60, max_retries=4, base_backoff=2.0, **params):
    """抓一個 FinMind dataset（`/data`）→ `list[dict]`（無資料則 `[]`）。

    params 例：`data_id='2330', start_date='2025-01-01', end_date='2026-06-09'`。
    402/429/5xx（限流/伺服器）與逾時/連線錯誤 → 指數退避；**403（額度耗盡/IP 限流）→ 固定冷卻 `QUOTA_COOLDOWN` 秒**等額度重置(不短退避反覆撞)；應用層錯誤（參數/token）→ 立即拋。
    """
    query = {**params, "dataset": dataset, "token": config.FINMIND_TOKEN}
    body = _protected_get(API_URL, query, dataset, timeout=timeout, max_retries=max_retries, base_backoff=base_backoff)
    if body.get("status") == 200:
        return body.get("data", [])
    msg = body.get("msg", "")
    # 單日型 dataset（FinMind 資料量大→一次只回一天、end_date 須 none，如 TaiwanStockNews）：移除
    # end_date 重抓該 start_date 單日 → by-date/backward-probe 逐日路徑自動相容（catch 訊息、非 hardcoded 清單，守 #3）
    if "end_date" in msg and "none" in msg and params.get("end_date") is not None:
        return fetch(dataset, timeout=timeout, max_retries=max_retries, base_backoff=base_backoff,
                     **{k: v for k, v in params.items() if k != "end_date"})
    # 應用層錯誤（如「Token is illegal」「parameter data_id can't be none」）→ 重試無益，直接拋
    raise FinMindError(f"{dataset}: status={body.get('status')} msg={msg}")


def fetch_dedicated(path, *, timeout=60, max_retries=4, base_backoff=2.0, **params):
    """抓 FinMind **專屬 endpoint**（非 `/data`；分點/權證/卷商統計等 special endpoint）→ `list[dict]`。

    `path` 例：`/taiwan_stock_trading_daily_report`（券商分點）·`/taiwan_stock_warrant_trading_daily_report`（權證分點）·
    `/taiwan_stock_trading_daily_report_secid_agg`（卷商分點統計，規模可行聚合版）。
    params 例：分點/權證 `data_id='2330', date='2026-06-12'`（per-(股,日)）；secid_agg `data_id='2330', start_date=…, end_date=…`（per-股範圍）。
    與 `fetch` 共用同一三層防護（`_protected_get`，#24）；**endpoint 即 dataset → query 不帶 `dataset` 鍵**。
    """
    url = API_URL.rsplit("/", 1)[0] + path
    query = {**params, "token": config.FINMIND_TOKEN}
    body = _protected_get(url, query, path, timeout=timeout, max_retries=max_retries, base_backoff=base_backoff)
    if body.get("status") == 200:
        return body.get("data", [])
    raise FinMindError(f"{path}: status={body.get('status')} msg={body.get('msg') or body.get('detail', '')}")  # 專屬 endpoint 400 用 detail 非 msg


def list_datasets(*, timeout=60):
    """回傳 FinMind 全部合法 dataset 名（送無效 dataset → 解析 422 enum）；支援 #3 動態列舉。"""
    _quota_gate()
    _pace()
    query = {"dataset": _PROBE_INVALID, "token": config.FINMIND_TOKEN}
    resp = requests.get(API_URL, params=query, timeout=timeout)
    body = resp.json()
    detail = body.get("detail")
    if isinstance(detail, list) and detail:
        expected = detail[0].get("ctx", {}).get("expected", "")
        return _DATASET_RE.findall(expected)
    return []


def translation_datasets(*, timeout=60):
    """回傳 `/translation` 支援之 dataset 全集（送無效 dataset → 解析 422 enum;同 `list_datasets` 模式,#18 動態、無白名單）。"""
    _quota_gate()
    _pace()
    resp = requests.get(TRANSLATION_URL, params={"dataset": _PROBE_INVALID, "token": config.FINMIND_TOKEN}, timeout=timeout)
    try:
        detail = resp.json().get("detail")
    except ValueError:
        return []
    if isinstance(detail, list) and detail:
        return _DATASET_RE.findall(detail[0].get("ctx", {}).get("expected", ""))
    return []


def translation(dataset, *, timeout=60):
    """某 dataset 之欄位中文對照（FinMind `/translation`）→ list（查無/不支援 → `[]`）。
    schema comment 中文之權威來源（#18 問 API、不抄文檔）；與 data fetch 同一防護（#17）。"""
    _quota_gate()
    _pace()
    resp = requests.get(TRANSLATION_URL, params={"dataset": dataset, "token": config.FINMIND_TOKEN}, timeout=timeout)
    try:
        data = resp.json().get("data")
    except ValueError:
        return []
    return data if isinstance(data, list) else []


def datalist(dataset, *, timeout=60):
    """列某 dataset 之 data_id 全集（FinMind `/datalist`）→ `list`。僅總經/契約類支援
    （如 GovernmentBondsYield→13 期別、TaiwanExchangeRate→幣別）；不支援之 dataset（台股 per-stock）回 `[]`。
    #18 維度 id 全集之權威動態來源——取代臆測白名單（實證 `/datalist` > 靜態文檔）。"""
    _quota_gate()
    _pace()
    resp = requests.get(DATALIST_URL, params={"dataset": dataset, "token": config.FINMIND_TOKEN}, timeout=timeout)
    try:
        data = resp.json().get("data")
    except ValueError:
        return []
    return data if isinstance(data, list) else []
