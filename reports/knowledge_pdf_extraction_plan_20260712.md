# 知識層 PDF 全文抽取計畫書(plan-first #20;D2 後續、待 hugo 拍板)

**日期**:2026-07-12|**緣起**:解析器計畫 T0 之 D2 拍板=「另立 PDF 抽取計畫」
**問題**:license 合法但**全文只有 PDF** 的內容現一律 `skip_pdf` 誠實停——既有帳 **976 件**+OAPEN **61 本**(cc_whitelist 學術書)+未來 IA/EDGAR 部分件。這是知識層最後一塊大內容缺口。

## §0 核心張力(先誠實面對,才有合格計畫)

**#1 逐字零 AI** 要求入庫內容=原文逐字。PDF 抽文的風險不是「AI 改寫」(抽取器是確定性工具、非 LLM)而是**工程性失真**:斷字連字(hy-phen)、雙欄順序錯亂、頁眉頁腳/頁碼混入、表格線性化成亂序、掃描件無文字層(需 OCR,P8 已裁不啟動)。
**立場**:抽取=確定性轉換(合 #1);失真=品質問題,用**機械品質閘 fail-closed** 治理——閘不過=該件維持 skip_pdf,不入半壞內容。

## §1 設計

**抽取器**:`pypdf`(純 Python、無 OS 依賴、活躍維護)為主;**不啟動 OCR**(掃描件=文字層缺→誠實 `skip_pdf_no_textlayer`)。
**品質閘(全機械、任一不過=不入庫)**:
1. `text_ratio`:抽出字元數 / PDF 頁數 ≥ 300 字/頁(過低=掃描件或抽取失敗)
2. `mojibake_rate`:替換字元(U+FFFD)與非預期控制字元佔比 < 0.5%
3. `dehyphen`:行尾連字修復(`-\n` → 併字)——確定性規則、非改寫
4. `boilerplate_strip`:重複頁眉頁腳偵測(同一行在 >60% 頁面重現→剝除)——確定性頻率規則
5. 長度 ≥ 2000 字(沿用現行 skip_short 判準)

**新終態章(需 DDL:CHECK 擴列)**:`skip_pdf_no_textlayer`(掃描件)、`skip_pdf_quality`(閘 2-5 不過);原 `skip_pdf` 語意收斂為「尚未嘗試抽取」→ 抽取後歸終態。

## §2 對應 schema 與程式規畫(v1.39.0)

**Schema**:
- `knowledge_fulltext_status.status` CHECK 擴兩值(migrate script、冪等 DDL)
- `knowledge_item_text` 既有欄直用;`source_type='pdf_extract'` 標示抽取路(與 `pd_fetch`/OA 區隔、可溯源 #10)
- 策略住 DB:`adapter_config.fulltext.content='pdf_extract'`(OAPEN 列 UPDATE 即納入;IA 404 之 PDF fallback 亦可後續加模板)

**程式(1 支新增+1 支修改)**:
- 新 `src/augur/knowledge/pdf_text.py`(library 模組、領域名詞#18):`extract(pdf_bytes) -> (text, metrics)|QualityFail` ——pypdf 抽取+§1 閘 1-4 全在此、可單測
- 修 `scripts/fetch_pd_fulltext.py`:dispatcher 增 `pdf_extract` 內容模式(下載 PDF→`pdf_text.extract`→閘過才 INSERT);OAPEN 之 oai_pmh 源 URL=PDF 直鏈(dc:identifier 已存)

**依賴**:`pypdf` 入 `pyproject.toml`(純 wheel、零 OS 依賴、#23 smoke 併驗)

## §3 分階段與驗收

| 階段 | 內容 | 驗收 |
|---|---|---|
| **P0** | hugo 拍板本計畫(含 CHECK 擴列 DDL、pypdf 依賴) | 拍板紀錄 |
| **P1** | pdf_text.py+單測(良品/掃描件/雙欄/亂碼四型樣本)+DDL | pytest 過;負向樣本全被閘擋 |
| **P2** | OAPEN 61 本最小 3 件端到端(fetch→extract→閘→item_text→句→嵌) | ≥1 本落地或全數誠實終態;抽出文抽查 3 段 vs 原 PDF 逐字一致 |
| **P3** | OAPEN 全量 61→skip_pdf 積壓 976 分批重試(200/批,D3 節奏) | 全歸終態;coverage 前後對比;`skip_pdf` 殘量=0(全轉 fetched/no_textlayer/quality) |

**紅線**:OCR 不啟動(P8 原裁定不動);品質閘 fail-closed 不入半壞內容;逐字驗收=抽查比對原件(#15);license 三軌 gate 原樣。
**token 經濟**:P1-P3 執行全本地零 Claude token。
