---
title: PDF-C｜弱／掃描 PDF 本機 OCR 補抽計劃
status: plan_first
series: kh_loop_evolve
open_problem: "PDF-C"
date: 2026-08-06
viewpoint: 2026-08-06T16:03+08:00
layer: "[I]"
role: 對 local 已入庫／可回溯原件之弱字層 PDF，以 Tesseract 做頁面光柵轉錄補抽——非開 caption、非開 ASR
parent: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
inherits_boundaries:
  - FZ/GATE-keep · no-SIM-apply · no-cron-B3 · hold 市場 #1
  - no web／對話裸 approve knowledge_source（T2 機械可）
  - #1：禁 AI 生成／caption／摘要改寫入 item_text；OCR＝有原件真兆的轉錄
  - 繼承 reports/augur_ocr_asr_transcription_amendment_20260713.md 否決結論：本計劃**不**重開 ASR／whisper、不改三治權命門 as-written
engine_intent: tesseract
engine_status: steward_selected
tool_go: audits/PDF-C-OCR-TOOL-GO-20260806.md
tool_status: executed
code_go: audits/PDF-C-OCR-CODE-GO-20260806.md
code_status: executed
apply_go: audits/PDF-C-OCR-APPLY-GO-20260806.md
apply_status: executed
render: pymupdf
self_reported: true
---

# PDF-C OCR plan-first · 2026-08-06

> **一句**：對 **local 弱／近空文字層 PDF**，用本機 **Tesseract（chi_tra+eng）** 頁面光柵轉錄；S0 標記；禁 ASR／caption。  
> **性質**：[I]；**P0 寫庫已 APPLY**（見 apply 帳）。  
> **工具／碼／apply**：✅ tool · ✅ code · ✅ **apply P0（4／4）**。

---

## §0 護欄

```text
PDF-C-OCR-plan | FZ/GATE-keep | hold-#1 | no-ASR | no-caption | tesseract-only
# 繼承 2026-07-13 OCR/ASR 修憲否決：不重開 whisper；不把假話寫進 Source-Pure 基石
```

| 准 | 禁 |
|---|---|
| PDF 頁→光柵→Tesseract 轉錄；原件可回溯 | caption／摘要／LLM 改寫入 `item_text` |
| 僅 `local_files`／既有 upload 真兆路徑 | 任意上傳圖「洗成」知識正文無 provenance |
| 標記 `source_type`／方法碼；品質門檻 fail-closed | 把 OCR 錯字當確定性 PDF 抽取、隱瞞來源 |
| 弱字層補寫／旁路段；幂等可重跑 | 無 GO 全庫盲掃；cron 自動上線 |
| 引擎：**Tesseract**（本機已有 `chi_tra`+`eng`） | 本計劃範圍內上 Paddle／雲 OCR／ASR |

---

## §1 與 2026-07-13 修憲否決的關係

[`augur_ocr_asr_transcription_amendment_20260713.md`](augur_ocr_asr_transcription_amendment_20260713.md) **as-written 否決**（laundering／下游洗白／whisper 流利幻覺）。本 PDF-C **不翻案**，改走**窄切**：

| 否決點 | PDF-C 對策 |
|---|---|
| whisper 幻覺 | **不納 ASR**；僅 Tesseract |
| laundering（生成→圖→轉錄） | 客體限：**已登録 local PDF 原件**（`source_url=file://…`／uploads 樹）；新 OCR 寫入須綁 `origin_media_sha`＝原 PDF sha |
| 下游洗白（當逐字權威） | OCR 段 **明示非 pypdf 逐字**；advisor／readout 展示可標「OCR 轉錄」；可選：OCR 段不進 verbatim 強閘同權（P3 二選一，GO 時釘） |
| 動三治權命門 | **本計劃不改靈魂／原則精華／憲章**；若需新 `source_type` 值，另開 admission 白名單擴充 GO（見 §4） |

**殘餘誠實**：Tesseract 仍有錯字／欄位亂序——接受「可核對殘差」，換掃描檔可用性；**零誤差不宣稱**。

---

## §2 客體與觸發

### 2.1 優先佇列（建議）

| 優先 | 條件 | 約量（2026-08-06） | 備註 |
|---|---|---|---|
| **P0** | `nchars < 200` 且 domain=`local` 標題 `.pdf` | **4** | 弱字層；先煙測 |
| **P1** | acquire `short`／`no_text` 跳過但 FS 仍有檔 | ≥1（`p_cron..` 等） | 需新建或補段 |
| **P2** | `200 ≤ nchars < 2000` | **25** | 可抽樣 OCR 對照，勿盲蓋優質字層 |
| **P3** | 字層足但抽樣抽查失敗 | 按需 | 不預設全跑 |

### 2.2 觸發規則（碼開後）

1. **先** `pypdf`（現行 `fileparse._read_pdf`）。  
2. 僅當 `strip` 後長度 **&lt; `OCR_TRIGGER_CHARS`（建議預設 200）** 或 reason∈{`no_text`,`short`} → 才進 OCR 臂。  
3. 頁數／耗時上限：`OCR_MAX_PAGES`（建議 40）、超則截斷並記 note（#15 誠實）。  
4. 合併策略（釘定於 GO）：  
   - **A（建議）**：弱字層 → **替换／補寫** `item_text`（留 `source_type`／note＝ocr）；或  
   - **B**：原字層 seq 保留，OCR 寫入 **後續 seq** 並標 method。

---

## §3 機械設計（草案·不開碼）

### 3.1 管線

