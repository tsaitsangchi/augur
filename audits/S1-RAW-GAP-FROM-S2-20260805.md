---
status: expand_executed_20260805
executed: audits/LOOP-S2-TO-S1-EXPAND-EXECUTED-20260805.md
series: c1_arc_b
depends_on:
  - reports/augur_s1_s2_s3_closed_loop_plan_20260804.md
  - audits/S2-KH-BACKLOG-20260804.md
  - reports/augur_s3_features_for_market_model_families_20260804.md
  - audits/S3-WAVE-B-EXECUTED-20260804.md
  - audits/API-THAW-20260804.md
live_refresh: 2026-08-05T11:58+08:00
self_reported: true
---

# S1 RAW GAP FROM S2｜C1 Arc B · 2026-08-05

> **位階**：[I] Arc B 產出（raw gap list）——**零 API sync**、**零 build**、**零 INSERT**。  
> **觸發證據**：B1（S2 backlog 組 8／9／13）＋B2（S3-B 股級 macro SKIP；xsec 未晉升）＋B3（S4 C/D/E SKIP＝契約／邊缺，非本表默授放量）。  
> **下一步**：Steward 貼 `LOOP-S2-TO-S1-EXPAND-go`（見同日 GO 草稿）後，僅得執行本表 `thaw_daily` 白名單項。  
> **self-reported（#32a）**；`in_db_now`＝本窗 live SELECT。

---

## 0. LIVE 錨（2026-08-05）

| 錨 | 值 |
|---|---|
| `TaiwanStockPriceAdj` max／TAIEX | **2026-08-04** |
| Institutional／Margin／Lending max | **2026-08-04** |
| `feature_values` max panel／distinct feature | **2026-08-04**／**38** |
| `core_universe_asof` max | **2026-08-04** |
| `prediction_probability` max | **2026-08-04** |
| `market_direction_feature` max | **2026-07-31**（落後價日 **3** 交易日級） |
| `macro_vintage`／`fred_observation` | **無表** |
| `fred_series` | **有**（名冊；≠觀測落地） |
| Dividend（tw／TaiwanStockDividend） | **無表／未落地** |
| `TaiwanStockIndustryChain` | **51,124** 列（覆蓋債≠新 sync） |

**predict 影響**：上列熱路徑價／籌碼 **have＠D** → 預測熱路徑**可**續跑（⊥ live API）。缺口主要在 **macro PIT 落差**、**股級 macro SKIP**、**圖邊／序列契約**、**Dividend 另帳**。

---

## 1. Raw gap list

| gap_id | from_arc_a | raw_need | in_db_now | expand_class | s1_action | predict_impact |
|---|---|---|---|---|---|---|
| **RG-PX-COV-01** | 組 1–4 價量 | PriceAdj 日頻至庫內 D | **have**＠08-04 | `thaw_daily` | 納入日後 standing／arena 日鏈 heal；缺口＝滯後日告警 | 可續跑 |
| **RG-CHIP-COV-02** | 組 7 籌碼 | Institutional／Margin／Lending 至 D | **have**＠08-04 | `thaw_daily` | 同日頻白名單；覆蓋誠實 | 可續跑 |
| **RG-DIR-PIT-03** | 組 9／10；S3-B | `market_direction_feature` panel＝價日 D | **partial**＠07-31（價＠08-04） | `thaw_daily` | **EXPAND 優先**：`--skip-sync` 刷新方向特徵至與 PriceAdj 對齊；**不解凍放量** | 可續跑；方向旁路 as-of 誠實落後 |
| **RG-MACRO-SER-04** | 組 9 P0 | FRED／macro **觀測**＋PIT／vintage | **partial**：`fred_series` 有；觀測／`macro_vintage` **missing** | `thaw_daily`（`sync_macro --no-catalog`）＋概念先 | 計畫：THAW-bounded macro heal；**禁**當 NF／放量藉口；股級特征仍另 `S3-WAVE-*` | 可續跑（股級 macro 已 SKIP） |
| **RG-MACRO-XSEC-05** | 組 9；S3-B SKIP | 股級 macro→`feature_values` 原料契約 | **missing**（FEATURE 誠實 SKIP） | `narrow_auth`／builder 債 | **不做**本 EXPAND 默授；記「特徵／S3 另句」；勿假綠 | 可續跑 |
| **RG-XSEC-INFO-06** | 組 8；Wave-B 候選 | Info／產業欄覆蓋（相對化原料） | **partial**：Info＋IndustryChain 在；xsec **未**進 prodset | `thaw_daily`（覆蓋）／S3 晉升另 | S1＝Info as-of 覆蓋稽核；晉升≠本 GO | 可續跑 |
| **RG-SEQ-WIN-07** | 組 12；S4-C/D SKIP | 多通道長窗價量深度 | **partial**：價有；序列 **契約**缺 | `defer_infra`／`narrow_auth` | 記帳；禁寬窗 probe；對齊 S3-D plan | 可續跑；族 SKIP 不變 |
| **RG-GRAPH-08** | 組 13；S4-E SKIP | 同業／相關**邊產物** | **missing** 邊 | `defer_infra` | 概念＋S3-D；**非** sync 放量 | 可續跑；GNN SKIP |
| **RG-DIV-09** | G-DIV 另帳 | Dividend／還原股利鏈 | **missing** 表 | **`dividend_auth`** | **待另句**；不入本 EXPAND 執行集 | 可續跑（現用 PriceAdj） |
| **RG-LOB-NLP-10** | 組 14–15 | LOB L2／未授權 NLP raw | N/A／gated | `wide_forbid` | **不做** | 可續跑 |

