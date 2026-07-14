# OCR/ASR 轉錄軌修憲——重寫版 v2：隔離降級素材層（plan-first #20；hugo 堅持 B 後重寫；待親拍）

**日期**：2026-07-13 ｜ **性質**：**動 #1 命門**重寫版（v1 `augur_ocr_asr_transcription_amendment_20260713.md` 經對抗審查否決；hugo 堅持保留轉錄能力→依裁定重寫非修訂）。
**AI 立場（雙留痕，先明示）**：v1 被證偽的三個結構性 blocker，本 v2 的處置是**堵住 1 個（下游洗白）、降級 1 個（laundering）、誠實承認 1 個無法消除（whisper 流利幻覺無自動檢出）**。∴ **本軌明文達不到 #1「零幻像」標準**——它靠「隔離＋標記＋永不逐字引用」把幻覺危害從『真兆污染』降到『標記為不可靠的語意素材雜訊』，而非消除幻覺。hugo 須明知在對命門開此受控例外才拍。我仍持保留。

---

## §0 v1→v2 的根本定位轉變（這是可辯護性的地基）

| | v1（被否決）| v2（重寫）|
|---|---|---|
| 轉錄內容是什麼 | **真兆逐字內容**（入 item_text、可被 advisor 逐字引用）| **隔離的、標記的、非真兆「降級語意素材」**——機械排除於 verbatim 引用、只供語意檢索與研究參考 |
| 分野論證 | 「有無真實來源」（被 v1.18.0 反例證偽）| **不再主張轉錄=真兆**；承認 whisper 幻覺在「生成側」，靠**隔離**而非「歸類為真兆」處理 |
| 對 #1 | 宣稱「非鬆動、邊界內」（自欺）| **誠實：受控接受敵人①殘餘、達不到零幻像**，靠隔離控危害 |

**核心洞察**：對抗審查的最強反對是「幻覺句被 guard 逐字閘當權威真兆引用給用戶」（最後防線污染）。v2 從根斷此路——**轉錄類永不進 verbatim-citable 集合**。幻覺句最多成為「一筆標記為轉錄、不可逐字引用、advisor 只能語意參考的素材」，永遠到不了「權威逐字引文」出口。

---

## §1 三個 blocker 的逐一處置（對抗審查裁定為驗收基準）

### Blocker 2「下游洗白」→ **堵住**（可機械驗證）
轉錄類（`source_type∈{ocr_transcribe,asr_transcribe}`）在**消費三處**機械排除於逐字引用：
- **`corpus.clean_item_sql`**（切句/嵌入/檢索准入，現 :38-51 只有 license×entity_type）：加 `source_type` 感知——轉錄類**可入語意檢索索引**，但打 `is_verbatim_citable=false` 旗。
- **`philosophy/retrieval.py`**（citation 組裝，:240 text=逐字原句）：citation dataclass 加 `source_type`/`verbatim_citable` 欄；轉錄類 citation 標記帶出。
- **`guard.py:48`**（`cite_texts=[c.text for c in citations]`＝逐字閘基準）：**轉錄類 citation 排除於 `cite_texts`**——advisor 引號逐字引文若命中轉錄內容，逐字閘**不放行**（因它不在 verbatim 基準集）→ 轉錄句無法被當逐字真兆引用。
**驗收**：紅測——植入 whisper 幻覺句入轉錄類 item_text→advisor 逐字引用該句→guard **必攔**（不在 cite_texts）；語意檢索仍能命中該筆但標記「轉錄、僅供參考」。

### Blocker 1「laundering 通道」→ **降級 + 收窄**（無法機械歸零，誠實）
AI 內容變圖/音洗白：v2 用四道收窄，且因 Blocker 2 已堵逐字引用，**危害從『權威真兆污染』降到『語意素材雜訊』**：
1. **限自產媒體**：僅用戶**親自錄製/拍攝**之媒體（自錄會議/自拍/自掃描），非網路下載/他人媒體。
2. **內容 provenance 聲明**：入庫時強制 `--origin-attestation`（人類原創聲明，留 provenance）。
3. **`source_type` 白名單 fail-closed CHECK**（改黑名單→白名單，比照 license 設計）＋**媒體登錄表 FK**（`media_registry(media_sha PK)`，item_text.origin_media_sha REFERENCES 之，堵捏造 sha）。
4. **轉錄專用 DB role grant**：僅 `augur_transcribe` role 可寫轉錄類 source_type（一般寫入端不可偽裝）。
**誠實殘餘**：「限自產媒體＋原創聲明」無法機械驗證「這張自拍截圖裡不是另一個 AI 的輸出」——靠人的聲明。但危害已被 Blocker 2 降級（不進逐字引用）。

