# TTAI/ERP 知識向量統一至 augur pgvector（棄 Qdrant）計畫

**性質**：plan-first 計畫書（憲章 v1.31–v1.33）——**只規劃、不實作**；動工前逐點人拍板。
**範圍**：把 TTAI（Tiptop ERP 知識抽取專案）現行以 **Qdrant + bge-m3** 承載的向量表示，改用 **augur 現行向量方案（pgvector + e5-small）**，使 ERP 知識與 augur 既有哲學/財經知識落在**同一向量空間**、由「誠實博學的我」統一檢索。
**與母計畫關係**：整合母計畫＝`reports/augur_ttai_erp_integration_master_plan_20260706.md`（broad SOP，含 schema 逐欄映射／擷取 adapter／domain 治權／§⑦ 統一向量空間，且親讀 code 更 grounded）。本檔為其**向量層決策深入版**——聚焦母計畫未深入的 **bge-m3→e5-small 品質取捨** 與 pilot rank@k 量測 gate；**向量機制細節（粒度、指令、CLEAN 閘）一律以母計畫為準**，本檔已對齊（#12 避免漂移）。
**治權定位**：ERP 知識屬 augur **知識/素養層**——**零量化價值、不進台股預測管線、不產因子**（憲章 v1.19；import-lint 隔離 `augur.knowledge`）。本計畫只動「知識檢索之向量表示」，與預測管線完全無關。

---

## 1. 現況對照（recon 實證）

| 面向 | TTAI 現行 | augur 現行（目標方案） |
|---|---|---|
| 嵌入模型 | `BAAI/bge-m3` dense（刻意選型，繁中 ERP 品質佳；MIT） | `intfloat/multilingual-e5-small` |
| 向量維度 | **1024** | **384** |
| 向量庫 | **Qdrant** local（`.qdrant` / `.qdrant_poc`，具名向量 zh/en/cn + payload） | **pgvector** + HNSW（同庫 SSOT，`vector(384)`） |
| 追蹤表 | `buffer.buffer_embedding`（model/dim/point_id/hash/狀態） | `knowledge_*_embedding`（PK→來源、model_tag 欄） |
| 被嵌內容 | `buffer.knowledge_unit.semantic_text`（多語 zh/en/cn，缺則退 title→erp_identifier），經 `buffer.v_qdrant_export` view 投影 | 三粒度：lexicon 154,875 / sentence 33,867 / chunk 126,609 |
| 抽取來源 | ERP 4gl/4fd/程式碼 → `knowledge_unit`（unit_type：module/program/table/column/function/code/relation/process）142,040 列 | — |
| 檢索路徑 | Qdrant client kNN + payload 過濾 | `src/augur/philosophy/retrieval.py` pgvector kNN → advisor guard |

> 來源：ttai DB（**全 16 表住 `buffer` schema、augur 對 buffer 讀取被拒 permission denied；public 無鏡像**，`to_regclass('public.knowledge_unit')=NULL`，取數路見 §6 前置）；`reports/embedding選型PoC_20260624.md`、`ERP轉Qdrant通用系統設計_20260624.md`；augur `scripts/embed_knowledge.py`、DB 實查。

---

## 2. 核心技術事實（本計畫的立足點）

**不同嵌入模型 / 不同維度的向量，不能放進同一檢索空間比對**——bge-m3(1024) 與 e5-small(384) 的餘弦相似度跨模型無意義。因此「Qdrant 向量庫改為 augur 的向量資料」在技術上**唯一正確的意思是**：

> **ERP 文本（`semantic_text` 多語）必須用 augur 的 e5-small 重新嵌入、寫入 augur pgvector；TTAI 原有的 bge-m3/Qdrant 向量在 augur 端不採用（棄用或僅留 TTAI 內部）。**

「遷移向量」不是搬 1024 維數字（搬過來也無法與 384 維共存），而是**搬文本、在 augur 端重嵌**。這一點決定整個計畫是「re-embed」而非「copy vectors」。

---

## 3. ⚠️ 關鍵取捨（誠實揭露，#15）——本計畫最重要的拍板點

