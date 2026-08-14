# FinMind／FRED 日排程時點 — 問答備忘（2026-08-04）

> **位階**：[I] 工具／接續記憶（非 META [N]）  
> **觸發**：Steward 問「每天什麼時間最佳抓取 FinMind 及 FRED」  
> **約束**：不改 cron 時點；不打 live API；預測 ≠ sync（`predict-vs-market-api`）  
> **2026-08-14 修訂**：預測日更取數＝核 A＋TRI（`run_l0_hotpath_daily.sh`）；20:00 時點不變，①不再是 93 表 `daily_maintenance --end D`。見 `audits/L0-HOTPATH-PREDICT-DAILY-ADOPTED-20260814.md`。

---

## 1. 專案已拍板時點

| 時點（Asia/Taipei） | 內容 | 位階／出處 |
|---|---|---|
| **平日 20:00** | `check_finmind_quota.py --read` → `run_arena_daily_pipeline.py --run`（內含 FinMind 日頻＋FRED） | **[I]** 拍板：2026-07-26 hugo「讓 arena 的鐘重新走起來」→ freeze rule **V2-FZ-scope**（cron 20:00 arena 管線內）；排程 SSOT＝`install_cron.sh` `0 20 * * 1-5` |
| **同鏈順序** | ① `run_l0_hotpath_daily.sh --date D --apply`（核 A＋TRI＋FRED）→ ②–⑤ 庫內特徵／對局 | **[I]** 2026-08-14 採納；`scripts/run_arena_daily_pipeline.py` `_steps` |
| **平日 21:30** | `settle_arena_labels`（結算；**非**取數） | **[I]** `install_cron.sh` |
| **解凍後白名單** | 仍准上述日頻增量＋`sync_macro --no-catalog`；禁 Dividend rebuild／寬窗放量除非另授 | **[I]** `audits/API-THAW-20260804.md` §3（與 V2-FZ-scope 同形） |
| ~~平日 16:00~~ | 舊 stock_backend FinMind cron | **已廢**：2026-07-13 hugo 取消（同 IP 疊加）— `HANDOFF.md` |

**非 [N]**：時點未入 META／領域憲章條文；權威＝Steward 拍板＋`install_cron.sh`＋freeze／THAW audits。

**過時記載**：`ops/machines/PC002-S1800.md` 曾寫 arena `22:30`——以 **`install_cron.sh` 20:00** 為準。

---

## 2. 建議日排程表（與現況對齊＝最佳預設）

時區一律 **Asia/Taipei**；交易日＝週一至五（休市管線誠實缺席 exit 0）。

| 順序 | Clock | 作業 | Why |
|---|---|---|---|
| 0 | **20:00** | 讀 FinMind 額度錶（`--read`，不擋道） | 可見點；真正放量閘在 `_quota_gate`（#24） |
| 1 | **20:00+**（同 job） | **FinMind 核 A＋TRI**：`run_l0_hotpath_daily.sh --date <當日> --apply` | TW 收盤≈13:30；留 **盤後上架／鏡射延遲** 緩衝。**不是** 93 表。舊 16:00 已廢。20:00 仍早於結算 21:30／TWEVO 23:00 |
| 2 | **緊接①之內**（同熱路徑） | **FRED macro**：`sync_macro --no-catalog`（殼步驟 D） | 與 FinMind **同節奏、同管線、先台後美** |
| — | **勿另開第二個日中 FinMind cron** | — | 限速是 **in-process**；兩進程對外速率相加（master plan 實證註）。白天僅 Steward 明示 catch-up／audit |

**若另立「僅取數、不跑 arena」**：仍建議 **同一 20:00 窗**（或緊接其後單一 job），**不要**再掛 16:00／日間第二條。

**預測熱路徑**：不需對齊此表——庫內 as-of 即可 train／predict（PREDICT-ORTHOGONAL）。

---

## 3. 解凍邊界下「不要排」什麼

即使 API 已解凍（`API-THAW-20260804`），**預設 cron／日班不得排**：

- `TaiwanStockDividend` rebuild／歷史重抓  
- 寬窗／窄窗 probe、`refetch_fixed_tables`、放量補洞  
- `--with-dim-sync`／`--full-universe` attest（須另授）  
- 撞 403／ban 後的重試風暴；當日缺席→翌日再試  

Attestation 長窗（`audit_selfheal`／watchdog）≠ 日頻增量排程；勿與 20:00 熱路徑並行狂打。

---

## 4. 與現況 A1（額度閘）的關係

| 項 | 現況（≈2026-08-04 11:34） |
|---|---|
| A1 | `daily_maintenance --end 2026-08-04 --audit-days 14 --audit-all --heal` 仍跑；曾卡額度閘、後見續抓；**403=0** |
| A2 | `sync_macro` ✅ 已完成 |
| 紀律 | **不殺、不疊**第二支同日 `daily_maintenance`（`OPT-R3-W2PREP-A1-WATCH`／opt 計畫） |

**排程含義**：A1 未 exit 前，**今晚 20:00 cron 若再起 FinMind＝同 IP／同額度雙進程疊加**——應等 A1 終態，或當日以 `--skip-sync` 跑庫內段（人裁）。**定排程答案仍是 20:00**；操作上「本輪勿再疊」。

---

## 5. 一句答

**最佳日排程＝平日 Asia/Taipei 20:00 單一 arena 管線：先 FinMind 日頻增量，緊接 FRED `--no-catalog`；禁 Dividend／寬窗放量；A1 額度閘未清前勿再疊第二條 FinMind。**

---

*備忘日：2026-08-04。位階 [I]。*
