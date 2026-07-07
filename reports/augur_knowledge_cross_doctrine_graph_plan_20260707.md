# L6 跨學說思想關聯圖 — plan-first 計劃（v2，對抗壓測後重寫）

**日期**：2026-07-07 ｜ **性質**：計畫先行報告（CLAUDE #20），寫給用戶拍板 ｜ **層次**：知識理解金字塔 L6（素養層、零量化價值、不進預測管線）
**修訂**：v1 基於**不完整現況實查**（漏查 affinity/corpus_stats/edge/derivation_method），提議重造已存在物 + 用 free jsonb 拆既有護欄 → 經 4 鏡對抗壓測（wioqo9d5w）**REVISE**，v2 據實查真實現況重寫。**教訓：planning 前須窮舉查現況（#15）。**

---

## 0. 三十秒讀完 + 誠實定調

**最重要的更正**：**L6 的計算 machinery ~80% 已經建好了**（見 §1）。詞級相關係數（npmi/jaccard/llr 296 萬對）、實體級邊（school/thinker cosine）、邊際 SSOT、關聯邊表、**no-AI 機械閘**全已存在。**L6 不是「從零建圖」,是「把既有 affinity 統一成可查、逐字可溯源、advisor 可誠實解讀的關聯視圖」——一個小很多的整合工作。**

**🔴 治權命門（既有設計已守,v2 只准沿用不准拆）**：
- **no-AI 靠 schema 機械閘**：所有 stat 表 `method_key FK → knowledge_derivation_method`,其 `method_kind CHECK IN (counting, closed_form_stat, string_rule, sql_join)` **結構上封死 AI 生成**。v1 的 free jsonb + 非-FK method_key 會拆掉這個閘 = #1 破口。**v2:任何新表一律 FK method_key、constrained provenance,禁 free jsonb 存文字。**
- **跨語靠 count-based 迴避**：既有 `group_affinity` 刻意用 count-based tfidf_cosine（零 embedding、language 為 PK＝同語言內）,**正是為了避開 e5-small 跨語崩壞**（本 session 已實證）。v1 提議 embedding 質心 cosine 是走回頭路。**v2:沿用 count-based;跨語關聯一律標低信度。**

---

## 1. 真實現況（實查坐實,取代 v1 錯誤現況）

### 1.1 已存在的 L6 計算 machinery（v1 漏查、實為已建）

| 表 | 列數 | 內容 | 對應 v1 誤以為要建的 |
|---|---|---|---|
| `knowledge_term_affinity` | **2,957,154** | 詞對 npmi/jaccard/llr（stat_value/basis_n/rank_in_a、method_key FK） | v1 P1「build_term_edges」 |
| `knowledge_group_affinity` | **6,968** | school/thinker 級 tfidf_cosine_counts + keyness（**count-based、同語言**） | v1 P2「build_entity_edges」 |
| `knowledge_term_group_affinity` | **206,670** | 詞→群組 keyness（哪些詞刻畫哪個學派/思想家） | v1 未及 |
| `knowledge_term_corpus_stats` | **448,125** | 邊際 tf_total/df_works/df_sents（**PMI 分母 SSOT**） | v1 §4 誤擔心「算不出 PMI」 |
| `knowledge_edge` | 1,374 | 關聯邊（predicate/src/dst/provenance/method_key FK/evidence_n） | v1 §3.2「concept_edge」 |
| `knowledge_derivation_method` | 17 | **no-AI 方法 registry**（CHECK 封死 AI 生成） | v1 §8 只用文字承諾（更弱） |

### 1.2 L6 真正缺口（小很多）
1. **逐字證據連結**：affinity 邊的「逐字共現出處」是否已連 concordance/sentence?（`knowledge_edge.provenance` 是 enum、非 sent_id 指標）——**須確認 + 補一層 edge→concordance 逐字證據**。
2. **統一可查視圖**：affinity 分散在多表;是否要一個統一 node/edge 查詢介面供 advisor?（可能只需 VIEW,非新表）。
3. **advisor 整合**：advisor 現用 retrieval/lexicon/concordance,**尚未查 affinity**——接進來 + 誠實解讀。
4. **coverage 誠實指標**：affinity 的稀疏性/語料局限/跨語低信度尚未匯成 coverage 報告。

---

## 2. 修正後的設計（沿用既有 pattern、不拆護欄）

### 2.1 若需新表,一律 follow 既有 no-AI pattern
- 任何新 stat/edge 表：`method_key FK REFERENCES knowledge_derivation_method`、provenance 用 constrained enum 或結構化 FK（sent_id int[]）、**禁 free jsonb 存文字**。
- 節點：ref_id 一律指回**既有真實實體**（thinker/school/work/lexicon term）;**禁 'concept' 型別走 LLM 抽取/命名**（v1 破口,刪除或釘死＝lexicon 真實字詞）。