### Blocker 3「whisper 流利幻覺無自動檢出」→ **誠實承認、無法消除**
技術事實：文字層無信號辨流利幻覺（"感謝觀看"訓練污染語 token 機率高→過信心閘）。v2 品質閘盡力但**明文承認殘餘無自動檢出**：
- **VAD 前處理**（faster-whisper `vad_filter`＝真正「丟棄靜音段防幻覺」）＋**segment 級**閘（非 document 均值）＋**temperature=0**（禁 fallback、使可重現）＋**compression_ratio 閘**（抓重複迴圈）。
- **誠實入憲**：「殘餘流利幻覺無自動檢出、僅人工抽聽；本軌達不到 #1 零幻像標準」——**不以品質閘充當充分性**。
**驗收**：轉錄含已知幻覺樣本→segment 閘擋掉低信心段；流利幻覺段**承認可能漏**，靠隔離（不逐字引用）＋標記控危害。

---

## §2 對應 schema 與程式規畫（v1.39.0；消費側全補齊，補 v1 之缺）

**Schema（DDL，audit 綠後）**：
- **新表 `media_registry`**：`media_sha varchar(64) PK, media_type varchar(8), origin_attestation text NOT NULL, owner_user_id int, registered_at timestamptz`（自產媒體登錄、provenance 硬存）。
- `knowledge_item_text` 加 `origin_media_sha varchar(64) REFERENCES media_registry(media_sha)`（FK 堵捏造）、`transcribe_min_confidence real`（**段級最壞分**非均值）。
- **`chk_itext_source_type` 改白名單 fail-closed**：`source_type IS NULL OR source_type IN ('erp_extract','pd_fetch','ocr_transcribe','asr_transcribe','local_file',...)`（封閉集、比照 license CHECK；杜絕任意字串偽裝）。
- **`chk_transcribe_provenance`**：轉錄類**硬綁** origin_media_sha NOT NULL＋transcribe_min_confidence NOT NULL＋license='owned_local'。
- `knowledge_item_text` 加 `verbatim_citable boolean DEFAULT true`；轉錄類寫入時強制 false。

**程式（1 新模組＋消費側 3 修改＋ingest）**：
- 新 `src/augur/knowledge/transcribe.py`：`ocr`/`asr`（faster-whisper，VAD＋segment＋temp=0＋compression_ratio 閘，全本地零 token）。
- **消費三閘**（v1 之缺、對抗審查點名）：`corpus.clean_item_sql`（加 source_type/verbatim_citable 感知）、`philosophy/retrieval.py`（citation 帶 source_type/verbatim_citable）、`guard.py`（轉錄類排除於 cite_texts 逐字基準）。
- `acquire_local_files.py`：圖/音→transcribe，強制 `--origin-attestation`、寫 media_registry、source_type=*_transcribe、verbatim_citable=false。
- DB role：`augur_transcribe` GRANT（僅它可寫轉錄類）。
- 依賴：faster-whisper（pip）＋tesseract（OS）＋VAD 模型。

---

## §3 治權修訂（打對 SSOT 位；對抗審查糾正 v1 誤植）

- **不動原則精華 #1**（v1 誤植——#1 是預測層特徵值命門、(a)(b)(c) 實住 #15；素養層 item_text 靈魂:48「不構成第四類來源」）。
- **靈魂**：三敵①加**隔離但書**「(此不涉素養層轉錄素材層；轉錄僅供語意檢索、永不進特徵值、永不逐字引用當真兆)」。
- **憲章 philosophy 層共同不變式①（:157）**：加**轉錄素材子軌**（掛 owned_local 下）——明文：「轉錄類（OCR/ASR 自產媒體）為**隔離降級語意素材**、`verbatim_citable=false` 機械強制、永不進 verbatim 引用、**達不到零幻像、殘餘靠隔離＋人工抽聽**；`ai_generated`/caption/摘要/詮釋仍禁」。
**升版**：靈魂＋憲章次版（判準擴充型）；**雙留痕**：本 §0/§1/§5 AI 保留＋對抗審查證偽（v1 §5）＋hugo 決定並存。

