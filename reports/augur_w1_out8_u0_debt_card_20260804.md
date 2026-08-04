# W1｜out 候補 8 呈裁 ＋ U0 五卡結構債清單（2026-08-04）

> **位階**：[I] 呈裁／清單。**授權**：`W1-go`。**AI 不代勾**。  
> **上游**：`reports/augur_w2_65_triage_20260804.md`；concept cards；Gold／39 已登錄（不在本五卡）。

---

## A. out 候補 8（R3）——是否踢出 K1 分母

| binding | 表 | 建議預設 | 圈選 |
|---:|---|---|---|
| 14 | `EuropeStockInfo` | out_of_scope（名冊） | ☑ **踢出 K1**（`OUT8-kick-all-go` · 2026-08-04） |
| 22 | `JapanStockInfo` | 同上 | ☑ **踢出 K1** |
| 33 | `TaiwanStockInfoWithWarrantSummary` | 同上 | ☑ **踢出 K1** |
| 36 | `USStockInfo` | 同上 | ☑ **踢出 K1** |
| 58 | `TaiwanStockInfoWithWarrant` | 同上 | ☑ **踢出 K1** |
| 67 | `TaiwanSecuritiesTraderInfo` | 同上 | ☑ **踢出 K1** |
| 84 | `TaiwanStockNews` | 同上 | ☑ **踢出 K1** |
| 91 | `UKStockInfo` | 同上 | ☑ **踢出 K1** |

**整批捷徑（已採）**：`OUT8-kick-all-go` → 登錄 `audits/OUT8-N7-043-CUTS-20260804.md`。

---

## B. U0 剩餘五卡結構債（R4）——可登／俟／不登

| 卡 | binding | 鍵（提案） | 主債 | 建議／定案 |
|---|---:|---|---|---|
| U0-1 | 7 | `tw.convertible_bond.terms` | W2-1 多欄 | ☑ **登(a)** → EXECUTED（`U0-CIRCLE-765`） |
| U0-2 | 37 | `jp.daily_bar` | Q-R8；W2-3 Adj_Close | ☑ **STRUCT＝俟｜jp-ok**（零寫庫；出口＝`Q-R8=jp-ok`→另 REGISTRY-GO） |
| U0-4 | 65 | `tw.option.institutional_flow.after_hours` | W2-1；列鍵 | ☑ **登(a)** → EXECUTED |
| U0-5 | 80 | `tw.corporate_action.split` | W2-5 同表兩概念 | ☑ **STRUCT＝俟拆｜登事件欄**（零寫庫；先拆綁定→未來登事件欄） |
| U0-6 | 97 | `tw.futures.daily_bar` | W2-6／Q-R7 全 PK | ☑ **STRUCT＝俟偵測器｜不登**（零寫庫；偵後再裁 map 或終局不登） |

**Steward STRUCT（2026-08-04）**：`U0-STRUCT: 37=俟|jp-ok ; 80=俟拆|登事件欄 ; 97=俟偵測器|不登`  
→ `audits/U0-STRUCT-378097-20260804.md`；備料 `reports/augur_u0_struct_next_paths_20260804.md`。

**已登錄（對照）**：U0-3 binding 50 `cm.gold.spot_price` ✅；HP-39 ✅；U0-1／U0-4 ✅。

---

## C. 不做

- OUT8 已踢出見 `OUT8-N7-043-CUTS`；本節不再等人勾。  
- U0 37／80／97：**STRUCT 已定仍俟**——不寫 Registry、不發 honesty，直至各出口 go／REGISTRY-GO。  
