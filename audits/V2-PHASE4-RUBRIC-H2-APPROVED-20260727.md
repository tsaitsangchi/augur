# V2-CTRL-go＋GATE-raise＋V2-RUBRIC-go＋H2 處置方向 拍板登錄（2026-07-27）

> **性質**：拍板登錄（比照 `V2-ADOPTED-SUNSET-20260726.md` 先例）。
> **hugo 對話拍板原文（逐字，2026-07-27 於 PC002-S1800 session）**：
>
> 「開 Phase 4——修 TWEVO 的尺
> A 軸內容敏感判準；開了才能量測 RAW→LAI 唯一活邊
> 其晉升依據已作廢（舊尺 0.492 低於零知識地板）知識需再參考計畫本地AI再自我學習進化」
>
> **簽名誠實註記**（§8.1／never-type-human-signature 紀律）：本檔由 claude 依 hugo 對話拍板繕寫登錄；
> 決策者＝hugo、繕寫者＝claude，二者分立如實記載，不冒充親簽欄位。

## 一、`V2-CTRL-go`＋`GATE-raise`（Phase 4 開；對應 v2 §3.4 M-1／§6 Phase 4／人閘 H4）

- 範圍＝M-1 四項：置換臂＋隨機特徵臂（走完全相同 local-gates 路徑、≥200 draws、結果寫 `evolution_evidence_run`）；事前預註冊決策規則；符號一致性；`volume_gini_60d` 處置獨立人裁（H5，見 §四）。
- **GATE-raise 預註冊決策規則（逐字凍結，v2 §3.4 M-1 原文）**：「經驗偽陽率 > 10% ⇒ 將 `min_abs_hac_t` 調至經驗 95 分位」。升嚴唯一方向；放寬一律不許（GATE-keep 不變）。
- 符號一致性：`sign(mean_ic)` 須與 `principle_factor_map.direction` 一致，不一致 → verdict `FAIL_SIGN`（**非 SKIP**），並禁 I8 回填 `validated`；`gate_json` 記 `expected_direction`／`observed_sign`。
- 驗收＝v2 §6 Phase 4 原文：`evolution_evidence_run` 有 axis='tw' 之 shuffled／mismatched 列；重跑既有閘評，`volume_gini_60d` 判 `FAIL_SIGN`。

## 二、`V2-RUBRIC-go`（H6；A 軸內容敏感子判準）

- 前置「Phase 1 結果」已成立（behavior F@L1=0.933 判準 A PASS；本機 2026-07-27 已逐位元複現凍結集＋四離線臂）。
- **已知後果（誠實）**：改 `behavior_rubric.py` 即換 `eval_code_hash`（`_code_hash()` 涵蓋判準模組全文＋產答路徑）→ 既有 run 退出可比範圍、開新一代尺。
- **時序紀律**：本機 LLM 臂（舊尺 `f3075238eb55`）與 H2 之 pack 重評**完成後**才動 `behavior_rubric.py`——舊尺收尾與新尺開版不交錯。
- 驗收目標（機械、離線數秒可驗）：新尺下 ceiling A 軸仍 1.000；**shuffled 之 A@L3/L4 由 0.967 崩落**（內容敏感生效＝能區分「行為類別對但內容錯」）；floor／mismatched 仍 0。

## 三、H2：現役 serving `pp_3ab2efebb04e` 處置方向

- hugo 指示方向＝**依 LAIEVO 自我學習進化迴圈處置**：以新量測體系重評，證據決定去留，非逕行 retire。
- 機械第一步：跑 `pack:pp_3ab2efebb04e` 臂於凍結集 `4183475c5089`（**舊尺**，與 grammar／behavior／floor 同尺可比）→ 證據呈人裁（keep serving／retire）。
- 晉升人閘不變（P5.W2）：任何 serving 變更須 `promoted_by` 人簽。

## 四、明列未決（本檔不代決）

| 項 | 狀態 |
|---|---|
| H5：`volume_gini_60d` 回溯處置（demote／標註／保留註記） | 待 Phase 4 對照臂產出 `FAIL_SIGN` 證據後人裁 |
| H10：`principle_domain_map` vs `field_lens_map` 分層；域概念之定位 | 討論中（hugo 2026-07-27 提問「知識可否無域」——分析見對話；任何判準變更另案） |
| **兩機 arena 歸屬** | **已於同日稍後拍板，見 §六** |