TTAI **當初刻意選 bge-m3（1024）** 是因為它對**繁中 ERP 檢索品質佳**；e5-small（384）是**小而快**的模型。把 ERP 從 bge-m3 降到 e5-small，**ERP 檢索品質很可能下降**。這不是實作細節，是決策層取捨，必須你拍板：

| 方案 | 做法 | 得 | 失 |
|---|---|---|---|
| **A（你的指示·本計畫主線）** | ERP 文本用 **e5-small 重嵌 → augur pgvector**，其餘 augur 知識不動 | 統一向量空間、沿用 augur 現行、零新模型依賴、儲存小(384) | ERP 檢索品質可能不如 bge-m3；與 TTAI 選型的品質判斷相左 |
| **B（品質替代·統一「往上」）** | augur **整個知識層升級 bge-m3(1024) pgvector**，全部重嵌（155k+34k+127k+ERP） | 全域最佳品質、統一空間、承接 TTAI 選型成果 | 巨量重嵌（三粒度全砍重來）、pgvector 1024 維儲存/HNSW 成本 ~2.7×、動 augur 現行向量（風險大） |
| **C（不建議）** | 雙模型雙索引、不跨模型檢索 | 各自最佳 | **違「統一向量資料」意圖**、advisor 無法一次跨域檢索 |

**本計畫預設走 A（依你當次明示方向）**，但把品質差距做成**可量測的 gate**（§7 pilot 用 rank@k 對照 e5-small vs bge-m3），若 pilot 顯示 ERP 檢索品質掉太多，再由你決定是否轉 B。**在你未拍板前不擅自改 augur 現行向量（不碰 B）。**

---

## 4. 目標架構（方案 A）

ERP 知識落地 augur 知識層、與既有域共用 e5-small pgvector 空間：

- **落地層**：ERP `knowledge_unit` → augur `knowledge_item`（一 unit 一 item，`domain='erp_tiptop'`、`provenance=ttai`、`access_scope='local_private'`、`stable_key` 為冪等鍵）；`semantic_text` 多語 → `knowledge_item_text`（逐語言列，語言欄）。ERP 專屬元資料（unit_type/erp_identifier/attributes/relations）保留於 item 的結構欄或 JSONB，不失真。
- **向量層（已對照 augur code 修正、對齊母計畫）**：augur `embed_knowledge.py` **已內建 item 側嵌入路徑**——ERP `knowledge_item_text` 經 **`--layer sentence --scope items`** 切句、寫入**既有 `knowledge_sentence_embedding`**（e5-small、`vector(384)`、多語由 `knowledge_sentence.language` 分區），與 lexicon/sentence/chunk **同一 e5-small 空間**、以 `domain='erp_tiptop'` 過濾檢索。**不需新建 item 級嵌入表**（沿用既有三粒度基礎設施、零新 DDL）；ERP 三語具名向量（zh/en/cn）以 `knowledge_sentence.language` 近似。
- **檢索層（對齊母計畫 D13=A）**：`philosophy/retrieval.py` 之 `retrieve_all` **不 filter domain**——跨域隔離靠 **RBAC grant 拓撲**（單域對單群組部署）；`retrieve_items` 則接受 `domain` 參數；private 走 owner 收窄；advisor 由「哲學/財經」→ 涵蓋 ERP 的統一檢索；guard 對 ERP 引文**逐字比對真實 `semantic_text`/源**（引文=真兆、非杜撰）。

> ⚠ **兩道靜默失敗閘**（母計畫親讀 code 實證、務必守）：(1) `embed_knowledge.py` **預設 `--scope works`**，對 ERP items **一句都不嵌** → 必須明指 `--scope items`；(2) items 側再吃**第三道 `license×entity_type` CLEAN 閘**（`corpus.clean_item_sql`）——ERP 的 license 若未進 `corpus.LICENSE_WHITELIST`，縱使切句成功也「**嵌入 0 列、檢索永遠空手**」。故 §8 D4 的 license 決策**直接連動嵌入是否有效**。

---

## 5. 遷移步驟（方案 A 主線，每步附可驗證 gate）