### 2.2 逐字證據（更正 v1 的 schema 落差）
- concordance 只有 `(term, language, sent_id, position)`,**無 char_range**;char_start/char_end 住 `knowledge_sentence`。
- 逐字回溯路徑 = affinity 邊 → 共現 term → `concordance(sent_id)` JOIN `knowledge_sentence(char_start/char_end)` → byte-equal 原文。P-grounding 驗收須跨此 join 驗。

### 2.3 關聯種類（沿用既有、不引 e5 跨語）
- 詞級：npmi/jaccard/llr（已有,term_affinity）。
- 實體級：tfidf_cosine_counts + keyness（已有,group_affinity,**count-based 同語言**）。
- **跨語關聯**：既有設計刻意不做 en↔zh;若 advisor 要答跨學說(中↔西),一律標「**跨語低信度、count-based 不可跨、e5 cosine 已證弱**」,不給硬數字。

---

## 3. 修正後的分階段（整合為主、非重算）

| 階段 | 元件 | 驗收 |
|---|---|---|
| **P0 確認 + 視圖** | 實查 affinity 邊是否已連逐字;若否,設計 edge→concordance 證據連結;建統一查詢 VIEW（node=既有實體、edge=既有 affinity） | 能對任一 affinity 邊回查逐字共現句;VIEW 不重造 stat |
| **P1 逐字證據補全** | edge→concordance(sent_id) JOIN sentence(char_range) 之 provenance 連結（若缺）;method_key FK 一律齊 | 抽樣邊逐字 byte-equal;no-AI FK 機械擋（非文字承諾） |
| **P2 coverage 誠實指標** | 節點覆蓋/邊密度/逐字支撐率/**跨語低信度旗標**/語料局限 | 稀疏與跨語限制誠實揭露 |
| **P3 advisor 整合** | advisor 查 affinity + 逐字回查 + guard | 解讀 grounded、數字 ∈ affinity 白名單、逐字回查、**零預測洩漏**（isolation 靠 src/augur/knowledge/ 之 import 前綴自動覆蓋,既得） |

---

## 4. 修正後的 advisor 例（v1 招牌是幻覺,更正）

- **v1 錯例**：「孔子的仁 ↔ 孟子的義 PMI 3.2」——實查「義」**不在 stat_vocab**,(仁,義) 在 term_affinity 是 **0 列**（即使 concordance 同句共現 318 處）。**advisor 對不存在的邊講數字 = 幻覺**。
- **v2 正例**：只用**實際存在的邊**（如仁↔禮 cooc_sents=74、term_affinity 有值）;概念不在 stat_vocab（zh 僅 ~4,625 詞）者,coverage 誠實標「未進 stat_vocab、無法成邊」,advisor 據實說「語料中此概念未達統計門檻,無法給關聯數字」。

---

## 5. 命門 / 不做什麼（明文）

1. **no-AI 靠 schema FK 機械閘**（method_key → derivation_method）,不靠文字承諾;禁 free jsonb 存 LLM 文字。
2. **相關係數沿用既有 count-based**（term_affinity/group_affinity + corpus_stats 分母 SSOT）,**禁引 e5 embedding cosine 做跨語**（已證弱）。
3. **每邊逐字可溯源**（edge→concordance→sentence char_range byte-equal）;無證據標「弱/方向性」。
4. **概念節點＝既有真實字詞/實體**,禁 LLM 抽取命名。
5. **誠實 coverage**（含跨語低信度、stat_vocab 門檻外概念）非宣稱全知。
6. **advisor 解讀「不入 knowledge_*/不成 citation/不進預測管線」**（isolation 已由 import_isolation 機械釘死）;會話原文仍寫 chat_message（local_private、owner 收窄）——區分「真兆知識庫」與「對話原文庫」。
7. **正名**：「關聯圖」為主、「真理圖」為喻;避免過度宣稱。

---

## 附註 — 對抗壓測（wioqo9d5w）關鍵修正

| 鏡抓到 | v1 錯 | v2 修 |
|---|---|---|
| L6 已建 | 現況失實、提議重造 | §1 據實查改寫、整合為主 |
| provenance free jsonb | 拆掉 no-AI schema 閘 | method_key FK + constrained provenance |
| PMI 邊際 | 誤以為算不出 | corpus_stats 已是分母 SSOT |
| 招牌例仁↔義 | 幻覺(義不在 vocab) | 改用實際存在的邊 + coverage 誠實標 |
| char_range | schema 落差(concordance 無) | JOIN sentence 取 char_range |
| 跨語 cosine | 走回頭路引 e5 | 沿用 count-based、跨語標低信度 |
| 「不落庫」 | 措辭含糊 | 精確化(不入真兆庫 vs chat_message 持久化) |

*本計劃屬 plan-first（CLAUDE #20），實作前須用戶拍板。真實 gap 小、風險低（整合既有 machinery、非從零建）。*
