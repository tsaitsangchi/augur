# U0 五卡圈選呈請（U0-circle-ask · 2026-08-04）

> **位階**：[I] 呈請。**授權**：`OPT-R3-W2prep-go`＋`U0-circle-ask`。  
> **AI 不代勾**。寫庫須另句 `REGISTRY-GO`＋新 honesty。  
> **底稿**：`reports/augur_w2_concept_cards_hot39_u0_20260804.md`；債表：`reports/augur_w1_out8_u0_debt_card_20260804.md` §B。  
> **已登錄對照**：HP-39、U0-3（Gold）——不在本呈請。

---

## 請回一句（整批或逐卡）——**本呈已結**

**整批示例（史料）**：

```text
U0-CIRCLE: 7=登(a) ; 37=俟 ; 65=登(a) ; 80=俟拆 ; 97=俟W2-6
```

---

## 圈選表

| 卡 | binding | 提案鍵 | 主債 | 建議預設 | 你的圈選 |
|---|---:|---|---|---|---|
| U0-1 | **7** | `tw.convertible_bond.terms` | W2-1 | 登(a) 或俟 | ☑ **登(a)**（`U0-CIRCLE`）→ EXECUTED |
| U0-2 | **37** | `jp.daily_bar` | Q-R8／W2-3 | 俟（或 `Q-R8=jp-ok`） | ☑ **俟｜jp-ok**（`U0-STRUCT`） |
| U0-4 | **65** | `tw.option.institutional_flow.after_hours` | W2-1／列鍵 | 登(a) 或俟 | ☑ **登(a)** → EXECUTED |
| U0-5 | **80** | `tw.corporate_action.split` | W2-5 | 俟拆第二 binding | ☑ **俟拆｜登事件欄**（`U0-STRUCT`） |
| U0-6 | **97** | `tw.futures.daily_bar` | W2-6／Q-R7 | 俟偵測器 | ☑ **俟偵測器｜不登**（`U0-STRUCT`） |

**Steward CIRCLE**：`U0-CIRCLE: 7,65=登(a) ; 37,80,97=俟`  
**dry**：`audits/U0-CIRCLE-765-20260804.md`  
**EXECUTED（7／65）**：`audits/U0-CIRCLE-765-EXECUTED-20260804.md`（`REGISTRY-GO`＋honesty 已消費）。

**Steward STRUCT（37／80／97 · 2026-08-04）**：

```text
U0-STRUCT: 37=俟|jp-ok ; 80=俟拆|登事件欄 ; 97=俟偵測器|不登
```

- 詮釋：`|`＝具名退出、主狀態仍俟；**今日零 Registry**。  
- 留痕：`audits/U0-STRUCT-378097-20260804.md`  
- 備料：`reports/augur_u0_struct_next_paths_20260804.md`

---

*本檔＝ask 已結；7／65 寫庫見 EXECUTED；37／80／97＝STRUCT 俟＋出口、零寫庫。*
