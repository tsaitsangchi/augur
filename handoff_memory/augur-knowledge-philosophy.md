---
name: augur-knowledge-philosophy
description: 知識三部曲+哲學素養/顧問層全貌 — 八層金字塔、命門與隔離不變式、工具鏈(T/W/P 編號)、review_flag 三態、嵌入口徑、版權雙軌、未實作債
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9009c955-58bc-46c5-904b-ed515e2be723
---

augur 知識/哲學層(2026-07-03 建錨)。**三部曲**:①expansion(registry 自我窮舉:OpenAlex 分類樹/re3data/獎項→taxonomy 4,798/query 4,706)→②harvest v1.3(上線:排程矩陣+熔斷+resume)→③text v2.0(八層金字塔 L0 來源→L1 全文→L2 句/concordance→L2.5 統計→L3 lexicon 定義→L3.5 衍生→L4 三粒度嵌入→L5「誠實博學的我」→L6 治理橫切;執行序 W1-W9、W5 嵌入進行中)。計畫 SSOT=`reports/augur_knowledge_{registry_expansion,harvest_landing,text_understanding}_plan_20260702.md`(讀計畫檔以最新修訂節為準——計畫宣稱曾兩度失實 #15)。

**命門 7 條(text v2.0)**:①逐字定義不由 AI 生成入庫(合法載體=公版辭書/註疏+concordance+純計算+真實文獻)②「全知」字面不得鑄入 schema(一律 coverage)、必答「不知道」分三級 ③知識層零量化價值不進預測管線不產因子(機器強制)④確定性優先禁 LLM 判斷入庫 ⑤AI 記憶物理隔離籠(獨立 schema+is_ai_generated 恆真 CHECK)⑥charter 宣稱誠實化 ⑦嵌入=索引非內容(命中後仍逐字引原文)。

**隔離三重強制**:AST import-lint(`tests/test_philosophy_isolation.py`:7 預測 pkg 禁 import philosophy/advisor)+DB role 無 SELECT+DB CHECK(work_type/license/source_type 禁 ai_generated、derivation_method.method_kind 封閉 4 值無 LLM/embedding)。哲學對預測績效貢獻誠實評≈0(因子飽和、ROE/PEG/F-Score 皆過 #14 淘汰),買的是可解釋性;哲學→量化唯一橋=`verify_philosophy_factors.py`(principle_factor_map 回填 validated_ic/econ、HAC-t+#14)。advisor 防幻覺=機械閘非自律(引文逐字∈citations、數字∈payload.numbers() round4、檢索空=固定句、逆向不翻轉模型結論);LLM 界面抽象未綁定。

**工具鏈編號體系**:T-1 歸屬稽核(`audit_work_attribution` 姓名 token 子集+生卒容差全等±15/子集±2、寧殺勿留)→T0 DDL(`migrate_text_understanding_ddl`;harvest 層 DDL 另住 `harvest_knowledge.py --migrate-only`、**兩住所勿混**)→T1 OA 全文(`fetch_oa_fulltext`,Unpaywall、需 UNPAYWALL_EMAIL)→T2 lexicon(`build_lexicon` 六源:說文/康熙/Webster1913/Roget1911/王弼注/十三經注疏)→T3 切句(`build_sentences`,排除 work_type dictionary/thesaurus)→T4 concordance(`build_concordance`,textnorm 斷詞、16 hash 分區)→T5 chunk。雙引擎:`acquire_knowledge`(13 adapter;generic_json=新來源零 code)+`promote_knowledge`(mapper;external_id 優先序 doi>arxiv>chembl…)。嵌入 `embed_knowledge`(lexicon/sentence)+`embed_philosophy_chunks`(chunk)。

**review_flag 三態=全下游共同閘**:NULL=未稽核、true=誤配、false=通過;builder 用 IS NOT TRUE、**嵌入層最嚴 fail-closed(=false 才嵌)**;常備不變式:有全文 work NULL=0、concordance 計數=grep 數、reference(corpus_class)語料句數=0。reviewed_by∈audit/provenance/human,provenance 僅限策展+身分可驗(staging 晉升 516+T2 辭書源 7=523;其餘 794=audit)。

**嵌入口徑**:統一 `intfloat/multilingual-e5-small` 384 維 CPU、"passage: "/"query: " 前綴、normalize(bge-m3 CPU 53.7h 遭棄);**分表分層**(HNSW post-filter 陷阱)、灌完才建 HNSW(maintenance_work_mem 2GB)、帶過濾 kNN 用 hnsw.iterative_scan=relaxed_order;zh junk 過濾禁按長度(短句=真訓詁)、僅全符號規則;resume=knowledge_build_meta 游標。吞吐實測:lexicon ~10 條/s(全量 ~4.3h)、句 77/s、T4 44k 列/s。**textnorm=L2/L3/L5 JOIN 鍵契約 SSOT**(NFC+不繁簡互轉、中文逐字+jieba HMM=False ≥2 全 CJK、西文 Porter 1980 內建;jieba 換版須重建 concordance;Porter 正規形查詢 value→'valu')。

**版權雙軌(憲章 v1.20)**:哲學原典 work_text 限公版;knowledge_item_text=公版+CC 白名單四值(cc-by/cc-by-sa/cc0/public_domain,DB CHECK);NC/ND/未明停 metadata;現代版權著作僅核心精神經真實文獻 citation→principle→factor_map→#14。

**未實作債(2026-07-03)**:`verify_text_integrity.py`(W2)、`review_flagged_works.py`(151 部 flag 人審)、`refresh_text_understanding.py`、L5(`answer.py`/`profile.py`/coverage report)、W6 term_stats/W7 衍生層/W9 en 句嵌入(拍板 C 子集);康熙 p1 餘 174 部首、十三經餘十一經;chunk junk 塊清理(「_」0.84 污染)須先於跨語驗收+rank@10 驗收本身。注意 `embed_philosophy_chunks.py --smoke` 不限量會跑全量、且跳過建索引(index 只在非 smoke 模式建;補建用 script 內同款 DDL idx_chunk_emb_hnsw)。harvest 常規批:`python scripts/harvest_knowledge.py --batch 300 --rounds 4 --max-minutes 120`。

**v3.0 W1-W9 建置進度(2026-07-04)**:Phase 0 已 W2.5(corpus_class 單一語意閘,三 builder 引 corpus.clean_work_sql)+W2(verify_text_integrity.py 常備稽核,硬不變式全過/C6 諮詢級)。**W8 answer.py 三級誠實分級器已落地**(拍板3):honesty_level——level3 有真兆交 advise、level2 檢索空但隔離館藏(review_flag=true 151部)title 被提及(unverified_attribution_lookup 旁查)→第二固定句、level1→第一固定句;接入 advise 空檢索分支、guard_empty_retrieval 認 HONESTY_CLOSED_SET 二句。Phase 0 續:W6 report_term_coverage.py(三層可解率:zh 定義層 45%/en 6.9%/思想層 0%=term級edge未建;命門2 漸近coverage)。**admin 知識控制台 P1/P2/P3 全建**(計畫=augur_admin_knowledge_console_plan_20260704.md):P1 fileparse.py+acquire_local_files.py(+資料夾遞迴入庫,license DB CHECK 硬擋白名單、access_scope 私有隔離、source_type<>ai_generated);P2 acquire_topic.py(主題→domain映射含中文別名→觸發harvest確認頁,--run放量);P3 serve_admin_console.py(:8500 後台,pbkdf2認證/session HttpOnly/路徑realpath圍欄/subprocess shell=False/審計log,觸發P1/P2、反代:8090對話不繞guard)。**死點①②修**:retrieve_all(work+item 交錯)接入 serve_advisor_openai、entity_type 'document' 入 SEMANTIC_ENTITY_TYPES;clean_item_sql +access_scope(None 嵌入/public 檢索);prompt getattr 相容 Citation/ItemCitation。稽核決3(月營收 gate=公告月同月15日)特徵值變、全面板重建中→待重驗證。

**端到端管線+誠實對話(2026-07-04,commit 591acc2/tag knowhow-e2e-chem-firstrun-r2;憲章 v1.23.0 準則)**:七段一驅=registry→promote→item_text→統計→pgvector→Milvus 單向匯出→guard 對話。既有工具+新缺件 N1-N9(corpus 述詞/embedspec 版本化/vectorindex 介面/ollama adapter/oai_compat 殼/refresh 驅動器)。化學域首跑:item 8,721/item_text 571 句/concordance 12,170/Milvus 兩 collection。**對話棧**:Ollama qwen3:8b + advisor 殼(:8399 OpenAI 相容,唯一編排=advise+guard) + serve_chat_ui.py(:8090 零依賴前端,**非 Open WebUI**——後者在此 WSL crash-loop 於 HF 嵌入模型);systemd user units(~/.config,開機自啟需 `sudo loginctl enable-linger hugo`+Windows Task Scheduler 啟 WSL);啟動器 start_chat.sh。**R2 誠實對話定調**:系統附逐字原文(檢索真兆零幻像)、模型只白話解讀;think:false+temp 0.15+strip_quote_marks(8B 無法可靠照抄名典之根治;guard ① 無可攔但 ②③④ 仍守=#1 不鬆)。GPU=GTX1650 4GB,e5 嵌入 842 句/s,qwen3:8b 對話 ~190s/則。

關聯:[[augur-project-map]](兩機/dump 狀態)、[[augur-three-lens-research]](三鏡頭=投資哲學操作化)。
