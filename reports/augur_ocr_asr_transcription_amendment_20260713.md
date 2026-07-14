# #1 命門修憲提案：OCR/ASR 轉錄軌（plan-first #20 最高風險門檻；待 hugo 親拍）

**日期**：2026-07-13 ｜ **性質**：**動 #1 命門（三敵之首）**，跨三治權檔（靈魂/原則精華/憲章）——#20 高風險門檻，附對抗審查發現表＋AI 勸阻雙留痕。
**用戶定案（2026-07-13 hugo）**：A 最小傷害版——**只開 OCR/ASR（轉錄既有內容）＋五道緩解；caption（AI 生成詮釋）維持禁**。
**AI 立場（先明示，雙留痕）**：我對「任何模型輸出文字入 item_text」持保留；本提案的可辯護性**完全繫於「轉錄既有內容 vs 無中生有」的區分成立、且五道緩解硬綁**。若區分不成立或緩解可繞，則此修憲＝鬆動三敵①，我不背書。以下把論證與反論證都攤開，交決策層裁。

---

## §1 核心論證：這是「三敵① 邊界澄清＋轉錄軌」，非鬆動

**三敵① 的原文定義**（靈魂 v1.8.0:58）：「假資料（AI 幻像）＝ imputed／補值／hardcoded／推估——**沒有真實 API 來源的值**」。三基石之首 Source-Pure＝「非『真實來源經數學轉換』的值一律排除」。

**關鍵**：三敵① 防的是**「沒有真實來源的值（無中生有）」**，判準是**有無真實來源**，非「有無用到模型」。據此分野：

| | 真實來源 | 性質 | 對三敵① |
|---|---|---|---|
| **OCR** | 原始圖檔（圖中字**客觀存在**）| 對既有內容的**轉錄提取** | ✅ 有來源——如同 PDF 抽取對 PDF |
| **ASR** | 原始音檔（音中話**客觀存在**）| 對既有內容的**轉錄提取** | ✅ 有來源 |
| **caption** | 無（圖裡沒這段描述文字）| AI **無中生有的詮釋** | 🛑 無來源——落三敵① |
| e5 embedding | 原文（索引非內容）| 索引 | ✅ 既有先例 |

**論證**：OCR/ASR 轉錄的目標＝忠實還原原件中**客觀存在**的文字/話語（真兆），與「PDF 抽取」同構（確定性提取既有內容、有工程失真、用品質閘治理）。原始檔是真兆來源、可回溯核對。∴ 定位為 **Source-Pure 邊界內的「轉錄軌」**，caption 因無真兆來源守禁——**分野與三敵① 定義（有無真實來源）一致**。

---

## §2 誠實勸阻：殘餘「無中生有」風險（雙留痕之 AI 保留意見）

論證有一個**必須誠實面對的裂縫**——轉錄不等於純確定性抽取：

1. **whisper hallucination（最重）**：whisper 在靜音/雜訊段會**無中生有**（生成訓練污染語如「感謝觀看」、重複字幕、不存在的句子）。這是真實的「無來源之值」＝落三敵① 的殘餘。
2. **OCR 錯字/雙欄亂序**：辨識錯誤引入原件沒有的字。
3. **與 PDF 抽取的差異**：PDF 抽取是**確定性**（同輸入同輸出、失真可預測）；ASR/OCR 是**神經網路推論**（有不確定性、可幻覺）。

∴ **五道緩解是必要非充分**——它們把風險壓到「標記為轉錄、可核對」的可控範圍，但**無法保證零無中生有**。這是本修憲與「PDF 抽取（確定性）」的**本質差異**，也是我保留的核心：**開這條軌＝接受「有品質閘與誠實標記守護的、可核對的殘餘轉錄誤差」，交換圖/音內容的可用性**。caption 守禁正因它是**純無中生有、無真兆可核對**（連殘餘可控性都沒有）。

**decision-relevant**：若你認為「可核對的殘餘轉錄誤差」不可接受，應否決本提案（回到 image/audio 只存原檔+多模態索引 B1、不入 item_text）。

---