```text
PDF path → (pypdf 字層)
        → if weak/empty:
             pdftoppm/PyMuPDF 渲頁圖（DPI 建議 200）
             → tesseract -l chi_tra+eng
             → 品質閘（見 §3.3）
             → 寫入 item_text（標記）＋ kh4.refresh
```

### 3.2 依賴（本機現況 2026-08-06）

| 件 | 現況 | 計劃動作 |
|---|---|---|
| `tesseract` | ✅ `/usr/bin/tesseract` 5.x；lang=`chi_tra`,`eng`,`osd` | 守；繁中文件用 `chi_tra+eng` |
| `pytesseract` + PIL | ✅（`fileparse._read_image` 已用） | 複用 |
| 渲頁 | ✅ **pymupdf**（tool-go）；可不裝 poppler | 守；備援仍可 poppler `pdftoppm` |
| `fileparse._read_pdf` | 空字層 → `no_text` | 接 OCR 臂（僅 flag／GO 後） |

### 3.3 品質閘（fail-closed 草案）

| 閘 | 草案 |
|---|---|
| 最短正文 | OCR 全文 &lt; `MIN_CHARS`（與 acquire 對齊 50，弱補建議 ≥80）→ 不寫庫 |
| 空頁比 | 空白頁 &gt; 50% → skip／人工 |
| 字符可信 | 可選：逐頁 mean conf &lt; 閾 → 該頁丟弃或整檔拒（Tesseract TSV） |
| 禁幻造標記 | 寫入前綴或 metadata：`via=pdf_ocr`；**禁止** LLM 润色後再入庫 |

### 3.4 `source_type`／provenance

| 方案 | 內容 | 取捨 |
|---|---|---|
| **S0（最小·建議 v1）** | 仍用 `local_upload`；正文頭或旁注 `<!-- via=pdf_ocr -->`；另表／log 記 sha | 零白名單改動；展示力弱 |
| **S1** | 白名單加 `ocr_transcribe`＋admission 擴充；硬綁 origin sha | 較清；須獨立 GO／對照 07-13 緩解 |

**推薦**：試點用 **S0**；若正式入顧問引文出口，再升 **S1**＋「OCR 段展示揭露」一併 GO。

### 3.5 模組落點（開碼後）

| 落點 | 職責 |
|---|---|
| `fileparse` | `_read_pdf` 弱則可呼叫 `_ocr_pdf_pages`；reason=`pdf_ocr`／`missing_ocr` |
| 新 `scripts/backfill_pdf_ocr.py`（或等價） | 佇列 P0→P2；`--dry-run`；`--item-id`；禁止無上限全表 |
| `acquire_local_files` | 可選：新入庫 `no_text` 時若 `--ocr` 旗才試（預設 off） |

---

## §4 分階段

| 階 | 交付 | GO |
|---|---|---|
| **P0** | 本計劃＋弱清單凍結＋引擎釘 Tesseract | 本檔 ✅ |
| **P1** | 渲頁依賴選定並裝好；單檔煙測 | `PDF-C-OCR-tool-go` ✅ `audits/PDF-C-OCR-TOOL-GO-20260806.md` |
| **P2** | `fileparse` OCR 臂＋`--dry-run` backfill；P0 四件對照 | `PDF-C-OCR-code-go` ✅ `audits/PDF-C-OCR-CODE-GO-20260806.md` |
| **P3** | 准寫庫：S0 標記＋kh4.refresh；P0 | `PDF-C-OCR-apply-go` ✅ `audits/PDF-C-OCR-APPLY-GO-20260806.md` |
| **P4** |（可選）S1 `ocr_transcribe`＋顧問「OCR 轉錄」揭露 | 另句 |

**未 GO 前**：不改 acquire 預設、不寫庫、不裝成 cron。

---

## §5 與閉環 §4 其他刀的關係

| 刀 | 關係 |
|---|---|
| **#1c AUTO-LIFT** | **∥ 不擋**；OCR 補料後答對再抬 |
| **#1h live** | OCR 後可納弱 PDF 為抽樣題 |
| **#5 KH8** | 正交；不因 OCR 宣佈加深 |
| **PDF-A／PDF-R** | ✅ 已結；本刀接棒 |

```text
可同步:  #1c 開旗試點  ∥  PDF-C P0–P1（計劃／工具）
串列:    寫庫（P3）須 tool+code GO；S1 須另 GO
```

---

## §6 Paste-ready

確認引擎（已選）：

```text
PDF-C-OCR-engine = tesseract | langs=chi_tra+eng
```

工具依賴 GO（例）：

```text
PDF-C-OCR-tool-go | engine=tesseract | render=poppler|pymupdf | FZ/GATE-keep
```

開碼：

```text
PDF-C-OCR-code-go | trigger_chars=200 | max_pages=40 | source_mark=S0 | no-ASR | no-caption
```

准寫庫：

```text
PDF-C-OCR-apply-go | queue=P0 | dry-run-pass | FZ/GATE-keep
```

---

## §7 驗收（本計劃書）

1. 能復述：客體＝弱／掃描 **PDF**；引擎＝**Tesseract**；禁 ASR／caption。  
2. 明寫與 2026-07-13 否決之繼承與窄切。  
3. 分階 GO；預設不寫庫。  
4. 本機依賴與弱檔量誠實（105 已入庫；OCR＝補豐）。  
5. 與 evolve SSOT `#PDF-C` 對得上。

---

## §8 讀序

1. `reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md` §4  
2. `reports/augur_ocr_asr_transcription_amendment_20260713.md`（否決邊界）  
3. **本檔**  
4. `src/augur/knowledge/fileparse.py`（現行 `_read_pdf`／`_read_image`）

*完。[I] self-reported。status=plan_first；開碼須 GO。*
