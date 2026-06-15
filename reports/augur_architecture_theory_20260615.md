# augur 架構理論對照 — 業界 4 維度驗證（2026-06-15）

**性質**：研究報告 / 理論定位背書檔。**被憲章附錄 C「理論定位」引用**（憲章承載定位框架、本檔承載逐項對照 + 業界出處，守憲章第六部 SSOT 分家 + 30 分鐘可讀）。
**clean-room（#16）**：只依 augur 自身治權檔 + 公開業界架構文獻（PEP / Martin / Evans / Cockburn / Beauchemin / Ousterhout 等）；**零 stock_backend 參考**（業界理論為概念層對映、不移植任何 code）。
**緣由**：回答用戶之問——「Screaming / DDD / PEP 8 三套業界理論可架構整個 augur 嗎?」→ 詳查業界架構理論、對照 augur 既有架構、誠實定位。

---

## 0. 結論先講（#15）
1. **3 套不足**：用戶初指的 Screaming Architecture / DDD / PEP 8 只覆蓋「**組織 + 命名**」1 個維度；完整架構一個 clean-room 資料+ML 系統需 **4 維度、約 9 套理論**。
2. **augur 已獨立體現 ~90%**：augur 從第一性原理（只用真實資料、誠實預測台股）長出的架構（三敵人 + 管線 + source-purity）恰對映這 4 維度——業界理論之角色為**外部驗證 + 共同詞彙 + 補小缺口**，**非架構 SSOT**（SSOT 仍是靈魂 + 憲章）。
3. **augur 是「收斂實例」非「應用對象」**：最強證據——業界防 data leakage 的判準 *"Would this feature realistically be available at the time of prediction? If no, remove it"* **＝ augur 北極星 ②「決策當下真看得到嗎?」逐字翻版**。

---

## 1. 維度一　組織 + 命名（Structure & Naming）
**業界理論**
- **Screaming Architecture**（R. C. Martin, *Clean Architecture* ch.21）：目錄結構該「吼出系統用途」、非所用框架；package-by-feature ＞ package-by-layer。
- **DDD Ubiquitous Language**（E. Evans）：用領域詞彙入碼 → 自我說明（intention-revealing interfaces）；module 名是 ubiquitous language 的一部分。
- **PEP 8 / PEP 423**：module/package 名 short、lowercase、**semantic、反映用途非實作**（避免 utils / helpers / manager 通用名）。

**augur 對映**
- package ＝靈魂管線階段（`ingestion / features / universe / models / evaluation` + 橫切 `core / audit / catalog`）→ 結構即「台股預測管線」（screaming）。
- module ＝治權領域詞（`finmind / fred / reconcile / generic_schema / catalog`）→ ubiquitous language。
- 命名慣例（本 session 確立）：library 模組＝**領域名詞**、CLI script＝**動作動詞**；`augur.<pkg>.<module>` 單看即知做什麼。

**狀態**：✅ 完全體現。

## 2. 維度二　依賴 + 模組邊界（Dependency & Boundaries）
**業界理論**
- **Hexagonal / Ports & Adapters**（A. Cockburn）＋ **Clean / Onion**（Martin）：依賴反轉——business core 定義介面（ports）、外部技術實作（adapters）；**所有原始碼依賴指向 core**、core 不依賴 infra。
- **Deep Modules**（J. Ousterhout, *A Philosophy of Software Design*）：好模組＝**簡單介面 + 複雜實作**、information hiding；軟體設計＝對抗複雜度。

**augur 對映**
- 憲章第三部「**各層職責不越界**」＋「**core 不抓 API**」＝依賴方向（core 為穩定中心、`ingestion` 為外部 API 的 adapter、依賴指向 core）。
- deep modules：`finmind`（三層限速藏在 `fetch()` 後）、`generic_schema`（auto-schema 引擎藏在 `infer_schema / ensure_table` 後）、`catalog`（探測藏在 `build() / optimal_mode()` 後）。
- ⚠️ **缺口**：augur 有分層、但無正式抽象 ports（介面）。`finmind / fred` 實為「外部 API adapter」，可顯化共同 fetch port——惟現批次管線分層已夠用、非急需。

**狀態**：⚠️ 大致體現（分層 + deep modules ✅；正式 ports/adapters 未採，現況夠用）。

## 3. 維度三　資料管線（Data Pipeline）
**業界理論**
- **Medallion Architecture**（bronze / silver / gold）：raw → cleaned/標準化 → business-ready，品質分層遞進。
- **Functional Data Engineering**（M. Beauchemin）：pure tasks、**idempotency + immutability**、reproducibility、recomputability；「partition 視為不可變區塊、pure task 全覆蓋輸出」。
- **Data Lineage**：血緣溯源、provenance、版本 + 時戳、stewardship。
- **Data Contracts**：schema 鎖定/強制、quality gate、版本化。

**augur 對映**
- **medallion**：`raw`（bronze ＝ API 原值 byte-equal）→ `feature`（silver ＝ source-pure 標準化）→ `universe`（gold-ish ＝ 資料乾淨核心股）→ `model`。
- **functional**：#6 冪等 + 斷點續傳（`ON CONFLICT DO UPDATE`）＝idempotency；as-of append-only（首見即存，優化計畫 §5）＝immutability；#15 固定 `random_state`、半年重跑一致＝reproducibility。
- **lineage**：#15 每值 trace 回 (a)程式/(b)DB/(c)API；catalog `source_provenance` / `last_verified` 欄＝逐欄血緣。
- **contracts**：#2 API 即權威 + #7 DB↔API 對帳 attestation ＝ data contract enforcement（reconcile ＝ quality gate）；catalog ＝元資料契約。
- ⚠️ **缺口**：data-contract schema **版本化**（FinMind 改欄之遷移規則）可補；as-of / bitemporal 可形式化（vintage 表，優化計畫 §5 已設計）。

