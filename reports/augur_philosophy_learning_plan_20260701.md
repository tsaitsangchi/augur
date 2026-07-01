# augur 哲學思想學習計畫

🎯 讓 augur「博學投資大師」角色學習專案所有哲學思想的相容路線圖 —— 釐清「學習」= 顧問解讀層素養擴充(L1 因子假說 / L2 公版全文 RAG 逐字檢索 / L3 綁真兆的哲學翻譯前端),與預測管線以 schema + DB role + import-lint 三重可強制隔離;哲學永遠是「假說來源 + 事後解讀」,經濟價值 #14 是唯一裁決者。
守原則 #1(逐字可溯源、禁 AI 生成) · #8(anti-leakage) · #14(經濟價值裁決) · #15(誠實不誇大) · #16(#17 clean-room) · 憲章 v1.17.0 philosophy 邊界。
產出方式:workflow 5 agents 多視角設計(知識檢索 / 因子假說 / 顧問角色)+ 守治權對抗審查(抓到並修正 3 處「哲學凌駕數據」隱患)綜合。
日期:2026-07-01｜承 tag philosophy-erudition-20260701 之後續規劃依據。

---

# 《augur 哲學思想學習計畫》

## 前言:治權審查結論(先剔除違憲,再綜合)

四個視角經對抗審查後,整體合憲,但有若干處需**明確標註修正/收緊**,以免落地時滲漏。以下先列審查裁定,後續路線圖已納入修正。

**A. 視角一(知識檢索層)— 通過,一處收緊。**
- 收緊點:「pgvector embedding 是檢索用途數值指紋、非 AI 生成入庫」的論述正確,但須補一條硬邊界——**embedding 向量本身永不可被任何 feature/model 讀取當作特徵**(即使有人辯稱「這是數值」)。原設計已用 import-lint 擋,裁定**保留並升為 DB role 層隔離**(檢索層的 embedding 表,feature pipeline DB 角色無 SELECT 權)。
- 裁定:R1 邊界滲漏列為最高風險正確;pgvector 需裝 OS 套件屬 #23 環境前置、須用戶授權,正確標為決策點。

**B. 視角二(因子假說機制)— 通過,一處澄清。**
- 澄清點:此機制合憲的前提是「投資哲學原則(非全文)是合法因子假說來源」——這點憲章 v1.17.0 明文支持,無違。但須釘死:**進料口 A/B/C 產出的候選,採用與否 100% 由經濟價值 #14 裁決,哲學權威零加權**;且「被淘汰因子不得因新學派映到同一因子而復活重測」——ledger 永久留存淘汰理由,此為防重測燒 usage 的關鍵,裁定保留。
- 裁定:此機制對「預測績效」的真實期望貢獻**近乎零**(因子層已飽和,見 §8 誠實評估),其價值在「把哲學庫成長接成有紀律的、去重的、可宣告飽和的閉環」,而非期待挖出新 alpha。此定位須在報告中誠實標明,不得誇大。

**C. 視角三(顧問角色)— 通過,但這是審查重點,已找到並修正三處「哲學可能凌駕數據」的隱患。**

> 任務明文要求特別查視角三。以下三處若不修正,會讓哲學越界:

1. **「逆向鏡」的措辭風險**:原設計「別人貪婪我恐懼」的 contrarian 姿態,若 LLM 執行時把「逆向提醒」寫成「所以這檔其實該賣/該反著做」,即哲學翻轉了模型結論。**修正**:逆向鏡**只能輸出「風險視角/需注意的位階資訊」,禁止輸出任何與模型分數相反的行動含義**;且該提醒本身也須錨定真實特徵(如 `cycle_position` 在高分位),非 LLM 主觀「感覺過熱」。原設計輸出範例已含「此為風險視角,不改變上述模型分數」一句,裁定**將此句從範例提升為強制契約**(生成後驗證 [5] 須檢查:逆向段落不得出現改變排序/分數的祈使語)。

