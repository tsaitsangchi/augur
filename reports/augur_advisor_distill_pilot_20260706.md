# advisor 蒸餾 Tier-2 資料合成 — S1-S5 pilot 收尾報告

**日期**:2026-07-06→07 ｜ **性質**:pilot(274 題)、未 commit gold(本地 DB/jsonl)、生產 guard 一字未動
**決策脈絡**:硬體未到位(本機無 GPU)→ S6 訓練延後;用戶拍板「跑 S1-S5 資料合成」、S4 teacher=workflow Claude agents、pilot 過關即 bank(不放量 3k、省 usage #28)
**守**:#1(界線-B:gold 事實只溯 context)· #15(誠實 decline > 流暢唬爛)· #28(usage 經濟)· 憲章 guard 閉集(複用零鬆)

## 一、pilot 成果
- **274 題 pilot(batch_tag=pilot2)** → S2 生題 / S3 真檢索 context / S4 teacher gold / S5 硬校驗。
- **171 條乾淨 SFT 樣本**(`data/distill/sft_pilot2.jsonl`,本地 gitignore):**drop rate 37.6% < 40% GATE**,pilot **過關**。
- 通過分佈:ANSWER 23/76、DECLINE 133/182、REFUSE 15/16。

## 二、核心發現(pilot 的價值:小成本抓到管線問題)
1. **teacher 嚴守界線-B、拒張冠李戴**:S4 teacher agents 把 ~21 題「檢索到錯書」的 ANSWER **誠實改判 DECLINE**(如「六韜」撈到莊子、「論語核心思想」撈到論衡、「三十六計」撈到王陽明)——**拒絕憑世界知識捏造 named book 的內容**,標籤 ANSWER 76 → 實際行為 55。這是要的誠實。
2. **檢索召回對古籍主題很弱**(同 TTAI e5-small 誠實崩壞):「XX核心思想/道理」這類抽象問法對真有嵌入的經典**召回到錯書**(論衡冒充論語)。→ named-book 問法需檢索改善才能成 ANSWER 樣本。
3. **S4↔S5↔guard 曾對不齊(已修)**:首輪 S5 **100% drop**——非 gold 爛,而是 (a) `grounding_ok` 用文言 citation 算白話 gold 覆蓋(墨子 gold cov 0.21 其實 grounded)(b) 自然 decline ≠ 固定句閉集 (c) guard_attribution 誤殺點書名的誠實 decline。

## 三、S5 修法(執行層、**生產 guard guard_knowledge/attribution/empty_retrieval 一字未動**)
- `grounding_ok`:floor 0.60→**0.30**,新增 **verbatim-substring 路徑**(gold 含 ≥8 字逐字片段 ∈ citation 即 grounded,相容白話轉述夾真片段);decline/refuse 依 expected/閉集**豁免 grounding**(誠實由 guard 保證非 grounding)。
- **自測 5 案全對**:ANSWER+逐字片段✓、DECLINE 固定句✓、REFUSE✓、**編造數字 IC 0.9987→FAIL✓(guard_knowledge)**、**白話無據外插→FAIL✓(grounding)**——**防偽兩路仍在、無為過放水**。

## 四、放量前的 teacher-prompt 改進(留給未來 3k 放量、非 pilot 阻擋)
使 gold 對齊生產 guard(把 171 → ~230+ 且更 production-conformant):
- **DECLINE**:出固定句「知識庫中無此內容」(不點被問書名,避 guard_attribution;空檢索題須逐字等於閉集句)。
- **ANSWER**:夾 ≥1 短逐字 citation 片段(過 guard ≥8字∈citations 且拉高 grounding verbatim 路徑)+ 白話轉述。
- **label 覆寫**:以 S3/teacher 真 grounding 為準覆寫樂觀 ANSWER 標籤(named book 不在 context → DECLINE)。

## 五、決策與限制
- **bank 171、deferred 放量(#28)**:pilot 已達目的(管線端到端證通 + 171 乾淨樣本 + 修法驗證可行);S6 訓練需 GPU(6144-core/128GB 未到位),teacher-prompt 改進 + 3k 放量待硬體/有空時一次到位。
- **界線 A/B/C 全程守**:gold 住 advisor 側 advisor_distill_* 表、不落 knowledge_*/philosophy_*/feature_values、不成 citation、不進預測管線(import_isolation 稽核 0 違規、負向測試證抓得到)。
- **限制**:171 樣本僅 pilot 規模(訓練需 3k+);古籍檢索召回弱使 named-book ANSWER 稀少(需檢索改善);teacher-prompt 未對齊生產 guard(下輪修)。