---

## §4 誠實入憲的殘餘（hugo 拍板前須明知）

1. **本軌達不到 #1 零幻像標準**——whisper 流利幻覺無自動檢出，靠隔離控危害非消除。
2. **laundering 靠人的原創聲明**——無法機械驗證自產媒體內容非合成；危害已由「不逐字引用」降級。
3. **advisor 讀轉錄做研究時仍可能誤信**（LLM 固有）——緩解＝強制 caveat 標記，但無法全防。
∴ **接受本軌＝接受「一個明文標記、機械隔離、達不到零幻像的降級轉錄素材層」，換圖/音內容的語意可研究性。**

## §5 拍板點（hugo 親拍，雙留痕）

- **B1** 接受定位轉變（轉錄=隔離降級素材、非真兆、永不逐字引用）？
- **B2** 接受 §4 三項誠實殘餘（尤「達不到零幻像」）？
- **B3** 核准 §2 機械落地（media_registry FK＋白名單 CHECK＋消費三閘＋role grant＋whisper 品質閘）？
- **B4** 核准 §3 治權修訂（憲章 philosophy 層＋靈魂隔離但書、**不動 #1**）＋雙留痕入憲？

> **執行前確認**：本 v2 須先過**第二輪對抗審查**…

---

## §6 第二輪對抗審查結論（2026-07-13）：**結構性二選一，工程無解**

二審用 code/DB 實證，確認 v2 較 v1 誠實有改進（刪「確定性」假話、明認達不到零幻像），但**「隔離成立」的核心宣稱在四條獨立通道全被證偽**，其中**一條是結構性、機械不可修**：

**核心張力（不可解）**：用戶要 AI 用轉錄做研究 ⟺ LLM 必須讀轉錄 ⟺ **顧問本體是「強制改寫引擎」**（SYSTEM_PROMPT `prompt.py:128-129` 命 qwen「不打引號、用自己的話轉述」；`build_prompt:194` 照餵 citation.text 進 LLM）。v2 的「排除於 cite_texts」只封了**逐字引用這道冷門路**——而顧問**預設根本不走逐字，主路徑是改寫複述，完全未擋**。真正機械隔離只有一條＝**轉錄整筆不進 build_prompt（不進 LLM）**，但那＝**退回 B1、殺死研究能力**。∴ **二者不可兼得**。

**可修的（六項，計畫層補實）**：guard_knowledge（`:105` 主路徑漏改）＋verified 豁免洗白／數字通道（`citation_numbers`）／DB CHECK 硬綁 `source_type↔verbatim_citable`／role grant 失效（owner=augur 繞過 GRANT→改 trigger/RLS）／caveat vaporware（prompt＋輸出側落地）／治權留痕誠實（首例對敵人①開受控例外、行號 :153）。
**不可修的（一項，結構性）**：**改寫污染**——只要轉錄進 LLM 供研究，whisper 流利幻覺經 LLM 改寫成流暢顧問白話、guard.pass=true、無來源可溯，**機械不可堵、僅 prompt 自律+人為接受**。

**重要澄清**：命門#1 的**預測層/特徵值面 airtight**（隔離不變式完好、轉錄永不進特徵值）；破口**只在素養層 advisor 改寫出口**。

**∴ 修訂方向須二擇一、如實呈 hugo（決策層受控例外）**：
- **(A) 轉錄不進 LLM** ＝ 真隔離、但退回 B1、殺死「AI 用轉錄研究」能力；
- **(B) 明文接受改寫污染為命門①受控殘餘** ＝ 自律緩解+人為接受，hugo 親簽（可修六項先補實把危害降最低，但改寫殘餘無法消）。

**(C) 折衷（AI 補充建議）**：轉錄進 DB 供**人**離線查詢/研究，但**不進 advisor 作答語料**（AI 不讀→命門乾淨；人仍可用轉錄內容做研究）——若你的「研究分析」是人做而非 AI 作答，此路兼顧。

> **本檔即完整雙留痕**：AI 兩輪勸阻＋兩輪對抗審查證偽（v1 §5 十 blocker、本 §6 四通道）＋用戶決定並存。**結構性二選一交決策層，未定前不改任何治權檔（#19/#26）。**