2. **`stock_philosophy_tag` 落地的越界風險**:視角三提「as-of 從 `feature_values` 量化判定每股偏哪學派」。裁定**合憲但須加註**——此 tag 的 `score` 必須是**純數值規則**(如某股估值分位低→標 value 傾向),由**量化本體寫入、非 LLM 判定**;且此 tag **只供顧問分類解讀,永不回流為 feature/model 輸入**(否則哲學標籤變成預測特徵,踩紅線 1)。

3. **「品質鏡:高毛利為護城河訊號——原文逐字引自 Berkshire 股東信」**:裁定**須降級處理**。Berkshire 股東信**非公版**(Buffett 著作權存續),不在 `philosophy_work_text`(該表 `license='public_domain'`)。原範例引用一份庫內不存在、且非公版的來源,**違紅線 3 與 clean-room**。**修正**:顧問**只能引 `philosophy_work_text` 內實際存在的公版逐字段落**;檢索不到對應公版原文時,**明說「素養庫無對應公版原文」而非改引非公版來源或憑記憶補**。範例中的 Berkshire 引用**刪除**,改為「品質鏡的視角存在,但 augur 素養庫目前無此主題之公版原文可引」。此修正同時是 #1(零幻像)在引用層的落地。

- 其餘裁定:視角三「數字向上游要唯讀、智慧向素養庫要逐字、生成後機械校驗」的三層架構**優秀且合憲**,保留為顧問層核心。界面「物理唯讀 + 快照凍結 + 雙源不混」正確。

**D. 視角四(對抗審查者)— 通過,直接採為 §6 紅線總表。** 八條紅線與防護總表無違憲,結構完整,綜合入本報告。

---

## 1. 釐清「學習」的相容定義(三層意涵 + 兩條不是)

「讓 augur 角色學習專案所有哲學思想」——經審查,唯一合憲解為**擴充顧問解讀層(what/why 素養),零觸碰預測管線(raw→feature→universe→model→validate)**。三層意涵:

| 層 | 「學習」意涵 | 交付物 | 屬性 |
|---|---|---|---|
| **L1 因子假說** | 從投資哲學**原則**(非全文)萃取可證偽因子假說,餵四道漏斗 | 過去/未來被 #14 裁決的因子候選 | 唯一可能觸及預測管線之處,但**須經濟價值裁決、哲學零加權** |
| **L2 知識檢索解讀** | 對 298+ 部公版全文語義檢索、逐字引用,供顧問解釋市場 | 只讀 RAG 檢索層(逐字可溯源) | 純解讀素養,**物理隔離於預測管線** |
| **L3 顧問角色素養** | LLM 顧問用多視角/逆向/週期觀的認知紀律,把真實數字翻成有智慧脈絡的人話 | 綁在真兆上的哲學翻譯前端 | 純 what/why,**數字唯讀不改** |

**兩條「學習不是」(不可違,寫入 README 與 system prompt):**
- **「學習」不是用哲學文本訓練預測模型。** 預測模型訓練語料**永遠只有數值市場/總經特徵**;哲學全文 embedding / 字頻 / 情緒**永不成為 feature**。augur 本體不是 LLM。
- **「學習」不是讓哲學取代真實資料或凌駕模型結論。** 預測數值 100% 來自既有數值模型(F3 Ridge 等),trace 回真實 API/DB/程式輸出;哲學只在**事後**對已算出的真實數字做解讀,不回寫、不加權、不改排序。

---

## 2. 現況盤點(實證為據,非推測)

| 項目 | 現況 | 來源 |
|---|---|---|
| 哲學素養庫 thinker | 765 位 | DB `philosophy_thinker`(跨機獨立,實查為準) |
| 公版全文 works | 298+ 部(`philosophy_work_text` 311 部有全文) | DB |
| 全文字數 | 約 1.6 億字 / 168.7M(Gutenberg 英文 168.5M + 維基文庫 CJK 8.1 萬) | DB 實查 |
| 全文段數 | 13,174 段(帶 `source_url`+`license`,全 `public_domain`) | DB |
| 既有切塊 | 極不均(最大 65,067 字/段),不可直接嵌入 | DB 實查 |
| 框架表 | `philosophy_school`/`philosophy_principle`/`principle_factor_map`(42 筆映射,含 `direction`/`validated_ic`/`validated_econ`)/`stock_philosophy_tag`(現 0 列) | DB |
| 特徵層 | 35 特徵覆蓋 8-9 大學派;單因子哲學缺口(ROE/PEG/F-Score/低波…)試盡皆過 #14 淘汰 = **因子層飽和** | memory `feature-execution-plan` |
| 模型現況 | F3 as-of Ridge H60 rank IC +0.1418、long top10% Sharpe 1.26(alpha 僅 long 側、long-short 無效) | memory |
| 基礎設施 | pgvector **未安裝**(僅 `pg_trgm 1.6`);PostgreSQL 17.9;`deep=[torch]` extra 已隔離 | 視角一實查 |

