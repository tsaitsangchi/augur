---
name: asof-completeness-per-table-verification
description: as-of 完整性須逐表實證 max(date)、sync「全市場全史」不保證每表到 as-of；GoldPrice 漏抓2022-2026已補、84/84達成
metadata:
  node_type: memory
  type: project
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

宣稱 augur DB「到 as-of 2026-05-31 完整」前，須**逐表實證 `max(date)` vs as-of**，不能假設 sync 跑過「全市場全史」就每表到 as-of。2026-06-24 驗證 84 表 → 發現 **GoldPrice 唯一真漏抓**（2022-2026），補後 **84/84 達成**。⚠**2026-07-17:此「84/84 @ 2026-05-31」為凍結期里程碑,現況已 live 增量滾動**(GoldPrice max 已 2026-07-16、非 05-31);表名=`GoldPrice`(非 TaiwanStockGoldPrice);dataset_catalog 現 97。方法(逐表 max(date) vs as-of、勿假設 sync=每表到)仍現行。

**驗證法（三分類）**：查 84 表 `max(date)` vs as-of —
- `max ≥ as-of` → ✅ 完整（67 表）
- `max < as-of` 但 API 該窗也空（低頻/稀疏/財報季頻 Q2 未發布/事件無新）→ ✅ 正常（~8 表）
- `max < as-of` 且 API 該窗**有資料** → ⚠️ 真漏抓

**漏抓 vs API 停更 判別（關鍵）**：probe API 在「DB 缺的窗」+「DB 有的窗」兩段 —
- 缺窗有、有窗也有 → **真漏抓**。實證 GoldPrice：API 2026-05 有 257 列/日、DB 停 2022-06-07 → sync resume by-date 補 **+1056 列** → max 2026-06-24、對帳 passed（VM=0 EX=0 MIS=0）。
- 缺窗空、有窗有（早期有、後期停）→ **API 停更非漏抓**，DB=API 即完整。實證 ExchangeRate：`data_id='Canda'` 2019/2020 有 311/362 列、2020-11 後 0 → FinMind 停更 2020；國際股 Info（Europe/Japan/UK）API 停 2019=DB。

**Why**：完整性判準入憲（原則精華 v1.7.1/憲章 v1.9.1）後，「完整」須可定案可驗證；GoldPrice 漏抓 2022-2026 唯逐表驗證 max date 才察覺，不靠「我以為 sync 全史已完整」（[[rigor-completeness-discipline]] #20）。

**How to apply**：宣稱「DB 到 as-of 完整」前跑逐表 `max(date)` vs as-of；`max<as-of` 者必 probe API「缺窗+有窗」判漏抓 vs 停更；真漏抓走 sync resume 補 + 對帳驗。更深一層完整性＝逐表逐交易日 gap（每股每日齊全）為第二層、本輪未做（如需再查）。驗證報告 reports/augur_asof_completeness_verification_20260624.md。關聯 [[finmind-fetch-methods]]（抓法判別）、[[finmind-data-source]]（API 停更地圖）。
