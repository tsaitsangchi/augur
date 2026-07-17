# Augur — Enterprise AI Operating System

Augur 是一套企業級 AI 作業系統，其最高使命：

> Augur exists to faithfully represent reality through persistent identity and traceable evidence, enabling trustworthy intelligence.

本儲存庫封存 Augur 的 **Layer 0 元憲章（Meta-Constitution）** 與各層規格 — 約束所有後續技術規格、資料模型、程式實作與 AI Agent 行為的最高設計憲章體系。

**現行生效狀態（2026-07-17）**：**Layer 0–6 已生效**（L0 元憲章 v1.3；L1–L6 規格 v1.0，各經 Steward 充任認定，見下表）；其中 **L5 為 provisional**（形式關卡充任、`§8.2` 實質人類審查延後），**L6 為唯一另經 `§8.2` 實質人類審查者**。**Layer 7（Infrastructure）僅有 `v0.1-draft`、尚未生效**，其充任受阻於 `§8.2` 實質審查。

> ⚠️ **生效 ≠ 無瑕疵**：`§8.3` 機器 gate（`tools/constitution_lint/`）於 2026-07-17 硬化後，測得**已生效規格仍有未結之 WM.44-LABEL error**（憲章標籤誤標），且 L2 之 Annex TR 矩陣曾因標題層級而**從未受檢**卻以 PASS 發布。**不得以 linter 綠燈為充任依據**。現況、待裁事項與具體數字見 [HANDOFF.md](HANDOFF.md)（待裁 #22）。

## 文件

### 導覽（[I] 資訊性）

| 文件 | 說明 |
|---|---|
| [HANDOFF.md](HANDOFF.md) | **交接文件 [I]**（現況、待裁事項、紅線、踩過的雷 — 接手請先讀） |
| [ARCHITECTURE-OVERVIEW.md](ARCHITECTURE-OVERVIEW.md) | **架構總覽 [I]**（2 層 × 8 層 × 2 repo 對映；給人看的導覽圖） |
| [CONSTITUTIONAL-ROLLOUT-PLAN.md](CONSTITUTIONAL-ROLLOUT-PLAN.md) | **憲章展開總綱**（治權主導混合式；L0→L7 展開路徑、九階段、三里程碑） |

### Layer 0 — 元憲章（constitution/）

| 文件 | 說明 |
|---|---|
| [constitution/META-CONSTITUTION.md](constitution/META-CONSTITUTION.md) | **現行有效版本 v1.3** |
| [constitution/GOVERNANCE-ANNEX.md](constitution/GOVERNANCE-ANNEX.md) | 治理附則 v1.0（憲章 §8.1 要求） |
| [constitution/AMENDMENT-LOG.md](constitution/AMENDMENT-LOG.md) | 修訂登錄簿（AL-2026-001 起） |
| [constitution/COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md](constitution/COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md) | 合規聲明暫行模板（§8.3 過渡規則） |
| [constitution/META-CONSTITUTION-v1.2.md](constitution/META-CONSTITUTION-v1.2.md) ／ [v1.1](constitution/META-CONSTITUTION-v1.1.md) ／ [v1.0](constitution/META-CONSTITUTION-v1.0-original.md) | 歷版歸檔 |
| [constitution/REVISION-RECORD-v1.0-to-v1.1.md](constitution/REVISION-RECORD-v1.0-to-v1.1.md) | v1.0 → v1.1 修訂證據記錄（36 項議題裁決全文） |

### Layer 1–7 — 各層規格（specs/）

依 Layer 序。**生效者**均經 Steward 充任認定（`§0.5`／`§8.6`）並登錄 Amendment Log。

| Layer | 規格 | 現行地位 |
|---|---|---|
| L1 | [WORLD-MODEL-SPECIFICATION.md](specs/WORLD-MODEL-SPECIFICATION.md) | ✅ **AUGUR-WM v1.0 生效**（2026-07-16；裁決 2026-002／AL-2026-005） |
| L2 | [ONTOLOGY-SPECIFICATION.md](specs/ONTOLOGY-SPECIFICATION.md) | ✅ **AUGUR-ONT v1.0 生效**（2026-07-17；裁決 2026-003／AL-2026-007） |
| L3 | [IDENTITY-SPECIFICATION.md](specs/IDENTITY-SPECIFICATION.md) | ✅ **AUGUR-ID v1.0 生效**（2026-07-17；裁決 2026-004／AL-2026-008） |
| L4 | [KNOWLEDGE-SYSTEM-SPECIFICATION.md](specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md) | ✅ **AUGUR-KS v1.0 生效**（2026-07-17；裁決 2026-005／AL-2026-009） |
| L5 | [COGNITIVE-KERNEL-SPECIFICATION.md](specs/COGNITIVE-KERNEL-SPECIFICATION.md) | ⚠️ **AUGUR-L5 v1.0 生效（provisional）** — 形式關卡充任、**`§8.2` 實質審查延後**（裁決 2026-006／AL-2026-010） |
| L6 | [AGENT-RUNTIME-SPECIFICATION.md](specs/AGENT-RUNTIME-SPECIFICATION.md) | ✅ **AUGUR-L6 v1.0 生效** — **含 `§8.2` 實質人類審查**（裁決 2026-007／AL-2026-011） |
| L7 | [INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md](specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md) | 🔴 **v0.1-draft，未生效** — 充任受阻（待 `§8.2` 實質審查） |