---

## 2. EXPAND 執行集（本 GO 授權範圍｜候裁）

僅下列得在 `LOOP-S2-TO-S1-EXPAND-go` 後執行（仍 THAW-bounded／#24／403→停）：

| 優先 | gap_id | 建議動作（概念） |
|---|---|---|
| **P0** | RG-DIR-PIT-03 | 刷新 `market_direction_feature`（及依賴）使 `max(panel)≥PriceAdj.max`；skip-sync 優先 |
| **P0** | RG-MACRO-SER-04 | `sync_macro --no-catalog`（窄／白名單 series）；寫 as-of 帳；**不**造股級 feature |
| **P1** | RG-PX-COV-01／RG-CHIP-COV-02 | 若 D 落後價源：日頻 heal（可併 arena／standing A 車道） |
| **P1** | RG-XSEC-INFO-06 | 唯讀覆蓋稽核＋記帳；不強晉升 prodset |

**明確排除（另句）**：RG-MACRO-XSEC-05 特徵 build、RG-SEQ／GRAPH 契約實作、RG-DIV、RG-LOB、NF-pause 新族、β5、sim `--apply`、kill A1。

---

## 3. 另帳清單（不混入 EXPAND）

| 項 | 原因 |
|---|---|
| Dividend rebuild | `dividend_auth` |
| 股級 macro→feature_values | S3 builder／`S3-WAVE-*-go` |
| S3-D 序列／圖邊 | plan→另 GO |
| 寬窗／放量／`--with-dim-sync` | 顯式另授 |
| NF 新族／ARIMA P1 | `NF-pause` |
| 方向 GATE 升格 | 監控；憲政切片禁假確立 |

---

## 4. Paste-ready GO

```text
LOOP-S2-TO-S1-EXPAND-go | FZ/GATE-keep | NHC-keep | API-THAW-bounded | no-SIM-apply
# scope: audits/S1-RAW-GAP-FROM-S2-20260805.md §2 P0–P1 only
# exclude: Dividend / wide-sync / dim-sync / S3 feature build / NF-pause lift
```

對應 GO 草稿：`audits/LOOP-S2-TO-S1-EXPAND-GO-20260805.md`（候 Steward 裁 adopt）。

---

## 5. 驗收（執行波）

1. §2 各項：as-of 書面 ≥ 觸發日價錨，或誠實 `still-gap`。  
2. `market_direction_feature.max` **不再**系統性落後 PriceAdj（或記延期理由）。  
3. 預測／顧問 as-of **不因**本波被硬閘。  
4. 零 Dividend／零放量／零假 339 齊。

*完。Arc B list。*
