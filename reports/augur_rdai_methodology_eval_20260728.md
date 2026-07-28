# INTEG-G3：rdai 方法論反向吸收評估——來源權威分級 T0–T4 × augur 知識層治理

> **性質**：[I] 評估報告（整合計畫 P-G 之 G3；「另案小計畫再落 DDL、本檔不動 schema」）。
> **G1 驗收同檔附記**：rdai 六件 know-how（憲章／CLAUDE／README／三報告）已入庫且**端到端可檢索**（6 item／15 text 段／426 句／423 嵌入，口徑 `owned_local/local_private`）；**Qdrant 外流=0**（426 句逐一問 serving collection `kn_sent_it_ime5s30b1cd_tn1`，命中 0）。計畫原文「五件」為漏數（README 在列）。殘餘驗收＝advisor 實答 rdai 專有問題——需 Ollama 車道，批跑收後補測。

## 一、rdai 帶來什麼（原文出處＝rdai 專案憲章 §3.3／§3.2）

**T0–T4 權威分級**（逐字要旨）：T0 標準/法規原文（定義性事實最終依據）｜T1 同儕審查/國家級研究機構｜T2 產業權威數據/官方統計｜T3 廠商一手規格（**宣稱≠獨立驗證**，須標宣稱方）｜T4 產業媒體/社群（**不得單獨作為定量結論依據**）。**規則**：定義性/定量性語意至少 T0–T2；T3 只支撐「宣稱」類；T4 只當線索。

**外部來源三敵（④⑤⑥，接續 ttai 三紅線）**：④行銷誇大（獨立認證才升「事實」）｜⑤過時冒充現況（強制 `資料年份`）｜⑥來源衝突（**不武斷挑一個**——建 `conflicting` 單元並列多來源＋年份＋權威排序）。

**provenance 強制欄**：URL＋擷取時戳＋快照 hash＋權威級＋資料年份＋（DOI/標準號/章節）＋（宣稱方）——**無來源不得入庫**。

## 二、augur 知識層現況對照（實查 live DB）

`knowledge_source` 3,603 列（active 71）。現有治理欄：`approval_status/approved_by`（每源人閘）、`license_regime`（public_domain/cc_whitelist/owned_local/metadata_only 四值＝**版權軸**）、`fulltext_eligible`、`wave/protocol/pace/quota`（限速軸）、`abstract_policy`。條目層有 `review_flag` 三態（歸屬稽核）。

**缺口＝rdai 補的正是 augur 沒有的那一軸**：augur 的治理全在「**能不能拿**」（版權/限速/准入），**沒有任何欄回答「拿到的有多可信」**。`license_regime` 常被誤當可信度用——但 public_domain 的 1850 年教科書（過時）與 CC 的預印本（未審）在可信度上完全不同層。三敵中 augur 只防了①臆造（#1 零 AI 幻像）與部分⑥（review_flag），**④行銷誇大、⑤過時冒充現況在 augur 知識層無對應機制**。

## 三、augur 既有 71 個 active 源之 T 級試映（評估用，非落庫）

| T 級 | augur 源（節選） | 備註 |
|---|---|---|
| T0 類比 | `nist_webbook`；**內部 ground truth**：`ttai_erp_pilot`／`rdai_knowhow_docs`／`curation_*`（人工策展） | 內部源=rdai 所無之「T0-internal」，建議另立 `internal` 級不硬塞 T0 |
| T1 | `arxiv_search`·`europepmc`·`openalex_works`·`crossref_works`·`inspire_hep`·`nasa_ads`·`hal_france`·`doaj_articles`·`biorxiv_details`（preprint 宜 T1.5/註記未審） | 主體 |
| T2 | `fraser_stlouisfed`·`materials_project`·`gbif_species`·`chembl_molecules` | 機構數據庫 |
| T3/T4 | 現役 71 源中**近乎零** | augur 尚未接廠商/媒體源——**正因如此，現在加分級最便宜**（趁 T3/T4 還沒進來就把閘立好） |
| 不適用 | `gutendex`/`ia_fulltext`/`aozora`/`ctext`（哲學素養層公版原典） | 素養層零量化價值，本就不做定量宣稱；tier 記 `NA_philosophy` 即可 |

## 四、採納評估（建議案；DDL 另案待 hugo）

**建議採納（高值低本）**：
1. **`knowledge_source.authority_tier`**（`T0|T1|T2|T3|T4|internal|NA_philosophy`，NULL=未評）——一欄、一次 backfill 71 active 源、新源准入時隨 `approval_status` 一併人裁。這是把 rdai「規則」變成 augur 的**機械可查詢屬性**。
2. **advisor 引註帶 tier**：檢索命中排序不動（不做加權黑箱），但引註句尾標 `[T1]`——把可信度**交給讀者**而非演算法，合 augur「系統建議、人決策」。
3. **T3/T4 前置閘成文**：未來接廠商/媒體源時，「T3 只支撐宣稱、T4 不得單獨定量」寫進 harvest 准入判準（憲章知識層多域擴充準則之增補句，屬判準層→hugo）。

**建議緩採**：`data_year`/`claimed_by` 條目級欄——augur 現行條目多為文獻（year 已有）；廠商宣稱類內容尚未入庫，等 T3 源真要接時隨閘一起上，不預建空欄。

**不採**：多語言具名向量（augur e5-small 單空間夠用，換模走既有 SOP-A）；Qdrant point 覆蓋式 Upsert（augur 句層 append-only＋誠實閘為既定憲政，覆蓋與之相牴）；`conflicting` 獨立單元（augur `review_flag` 三態＋F 軸互斥否決已覆蓋現需求，重複建制＝兩套真相）。

**成本誠實估**：①＝一支 migration＋71 列 backfill（半日內）；②＝advisor 引註格式一行；③＝憲章增補句（hugo 拍板）。**風險**：tier 本身是判斷——backfill 由我提案、**逐源人核**（決策層），不得由 AI 逕定信任等級。

## 五、結論

rdai 對 augur 最有價值的輸出不是資料（其 DB 為空），而是**「可信度作為一級治理軸」**這個設計——augur 版權軸/限速軸已成熟，可信度軸空白，且趁 T3/T4 源未接入前補課最便宜。建議 hugo 拍板碼：`AUTHORITY-TIER-go`（採納①②③；我出 migration 小計畫與 71 源 tier 提案表供你逐源核）。