| 步 | 內容 | 做法 | Audit Gate（可驗證） |
|---|---|---|---|
| **S0 前置** | 權限＋治權 | ①授 augur 讀 ttai 來源表（`GRANT USAGE ON SCHEMA buffer / SELECT` 或 `pg_dump -n buffer` 快照進 augur 唯讀 staging；**public 無鏡像、無 fallback**）②`knowledge_domain_map` 註冊 `erp_tiptop`（決策層拍板 §8）③確認 import-lint 隔離仍過。**沿用既有 `knowledge_sentence_embedding`、零新 DDL（見 §4）** | 域已註冊；`test_philosophy_isolation` 綠燈 |
| **S1 抽取** | 讀 ERP 文本 | ttai 全 16 表住 buffer、augur 對 buffer 讀取被拒、public 無鏡像；**唯一取數路＝先 GRANT USAGE+SELECT on buffer、或 `pg_dump -n buffer` 快照進 augur 唯讀 staging**（對齊母計畫 §②/§⑤/§⑥）。取數後讀 `v_qdrant_export` 之 `embed_text`(semantic_text)、多語(zh/en/cn)、payload、`stable_key`、unit_type/erp_identifier/relations | 抽取列數 = ttai 單元數（142,040）× 有效語言；provenance 100% 帶 stable_key |
| **S2 落地** | 寫 augur 知識層 | 冪等 upsert `knowledge_item`(+`_text` 逐語言)，domain/provenance/access_scope 齊；ERP 關係(knowledge_relation)映射另見母計畫 | item 落地數對帳 = 抽取數；每列可 trace 回 ttai stable_key（#10） |
| **S3 重嵌** | e5-small 嵌入 | 沿用 augur `embed_knowledge.py`（e5-small 384）：**`--layer sentence --scope items --language zh`（及 en）** 將 ERP item_text 切句嵌入既有 `knowledge_sentence_embedding`；游標增量、junk 過濾。**前提**：ERP license 須先進 `corpus.LICENSE_WHITELIST`（否則第三道 CLEAN 閘致嵌 0 列） | `knowledge_sentence_embedding` JOIN 至 `domain='erp_tiptop'` 計數 **>0**（防切句成功卻嵌 0 列之靜默失敗）；抽測維度=384、model_tag 世代正確 |
| **S4 檢索整合** | advisor 四域 | `src/augur/philosophy/retrieval.py` 加 erp 域 kNN（同 e5-small 空間、domain 過濾）;guard 對 ERP 引文逐字比對 | 端到端：ERP 查詢（如「gaz 三語代碼」「amdp261 程式用途」）回真實 ERP 引文、guard pass |
| **S5 退役 Qdrant** | 收斂單一向量真相 | augur 端零 Qdrant 依賴；TTAI 的 `.qdrant`/`.qdrant_poc` 於 augur 側不再使用（TTAI 專案內部是否保留由用戶定）；文件標「ERP 向量 SSOT = augur pgvector」 | augur 檢索不觸 Qdrant；§7 品質 gate 通過後才正式退役 |

---

## 6. 前置阻礙（recon 已發現，須先解）

- **權限**：ttai 全 16 表住 `buffer` schema、augur 帳號對 `buffer` **讀取被拒**（`buffer.buffer_embedding` permission denied，實測連 `semantic_text` 來源表 `knowledge_unit` 亦拒）；**`public` 無鏡像**（`to_regclass('public.knowledge_unit')=NULL`），無 public fallback。S1 唯一取數路＝**先 GRANT USAGE+SELECT on buffer，或 `pg_dump -n buffer` 快照進 augur 唯讀 staging**（對齊母計畫 §②/§⑤/§⑥）。**唯讀、不改 ttai**。
- **多語處理**：TTAI 有 zh/en/cn 三語 `semantic_text`；augur `knowledge_item_text` 須逐語言落地 + 逐語言嵌入（e5-small 多語模型，跨語檢索可用但須驗，呼應 augur 既有跨語 rank 教訓）。
- **粒度不匹配**：augur 現有嵌入是 lexicon/sentence/chunk，無 item 級；本計畫**沿用既有 `knowledge_sentence_embedding`（零新 DDL，見 §4）**——ERP item_text 經 `--scope items` 切句寫入既有句級表、以 `domain='erp_tiptop'` 過濾，不新建 item 級表。

---

## 7. 分期與品質驗收（pilot 先行，決定 A 是否夠好）