**狀態**：✅✅ 強體現（augur 本質即嚴謹的 functional-data-engineering medallion 管線 + lineage + contracts）。

## 4. 維度四　ML 系統（ML System Design）
**業界理論**
- **Data Leakage Prevention**：「該特徵在預測當下真的拿得到嗎?拿不到就刪」；含 train/test overlap、target leakage、survivorship。
- **Reproducibility**：每值版本化 + 時戳、可精確重建昨日 training set、可審。
- **Feature SSOT / Training-Serving consistency**：compute-once-use-everywhere、feature 定義一致（feature store 動機）。

**augur 對映**
- **leakage**：#8 anti-leakage（≤t 已知、t+1 套用、purged-CV、含 survivorship / 選股偏差防護）＝**北極星 ② 逐字命中**。
- **reproducibility**：#15（固定 `random_state`、pipeline 確定性、半年重跑一致＝靈魂的成功定義）。
- **feature SSOT**：#12 單一 helper（panel + metric）＝ compute-once-use-everywhere、跨模型可比。
- ⚠️ **缺口**：train/serve skew——augur 目前純批次、無 online serving → 暫不適用；#12 已是 feature-SSOT 精神，未來上 serving 再套 feature-store。

**狀態**：✅✅ 強體現（三敵人 #1/#8/#15 即 ML 系統設計紀律）。

---

## 5. 核心洞察
augur **不是「缺架構、要套理論」**，而是「**從第一性原理長出架構、恰收斂到業界 4 維度**」。三敵人即業界理論之**領域化身**：

| 敵人 | 業界理論化身 |
|---|---|
| ① 假資料 | Data Contracts + Lineage + Source Purity |
| ② 偷看未來 | ML Leakage Prevention（≤t as-of） |
| ③ 自我欺騙 | Reproducibility + Functional Recomputability |

→ 故業界理論是 augur 的**外部驗證與共同詞彙**；augur 架構 SSOT 仍是靈魂 + 憲章，**不被任一業界理論凌駕**。

## 6. 對映總表
| 維度 | 業界理論（代表） | augur 對映 | 狀態 |
|---|---|---|---|
| 1 組織+命名 | Screaming Arch.· DDD Ubiquitous Lang.· PEP 8 | package＝管線階段、module＝領域詞 | ✅ |
| 2 依賴+邊界 | Hexagonal/Clean Ports&Adapters· Deep Modules | 職責不越界 + core 不抓 API；deep modules | ⚠️ 無正式 ports |
| 3 資料管線 | Medallion· Functional DE· Lineage· Data Contracts | raw→feature→universe；#6 冪等+as-of；#15+catalog provenance；#2/#7 對帳 | ✅✅ |
| 4 ML 系統 | Leakage Prevention· Reproducibility· Feature SSOT | #8 anti-leakage· #15 重跑一致· #12 單一 helper | ✅✅ |

## 7. 誠實 caveats（#15）
- 本對照為**事後對映驗證**（augur 先有架構、後對業界理論），非「augur 照理論設計」。
- 「✅ 體現」指**概念對映**，非逐行符合每套理論之全部細節。
- 小缺口（正式 ports / 契約版本化 / bitemporal / serving）為理論指出之**可選增強**、非缺陷——augur 現批次 clean-room 範圍內已自洽。
- 業界出處為**公開文獻**；augur 零移植其 code（#16 clean-room 僅概念層對映、不回流 code）。

## 8. 業界出處（Sources）
- **維度一**：[PEP 8](https://peps.python.org/pep-0008/) · [PEP 423](https://peps.python.org/pep-0423/) · [Clean Architecture ch.21 Screaming Architecture](https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/ch21.xhtml) · [Package by feature vs layer (hgraca)](https://herbertograca.com/2017/08/31/packaging-code/) · [DDD Reference — Evans](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) · [Ubiquitous Language — Agile Alliance](https://agilealliance.org/glossary/ubiquitous-language/)
- **維度二**：[Hexagonal Architecture (MaibornWolff)](https://www.maibornwolff.de/en/know-how/hexagonal-architecture/) · [Ports & Adapters (jmgarridopaz)](https://jmgarridopaz.github.io/content/hexagonalarchitecture.html) · [A Philosophy of Software Design — Ousterhout (notes)](https://bagerbach.com/books/a-philosophy-of-software-design/)
- **維度三**：[Medallion Architecture (ml4devs)](https://www.ml4devs.com/what-is/medallion-architecture/) · [Functional Data Engineering — Beauchemin (ssp.sh)](https://www.ssp.sh/brain/functional-data-engineering/) · [Data Lineage Best Practices (Atlan)](https://atlan.com/know/data-lineage-best-practices/) · [Data Contracts (Soda)](https://soda.io/blog/guide-to-data-contracts)
- **維度四**：[Data Leakage in ML (Educative)](https://www.educative.io/blog/what-is-data-leakage-in-machine-learning) · [Training-Serving Skew (Qwak)](https://www.qwak.com/post/training-serving-skew-in-machine-learning) · [Feature Stores — Hierarchy of Needs (applyingml)](https://applyingml.com/resources/feature-stores/)