## §3 要改的治權檔（逐條前後對照）

**定位**：判準**擴充**（用戶拍板、非鬆動三敵——如 v1.20.0 CC 軌/v1.36.0 owned_local 軌之先例），原則精華維持結構、憲章＋靈魂承載。

| 檔 | 現行 | 修憲後（增） |
|---|---|---|
| **靈魂** 三敵①（:58）| 假資料＝無真實來源的值 | 補註：「**轉錄既有內容**（OCR 圖中字/ASR 音中話，**原件為真兆來源、標記非原文逐字**）≠ 無中生有的 AI 生成；caption 等**無來源詮釋**仍屬敵人①」 |
| **原則精華 #1**（三基石 Source-Pure）| 三類唯一來源 (a)(b)(c) | 補第四類界定：「**(d) 對自有真實原件之確定性轉錄**（ASR/OCR，強制品質閘＋誠實標記＋保原件＋owned_local）；**排除**無來源生成（caption/摘要/詮釋）」 |
| **憲章** 全文准入軌＋共同不變式①（:153/:157）| 三軌（公版/CC/owned_local）；禁 AI 生成入庫 | 加**轉錄子軌**（掛 owned_local 下）：`source_type∈{ocr_transcribe,asr_transcribe}`、硬綁品質閘＋原件保留＋誠實標記；明文 **caption/摘要/詮釋仍禁**（`ai_generated` DB CHECK 不動） |

**升版**：靈魂→次版、原則精華→次版（新增判準類別 (d)、屬「判準擴充」連動）、憲章→次版。**雙留痕**：本 §2 勸阻全文＋用戶定案並列入憲（憲章雙留痕機制，如 v1.45.0）。

---

## §4 機械落地（五道緩解，v1.39.0 schema＋程式）

**Schema**：
- `knowledge_item_text.source_type` 新增值 `ocr_transcribe`/`asr_transcribe`（**非 `ai_generated`**，現行 `chk_itext_source_type` 已相容、**零 DDL**）。
- **新增品質/溯源欄**（DDL，audit 綠後）：`transcribe_confidence real`、`origin_media_sha varchar(64)`（原件 sha、可回溯）、`origin_media_path text`（原件本機路徑，owned_local）。
- **新 CHECK**：`chk_transcribe_guard`＝`source_type NOT IN ('ocr_transcribe','asr_transcribe') OR (transcribe_confidence IS NOT NULL AND origin_media_sha IS NOT NULL AND license='owned_local')`——轉錄類**硬綁**品質分數＋原件＋私有。

**程式（1 新模組＋1 修改）**：
- 新 `src/augur/knowledge/transcribe.py`（領域名詞 #18）：`ocr(image_bytes)->(text,conf)|QualityFail`（tesseract 確定性）、`asr(audio_bytes)->(text,conf,segments)|QualityFail`（whisper 本機，**no_speech_prob/avg_logprob 品質閘 fail-closed**、丟棄靜音段防幻覺）。全本地零 Claude token。
- 修 `acquire_local_files.py`：`.png/.jpg/.tiff`→ocr、`.mp3/.wav/.m4a`→asr，走 owned_local，落 source_type+conf+原件 sha。
- **依賴**：tesseract（OS）＋openai-whisper 或 faster-whisper（pip）＋原件保留——#23 前置。

**五道緩解對映**：① 誠實標記＝source_type+advisor 展示層揭露「轉錄非原件逐字」｜② 品質閘＝conf 門檻 fail-closed｜③ 保原件＝origin_media_sha/path｜④ owned_local＝license 硬綁 local_private｜⑤ 不進預測管線＝domain 隔離不變式不動。

---

## §5 對抗審查發現表（2026-07-13 完成，5 維度 × 綜合裁決）

**綜合裁決：應否決、回 B1（image/audio 只存原檔+多模態索引、不入 item_text）。** 10 blocker，**三個結構性/技術性、非改文字可解**：