1. **pilot 小樣本**：挑一個 `unit_type`（如 `program` 874 列）或一個模組，走完 S1–S4。
2. **品質對照 gate（本計畫核心量測）**：對一組 ERP 代表性查詢（代碼/識別碼/程式用途/欄位語意），量 **rank@10 命中**，**e5-small(augur) vs bge-m3(TTAI 原 Qdrant)** 並列對照。
   - e5-small 品質**可接受** → 放量走 A 全量。
   - e5-small 品質**掉太多**（ERP 代碼/識別碼類查詢尤敏感，PoC 曾建議 bge-m3 hybrid+sparse）→ **回報你、由你決定是否轉方案 B**（升級 augur 為 bge-m3）。
3. **放量**：pilot 過關才全量 re-embed（142,040 單元 × 多語）。

---

## 8. 決策層拍板清單（動工前須拍）

- **D0（最關鍵）**：**方案 A（e5-small 統一、可能降品質）vs 方案 B（升級 augur 為 bge-m3、全域重嵌）**。本計畫預設 A、pilot 量測後可轉 B。
- **D1（已解、無需再拍）**：ERP 落地**粒度**——經對照 augur code，走**既有 `--scope items`→句級 `knowledge_sentence_embedding`**（零新 DDL、同 e5-small 空間），非新建 item 表；與母計畫一致。
- **D2**：新增 **domain `erp_tiptop`** 註冊（憲章 v1.19「能抓≠該抓」/決策層拍板）；命名（`erp_tiptop` / `software_erp`）。
- **D3**：**access_scope**——ERP 是用戶自有專案資料，建議 `local_private`（僅授權者可檢索）;是否對所有登入者開放由你定。
- **D4**：**provenance/license**——自有資料非公版/CC，如何標來源與授權。`source_type` 走接口 B 硬編 `'local_upload'`（過 `chk_itext_source_type` CHECK、無法覆寫為 `ttai_erp`）；命門在 license 承載，詳母計畫 §⑩ D4 三連動點。
- **D5**：**TTAI 的 Qdrant 是否保留**（augur 端一律棄用；TTAI 專案內部是否續用由你定）。
- **D6**：ERP `knowledge_relation`（67,914 關係）如何在 augur 表達——本向量計畫不含，屬母計畫 schema 映射（此處僅標依賴）。

---

## 9. 資源估算（e5-small，方案 A）

- 落地：142,040 單元 × 有效語言（估 1–3 語）→ ~14–40 萬 item_text 列。
- 重嵌：e5-small 本機 CPU 實測 ~35 句/s（augur 先前 lexicon 嵌入實績）→ 40 萬列估 ~3–4 小時（背景、游標增量、resume-safe）。
- 儲存：384 維 × ~40 萬 ≈ 數百 MB 向量 + HNSW；遠小於方案 B 的 1024 維。
- **驗收判準**：落地數對帳（#7）、向量維度/model_tag 抽驗、HNSW 建成、pilot rank@10 品質報告、端到端 advisor ERP 問答 guard pass、隔離不變式綠燈。

---

## 10. 治權合規總表

| 治權 | 本計畫落實 |
|---|---|
| #1 零幻像 | ERP 向量來自真實 `semantic_text`（抽取自 4gl/4fd/code）、非 AI 生成；guard 逐字比對引文 |
| #8 anti-leakage | 此域無時序預測，主守 provenance 真實性；ERP 知識不進預測管線 |
| #15 誠實 | bge-m3→e5-small 品質取捨明文揭露（§3）、pilot 量測有據、不默默接受退步 |
| #16 clean-room | ERP 4gl/4fd/code 是**資料**入知識層；**絕不回流 augur 自身 codebase** |
| v1.19 素養層 | ERP 知識零量化價值、不產因子、不進台股預測；`domain` 隔離、import-lint（`augur.knowledge`）擋 |
| v1.20 全文准入 | 自有資料治理：access_scope local_private + provenance；非公版/CC 之自有資料另立判準（D4 拍板） |

---

> **下一步**：先拍 **D0（A vs B）** 與 **D2（domain 註冊）**；拍板後我依此走 pilot（S0–S4 小樣本 + §7 品質對照），量測結果回報再決定放量或轉 B。母計畫（`wnf5f2msi`）落地後,本檔掛為其向量層 SSOT。
