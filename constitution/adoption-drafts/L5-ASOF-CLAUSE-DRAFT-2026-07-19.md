# L5 as-of 消費條款草案 ＋ 重採認前置包 [I]——呈 Steward 審

* **日期**：2026-07-19｜**性質**：草案，未經 Steward 核示不入 [N]。RULING-2026-019 決策二「L5 矩陣重作」之最後一塊。
* **緣起**：L5 首審三鏡＋矩陣重作窮舉查獲——**6 處矩陣列宣稱 as-of／雙時間／anti-leakage 落於 L5.2，但 L5.2 本文零 as-of 內涵（幽靈落點）**。即：L5 號稱消費 as-of 推理，卻無承載該義務之 [N] 條款。矩陣機械補列已標「待補」；本草案補此**真落點**。

## 一、問題精確化

| 幽靈列 | 宣稱 | 實況 |
|---|---|---|
| LDI.5／LDO.5 | 承接 KS KDO.6 之 as-of gate → L5.2 | L5.2＝Evidence 引用鏈完整性，無 as-of |
| TR.A §P4.E2 | 雙時間性承接 → L5.2 | 同上 |
| TR.C WM.30–31 | 雙時間/as-of 存在層宣告 → L5.2 | 同上 |
| TR.C HOOK-01 | anti-leakage（vintage/發布日 gate）→ L5.2 | 同上 |
| D22 | 核心宇宙 gate 受 L5.2 as-of 約束 | 無 as-of 紀律可約束 |

**分工前提（不變）**：as-of **重建機制**由 Layer 4（`AUGUR-KS v1.1 §5` KS.40–46）定義、其查詢引擎實作下放（KDO.6→L5/L7）；**L5 為推理層，消費該能力、不重定義機制**。缺的是「L5 之推理如何受 as-of 邊界約束」之條款。

## 二、擬新增條款（呈審）

> **L5.10（as-of 推理消費——推理之時間邊界與 anti-leakage）[N｜carries｜`AUGUR-MC v1.4 §P4.E2`；refines｜`AUGUR-KS v1.1` KS.40–KS.46；承接｜`AUGUR-KS v1.1` KDO.6 之 L5 面向]**
> 本規格之 Inference **消費**上游 Layer 4（`AUGUR-KS v1.1 §5` KS.40–KS.46）所定之 as-of 重建能力等級，**不重定義**重建機制。凡以 as-of 時點 T 為基準之推理：
> **(a) 時間邊界**：結論所引之全部 Evidence／Knowledge 節點，其 valid time／發布日（vintage）**必須** ≤ T（`§P4.E2` 雙時間性）；納入 vintage ＞ T 之節點（未來洩漏／lookahead）者，**不得**產出 as-of T 之結論。
> **(b) anti-leakage 消費**：purged／embargo／發布日 gate 之判定由 KS §5 能力等級與其下放之查詢引擎（`KDO.6`→L5/L7 實作）供給；本層**必須**於推理入口以該 gate 過濾輸入，未過濾即納入者違反本條。
> **(c) 能力等級透明**：as-of 重建之能力等級（KS.40–46 之 A0–A3）**必須**隨結論標示；能力等級不足以支持所宣稱 as-of 精度者，結論之 as-of 宣稱降級或標 provisional。
> **義務主體**：本規格、Reasoning 引擎、Layer 5–7 承載構件。**可判定判準**：存在任一 as-of T 推理，其輸入 Evidence 集含 vintage ＞ T 之節點、或未經 KS §5 as-of gate 過濾者，違反本條（機器可判：對每一 as-of 結論之輸入集掃描 vintage vs T）。

**性質**：refines/carries 既有上層（不新增規範內涵，將 §P4.E2＋KS §5 之 as-of 於 L5 推理面**機制化落點**）；填 6 幽靈之真落點。

## 三、簽核後之施作（機械）

1. 新增 L5.10（上文）於 L5.9 後、L5.90 前。
2. 6 幽靈列之「L5.2〔as-of 待補〕」→ 改指 **L5.10**（真落點）。
3. TR.F 之 KS §5 列「as-of 落點待補」註記 → 改指 L5.10。
4. gate＋selftest＋G5 複驗。

## 四、L5 重採認前置——兩件齊備

L5 回復完整 v1.0（自 provisional·充任暫停）之前置＝(甲) 矩陣重作〔**已機械完成**：TR.F 補 KS 16 區塊＋D1-6＋版本〕＋(乙) **本 as-of 條款**〔呈審〕。二者 Steward 核可後，L5 即備齊重採認（§8.2/§8.6）之全部要件。

## 五、簽核

> **請 Steward 核示**：
> - [ ] **准 L5.10 入 [N]**（幕僚據以施作＋重指幽靈＋G5）
> - [ ] 修改意見：＿＿＿
> - [ ] （另）L5 重採認（§8.2/§8.6）——待 L5.10 施作＋G5 綠後