1. **Laundering 通道（最強反對）**：AI 生成文字只要先變成圖/音檔，經轉錄軌標 `asr_transcribe` 即逐字入 item_text。`chk_itext_source_type` 只是黑名單（`<>'ai_generated'`、DB 實查證實）、`source_type` 由 writer 自填、無媒體登錄 FK、**DB 層無法區分「轉錄 vs 生成」**——「禁 AI 生成入庫」從『DB 物理擋』退化為『信任每個寫入端誠實』。
2. **下游洗白（code 實證）**：whisper 幻覺句入 item_text→成 citation→guard 逐字閘（guard.py:50 只驗 quote∈cite_texts、無 source_type 感知）**PASS**→當權威真兆逐字引用給用戶。緩解①「展示層揭露」是 **vaporware**（ItemCitation/retrieval._ITEM_COLS 皆無 source_type，旗標到不了 advisor；且與憲章 v1.30.0 逐字區塊不對外顯示衝突）。**最後防線（對話出口）被靜默污染**。
3. **whisper 流利幻覺無自動檢出（技術事實）**：品質閘 no_speech_prob/avg_logprob 對訓練污染語（「感謝觀看/請訂閱」，token 機率高→avg_logprob 不低）**結構性失明**；whisper 內建抑制 `no_speech_prob>0.6 AND avg_logprob<-1.0` 的 AND 條件使流利幻覺不被抑制。文字層無信號可辨，**唯一 ground truth 是重聽音檔（規模上無人做）**。（Koenecke et al. "Careless Whisper" FAccT 2024：~1.4% 轉錄含整句幻覺、38% 含有害捏造。）

**§1 地基被 v1.18.0 反例證偽**：AI 整理版權著作「有原書來源」卻仍被判死為 AI 生成——證明真正判準是「**逐字複製既有內容 vs 生成新語意**」，非「有無真實來源」。whisper 幻覺段落在**生成側**（被 v1.18.0 判死那側）。

**另兩個治權自傷**：§3 把轉錄豁免誤植入原則精華 #1（預測層命門，(a)(b)(c) 實住 #15、素養層 item_text 靈魂:48 明言「不構成第四類來源」）＝污染命門；§3 草擬「確定性轉錄」與 §2 自承「神經推論可幻覺」矛盾＝**把假話寫進基石＝敵人③入憲**。

---

## §6 結論（2026-07-13）：**本提案 as-written 否決，AI 建議回 B1**

對抗審查發現三個**非改文字可解的結構性 blocker**（laundering 通道／下游洗白／流利幻覺無檢出），且 §1 地基被 v1.18.0 反例證偽。**動三敵之首、最後防線（advisor 對話出口）會被靜默污染——這是最不可接受的失效。AI 立場：認同否決，不以本提案呈拍板。**

**替代 B1（AI 建議、治權內、不碰 #1）**：image/audio 存**原檔**（真兆、owned_local）＋ **多模態 embedding 作檢索索引**（可拋棄可重建，如同 e5 對文字）——`不入 item_text 當內容`。這滿足「本地 AI 研究圖/音（語意檢索、相似度分析）」的實質，且與現行架構對稱、零命門風險。需開 embedspec 新向量世代（P6 級技術拍板，非修憲）。

**若仍堅持轉錄能力**（決策層有權）：對抗審查裁定須**另立全新提案（重寫、非修訂）**，且至少含：限**用戶自產媒體**＋內容 provenance 聲明／`source_type` 白名單 fail-closed CHECK＋媒體登錄表 FK（堵捏造 sha）＋轉錄專用 DB role grant／**轉錄類永不進 verbatim-citable 集合、只供語意檢索**（retrieval/guard/corpus 三處補 source_type 機械閘）／whisper segment 級閘＋VAD＋temperature=0＋compression_ratio 閘／**誠實入憲「殘餘幻覺無自動檢出、僅人工抽聽」＋承認此軌無法達 #1 零幻像標準**。—— AI 對此仍持重度保留（雙留痕）。

> 本檔即雙留痕：AI 勸阻（§2/§6）＋對抗審查證偽（§5）＋用戶決定並存，供決策層裁。**未化解結構性 blocker 前，不改任何治權檔（#19/#26）。**
