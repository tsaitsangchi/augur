"""augur FRED API client — 從 FRED 抓總體經濟 series 觀測值（含節流 / 退避 / 重試）。

🎯 這支在做什麼（白話）：
- 對 FRED `series/observations` API 的薄 client：給一個 `series_id`（如 `T10Y2Y` 殖利率曲線、
  `UNRATE` 失業率），回傳該 series 的觀測列 `list[dict]`。
- **每列補上 `series_id`**：FRED 回應本身不含 series_id；補上後 generic_schema 才推得出
  `(series_id, date, realtime_start)` 複合主鍵（所有 series 同落 `fred_series` 一張表，#2；realtime_start 見下）。
- 認證用 `config.FRED_API_KEY`（不寫死）；同 #17 韌性：逾時/限流（429）→ 指數退避重試（FRED 限速寬、單層退避足夠）；
  api_key/series_id 錯 → 立即拋 `FredError`。
- FRED 缺值回 `"."`（其「無觀測」佔位）→ 轉成 `None`（存 NULL）：那是「無值」非真實值，
  轉 NULL **不違 #1**；其餘為數值字串，交 generic_schema 推成 NUMERIC、PG 精確 cast。

- **vintage（point-in-time，#8）**：`vintage=True` 走 ALFRED 全 realtime 範圍（output_type=1），每觀測日
  回多列、各帶該值「成為當時現行版」之 `realtime_start`（會被回溯修訂的月/季/週數列用，feature 層才能取
  面板日當下真看得到那版）；`vintage=False`（每日市場數列）回最新值、`realtime_start` 設為觀測日本身
  （當日收盤即知＝正確 PIT、非近似）。`realtime_end` 隨查詢日變，不存。

邊界：只抓 FRED 資料（不建表/不寫 DB——ingest.py + generic_schema 負責）；不算特徵、不選股。
具體要抓哪些 series（及各檔走不走 vintage）由呼叫端（features/macro.py）決定，本 client 不持清單。

守 #8（vintage＝anti-leakage PIT）· #17（節流/退避/重試）· #2（欄名照 API + series_id 主鍵）· #1（"." → NULL）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.ingestion.fred              # 印用途+公開入口（唯讀）
  python -m augur.ingestion.fred --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import time

import requests

from augur.core import config

API_URL = "https://api.stlouisfed.org/fred/series/observations"


class FredError(RuntimeError):
    """FRED API 應用層/連線錯誤。"""


def fetch(series_id, *, start_date=None, end_date=None, vintage=False,
          timeout=60, max_retries=4, base_backoff=2.0):
    """抓一個 FRED series 的觀測 → `list[dict]`（每列含 series_id + realtime_start；`"."` → None）。

    start_date/end_date 為 `YYYY-MM-DD`（對映 FRED 之 observation_start/observation_end）。
    vintage=True：走 ALFRED 全 realtime 範圍 + output_type=1，回所有 vintage（每列 realtime_start
    ＝該值成為當時現行版之起日，供 feature 層做 point-in-time 取版，#8）；vintage=False：回最新值，
    realtime_start 注入觀測日本身（每日市場數列當日即知＝正確 PIT）。
    """
    params = {
        "series_id": series_id,
        "api_key": config.FRED_API_KEY,
        "file_type": "json",
        "limit": 100000,
    }
    if start_date:
        params["observation_start"] = start_date
    if end_date:
        params["observation_end"] = end_date
    if vintage:
        params["realtime_start"] = "1776-07-04"   # FRED 允許之最早 realtime（全 vintage 起點）
        params["realtime_end"] = "9999-12-31"      # FRED 允許之最晚 realtime（全 vintage 終點）
        params["output_type"] = 1                  # by real-time period：每 vintage 一列（長格式）

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
            msg = body.get("error_message", body) if isinstance(body, dict) else body
            # ALFRED 單檔 vintage 數上限 2000：每日數列（vintage 數遠超）才會撞 → 該走 Tier A
            if vintage and resp.status_code == 400 and "vintage date" in str(msg):
                raise FredError(
                    f"{series_id}: vintage 數超過 ALFRED 單檔 2000 上限（{msg}）；"
                    f"此為高頻數列、應改走 vintage=False（Tier A）。"
                )
            raise FredError(f"{series_id}: HTTP {resp.status_code} {msg}")

        obs = body["observations"]
        count = body.get("count", len(obs))
        if count > len(obs):   # 超單頁 → 寧可明失敗，不靜默截斷（#15 不漏資料）
            raise FredError(f"{series_id}: 回 {len(obs)}/{count} 列超單頁上限、需分頁（暫未支援）")

        # realtime_start：vintage→取 API 真實（該版可見起日）｜非 vintage→注入觀測日（市場當日即知）。
        # realtime_end 隨查詢日變（現行版＝9999）、PIT 取版只需 realtime_start，故不存（#8）。
        return [
            {
                "series_id": series_id,
                "date": o.get("date"),
                "realtime_start": o.get("realtime_start") if vintage else o.get("date"),
                "value": None if o.get("value") == "." else o.get("value"),
            }
            for o in obs
        ]

    raise FredError(f"{series_id}: 重試耗盡")   # 理論上到不了


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：本檔全 IO-bound（fetch 需連線）→ import-smoke
    + 公開入口/例外結構斷言 + fetch 簽名預設值（vintage 預設 False＝Tier A、退避參數）之回歸鎖。"""
    import inspect
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("公開入口 fetch 可呼叫", callable(fetch))
    chk("FredError 為 RuntimeError 子類", issubclass(FredError, RuntimeError))
    chk("API_URL 指向 FRED observations 端點",
        isinstance(API_URL, str) and API_URL.startswith("https://") and "observations" in API_URL)
    sig = inspect.signature(fetch)
    p = sig.parameters
    chk("fetch 有 series_id 位置參數", "series_id" in p)
    chk("fetch vintage 預設 False（Tier A、非 PIT 全 vintage）", p["vintage"].default is False)
    chk("fetch 退避參數存在（節流/重試 #17）",
        p["max_retries"].default == 4 and p["base_backoff"].default == 2.0)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("入口:fetch / FredError")
    print("(自測:python -m augur.ingestion.fred --selftest;免 DB 免 API)")
