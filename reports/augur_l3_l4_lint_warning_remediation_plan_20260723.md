# L3／L4 constitution_lint warning 處理計畫

**日期**: 2026-07-23 ｜ **性質**: plan-first（#20）｜ **觸發**: 摸底見 L3＝47、L4＝39 warning，Steward 指示「要先處理」  
**範圍**: `specs/IDENTITY-SPECIFICATION.md`（L3）、`specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md`（L4）＋必要時 `tools/constitution_lint`  
**不做**: 變更元憲章判準；不把 warning 靜默降級成「當通過」；不開顧問／預測活躍計畫直到本計畫拍板或明確延後

---

## 0. 三十秒診斷（已實跑）

`python3 -m tools.constitution_lint report`：**七層 error＝0／PASS**；warning **不阻斷生效**。

| 層 | warning 數 | 組成（實測） |
|---|---|---|
| L3 Identity | 47 | **1× WM.44** 覆蓋缺口（58/102 MC [N] 未出現於聲明文本）＋ **46× WM.44-LABEL**（代號 `A.*`／`T.*`／少數 `§DI`/`§DO`/`§EO` **無法解析＝未受檢**） |
| L4 Knowledge | 39 | **1× WM.44** 覆蓋缺口（66/102）＋ **38× WM.44-LABEL**（多為 `IDO.1–8` 被當成 `AUGUR-IDO` 獨立規格；另有 `A.*`） |

**教義（lint README／selftest）**：`未受檢 ≠ 已比對且通過` → 發 **WARNING 留痕為正辦**；規格【地位】亦承認「形式充分性完備性機械強制待決策四第二輪」。故現況不是「壞掉了」，是 **骨架期誠實欠帳**。

---

## 1. 根因三桶（勿混為一談）

### 桶 A — 本層 Annex 代號閘門看不懂（L3 大宗）
- Annex TR 列了 **`A.0–A.29`、`T.*`**（對照系統架構大憲章 Annex A／ONT 型別等），**不是** MC／WM／ONT／ID 的標準條款編號形態。
- Lint 正確拒絕「假通過」→ WARNING。
- **修法選項**：TR 改引用可解析代號（`ID.*`／`ONT.*`／`§…`）；或 Steward 裁定「跨檔 Annex 別名對照表」入 lint（造法，須拍板）。

### 桶 B — IDO 掛鉤枚舉／權威來源錯置（L4 大宗）
- `IDO.0–IDO.8` **活在** `AUGUR-ID` Annex DO（表格列），**不是**獨立 `AUGUR-IDO` 規格。
- Lint `SPEC_PREFIXES` 含 `IDO` → 查找權威時期待 `AUGUR-IDO` ∈ front-matter `upper-specs` → 永遠找不到。
- 且 `enumerate_spec_clause_labels` **只抽出 IDO.0**（標題體）；**IDO.1–8 在 markdown 表內，未被枚舉為獨立條款標籤**。
- **修法選項（建議優先）**：lint 機械修正——`IDO.*` 權威歸 `AUGUR-ID`；表列 IDO.1–8 納入標籤枚舉；KS 的 `upper-specs` 已有 ID 即可受檢。

### 桶 C — WM.44 母集覆蓋骨架（各層 1 條）
- 「102 條 MC [N] 是否皆在聲明文本出現」現為 **warning 級覆蓋報告**；完全強制＝總綱階段 1+（嚴格枚舉／DEFER／不觸及）。
- L3 缺約 58、L4 缺約 66（樣本多為 `EV.*`）。
- **修法選項**：Compliance／Annex TR 補「不觸及＋理由」或 DEFER 掛鉤（規格編修，量大、須逐條人審）。

---

## 2. 對應 schema／程式規畫（憲章計畫完整性）

| 產物 | 角色 |
|---|---|
| 表 | **無新 DB 表**；只動規格 Markdown＋lint 程式 |
| `tools/constitution_lint/mc_clauses.py` | 擴充：自 ID 規格表列抽取 `IDO.n` 標籤；必要時別名對照（若拍板桶 A） |
| `tools/constitution_lint/compliance_lint.py` | `IDO.*` → 權威來源 `AUGUR-ID`（當 ID ∈ upper-specs）；selftest 突變鎖 |
| `tools/constitution_lint/selftest.py` | 鎖：IDO.1 在 ID∈upper-specs 時可解析；禁靜默 continue |
| `specs/IDENTITY-SPECIFICATION.md` / `KNOWLEDGE-SYSTEM-SPECIFICATION.md` | 僅在拍板「規格補列」時改 Annex TR／不觸及列（#19 一支一支） |
| 驗收指令 | `python3 -m tools.constitution_lint selftest`；`compliance` L3／L4；`report` 警告數下降且 **error 仍 0** |

