# INV-1：「全部落地」正式定義 [I]（2026-07-24）

* **性質**：[I] 工具／接續記憶（**非** META-CONSTITUTION [N]）
* **觸發**：Steward 明示 `INV1-LAND-MECH`
* **SSOT 盤點**：`audits/ROADMAP-LANDING-INVENTORY-20260724.md` §2–§4
* **拍板登錄**：`audits/ROADMAP-INV1-APPROVED-20260724.md`
* **凍結護欄**：`.cursor/rules/finmind-fred-api-freeze.mdc`（本定義寫入；**未**解凍）
* **正交**：`.cursor/rules/predict-vs-market-api.mdc`（**預測 ≠ 解凍**）

---

## 0. 狀態

| | |
|---|---|
| **拍板碼** | ✅ **`INV1-LAND-MECH`**（已生效） |
| **附帶碼** | **`INV2-THAW-STILL-REQUIRED`**（解凍仍須第二句明示；本輪**未**解凍） |
| **未採** | `INV1-LAND-PROD`／`INV1-DEFER` |

---

## 1. 生效定義句

> **「憲章→實作路線圖全部階段落地完成」**＝  
> **機械近程完備**（各 R 當日授權範圍＋對應 U*〔U0 deferred；U2 可另開〕＋PME／P2H 機械閉合，以 inventory §1 為準）  
> **∧** Steward **書面接受**下列殘留 **partial 另帳**（不因另帳假關產品完備／確立級／可交易）。

**本定義滿足凍結條件前提 (1) 之「全部落地」語意**——**仍須**前提 (2) **用戶明示解凍句**才開 FinMind／FRED（`INV2-THAW-STILL-REQUIRED`）。

**禁止倒果**：另帳項（G-CAT／G-DIV／G-ATTEST 等）**正是**解凍後要做的事——**不得**因「全部落地＝LAND-MECH」自稱洞已補或已可開 API。

---

## 2. 另帳清單（殘留 partial；書面接受）

> 以 inventory §1 為準；下列為 Steward 接受「另帳、不擋 LAND-MECH」之最小列清。

| ID／項 | 現況 | 另帳含義 |
|---|---|---|
| **G-CAT-1** | partial（表級 catalog STALE；db_only 欄級綠） | 全量／表級 `build_catalog` → **仍 API 門**（INV-9） |
| **G-DIV-1** | partial（Dividend live 缺股；roster PAUSED） | resume → **仍 API 門**（INV-8）；本輪**不開** |
| **G-ATTEST** | partial（史料 PASS；當日 e2e SKIP） | 窄窗 audit／heal → **仍 API 門**（INV-10） |
| **G-HAR-1** | partial（UI 完成詞／庫存 pending） | R6 庫存清 → **非** FinMind 解凍前提（INV-7） |
| **R6 S3a／HAR-ext** | pending | 未開；≠可答完備；**非**解凍前提 |
| **2026-10-14 checklist** | blocked（日曆；七項未結清） | 不假關；U2 可選（INV-6） |
| **`direction_gate.evaluated_pass=0`** | 親驗 0 | **≠確立級／≠可交易**；禁假關 |
| **R5 大標** | 近程 DONE／大標 partial | ≠ universe→model→econ 全綠 |
| **R7 產品艦隊** | S1–S2＋U7 DONE／產品 partial | ≠產品全量出貨；G-R7-1 doc-only |
| **PME G-PROM／G-ECON** | partial | 機械完備 ≠ 可交易完備 |

---

## 3. 與解凍／預測的關係

| 軸 | 效力 |
|---|---|
| **LAND-MECH 已拍** | 凍結前提 (1)「全部落地」語意＝本檔 §1 |
| **解凍** | **仍否**——缺明示句（「解凍 FinMind／FRED」等）；**INV2-THAW-STILL-REQUIRED** |
| **預測正交** | 庫內 train／predict／as-of **可跑**；**不解凍**；**≠**洞已補 |
| **LAND-PROD** | **未採**；產品大標現行證據**未達** |

---

## 4. 未採選項（對照）

| 碼 | 定義 | 為何未採／狀態 |
|---|---|---|
| **LAND-PROD** | 產品大標閉合（確立級／可答完備／產品艦隊等） | 現行證據未達；若採則不可解凍直至大標綠 |
| **INV1-DEFER** | 維持未定義＝不可解凍 | 已由 `INV1-LAND-MECH` 取代 |

---

## 5. 本輪邊界

* ✅ 定義生效＋另帳列清＋freeze rule／HANDOFF／inventory／路線圖對齊
* ✅ 拍板登錄 `ROADMAP-INV1-APPROVED-20260724.md`
* ❌ **未**解凍；**未**開 Dividend／FinMind／FRED；**未**改 [N]
* ❌ **未**假關確立級／可交易／可答完備

---

*定義日：2026-07-24。位階 [I]；入憲另開案。*
