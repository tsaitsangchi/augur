# PME-XDOM-SOLAR ← KH10 核准四筆（2026-07-31）

> **位階**：[I] 計畫書＋SEED（#20）  
> **觸發**：Steward 採納並實作計畫 `PME Solar KH10`（KH10 id 2／3／9／18 → principle／map → PME 全鏈）  
> **拍板碼（本輪執行授權）**：`PME-XDOM-SOLAR-go`＋`PME-XDOM-SOLAR-S1`＋`FZ-keep`＋`GATE-keep`＋`NHC-keep`  
> **SEED**：下列 §三全文＝呈核 SEED；實作採納＝`SEED-SIGN-off`（實作指令等同簽核；你可另改字後重跑 curate）  
> **APPLY prodset**：另須 `PME-APPLY-go`（本計畫 Phase C 閘後才開）

---

## 一、範圍

| KH10 id | ledger | 探針 | 本輪 |
|---|---|---|---|
| 2 | 1 | RKI-FP-AI-SOLAR（KH7） | 進 SEED K1 |
| 3 | 2 | RKI-FP-SOLAR-CORE（KH7） | 進 SEED K2 |
| 9 | 3 | RKI-AI-SOLAR-RD（KH7） | 進 SEED K3 |
| 18 | 4 | RKI-FP-AI-SOLAR（KH6） | 併入 K1（同假說軸；downstream 雙掛） |
| 16／19–23 | deferred | SOLAR 旁支 | **不進** |

**載體 school（live 實查）**：`solar_supply_invest`（school_id=160，`domain=investment`）——已有 H1–H6＋map（provenance `xdom_loop=solar`）。本輪**不重寫 H1–H6**；只追加 KH10 橋接原則 K1–K3。

**紅線**：不灌 ERP／漿料 raw；不以 RKI cite／merged_hits 當 G-PROM；factor 只掛 `feature_values` 既有欄。

---

## 二、表／程式（完整性）

| 用途 | 表 | 程式 |
|---|---|---|
| 讀 | `knowhow_evolution_candidate`／`knowhow_governance_ledger`／`feature_values`／`philosophy_school` | — |
| 寫 | `philosophy_source`／`philosophy_principle`／`principle_factor_map`／`principle_domain_map`；ledger.`downstream_ref` | `scripts/curate_pme_xdom_solar_map.py` |
| 閘 | `evolution_run`／`promotion_queue`／`evolution_coverage_snapshot` | `run_philosophy_evolution.py --local-gates` |
| 促升 | `evolution_production_feature_set`／`evolution_apply_log` | `apply_evolution_promotions.py`（**僅** `PME-APPLY-go`） |

---

## 三、SEED（[DRAFT→SIGNED by implement]）

**School**（既有，不新建）：`solar_supply_invest`

**Sources**（冪等；與庫內既有報告並存可加）：

1. ITRPV, International Technology Roadmap for Photovoltaic, 14th ed., 2023 — report  
2. Fraunhofer ISE, Photovoltaics Report, 2024 — report  
3. BloombergNEF, Solar Supply Chain — Module Cost Dynamics and Manufacturing Capacity, 2023 — report  
4. Hastie, Tibshirani & Friedman, The Elements of Statistical Learning, 2nd ed., 2009 — book  
5. Marcos López de Prado, Advances in Financial Machine Learning, Wiley, 2018 — book  

**K1**（KH10 2＋18 · FP×AI×Solar）

- statement: 「第一性拆解 × 可證偽 ML 紀律（ESL／AFML）——太陽能技術核心假說須落成可觀測估值／成長／低噪代理，禁黑箱專答樹。」  
- hypothesis: `pe_ratio` 越低、`monthly_revenue_yoy` 越高、`volatility_60d` 越低 → 未來報酬假說（pe−／yoy＋／vol−）。  
- factors: `(pe_ratio,-1)`, `(monthly_revenue_yoy,1)`, `(volatility_60d,-1)`  
- domain_note domain=`materials_rd`: 將第一性＋模型進化探針對映為投資可觀測代理；**非** G-PROM 資格。  
- kh10_candidate_ids: `[2,18]`

**K2**（KH10 3 · FP Solar Core）

- statement: 「第一性列技術核心 → 品質／財務耐震（ITRPV 良率與成本學習曲線精神）——核心能力體現於毛利分位與低槓桿。」  
- hypothesis: `gross_margin_pctile` 越高、`debt_ratio` 越低 → 未來報酬假說（margin＋／debt−）。  
- factors: `(gross_margin_pctile,1)`, `(debt_ratio,-1)`  
- domain_note domain=`materials_rd`  
- kh10_candidate_ids: `[3]`

**K3**（KH10 9 · AI×Solar RD）

- statement: 「AI 模型進化強化材料研發 → 供應鏈贏家獲機構／資本效率認可（BNEF 產業鏈投資流向概念）。」  
- hypothesis: `institutional_net_buy_ratio_20d` 越高、`roe` 越高 → 未來報酬假說（inst＋／roe＋）。  
- factors: `(institutional_net_buy_ratio_20d,1)`, `(roe,1)`  
- domain_note domain=`ai_ml`  
- kh10_candidate_ids: `[9]`

**provenance（每 map）**：

```json
{
  "xdom_loop": "solar",
  "curate": "pme_xdom_solar_kh10_s1",
  "plan": "augur_pme_xdom_solar_from_kh10_plan_20260731",
  "kh10_candidate_ids": []
}
```

（各原則填入對應 ids。）

---

## 四、分階／驗收

| 階 | 內容 | 驗收 |
|---|---|---|
| A | 本檔 | 已落 |
| B | `curate_pme_xdom_solar_map.py` selftest＋dry-run | 綠 |
| B′ | `--apply` | K1–K3 冪等；ledger 1–4 `downstream_ref` 非空 |
| C | `--local-gates --dry-run`→正式 | 雙綠清單或誠實零雙綠 |
| D | `PME-APPLY-go` 後 APPLY | 僅雙綠；prodset 親驗；≠可交易 |

---

## 五、不做

AI 靜默 INSERT 異於本 SEED 之正文；無閘雙綠硬促升；解凍 API；defer 六筆；漿料 raw feature。

## 修訂

| 日 | 說明 |
|---|---|
| 2026-07-31 | 初版；對齊 live school 160；KH10 四筆→K1–K3 |
