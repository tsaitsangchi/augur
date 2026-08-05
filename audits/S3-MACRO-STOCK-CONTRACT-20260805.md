---
status: contract_accepted
series: s3_macro_stock
go: audits/S3-MACRO-STOCK-CONTRACT-GO-20260805.md
parent_plan: reports/augur_s3_n3_xsec_macro_dual_track_plan_20260805.md
date: 2026-08-05
layer: "[I]"
self_reported: true
---

# CONTRACT｜股級 macro 候選（≤3 名）· 2026-08-05

> **效力**：M1 契約已採納——**准許後續另貼** `S3-MACRO-STOCK-BUILD-go` 依本表實作；**本檔自身零碼零寫庫**。  
> **軌 X**：β5_stop 維持（不開 `#11`／不重跑 Wave-B 四名）。  
> **self-reported（#32a）**。

---

## 1. 問題與邊界

| 是 | 不是 |
|---|---|
| 經 `macro_vintage.as_of` 的 macro×股異質候選 → `feature_candidate_values` | 把 VIX 複製到每列就當「股級生產特徵」進 prodset |
| 月頻 panel（對齊 `feature_values`／core as-of） | 日頻 broadast 冒充 FV |
| 缺列誠實（#1） | median-fill／forward-fill 假齊 |
| skip-sync、庫內 as-of | 本契約解凍 FRED 放量 |

**與旁路分工**：`market_direction_feature`＝市場日面板（已＠08-04）；本契約＝**股×macro 候選**，不雙寫同一名義進兩表當兩套權威。

---

## 2. 選定 ≤3 名（凍結定義）

| # | feature | 異質級 | 定義（契約） | series／原料 |
|---|---|---|---|---|
| **1** | `stock_beta60_x_vix` | **強** | 同 panel：股對 TAIEX 過去 **60 交易日**日報酬 OLS β（`TaiwanStockPriceAdj`／TRI TAIEX，兩端 `date≤panel`）× `macro_vintage.as_of(VIXCLS, panel).value` | VIXCLS（Tier A）＋價 |
| **2** | `stock_ret20_x_t10y2y_chg` | **中** | 股 `ret_20d`（與 panel builder 同口徑、≤panel）×（`T10Y2Y` as-of panel − as-of **前一核心 panel** 之差；首 panel 缺列） | T10Y2Y（Tier A）＋價 |
| **3** | `mkt_vix_broadcast` | **弱／對照** | 全宇宙同值：`macro_vintage.as_of(VIXCLS, panel).value` 寫入每股候選列；**provenance 標記 broadcast** | VIXCLS only |

### 2.1 明確不選（本契約外）

- Tier B（UNRATE／CPI／GDP…）首輪不做——vintage 門已備，但股異質假說未收斂，避免一次灌月季落後噪音。  
- `industry_ret_exmkt × spread`——留 M2＋ 擴展；需產業日曆對齊另驗。  
- 任何直 SQL `fred_series` 而不經 `macro_vintage`。

---

## 3. PIT／可見性規則（#8）

| 規則 | 內容 |
|---|---|
| **唯一消費門** | 全部 FRED 讀取＝`augur.features.macro_vintage.as_of(cur, series_id, panel_date)` |
| **Tier A** | 模組內建 T−1 保守截止；不得自行改 lag |
| **價／β 窗** | 僅用 `date ≤ panel_date` 之交易日；β 不足 60 有效點→**該股該 panel 缺列**（不補 0） |
| **visible_date（候選列）** | 建議＝`max(panel_date, macro_obs_visible_bound)`；實作於 BUILD 帳釘死一式並自測 |
| **禁** | `realtime_start` 不理；用最新修訂扮歷史 |

---

## 4. 宇宙／頻率／落表

| 項 | 契約 |
|---|---|
| 宇宙 | `core_universe_asof` 於該 `panel_date` 之股票 |
| 頻率 | 與現有 `feature_values` **月頻 panel** 對齊（`build_feature_panel` 所用日期集） |
| 落表 | **僅** `feature_candidate_values`（新名）；**不**寫生產 `feature_values` |
| 冪等 | 同 `(panel_date, stock_id, feature)` DELETE+INSERT 或等價 upsert |
| 對照臂 | `#3` 必須產出；IC 判讀須分開「強／中」vs broadcast，禁把 broadcast 綠洗成異質成功 |

---

## 5. (a)(b) 實作規畫（BUILD 波才寫碼）

| 件 | 路徑 |
|---|---|
| library | `src/augur/features/macro_stock.py` — `build_candidates(conn, panel_date, stock_ids) -> rows` |
| CLI | `scripts/build_macro_stock_candidates.py --run --since … --until …`（skip-sync） |
| 註冊名 | `feature_candidate.py` 或平行 registry 串進 validate（BUILD GO 定） |
| 自測 | `macro_vintage` 既有 selftest＋本模組無 DB 單元（β／ret 公式純函式） |

---

## 6. 驗收尺（分波）

### M1（本檔）— 已達成

- [x] ≤3 名凍結定義  
- [x] PIT／缺列／broadcast 對照寫明  
- [x] β5／X 軌不開  

### M2（`S3-MACRO-STOCK-BUILD-go`）

- 三名材料化列數＋覆蓋率誠實帳（缺列率）  
- pan-hist／as-of IC（H20／H60）；**broadcast 與異質分表**  
- 零 prodset、零 median-fill  

### M3（`S3-MACRO-STOCK-VERIFY-go`）

- 僅對 **HAC \|t\|≥2** 之**異質名**（預設不對 broadcast 升 #11）跑 `verify_candidate_promotion --keep`  
- 多 seed Δ 規則同 Wave-B：**穩定為正才**建議提拔；否則維持候選  

### M4

- prodset 另句（極高）；本契約不預授  

---

## 7. Paste-ready 下一句

```text
S3-MACRO-STOCK-BUILD-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# implements: audits/S3-MACRO-STOCK-CONTRACT-20260805.md §2 names 1–3
# target: feature_candidate_values only; no prodset; no Tier-B
```

---

## 8. 對照開問題 #3

| 子項 | 本契約後 |
|---|---|
| 股級 macro SKIP 根因 | **契約已立** → 待 BUILD 才閉材料化缺口 |
| xsec 晉升 | **仍 β5**；不在本 GO |

*完。CONTRACT accepted＝M1。*