**盤點結論**:素養庫**已建齊、已飽和於「量」**。本計畫不再大規模抓取(能抓≠該抓);重心在**把已入庫全文接成可檢索/可解讀的知識層 + 顧問前端**,而非再挖因子 alpha。

---

## 3. 分階段路線圖

> 全程本地 CPU + 本地 DB、零 Claude usage(理解層判讀除外);每階段做完呈用戶過目再進下一(#19)。P0 需授權(裝 OS 套件),其餘 P1–P7 屬執行層可授權自主推進。

### 階段 0 — 環境前置與治權隔離骨架(須用戶授權)
- **目標**:備妥向量檢索基礎設施 + 建立「哲學↔預測」物理隔離骨架。
- **產出**:(a) 裝 `postgresql-17-pgvector` OS 套件 + `CREATE EXTENSION vector`(**退路**:numpy sidecar `float4[]` 方案,零新依賴);(b) 裝 `deep` extra(torch/sentence-transformers)+ import smoke test(#23);(c) `philosophy_*` 表確認為獨立 schema/namespace;(d) 建立 **feature/model pipeline DB role 對 `philosophy_*` 無 SELECT** 的隔離、與 import-lint 規則骨架。
- **守治權**:#23 環境前置;紅線 1/2/6 的 DB role + schema 隔離在此奠基。
- **依賴**:用戶授權裝 OS 套件。
- **驗收**:`SELECT '[1]'::vector;` 成功(或 sidecar smoke);feature role `SELECT` philosophy 表被拒;import-lint 對 `augur/{features,model,universe}` import `philosophy.retrieval` fail。

### 階段 1 — 全文語義切塊(L2 基建)
- **目標**:把 168.7M 字既有不均段落切成可嵌入單位。
- **產出**:`scripts/build_philosophy_chunks.py`(語義優先切塊:chapter→段→句、英文按句/CJK 按句讀、~500 token、重疊 ~15%、保留 `char_range` 溯源)→ 新表 `philosophy_chunk`(~9 萬塊)。DB-driven resume(#6)。
- **守治權**:逐字原文不改一字(#1);`license` CHECK `public_domain`;本地零 usage(#28)。
- **依賴**:P0。
- **驗收**:chunk 數落地、抽樣 chunk `content` 逐字 = `philosophy_work_text` 對應 `char_range`;無超嵌入窗巨塊殘留。

### 階段 2 — 本地嵌入(L2 基建)
- **目標**:為所有 chunk 產生檢索用向量。
- **產出**:`scripts/embed_philosophy_chunks.py`(bge-m3 多語模型、CPU batch、背景 + sentinel #22、增量只跑新塊)→ `philosophy_chunk_embedding`(`vector(1024)` + `model_tag` 供重嵌溯源)+ HNSW 索引(或 sidecar numpy)。
- **守治權**:全程本地 CPU、零 LLM API(#28);embedding 表對 feature role 無 SELECT(紅線 1)。
- **依賴**:P1。
- **驗收**:embedding 覆蓋率 100% chunk;`model_tag` 一致;kNN 抽樣返回語義相近段。

### 階段 3 — 混合檢索 API(L2 核心)
- **目標**:可語義檢索 + 逐字可溯源引用。
- **產出**:`src/augur/philosophy/retrieval.py`(語義 kNN + `pg_trgm` 精確片段驗證的 hybrid 檢索;`Citation` dataclass 帶逐字 `text`+`(work_id,chapter,char_range,source_url,thinker)`);`scripts/query_philosophy.py` 互動驗證。
- **守治權**:只回 DB 既存逐字字串(#1);溯源三元組強制;`pg_trgm` 存在性回查閘防「潤飾原文」。
- **依賴**:P2。
- **驗收**:抽樣查詢回逐字段落 + source_url 可開驗;精確路能回查字串真實存在;檢索層對預測表零寫入。

### 階段 4 — 情境映射 + 框架 join(L2/L3 橋接)
- **目標**:市場情境(來自真實模型輸出)→ 相關哲學原典的**單向解讀路由**。
- **產出**:`philosophy_context_map` 策展表(真實文獻對映,非 AI 生成)+ join `stock_philosophy_tag`/`philosophy_principle`。**`stock_philosophy_tag` 由量化本體以純數值規則寫入**(審查修正 C-2)。
- **守治權**:映射**單向**(情境由真實模型定、哲學只解釋,不反向決定情境);映射表策展非生成;tag `score` 純數值、非 LLM 判、永不回流 feature(紅線 1)。
- **依賴**:P3 + 量化本體提供 as-of 情境訊號。
- **驗收**:給定情境訊號回對應公版原典段落;tag 由 writer code 寫入、feature role 無法讀 tag 表當輸入。

### 階段 5 — 顧問前端與界面隔離(L3 核心)
- **目標**:LLM 顧問前端,數字唯讀轉述 + 哲學逐字解讀,兩源不混。
- **產出**:獨立 package `src/augur/advisor/`;`PredictionPayload` 唯讀界面契約(as-of 快照凍結、含 `validation` 誠實標籤);顧問 system prompt(人格三姿態 + 三條硬約束);**逆向鏡強制契約**(禁輸出與模型分數相反的行動含義,審查修正 C-1)。
- **守治權**:前端 DB 角色對 `feature_values`/模型/eval 表**只讀**、對哲學表只讀、**零寫回通道**;數字 100% trace payload;引文 100% 來自 `philosophy_work_text` 公版逐字(**檢索不到即明說「素養庫無對應公版原文」,禁改引非公版或憑記憶**,審查修正 C-3)。
- **依賴**:P3/P4 + 量化本體 as-of 輸出。
- **驗收**:開/關解讀層預測數值 byte 級一致(契約測試);逆向段落無翻轉語;無非公版引用出現。

### 階段 6 — 生成後防幻覺閘(L3 核心,三敵落地)
- **目標**:把「防幻覺」從 prompt 自律變成機械 gate。
- **產出**:生成後校驗器——(1) 回應中每個數字 ∈ payload,(2) 每句引號 ⊂ 檢索原文(`pg_trgm` 存在性),(3) 掃未來/事後洩漏語(#8),(4) 弱訊號有無配驗證標籤(#15);任一不過即攔截/標記/重生成。
- **守治權**:#1/#8/#15 在對話層的唯一可靠落地;無「哲學專屬豁免」(紅線 7)。
- **依賴**:P5。
- **驗收**:注入含杜撰數字/非庫引文/未來語的測試回應,校驗器全部攔截;抽樣人工核對引用 = 原文(#7 實測、#15)。

### 階段 7 — 因子假說持續學習閉環(L1,可選、低優先)
- **目標**:把哲學庫成長接成去重、可宣告飽和的因子假說進料口——**但期望 alpha 貢獻近乎零(因子已飽和),定位為紀律化閉環而非挖礦**。
- **產出**:`src/augur/philosophy/hypothesis_ledger.py`(指紋 canonical 化 + L1-L3 去重 + ledger CRUD);`scripts/propose_philosophy_hypotheses.py`(進料口 A 新學派未映原則 / B 未旋轉鏡頭 / C 有閘跨學派交互);在既有 6 表補假說生命週期欄(`transform_spec`/`hypothesis_fingerprint`/`funnel_status`/`rejected_reason`,冪等 `ADD COLUMN IF NOT EXISTS`);串既有 `verify_candidate_promotion.py` + `run_economic_eval.py`。
- **守治權**:採用 100% 由經濟價值 #14 裁決、哲學零加權;淘汰因子永久留 ledger 不復活;S1 定義語意/S8 判真假兆走理解層 ultracode、S3-S7 本地零 usage(#28);孤兒假說(無 `philosophy_principle` 溯源)拒收(#1)。
- **依賴**:P0(不依賴 P1-P6)。
- **驗收**:類比學派共因子被 L1 指紋去重零 usage 擋下;真新假說進漏斗、結果回填 ledger;**飽和可宣告**(連續 N 輪無 Δ>0 即停,不空轉燒配額)。

---

## 4. 技術架構(三層 + 界面隔離)

```
┌─────────────────────────── 量化本體(真兆源,不變)────────────────────────────┐
│ raw → feature_values → core_universe → model(F3 Ridge)→ eval(IC/Sharpe/#14)  │
│  ↑ 訓練語料永遠只有數值市場/總經特徵;philosophy_* 永不進此線                    │
└──────────────┬───────────────────────────────────────────────────────────────┘
     唯讀 PredictionPayload(as-of 快照凍結、含 validation 誠實標籤;零寫回通道)
                │
┌───────────────▼─── L3 顧問前端 src/augur/advisor/(LLM,唯一動筆處)────────────┐
│ 數字通道(唯讀轉述)  ⊕  引文通道(逐字檢索)→ 生成 → 生成後防幻覺閘(機械 gate)│
└───────────────┬──────────────────────────────┬───────────────────────────────┘
        map_features_to_schools           retrieve(逐字 + source_url)
                │                                │
┌───────────────▼────────── L2 知識檢索層 src/augur/philosophy/retrieval.py ─────┐
│ philosophy_chunk → chunk_embedding(pgvector/sidecar)→ hybrid(kNN+pg_trgm)     │
│ join principle_factor_map / stock_philosophy_tag / philosophy_context_map      │
└───────────────────────────────────────────────────────────────────────────────┘
┌── L1 因子假說閉環(可選,低優先)hypothesis_ledger → 去重 → 既有四道漏斗 → #14 ──┐
│ 唯一可觸預測管線者;採用由經濟價值裁決、哲學零加權;淘汰永久留存不復活          │
└───────────────────────────────────────────────────────────────────────────────┘
```

**三道界面隔離(架構不變式,可自動檢測):**
1. **物理唯讀**:顧問/檢索層 DB 角色對 `feature_values`/模型/eval 只有 SELECT;無 INSERT/UPDATE 任何預測資料的能力。
2. **schema + role 分離**:`philosophy_*` 獨立 schema;feature/model pipeline DB role 對 `philosophy_*` **無 SELECT**;禁跨 schema JOIN。
3. **import-lint 不變式**:`augur/{features,model,universe}` import `augur.philosophy.*` 或 `augur.advisor.*` = CI fail。把「絕不進預測管線」從口號變成可自動檢測的架構不變式。

---

## 5. 需用戶拍板的決策點

| # | 決策點 | 選項 | 我的建議 |
|---|---|---|---|
| D1 | **是否裝 pgvector OS 套件** | (a) 裝 `postgresql-17-pgvector`(#23 環境前置,須授權) vs (b) numpy sidecar `float4[]` 零新依賴 | 建議 (a),與 psycopg2/DB 同棧、join 框架表最順;(b) 為退路 |
| D2 | **embedding 技術選型** | bge-m3 單模型(多語、1024 維) vs dual-model(英文/CJK 各一) | 建議先 bge-m3 單模型(語料 99.95% 英文 + 高密度 CJK,單模型運維最簡),CJK 召回弱再上 dual |
| D3 | **是否建 LLM 顧問前端(L3)** | 建 `advisor/` 前端 vs 只做 L2 檢索 API 供人工查 | 取決於是否要「對話式顧問」;若只需可檢索的素養庫,L2 即足、可暫緩 L3 |
| D4 | **是否投入 L1 因子閉環(P7)** | 做 vs 不做 | **誠實建議暫緩/低優先**:因子層已飽和,期望 alpha 近乎零;其價值僅在「紀律化去重閉環」。除非用戶明示要此閉環,否則資源優先 L2/L3(可解釋性才是真價值) |
| D5 | **投入 vs 因子層已飽和之取捨** | 明確承認此計畫**主要價值在顧問可解釋性/角色深度,非預測績效** | 見 §8 誠實評估;請用戶以「要不要一個能引哲學解讀的顧問前端」而非「要不要更高 Sharpe」來衡量投入 |

---

## 6. 守治權紅線總表(綜合視角四 + 審查修正)

| # | 紅線 | 違憲點 | 架構強制 |
|---|---|---|---|
| R1 | 哲學全文/embedding 進特徵或預測管線 | #8 + 靈魂「只用真實資料」;全文量化零價值 | schema 分離 + feature role 對 `philosophy_*`/embedding 表無 SELECT + import-lint fail + 禁跨 schema JOIN |
| R2 | 哲學/LLM 解讀取代或加權預測數字 | #1 + 「靈魂成功=經濟價值非哲學說法」 | 解讀層唯讀下游、零寫回;開/關解讀預測 byte 級一致(契約測試) |
| R3 | AI 生成哲學內容入庫當真兆 | #1 + clean-room #16 | `work_type<>'ai_generated'`、`license='public_domain'` CHECK;`source_url`/`retrieved_at` NOT NULL;content hash 可重驗未改寫 |
| R4 | 因子假說跳過四道漏斗/#14 | #11/#14/#15 | 進生產須有 `verify_candidate_promotion`+`run_economic_eval` artifact;哲學來源僅元資料註記、非提拔依據;淘汰因子不復活 |
| R5 | 顧問編造數字/引用不可溯源 | #1/#10 | 數字欄必附 `source_ref`、引文必附 `work_id+locator`,缺 ref 攔截;生成後校驗;**非公版來源禁引(審查修正 C-3)** |
| R6 | 把「學習」誤解成用哲學訓練預測模型 | 紅線 1+2 合體 | 訓練 input loader 白名單只含 raw 市場/總經表;README 明列「哲學庫≠訓練語料」 |
| R7 | 三敵任一方向鬆動 | #1/#8/#15 零容忍 | 既有三敵護欄對哲學層一視同仁、無專屬豁免;宣稱「哲學提升績效」須有真實 eval artifact |
| R8 | 範圍蔓延納非哲學離題 | 「能抓≠該抓」排除純物理等 | `domain` 白名單 CHECK;抓取硬編碼主題來源、無開放域爬取;逐部判定主題 |
| R9 | **(審查新增)逆向鏡翻轉模型結論** | 哲學凌駕數據(視角三隱患 C-1) | 逆向段落只輸出風險/位階視角、須錨定真實特徵;生成後校驗禁與模型分數相反的祈使語 |
| R10 | **(審查新增)`stock_philosophy_tag` 回流為 feature** | 哲學標籤變預測特徵(紅線 1 變體) | tag `score` 純數值規則、量化本體寫入、非 LLM 判;tag 表永不進 feature 白名單 |

---

## 7. 成功定義

- **核心**:augur 顧問能**引哲學素養(多視角/逆向/週期觀)解讀市場,但預測仍 100% 來自真實資料模型**——可解釋性↑、角色深度↑、**預測誠實性與績效不變**。
- 具體可驗:
  1. 顧問對任一 top-N 選股,能給多學派鏡頭解讀,**每句哲學引文逐字可溯源(source_url 可開驗)、每個數字 trace 回 payload**。
  2. **開/關解讀層,預測數值 byte 級一致**(哲學零改動數字)。
  3. 生成後防幻覺閘攔截率:杜撰數字/非庫引文/未來語/非公版來源測試案例 100% 攔截。
  4. import-lint + DB role 隔離:feature/model 層對 `philosophy_*` 零可讀路徑(架構不變式恆成立)。
  5. (若做 L1)因子閉環:類比學派共因子被去重零 usage 擋下、真新假說走完 #14、飽和可宣告。

---

## 8. 誠實評估(#15,不誇大)

**對「預測績效」的真實貢獻:近乎零。**
- 因子層已飽和:單因子哲學缺口(ROE/PEG/F-Score/低波…)試盡皆過經濟價值 #14 淘汰;衍生/交互/raw 三層窮盡亦飽和(memory `feature-execution-plan`)。哲學能提供的**因子假說多半映到既有 35 特徵的共因子**,會被 L1 去重或 #14 淘汰。
- 廣博哲學全文**量化零價值**(治權明文):全文永不進預測管線,對 Sharpe/IC **零貢獻**。
- L1 因子閉環的期望 alpha 貢獻**近乎零**;其唯一價值是「把哲學庫成長接成有紀律、去重、可宣告飽和的閉環」,防止未來重複燒 usage 重測已死因子——是**成本紀律**而非**收益來源**。
- **不誇大**:任何「哲學加持後 Sharpe 更高」的宣稱,無真實 `run_economic_eval` artifact 即當假兆沉默(#15)。前沿仍是 horizon(H120>H60)×宇宙×執行,不是哲學。

**對「顧問可解釋性/角色深度」的貢獻:這才是價值所在。**
- 讓 augur 從「一串冷數字」變成「有投資智慧脈絡、能用 Graham/Le Bon/Marks/孫子解讀當下、且逐字可溯源」的顧問——直接兌現靈魂「有紀律的顧問,不是自動駕駛」。
- 提升的是**人採用預測時的理解與信任**(what/why),以及矛盾訊號的呈現(多視角防確認偏誤)——但**預測本身的誠實性與績效一位不變**。
- 一句話:**哲學給視角與縱深,數據給結論;此計畫買的是「可解釋性與角色」,不是「更高績效」——這定位必須誠實傳達給用戶,以此衡量投入。**

---

## 相關檔案(絕對路徑)

既有:
- `/home/hugo/project/augur/src/augur/philosophy/framework.py`(框架表 DDL + 學派/原則/映射/思想家 SEED)
- `/home/hugo/project/augur/scripts/build_philosophy_framework.py`(框架建表入口)
- `/home/hugo/project/augur/src/augur/core/db.py`(psycopg2 連線單一入口)
- `/home/hugo/project/augur/scripts/fetch_gutenberg_classics.py`、`fetch_all_thinker_works.py`、`fetch_public_domain_classics.py`(既有公版全文抓取)
- 方法論 SSOT:`/home/hugo/project/augur/reports/augur_feature_discovery_methodology_20260626.md`
- 提拔關卡:`/home/hugo/project/augur/scripts/verify_candidate_promotion.py`(HAC 於 `src/augur/evaluation/metrics.py:effective_t_hac`)
- 經濟價值收尾:`/home/hugo/project/augur/scripts/run_economic_eval.py`（`src/augur/evaluation/portfolio.py`）

建議新增:
- L2:`/home/hugo/project/augur/src/augur/philosophy/retrieval.py`、`scripts/build_philosophy_chunks.py`、`scripts/embed_philosophy_chunks.py`、`scripts/query_philosophy.py`
- L3:`/home/hugo/project/augur/src/augur/advisor/`(顧問前端 package,含唯讀界面契約 + 生成後防幻覺閘)
- L1(可選):`/home/hugo/project/augur/src/augur/philosophy/hypothesis_ledger.py`、`scripts/propose_philosophy_hypotheses.py`

新增 DB 物件(建議):`philosophy_chunk`、`philosophy_chunk_embedding`、`philosophy_context_map`、`hypothesis_ledger`;`stock_philosophy_tag` 由量化本體以純數值規則落地。

---

**一句話總結**:合憲的「學習」= 顧問**解讀層**素養擴充(L1 因子假說走 #14 裁決 / L2 公版全文 RAG 逐字檢索 / L3 綁真兆的哲學翻譯前端),與預測管線之間以 schema+DB role+import-lint 三重可強制隔離;哲學永遠是「假說來源 + 事後解讀」,經濟價值 #14 是唯一裁決者,三敵零容忍不因哲學任一方向鬆動;此計畫買的是可解釋性與角色深度,不是更高績效——誠實傳達,不誇大。