## 七、增補（同日再後）：LAIEVO 教材母體跨域化（`V2-RUBRIC-go` 範圍調整）

> **hugo 對話拍板原文（逐字）**：「此專案所有自進化迭代計畫know how不需要分域，而是交互相關進行學習自我進化提高本地AI能力」

- **裁定**：本地 AI 能力學習迴路（eval 題庫母體／gold 收割／pack 教材／自我求知選材）**不以域過濾**——F/P/A 量的是跨域通用行為（事實逐字／指名來源／拒答消歧義），域過濾係取材便宜行事而非原理。
- **落地＝併入 RUBRIC v2 同一次換尺（單次破尺）**：新一代凍結集之母體由 `DOMAINS=("quant_finance","software_engineering")` 兩域擴為**全知識層跨域抽樣**（philosophy／全 domain knowledge_item／ttai owned_local 私有 know-how／raw catalog 語意）；L4 消歧義因跨域同名多實體反而**更豐富**（如「緩衝層」之 ERP vs 市場語意）。夜間收割與 `evolve_self_seek` 選材同步撤域限。
- **不變式重申（跨域學習 ≠ 拆牆）**：①量化隔離不動——學習教材跨域 ≠ 任何內容入 `feature_values`／prodset（I2/I8/#8 原樣）；②私有邊界不動——ttai 教材僅本地學習（gold/eval 住 DB 不入 git、pack 為本地檔）、qdrant/git 零外流；③0/1 機械判準不鬆——跨域題仍須 live DB 可查核（L1 逐字/L3 NOT EXISTS），擴域不得以「跨域難驗」為由降判準；④凍結集 `4183475c5089` 原樣封存為可比史料。
- 與 §四 H10 分層裁定相容：domain 欄保留為 provenance／檢索注記（治理把手），自此**不再是學習迴路的牆**。

## 六、增補（同日稍後）：兩機歸屬拍板＝乙案（本機 PC002-S1800 當家）

> **hugo 對話拍板原文（逐字）**：「乙：本機當家。因為DESKTOP 當家只有在週六、日才會開」

- **歸屬**：進化程式（三軸）＋ arena 之正典帳本機＝**PC002-S1800**（週間常開、AC 永不睡眠已實測）；`DESKTOP-8MQPFS8`＝週末 GPU 實驗機。
- **決定性理由**：arena cron＝週一至五 22:30，DESKTOP 週間不開機——物理上不可能當家。
- **即刻生效**：本機 arena 三條 cron **保留**（今晚 22:30 起本機即正典擂台鐘；FZ 有界豁免之 sync 由本機執行、單機單配額）。
- **週末待辦（DESKTOP 下次開機時，hugo 執行）**：
  1. 停用 DESKTOP 之 arena／evolution cron 與 timer（防雙寫）；
  2. 將 07-26 08:49 dump 之後的進化狀態增量以**私有通道**（硬邊界：不入 git）搬至本機：`local_model_gold_sample` sample_id≥281（824 列）、`raw_evolution_iteration_ledger`（3 輪）、`evolution_hypothesis_hint`（含 H3 approved 列——人閘決策不可丟）、`raw_table_coverage_snapshot`、`local_model_eval_run` 之 LLM 臂列；
  3. 此後 DESKTOP 一律消費本機 dump，不再自行 sync／開輪。

## 五、拍板時點本機狀態快照（誠實基線）

- 凍結集 `4183475c5089`＋四離線臂已於本機逐位元複現（PC002-S1800，獨立於 DESKTOP-8MQPFS8）；LLM 臂（grammar／behavior）排隊中（等 project-memory 索引重建釋放 Ollama 單槽）。
- 本機 `evolution_kill_switch` 缺 `scope` 欄（無 migration 承載，Phase 2.4 之 repo 級缺口）——修復屬執行層待辦。
- V2-SUNSET 條件 (c) 之「獨立重跑複現」半條：本機複現行為即該證據之產生過程，LLM 臂完成後閉合與否以帳本為準。