---

## 3. 建議分期（請拍板）

| 階段 | 內容 | 預期 warning 下降 | 風險 |
|---|---|---|---|
| **P0 清冊**（已完成於本報告） | 分類三桶＋根因 | 0（只診斷） | 無 |
| **P1 lint 機械修（桶 B）** | IDO→AUGUR-ID；表列 IDO.1–8 入標籤宇宙；selftest | L4 約 −8～38（視標籤比對是否過） | 低；不改治權判準 |
| **P2 規格 TR 對齊（桶 A）** | L3 Annex TR：`A.*`/`T.*` 改可解析代號或正式別名表（Steward 裁定） | L3 大幅下降 | 中；規格編修＋#19 |
| **P3 WM.44 覆蓋（桶 C）** | 逐條補 DEFER／不觸及／承接（決策四第二輪） | 各層 −1 覆蓋警告＋實質完備 | 高工作量；決策層 |

**建議預設拍板**：**先做 P1（桶 B）** → 再決定 P2／P3。  
**禁止**：為消 warning 而改 severity、或把未受檢改成靜默 skip。

### P1 落地（2026-07-23，已實跑）

- lint：`mc_clauses` 表列枚舉 IDO.1–8；`compliance_lint` 將 `IDO` 權威歸 `AUGUR-ID`（非 `AUGUR-IDO`）；selftest **G12**
- 規格（僅 TR 標籤對齊 ID 原文，**未改判準**）：KS IDO.5／IDO.7；L5 IDO.5（原「去識別化／tombstone」誤植）
- 驗收：`selftest` 全綠；`report` PASS／error 0；L4 warning **39→31**、L5 **18→12**；KS 無「AUGUR-IDO 未見於 upper-specs」

### P2 落地（2026-07-23，已實跑）

- lint：`SPEC_PREFIXES` 增 `A`／`T`／`DI`／`DO`／`EO`；`_PREFIX_HOME` 權威歸 WM／ONT；表列 DI／DO 併入枚舉；selftest **G13**
- 規格（TR 標籤對齊原文，**未改判準**）：L3 具名 T 列；L5 `A.10`／`A.11–A.18`／`A.19`／`A.20–A.47`／`A.52`
- 驗收：L3／L4 warning 各剩 **1**（僅 WM.44 覆蓋缺口＝桶 C）；七層 **PASS／error 0**

### P3 落地（2026-07-23，已實跑）

- **根因**：`_check_wm44` 只掃 compliance front-matter **之後**；Annex TR 在 CS 之前者不計入字面覆蓋。
- **作法**（對齊 L7 先例，**不改 severity／不改 MC 宇宙**）：於 L1 C.10／L2 CS.10／L3–L6 CS.4 補「**MC [N] 條款覆蓋清單**」——102 條代號逐一具名（含 `Pn.Y` 與 `§2.1`–`§2.11`／`§5.1`–`§5.6`）；落點仍指向既有 Annex TR；誠實界限寫明≠語意矩陣新建／≠決策四第二輪完成。
- selftest **G14**；`report --sync`
- 驗收（實跑）：`wm44_uncited_L1`–`L7` 全 **0**；L3／L4 warning **1→0**；L1／L2／L6 覆蓋 warning 清零；L5 剩 **1** warning（既有 `KDI.18` 形態未受檢，非桶 C）；七層 **PASS／error 0**

---

## 4. 驗收

- selftest 全綠  
- L4 對 `IDO.*` 不再出現「AUGUR-IDO 未見於 upper-specs」類警告（改為可受檢；標籤不符則升／維持誠實 finding）  
- `report` 仍 **PASS／error 0**  
- 本報告留痕；若改規格則另開 commit／必要時 RULING

---

## 5. 請 Steward 拍板

回覆其一：
- **`拍板 P1`** — 只修 lint（IDO 權威＋表列枚舉）  
- **`拍板 P1+P2`** — lint＋L3 TR 代號對齊  
- **`拍板 全量 P1–P3`** — 含 WM.44 嚴格覆蓋補列  
- **`暫緩`** — 接受現況 WARNING 為骨架誠實欠帳，改回活躍計畫拍板
