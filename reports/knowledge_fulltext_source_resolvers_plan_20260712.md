# 知識層全文「源專屬解析器」計畫書(plan-first #20;待 hugo T0 拍板)

**日期**:2026-07-12|**性質**:執行層擴充(不動治權判準;全文准入三軌 gate 原樣沿用)
**問題**:#29b v1.20「harvest 完成=到達 license 允許終態」——現有 `fetch_pd_fulltext.py` 只抓「URL 直鏈且回 text/plain」,但四個已 active 源的全文都不是這個形狀,**2,620+ 件 license 合法可抓的內容卡在 metadata**。

## §0 實證地基(2026-07-12 最小探測,各 1 請求)

| 源 | 積壓 | 全文所在(實測) | 可行性 |
|---|---|---|---|
| internet_archive | **2,616** | `archive.org/download/{ia_id}/{ia_id}_djvu.txt`(302→檔案伺服器,GET -L 得純文字);`external_id`=ia_id 庫內齊全 | ✅ 探測 302 ✓ |
| sec_edgar_fulltext | 2(將增長) | `sec.gov/Archives/edgar/data/{int(cik)}/{adsh去dash}/{filename}`;組件在 staging payload(cik/adsh)+url 欄(`adsh:filename`) | ✅ 探測 200 text/html ✓ |
| fraser_stlouisfed | 2(將增長) | title API 通(X-API-Key header);**item/檔案端點形式未定**(`/api/title/{id}/items` 回 total 0)——T1 先解 | ⚠ 端點待探 |
| oapen_books | 61 | PDF 為主 | ❌ 撞 T1「誠實不解析 PDF」既有 policy(skip_pdf 帳 976 件同類)→ **T0 決策點 D2** |

**另**:今日測試在 IA 3 件上蓋了 `skip_ctype` 章——解析器上線時須先清這 3 列(見 §3 T2),否則被終態帳排除。

## §1 設計(資料驅動 #29b:策略住 DB、code 只加一個 dispatcher)

`knowledge_source.adapter_config` 增 `fulltext` 鍵(JSONB、UPDATE 資料列零 DDL):

```json
// internet_archive
{"fulltext": {"strategy": "url_template",
              "template": "https://archive.org/download/{external_id}/{external_id}_djvu.txt",
              "content": "text"}}
// sec_edgar_fulltext
{"fulltext": {"strategy": "edgar_archive", "content": "html_strip"}}
// fraser_stlouisfed(T1 探測後定 template)
{"fulltext": {"strategy": "url_template", "template": "<T1 定>", "content": "html_strip", "auth": "auth_header"}}
```

**判準**:「哪個源用哪種策略/模板」=策展資料→住 DB;「策略如何執行」(template 代換/EDGAR 組裝/剝標)=邏輯→code。新增同形源=UPDATE 一列,零改碼。

## §2 對應 schema 與程式規畫(v1.39.0 雙落實)

**讀寫表(全部既有、零新表零 DDL)**:
- 讀 `knowledge_item(item_id, source_key, external_id, url)` + `knowledge_source(adapter_config, pace_seconds, license_regime, approval_status)` + `knowledge_staging(payload)`(EDGAR cik/adsh 回查) 
- 寫 `knowledge_item_text(item_id, seq, content, language, source_url, license, access_scope)`(既有欄、逐字零 AI #1)
- 寫 `knowledge_fulltext_status(item_id, status, reason, source_url, checked_at)`(誠實終態帳,既有)

**程式(1 支修改、0 支新增)**:`scripts/fetch_pd_fulltext.py` 擴充——
- `resolve_fulltext_url(item, acfg) -> (url, content_mode) | None`:依 `adapter_config.fulltext.strategy` 分派(`url_template` 代換 `{external_id}`;`edgar_archive` 從 staging payload 組 URL);無 `fulltext` 設定→回退現行直鏈行為(向後相容)
- `content` 模式:`text`(現行 text/plain 路徑)|`html_strip`(複用 `fetch_oa_fulltext.py` 既有剝標函式,抽為共用或 import)
- 積壓查詢改為:含「有 `fulltext` 策略之源」時**忽略既有 `skip_ctype` 列**(限該源、一次性重試;其他 skip 終態不動)
- pace/limit/冪等/`--run --limit` 矩陣不變(#24/#25/#29d)

## §3 分階段與驗收

| 階段 | 內容 | 驗收(可機驗) |
|---|---|---|
| **T0** | hugo 拍板:D1 本計畫;**D2 OAPEN/PDF 路線**(a=維持 skip_pdf 誠實停〔建議〕/ b=另立 PDF 抽取計畫);D3 IA 放量節奏(建議 200/批,pace 依 DB) | 拍板紀錄 |
| **T1** | FRASER item 端點探測矩陣(≤5 請求,#25)→ 定 template 或誠實判「API 無文字端點→fulltext_blocked」 | 探測記錄+adapter_config 落列 |
| **T2** | dispatcher 實作+清 IA 3 列 skip_ctype+**每源最小 3 件端到端**(fetch→item_text→build_sentences→embed 由 03:30 timer 接) | 3 源各 ≥1 件 item_text 落地(FRASER 若 T1 判 blocked 則旗標驗收);sha 級逐字、零 AI 改寫 |
| **T3** | IA 2,616 放量(200/批背景、harness 可見、resume-safe)+EDGAR/FRASER 隨新 harvest 自動走 | `fulltext_status` 全積壓歸終態(fetched/skip_* 各有帳);coverage snapshot 前後對比 |

**紅線**:全文准入三軌 gate 原樣(public_domain/cc_whitelist 才抓);逐字零 AI(#1);skip=誠實終態非漏做;素養層零量化價值不進預測管線(隔離不變式不動)。
**token 經濟**:T1-T3 執行全本地零 Claude token;Claude 只出現在本計畫書(已花)。
**與開賽鏈零衝突**:不碰預測資料層、不碰 FinMind。
