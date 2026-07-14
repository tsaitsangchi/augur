# R-H 修憲提案 v3 — OCR/ASR 轉錄≠AI 生成 + 本機/SFTP 明文豁免

- **日期**：2026-07-14
- **性質**：#20 計畫先行／治權判準變更（憲章第三部 philosophy/知識層）；**高風險門檻**（改治權檔 + 跨檔一致 #19）→ 本提案先出，**待 hugo 審 + Fable 5 檔位終審後才動憲章本文**（#28 檔位表：治權檔增修＝Fable 5；本稿由 Opus 4.8 謹慎起草）。
- **決策前提（hugo 2026-07-14 拍板，本提案不重議、只落實）**：
  - **R-H-OCR**：機器逐字轉錄（OCR/ASR）**≠ AI 生成**，得入 `knowledge_item_text`。
  - **R-H1**：本機匯入②/遠端 SFTP③ 通道（自有資料）**明文豁免**來源審批狀態機，以 license DB CHECK + `cli_identity` TTY 身分閘為治權。
  - 依據：「②③都是為自有資料，所以都是合法必須打通」（owned_local 自有內容，非外部策展源）。
- **前史（誠實承接）**：本軌 v1（`augur_ocr_asr_transcription_amendment_20260713.md`）、v2（`augur_transcription_isolated_layer_v2_20260713.md`）經對抗審查兩度駁回，核心阻點＝**whisper 流利幻覺文字層無自動檢出**。hugo 已於決策層裁定接受此殘餘風險 → v3 **不再以此為 blocker，改為明文記載為已知極限**（#8 誠實、不佯稱已解）。

---

## 一、R-H-OCR：轉錄≠AI 生成

### 1.1 判準（三分，寫入憲章）

| 類 | 定義 | 裁決 | source_type |
|---|---|---|---|
| **轉錄**（transcription） | 把**既有真實內容**逐字轉為文字（圖片文字→OCR、語音→ASR），**不新增語意** | ✅ ≠AI 生成、得入庫 | `ocr_extract` / `asr_transcript` |
| **生成**（generation） | AI 產出**原本不存在**的新內容 | ❌ 違 #1、禁 | （`ai_generated` DB CHECK 硬擋） |
| **詮釋/caption** | AI 對圖/音**生成新的描述、摘要、標題** | ❌ 違 #1、**維持禁**（v1 已裁） | — |

**判準句（擬入憲章共同不變式①）**：「**逐字轉錄既有內容（OCR/ASR）＝真兆之搬運、非 AI 生成；AI 對內容之新增詮釋（caption/摘要/翻譯改寫）＝生成、禁入庫。** 判據：產出文字是否**逐字對應原始既有內容**——是→轉錄（准）；否（新增語意）→生成（禁）。」

### 1.2 憲章條文增修（精確定位）

- **共同不變式①**（line 152 `docs/系統架構大憲章_v1.45.0.md`）現：「來源限真實文獻、禁 AI 生成入庫（`source_type`/`work_type` 禁 `ai_generated`）」。
  **增補**：「——**機器逐字轉錄（OCR 圖片文字／ASR 語音）＝既有真實內容之搬運、不屬 AI 生成**，得以 `source_type∈{ocr_extract,asr_transcript}` 入 `knowledge_item_text`（限 owned_local 自有內容、逐字無新增詮釋、provenance 存原始檔 sha1＋引擎版本可溯源 #1）；AI 對圖/音之**新增詮釋（caption/摘要/翻譯改寫）維持禁**（違 #1）。」
- **全文准入三軌**（line 157 owned_local 軌）現：owned_local 限「4gl/4fd/程式碼語意」。
  **增補**：「——owned_local 軌之**自有圖片/音訊**得經 OCR/ASR 逐字轉錄入 `knowledge_item_text`（source_type=ocr_extract/asr_transcript、access_scope=local_private 硬綁不變）。」

### 1.3 實作（承 v2，本機零 usage #28）

- 新 `src/augur/knowledge/transcribe.py`（#18 領域名詞）：`ocr(image_bytes)->(text,conf)|QualityFail`（tesseract 確定性）、`asr(audio_bytes)->(text,conf,segments)|QualityFail`（faster-whisper 本機、VAD＋temperature=0＋compression_ratio 閘、丟棄靜音段）。
- `fileparse.py` 加 image/audio 分派（現落 `unknown_ext`）→ 呼 transcribe；`source_type` 標 ocr_extract/asr_transcript（過 `chk_itext_source_type` ∵ ≠ai_generated）。
- provenance：`source_url=file://原檔`、額外存原始檔 sha1 + 引擎版本（於 item_text.source_url 或 provenance 欄；#1 可溯源、可重轉核對）。
- 隔離不變式不動：轉錄內容 access_scope=local_private、素養層零量化、不進預測管線。

### 1.4 ⚠ 誠實殘餘風險（明文入憲、決策層已接受）

