---
title: 顧問絕對方向誠實拒答／改寫——憲政切片與未來修憲目標
status: slice_adopted_as_future_goal
layer: "[I] L5/L6 行為切片；未來目標可升 [N]（未動 MC）"
date: 2026-08-05
role: Constitution Steward 意向落檔（非 §8.5 正式議決；不改 META-CONSTITUTION [N]）
self_reported: true
depends_on:
  - constitution/META-CONSTITUTION.md
  - src/augur/advisor/prompt.py
  - src/augur/advisor/payload.py
  - src/augur/advisor/advise.py
  - reports/augur_advisor_predict_as_knowledge_plan_20260805.md
  - reports/augur_post_close_daily_asof_ops_design_20260805.md
---

# 顧問絕對方向：誠實拒答或改寫相對＋GATE 未過

> **Steward 意向（2026-08-05）**：此為**修憲級未來目標**與現行產品行為之**憲政切片**——今日碼已大致落在切片上；**未**依 §8.5 改寫 `AUGUR-MC` [N] 本文。升 [N] 另案提案＋議決。  
> **self-reported（#32a）**。

---

## 1. 一句話（未來目標＝擬入憲核）

對使用者問**絕對漲／跌、目標價、逐日路徑、方向準確率排名**時，系統**必須**二擇一（不得第三路「假確定」）：

1. **誠實拒答**——明載 `direction_gate` 狀態（通過數／判死），**不得**給可交易絕對方向機率或明牌股價；或  
2. **改寫**——僅提供**相對**真兆（`P(beat peer median | as-of, H)`／排序），並**硬綁**「**GATE 未過／不得確立絕對漲跌**」＋ `econ_verdict`（dead／thin≠可交易）。

含口語「**漲跌幅 Top N**／今天之後誰漲最多」：仍走改寫臂（相對 TopN＋disclaimer），**不得**空拒「無模型輸出」。

蒙地卡羅（`:8600/simulate`）＝**模擬情境導引**，數字**不進**對話當預測。

---

## 2. 上位錨點（現行 MC——不動 [N]，僅對齊）

| 條款 | 如何約束本題 |
|---|---|
| **PA／P1** | 無 Reality 對應之「會漲」不得當 Representation |
| **P2.E2／E3** | Model／Agent 輸出不得繞過 Evidence 通道變權威 Knowledge；self-reported 須標記 |
| **P4.E4／E5** | 「目前證據不足／GATE 未過」為**合法且必須可表達**狀態；禁止靜默消滅失敗證據 |
| **P4.E7／E8** | 高風險結論不得僅洗白自產；Confidence／消費等級受最弱環節約束 |
| **P5／F6** | 可交易級宣稱屬 Action 邊界——無授權＋無 GATE pass，不得當可執行明牌 |

本切片＝上述原則在**顧問外部介面**之落點；**不是**新設第六原則。

---

## 3. L5／顧問行為切片（現行＝義務級產品法）

```
絕對方向題
    ├─ 偵測：_asks_direction_or_path / market_binary_dir_intent
    ├─ 路徑 C：build_direction_refusal ← direction_gate 即時計數
    │         （n_pass=0 → 判死句；n_pass>0 → 仍 fail-closed 不自動可答）
    └─ 改寫臂（非絕對詞／乙案 B2）：payload.prob_note
              「相對非整 absolute」＋ GATE 未過／econ_verdict
```

### 3.1 真碼對照（切片＝描述現況，非許諾未完成）

| 行為 | 落點 |
|---|---|
| C 路誠實拒答 | `prompt.build_direction_refusal`；`advise.py` 短路 |
| 門狀態資料驅動 | `direction_gate`：`evaluated_fail`／`evaluated_pass` 計數（#29b） |
| n_pass>0 仍拒明牌 | `_compose_direction_refusal` fail-closed 保守句 |
| 相對改寫＋GATE 未過 | `payload` `prob_note`（auto_rel_topn／B2） |
| 預測進知識面（非嵌入 KH） | `reports/augur_advisor_predict_as_knowledge_plan_20260805.md` |
| 日更不因產品壓力松綁 | `reports/augur_post_close_daily_asof_ops_design_20260805.md` §5 |

### 3.2 硬禁（產品違＝切片違）

- 把 `p_beat_median` 說成「上漲機率／會漲機率」  
- GATE `evaluated_pass=0`（或 pass 未核定展示分級）時給**可交易絕對方向**  
- MC cone／`ret_p50` 寫進 chat 當預測（破四鎖）  
- 空 KH 時捏造方向填洞  

### 3.3 允許（誠實產品）

- 固定拒答句＋相對頁／模擬頁連結  
- 單股相對機率＋ `econ_verdict`＋ as-of／H 標籤  
- 「证据不足／判死」作一等公民回應  

---

## 4. 與 GATE／軸正交

| 軸 | 表／門 | 本切片 |
|---|---|---|
| **絕對方向** | `direction_gate`（H/D） | C 拒答之唯一權威狀態源 |
| **相對強度** | RankRidge／`prediction_probability`／`econ_verdict_rule` | 改寫臂；**≠** 方向 GATE |
| **Arena 入場** | `arena_admission_gate` | 正交；不替代 direction_gate |

跨軸誤植（把相對軸當絕對可答）＝違切片 §3.2。

---

## 5. 未來修憲路徑（目標，非今日施作）

| 階 | 內容 | 門檻 |
|---|---|---|
| **今** | 本切片 [I]＋產品碼維持／回歸守護 | Steward 已表「未來目標」 |
| **次** | 可選：領域大憲／原則精華加一則「顧問輸出契約」 | 領域檔 minor；MC 仍可不動 |
| **修憲** | 拟條草案（見下）入 MC 附件或 P4.E*／L5 行為規約升 [N] | **§8.5** 提案＋議決＋AL；**本日不做** |

### 5.1 拟條草案（非正式；候 §8.5）

> **［草案］顧問對外結論之方向口徑**：凡使用者請求之 estimand 為個股或市場之**絕對方向**（漲跌、目標價、逐日路徑、方向準確率排名），Agent **必须**拒絕以可交易確立級回覆，或改寫為相對強度真兆並顯式標記方向 GATE 未通過且經濟標籤非確立級。假確定、口徑洗白、模擬數入對話當預測，均屬違憲候選。

升 [N] 時須附：失效 Evidence（產品事故／對照用例）、下層衝擊（advise／guard／UI）、與 P4.E5「证据不足合法」之關係論證。

---

## 6. 驗收（切片守門；不升憲亦可跑）

1. 「2330 會漲嗎／漲或跌」→ 拒答或相對改寫；**不得**無 GATE 標籤之絕對機率。  
2. `build_direction_refusal`：`evaluated_pass` 計數可覆驗。  
3. B2／TopK `prob_note` 含相對定義＋ GATE／econ。  
4. 回歸：`verify_advisor_regression`／方向相關案不回退。  

---

## 7. 開問題清單更新（本切片後）

| # | 項 | 狀態 |
|---|---|---|
| 方向誠實拒答／改寫 | **憲政切片＋未來目標已立** | 開 → **目標軌**（碼已對齊；升 [N] 另議） |
| direction_gate pass=0 | 監控；不為日更／P6 而松綁 | 仍開（證據軌） |
| MC 升 [N] | 候 §8.5 | 未來 |

---

*完。呈 Steward：本檔＝[I] 切片與修憲目標；採納產品行為、不構成對 META-CONSTITUTION 之正式修訂。*
