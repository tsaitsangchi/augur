# INTEG-F3：ttai 工程模式選擇性移植評估（embed_cache 接入）

> **性質**：[I] 評估報告（整合計畫 P-F 之 F3；「#3 最小邊界，不為移而移」）。F1（16 檔入庫）／F2（142,040 對帳，未解釋 0）已完，本檔收 F 邊。

## 一、標的實貌（實讀 ttai `scripts/embed_cache.py`）

SQLite 後端之 text→vector 快取：key=md5(text)、value=float32 blob（1024×4B）、`get_many/set_many` 批次、WAL。**它解的問題**：ttai 的嵌入唯一存放在 Qdrant，重灌/重嵌流程從文本重算全部向量——1.5GB pickle 全載 RAM 會 OOM，故落磁碟快取（實測 773MB 規模）。

## 二、augur 側對照（實查）

| ttai 的洞 | augur 現況 |
|---|---|
| 嵌入只住 Qdrant，重灌=重算 | **嵌入住 pgvector＝持久一級存放**；Qdrant serving 由 `export_qdrant_index` 從 PG 匯出（**不重算**，INTEG-E 已驗 78,419 對齊） |
| 重跑無增量 | `embed_knowledge` 增量游標＋NOT EXISTS，重跑零重複 |
| OOM（pickle 全載） | 不適用（PG 批次讀寫） |

**但 ttai 經驗點出 augur 一個真數字**：`knowledge_sentence` 1,786,559 句中相異文本僅 1,399,205——**重複率 21.7%（387,354 次重複嵌入計算）**。重複榜首全是西文縮寫誤切句（`Cleo.`×1,632、`Hor.`×1,604、`Mr.`×1,295＝build_sentences 已知侷限）。平時增量無感；**SOP-A 換模全量重嵌時**（1.72M 句、CPU e5 估十數小時），21.7% 是白算的。

## 三、裁定

**① `embed_cache.py` 檔案級快取：不移植。** 理由：(a) augur 嵌入已有持久一級存放，快取檔＝**第二住所**（#12）；(b) 位於 append-only 誠實閘之外的旁路存放，與「嵌入數＋排除數＝來源數」機器等式的稽核面相牴；(c) 它解的 OOM 場景在 augur 不存在。

**② 採其精神不採其形：SOP-A 重嵌路徑加「批內 DISTINCT 去重」。** 換模重嵌時 `embed_knowledge` 以 `GROUP BY md5(sentence)` 取相異文本、一次計算、fan-out 回多 sent_id——省 21.7% 計算、**零新存放、零新檔**，邏輯住 writer（#12）。**現在不動碼**（#3：SOP-A 未進行中，預改無驗證載體）；登記為 SOP-A checklist 既定項，屆時實作隨換模驗證。

**③ ERP→Qdrant 通用匯出設計：已被實踐，驗證完畢。** `export_qdrant_index` 即該設計之 augur 版；INTEG-E 已驗 CLEAN diff=0、shadow eval mean_overlap 0.9700。不重造。

**④ 其餘（Oracle 連線池、SSH 檢查、4gl 掃描）：登記參考庫、不移植**（augur 無 Oracle/4gl 面；SSH 檢查與 `pull_desktop_evolution_delta.sh` 已有等價物）。

## 四、附帶發現（非 F3 範圍，登記不擴權）

21.7% 重複率的**組成**值得一提：大宗是 `build_sentences` 西文縮寫誤切的碎句（已知侷限、v1 誠實記載）。這些碎句本身嵌入價值低——若未來清理，**正解是改切句 writer 再重建**（#12），不是快取遮掩。列為知識層待議項，不在本檔動。

**F 邊至此三塊全收**：F1 ✓（16 檔）、F2 ✓（未解釋 0）、F3 ✓（本檔）。殘餘=advisor 實答驗收（F1/G1 共用，待 Ollama 車道）。