**whisper 流利幻覺無文字層自動檢出**（技術事實，Koenecke et al. "Careless Whisper" FAccT 2024：~1.4% 轉錄含整句幻覺、38% 含有害捏造）：
- 品質閘（no_speech_prob / avg_logprob / compression_ratio）對**靜音段幻覺、低信度段**有效，但對**流利幻覺**（訓練污染語如「感謝觀看/請訂閱」，token 機率高→avg_logprob 不低）**結構性失明**；文字層無信號可辨，**唯一 ground truth ＝重聽音檔**（規模上無人做）。
- **決策層裁決（hugo 2026-07-14）**：接受此殘餘風險。憲章**明文記載**此極限（不佯稱品質閘已解 #8）；**緩解**：(a) ASR 內容標 `source_type='asr_transcript'` 可審計、可回溯原音檔；(b) 素養層隔離（不進預測管線→幻覺不污染真兆）；(c) advisor 引用 ASR 內容時，其 citations 仍過 guard 逐字閘（幻覺文字若被引用，逐字可溯回轉錄檔、非憑空）；(d) 限 owned_local（自有音檔、非公開語料）。
- **邊界**：此接受**僅限素養層**；ASR 轉錄內容**永不**經任何路徑成為預測真兆（隔離不變式 + 三敵零容忍不因本修憲鬆動）。

---

## 二、R-H1：本機/SFTP 明文豁免來源審批狀態機

### 2.1 判準（自有資料 vs 外部策展源）

- **來源治理審批不變式**（line 180，v1.41.0）之 `proposed→approved→active` + 三層 fail-closed 閘，係為**外部策展源**設計（「能抓≠該抓」＝對外部世界的納入取捨、須人拍板哪些外部源可信/該抓）。
- **本機②/SFTP③ ＝ 用戶自有資料**：非外部策展源，「能抓≠該抓」的外部取捨語意**不適用**（自己的資料本就該用、合法）。故明文豁免審批狀態機。
- **豁免≠無治理**：改以**更貼合自有資料的治權**——(a) license DB CHECK（license∈白名單、owned_local⇒local_private 硬綁）、(b) `cli_identity` TTY 身分閘（人執行、拒 AI/管道，curation.py:44）、(c) 統一 `admission_gate` 四件（見件 H）。

### 2.2 憲章條文增修

- **來源治理審批不變式**（line 180）**增補**：「——**本機匯入②/遠端 SFTP③ 通道之自有內容（owned_local）明文豁免本狀態機**（自有資料非外部策展源、『能抓≠該抓』外部取捨不適用）；改以 license DB CHECK（owned_local⇒local_private 硬綁）＋ `cli_identity` TTY 身分閘（人執行、拒 AI）＋ `admission_gate` 四件為治權。外部 API 源①仍全受本狀態機。」

### 2.3 實作（件 A1/A2/H）

- `admission_gate(source_key,license,access_scope,source_type)` 單一住所（augur.knowledge，#12）：入 item_text 前過四件——(i) license∈白名單 (ii) owned_local⇒local_private (iii) source_type≠ai_generated（OCR/ASR carve-out 例外）(iv) 自有通道經 cli_identity TTY。
- 本機/SFTP 直入 item_text（豁免 staging），但 source_key 回填（修 NULL、provenance 對等，件 A1）。

---

## 三、跨檔一致性（#19 一處改、全鏈對齊）

| 檔/層 | 需同步 |
|---|---|
| **憲章** `系統架構大憲章_v1.45.0.md` | 共同不變式①（line 152）+ 全文准入三軌（157）+ 來源治理審批不變式（180）三處增補；升版 v1.46.0 |
| **原則精華** `原則精華_v1.9.0.md` | #1 命門若明文「禁 AI 生成」須同步「轉錄≠生成」carve-out（查該檔對應條、跨檔一致） |
| **CLAUDE.md** | #17 clean-room「哲學素養層內容產生」+ #29b 若述及 source_type/OCR，同步 |
| **code** | `transcribe.py`（新）、`fileparse.py`（image/audio 分派）、`admission.py`（新）、`acquire_local_files.py`（--source-key）、`chk_itext_source_type`（DB CHECK 確認 ocr_extract/asr_transcript 過關） |
| **DB CHECK** | `chk_itext_source_type`（現＝黑名單擋 ai_generated，ocr_extract/asr_transcript 自動過 ✓，無需改）；source_type 若升白名單須納入二值 |

---

## 四、驗收 + 待 Fable 5 終審

- **驗收**：(a) OCR/ASR 轉錄內容入 item_text 過 chk_itext_source_type；(b) caption/摘要仍被擋（無對應 source_type、或 admission_gate 拒）；(c) 隔離斷言＝轉錄內容零列進 term_affinity 預測統計；(d) 憲章明文含殘餘風險條款；(e) 三治權檔跨檔一致（`grep` 對照無矛盾）。
- **⚠ 待辦**：本提案為 Opus 4.8 起草。**治權檔本文編輯前，須 hugo 審本提案 + Fable 5 檔位終審**（#28 檔位表：治權檔增修＝Fable 5、跨檔一致性審）。確認後才動憲章/原則精華/CLAUDE 本文。

---

*承 #20 計畫先行、#19 逐段檢視跨檔一致、#8 誠實記殘餘風險、#26 治權判準變更決策層人拍板（已拍板、本稿只落實）。*
