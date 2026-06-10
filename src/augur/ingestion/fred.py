"""augur FRED API client — 從 FRED 抓總體經濟 series 觀測值（含節流 / 退避 / 重試）。

這支在做什麼（白話）：
- 對 FRED `series/observations` API 的薄 client：給一個 `series_id`（如 `T10Y2Y` 殖利率曲線、
  `UNRATE` 失業率），回傳該 series 的觀測列 `list[dict]`。
- **每列補上 `series_id`**：FRED 回應本身不含 series_id；補上後 generic_schema 才推得出
  `(series_id, date)` 複合主鍵（所有 series 同落 `fred_series` 一張表，#2）。
- 認證用 `config.FRED_API_KEY`（不寫死）；同 #7 韌性：逾時/限流（429）→ 指數退避重試；
  api_key/series_id 錯 → 立即拋 `FredError`。
- FRED 缺值回 `"."`（其「無觀測」佔位）→ 轉成 `None`（存 NULL）：那是「無值」非真實值，
  轉 NULL **不違 #1**；其餘為數值字串，交 generic_schema 推成 NUMERIC、PG 精確 cast。

邊界：只抓 FRED 資料（不建表/不寫 DB——ingest.py + generic_schema 負責）；不算特徵、不選股。
具體要抓哪些 series 由呼叫端（feature 設計）決定，本 client 不持 hardcoded series 清單。

守 #7（節流/退避/重試韌性）· #2（欄名照 API + 補 series_id 成主鍵）· #1（"." 佔位 → NULL，不捏造值）。
"""
from __future__ import annotations

import time

import requests

from augur.core import config

API_URL = "https://api.stlouisfed.org/fred/series/observations"


class FredError(RuntimeError):
    """FRED API 應用層/連線錯誤。"""


def fetch(series_id, *, start_date=None, end_date=None, timeout=60, max_retries=4, base_backoff=2.0):
    """抓一個 FRED series 的觀測 → `list[dict]`（每列含 series_id；`"."` → None）。

    start_date/end_date 為 `YYYY-MM-DD`（對映 FRED 之 observation_start/observation_end）。
    """
    params = {"series_id": series_id, "api_key": config.FRED_API_KEY, "file_type": "json"}
    if start_date:
        params["observation_start"] = start_date
    if end_date:
        params["observation_end"] = end_date

    backoff = base_backoff
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(API_URL, params=params, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise FredError(f"{series_id}: 連線失敗（重試 {max_retries} 次後）{type(e).__name__}") from e

        if resp.status_code == 429:   # 限流 → 退避重試
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise FredError(f"{series_id}: 限流 429（重試 {max_retries} 次仍失敗）")

        try:
            body = resp.json()
        except ValueError as e:
            raise FredError(f"{series_id}: 非 JSON 回應 (HTTP {resp.status_code})") from e

        if resp.status_code != 200 or "observations" not in body:
            raise FredError(f"{series_id}: HTTP {resp.status_code} {body.get('error_message', body)}")

        # 只取 (series_id, date, value)：FRED 的 realtime_start/realtime_end 為「查詢日 vintage
        # metadata」（隨查詢日變、非觀測值本身），存了破壞冪等與對帳 → 扣「只存真實值」不存。
        return [
            {
                "series_id": series_id,
                "date": obs.get("date"),
                "value": None if obs.get("value") == "." else obs.get("value"),
            }
            for obs in body["observations"]
        ]

    raise FredError(f"{series_id}: 重試耗盡")   # 理論上到不了