各層 `*-v0.1-draft.md` 為充任前之原文歸檔（`specs/` 內同名附 `-v0.1-draft` 者），保留以資對照。

### 裁決與審計

| 文件 | 說明 |
|---|---|
| [constitution/INTERPRETATION-RULING-2026-001.md](constitution/INTERPRETATION-RULING-2026-001.md) | 解釋裁決第 2026-001 號（P4.E3 刪除家族分級尺度） |
| [constitution/RULING-2026-002-LAYER1-ADOPTION.md](constitution/RULING-2026-002-LAYER1-ADOPTION.md) | 裁決第 2026-002 號（Layer 1 充任認定暨同案程序） |
| [constitution/RULING-2026-003-ONT-ADOPTION.md](constitution/RULING-2026-003-ONT-ADOPTION.md) | 裁決第 2026-003 號（Layer 2 Ontology 充任認定） |
| [constitution/RULING-2026-004-ID-ADOPTION.md](constitution/RULING-2026-004-ID-ADOPTION.md) | 裁決第 2026-004 號（Layer 3 Identity 充任認定） |
| [constitution/RULING-2026-005-KS-ADOPTION.md](constitution/RULING-2026-005-KS-ADOPTION.md) | 裁決第 2026-005 號（Layer 4 Knowledge System 充任認定） |
| [constitution/RULING-2026-006-L5-ADOPTION.md](constitution/RULING-2026-006-L5-ADOPTION.md) | 裁決第 2026-006 號（Layer 5 充任 — §8.2 延後） |
| [constitution/RULING-2026-007-L6-ADOPTION.md](constitution/RULING-2026-007-L6-ADOPTION.md) | 裁決第 2026-007 號（Layer 6 充任 — 含 §8.2 實質審查） |
| [constitution/RULING-2026-009-EXECUTION-REMEDIATION.md](constitution/RULING-2026-009-EXECUTION-REMEDIATION.md) | 裁決第 2026-009 號（AL-2026-012；RULING-2026-003～007 機械性生效步驟之執行補正） |
| [constitution/adoption-drafts/](constitution/adoption-drafts/) | **裁決草案區 — 一律不生效力**（見該目錄 README）。現有 `RULING-2026-008-L7-ADOPTION-DRAFT.md`（L7 充任審議草案，待 Steward `§8.2` 實質審查） |
| [audits/CODE-COMPLIANCE-AUDIT-2026-07-16.md](audits/CODE-COMPLIANCE-AUDIT-2026-07-16.md) | 程式碼庫合憲審計 AUD-01…26（已驗證＋裁決定調；基準錨定 code repo `e23a102`） |
| [audits/REMEDIATION-ROADMAP.md](audits/REMEDIATION-ROADMAP.md) | 補正路線圖（審計項之處置排程與現況） |

### 工具與環境

| 文件 | 說明 |
|---|---|
| [tools/constitution_lint/](tools/constitution_lint/) | **`§8.3` 機器稽核 gate**（compliance／audit／selftest；純 stdlib）。**綠燈不得作為充任依據** — 見其 README 之據實揭露節 |
| [infrastructure/ENVIRONMENT-SPEC.md](infrastructure/ENVIRONMENT-SPEC.md) | 部署環境規格（GB10／ARM64 aarch64） |

## 五大不可違反原則

1. **Reality First** — 真實世界優先
2. **Representation Before Intelligence** — 表徵先於智慧
3. **Identity Before Knowledge** — 身份先於知識
4. **Evidence Before Conclusion** — 證據先於結論
5. **Accountability Before Action** — 可歸責先於行動

## Layer 架構

```
Layer 0  Meta-Constitution（本儲存庫）
Layer 1  World Model
Layer 2  Ontology
Layer 3  Identity System
Layer 4  Knowledge System
Layer 5  Cognitive Kernel
Layer 6  Agent Runtime
Layer 7  Controlled External Interface / Infrastructure
```

## 修訂

憲章之解釋、違憲審查與修訂程序，依憲章 §8（Conformance, Interpretation & Amendment）辦理。
