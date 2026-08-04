#!/usr/bin/env python
"""augur 序列窗覆蓋率報告／快取匯出 — 呼叫 features.sequence 對核心股做 as-of 序列窗 reshape（S3-WAVE-D Phase 1）。

🎯 這支在做什麼（白話）：給定 as-of 與一或多個窗長，對核心股（`core_universe_asof`）逐股呼叫既有
`audit.field_correlation.build_stock_panel`（日頻對齊面板），reshape 成 (stocks, window, channels) 張量，
印覆蓋率（足窗股數／排除股數／各通道 NaN 率）。**預設唯讀、不寫庫**；`--export` 才把單一窗長之張量存成
`.npz` 檔案快取（非 DB 表，供訓練腳本讀取；可重建、非 SSOT，比照 `models/artifact.py` 之 artifact 慣例）。

守 #1（缺值不補、足窗才收）· #8（as-of 篩、不看未來）· #12（不重複造表，序列窗契約住 library 非 DB）。

執行指令矩陣:
  python scripts/build_sequence_panel.py --asof 2026-06-30                       （預設 window=20,60,120、覆蓋率報告）
  python scripts/build_sequence_panel.py --asof 2026-06-30 --window 60 --limit 20 （小樣本快速驗證）
  python scripts/build_sequence_panel.py --asof 2026-06-30 --window 60 --export /tmp/seq_60.npz  （匯出單一窗長快取）
"""
import argparse
import datetime as dt

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
import numpy as np

from augur.core import db
from augur.features.sequence import coverage_report


def _core_stock_ids(cur, as_of, limit=None):
    cur.execute(
        "SELECT stock_id FROM core_universe_asof "
        "WHERE as_of_date = (SELECT max(as_of_date) FROM core_universe_asof WHERE as_of_date <= %s) "
        "ORDER BY stock_id", (as_of,))
    ids = [r[0] for r in cur.fetchall()]
    return ids[:limit] if limit else ids


def main():
    ap = argparse.ArgumentParser(description="序列窗覆蓋率報告（唯讀預設）／匯出快取（--export）")
    ap.add_argument("--asof", required=True, help="as-of 日期 YYYY-MM-DD")
    ap.add_argument("--window", default="20,60,120", help="窗長（交易日），逗號分隔，預設 20,60,120")
    ap.add_argument("--channels", help="逗號分隔通道清單；預設=面板全部欄位（資料判定，不硬編）")
    ap.add_argument("--limit", type=int, help="只取前 N 支核心股（快速驗證用，非生產範圍限制）")
    ap.add_argument("--export", help="匯出 .npz（僅限單一 --window 值）")
    args = ap.parse_args()

    as_of = dt.date.fromisoformat(args.asof)
    windows = [int(w) for w in args.window.split(",") if w.strip()]
    channels = [c.strip() for c in args.channels.split(",")] if args.channels else None

    if args.export and len(windows) != 1:
        ap.error("--export 僅限單一 --window 值（避免一次匯出多個不同 shape 的檔案混淆）")

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            stock_ids = _core_stock_ids(cur, as_of, args.limit)
        if not stock_ids:
            print(f"as_of={as_of} 無核心股快照（core_universe_asof 空或早於首個 as_of_date）")
            return
        print(f"as_of={as_of}｜核心股 {len(stock_ids)} 支｜窗長 {windows}｜"
              f"通道={'（資料判定）' if channels is None else channels}")

        if args.export:
            from augur.features.sequence import build_sequence_tensor
            tensor, ok_ids, excluded, chans = build_sequence_tensor(
                conn, stock_ids, as_of, windows[0], channels)
            np.savez(args.export, tensor=tensor, stock_ids=np.array(ok_ids),
                     channels=np.array(chans), as_of=str(as_of), window_len=windows[0])
            print(f"✓ 匯出 {args.export}：shape={tensor.shape}｜足窗 {len(ok_ids)}／"
                  f"排除 {len(excluded)}（{excluded[:10]}{'…' if len(excluded) > 10 else ''}）")
            return

        report = coverage_report(conn, stock_ids, as_of, windows, channels, from_db=True)
        for wl, r in report.items():
            print(f"\n── window={wl} ──")
            print(f"  足窗 {r['ok']} ／ 排除 {r['excluded']}"
                  f"（樣本：{r['excluded_sample']}{'…' if r['excluded'] > 10 else ''}）")
            print(f"  通道數 {len(r['channels'])}")
            if r["nan_rate"]:
                worst = sorted(r["nan_rate"].items(), key=lambda kv: -kv[1])[:5]
                print("  NaN 率最高 5 通道：" + "、".join(f"{c}={v:.1%}" for c, v in worst))


if __name__ == "__main__":
    main()
