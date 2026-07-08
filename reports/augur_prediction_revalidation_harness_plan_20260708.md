# 持續再驗證 harness — plan-first 計畫(v2,5 鏡對抗審查後重寫)

**日期**:2026-07-08 ｜ **性質**:計畫先行(CLAUDE #20 新子系統)｜ **層次**:部署層 D5 持續再驗證
**修訂**:v1 4 缺口方向對,但**判停邏輯(核心)根本性錯誤**(DSR<95% 當判停會首輪誤殺薄 edge)+ 多項完整性漏洞,經 5 鏡對抗審查(`whvklsrw2` 全 REVISE)重寫。**教訓:薄 edge 的「再驗證」目標語義必先定義清楚,否則把「從未確立」誤當「崩壞」。**

---

## 0. 三十秒 + 目標語義(v2 最重要的更正)

edge 真實但薄:headline 淨 Sharpe ~1.0–1.2、**未過 deflation**(DSR 75.6–89.5% < 95%)、經典下市 survivorship≈0、完整度閘 incumbency −16.5%(全史齊 1.20 vs 當下可算廣宇宙 1.00、兩宇宙並存)。

**harness 監控對象(釘死語義,v1 缺此致命)**:**「薄但存活的 deflated point-estimate 地板**(有效 Sharpe ~0.26–0.48>0、net 勝基準)**不惡化」——不是「等 DSR 某天過 95%」**。故判停**兩軌分離**:

- **軌A 地板監測(絕對門檻 → 只標註、永不判停)**:DSR<95%、deflated 有效 Sharpe、net−bench 超額——記錄「薄 edge 現況/未達統計確立」。**DSR 屬此軌,絕不入判停觸發**(現況本就<95%,入判停=首輪誤殺)。
- **軌B 衰減告警(相對凍結 baseline 顯著劣化 → 判停)**:部署 cell 之 net 從曾勝基準**轉輸**、HAC-t 從曾>2**掉破**、deflated 地板從正**轉負/崩**——才是真 decay、才判停。

## 1. 現況實查(grounded,含 v1 漏列之既有物)

| 已存在 | 狀態 |
|---|---|
| `scripts/revalidate.py`(396 行) | ✅ 完整 harness:重跑 B(IC/HAC-t/pan-hist/shuffle)/C/D(經濟矩陣)、寫 ledger、`--track`/`--skip-existing`/`--dry-run` |
| `revalidation_ledger`(73 列、**僅 1 個 as_of=2026-05-31**) | ✅ 表在;**⚠無時間序列 → 軌B 還無錨** |
| `deflate_headline_verdict.py` | ✅ **已具 PASS/FAIL @ DSR≥95% 裁決 + per-period 正確口徑**(v1 漏列;新 verdict 須複用其邏輯、非重造) |
| `metrics.deflated_sharpe/expected_max_sharpe/sharpe_trial_variance` + `trial_ledger`(16 列) | ✅ 已建 |
| `src/augur/features/release_lag.py` + `src/augur/audit/import_isolation.py` + `tests/test_philosophy_isolation.py` | ✅ **既有 #8 gate + 機械不變式測試骨架**(v1 誤述「#8 無機械測試」;實為「無 release>T 特定斷言」) |

## 2. 真實缺口(4 項,spec 校正)

1. **P1 deflation 未整合**:revalidate.py 只記樂觀年化 net_sharpe、無 DSR。**校正**:DSR 需 per-period 序列(ledger 只存年化純量)→ 非「加一列」,須重跑 run_backtest 取 net_series 算 skew/kurt/per-period,且**抽 `deflate_headline_verdict` 邏輯為共用 helper**(#12,禁平行重寫)。
2. **P2 判停評估未建**:revalidate.py 只寫 ledger、不評估。**校正**:非「加判停」而是「建**兩軌三態**評估器」(見 §0);`deflate_headline_verdict` 的 DSR 裁決屬軌A、已在,新增的是軌B decay + 三態。
3. **P3 排程未接**:手動 `--run`。
4. **P4 #8 release>T 特定斷言測試未建**:既有 #8 骨架不涵此命題。**校正**:是 **build 端** gate 測試(feature_values 零 provenance、predict 端無法斷言)、且**併入 `audit` 領域元件**(非孤支 `verify_release_lag.py`,#12)。

## 3. 設計(補缺口 + 校正,不重造)

| 階段 | 元件 | 檔案 | 驗收 |
|---|---|---|---|
| **P0 兩宇宙 deflated 地板定錨**(新、優先) | 用 `survivorship_economic_verdict` + `deflate_headline_verdict` 對**全史齊 1.20 與廣宇宙 1.00 兩宇宙**各算 deflated 地板,寫入 baseline 錨。**兩者並存(用戶拍板)**:harness 以**部署宇宙(全史齊、predict_asof 實際交易口徑)為操作 baseline**(軌B 比較基準)、**廣宇宙 1.00 為並列誠實地板錨**(揭露 incumbency 不惡化)——非「主追廣宇宙」(部署交易的是全史齊,廣宇宙為誠實對照) | reuse 既有兩支 + baseline 錨列 | 兩宇宙 deflated 地板各有錨、incumbency −16.5% 標註;軌B 基準=部署全史齊 |
| **P1 deflation 整合** | 抽 `deflate_headline_verdict` per-period DSR 為共用 helper(如 `evaluation/deflation.py`);revalidate.py stage_cd 每 cell 走同 helper 算 DSR。**⚠實作前置(實查落差):`_backtest_cell` 現只回 sharpe/calmar/maxdd、丟棄 net_series → 須改為一併回傳 `net_series`+`ppy`** 供 helper 算 skew/kurt/per-period sr。**執行序釘死**:寫 revalidation_ledger → refresh trial_ledger → 讀 N(DISTINCT SOP 鍵)→ 算 DSR → 寫 dsr 列。**N 反身性(實查:已由 trial_ledger UNIQUE 鍵強制)**:同 config 重跑 ON CONFLICT UPDATE、不新增列 → N 不因重跑膨脹(非新工作、澄清即可);僅新 config 合理增 N。「DSR 隨時間變嚴」機制=**T(有效期數)增 → √(T−1) 標準誤縮 → DSR 收斂**,非 N 增 | 改 `scripts/revalidate.py`(`_backtest_cell` 回 net_series)、新 `src/augur/evaluation/deflation.py`(共用)、reuse `metrics.deflated_sharpe` | revalidate 算之 dsr == deflate_headline_verdict 同 as-of 同 cell(走同一 helper) |
| **P2 兩軌三態判停器** | 新 `scripts/revalidate_verdict.py`:**軌A**(絕對→標註未達確立、DSR 在此、永不判停)+ **軌B**(相對凍結 baseline:部署 cell〔Ridge H60 LO、as-of 口徑〕net 顯著轉輸 bench ∨ HAC-t 從>2 掉破 ∨ deflated 地板轉負,**連續 k 輪/滾動窗**、HAC-t=None→不定論不觸發、**同宇宙口徑鎖定**)→ **三態**輸出(部署中-未確立/疑似衰減-人審/確認衰減-停)。閾值住 `judgestop_threshold` DB 表(#29b、循 knowledge_topic_alias 先例);**閾值凍結、調整須人拍板留痕**(消 #29b 可調 vs #15 不調鬆張力) | 新 `scripts/revalidate_verdict.py`、`revalidation_verdict` 表(no-AI 機械判詞+provenance+隔離斷言:禁 import 素養/advisor、禁回讀 prediction_values)、`judgestop_threshold` 表 | 對現況(1 as_of)跑出**軌A 誠實地板標註**(H60 部署中-未確立);軌B 需 ≥k 輪錨、未達前停用(誠實揭露) |
| **P3 排程觸發** | panel-cadence(資料驅動非硬編「季」)增量 build→revalidate --run→revalidate_verdict;一次性排程/背景、**不輪詢不自掛長喚醒鏈**(#28);**判停告警落地管道**(一次性通知,非背景無人看) | 編排 + 告警管道 | 手動觸發一輪端到端(build→reval→verdict→若判停則告警)過 |
| **P4 #8 build 端 gate 測試** | **併入 `audit` 領域**(非孤支):T-1 注入型(re-build 一 panel、斷言財報型特徵不反映 release∈(T,T+Δ])+ T-2 邊界型(直測 `release_lag.financial_released/revenue_released` ±1 日布林)+ 日頻 date≤panel 同日邊界。**先確立各源 release 時點欄可信度**(Dividend.AnnouncementDate / MonthRevenue.create_time〔memory:待實證〕/ 財報法定 lag)再建閘 | `src/augur/audit/release_lag_invariant.py` + `tests/` | 故意注入 release>T → 測試 fail(對抗反例);明說驗 build 純度、predict 端繼承 |

## 3.5 新表 schema(產表附 schema,憲章計畫完整性)

```sql
-- 判停閾值(#29b 資料驅動、循 knowledge_topic_alias 先例:runtime 讀表、admin INSERT 零改碼、seed bootstrap 非 hardcode)
CREATE TABLE judgestop_threshold (
  policy_key    text NOT NULL,          -- net_excess_decay / hac_t_floor / dsr_annotate / verdict_n / consecutive_k
  horizon       int  NOT NULL DEFAULT 0,-- 0=全域;60/120=該 horizon
  track         text NOT NULL,          -- 'A_annotate'(標註、永不判停) | 'B_decay'(衰減判停)
  threshold     double precision NOT NULL,
  frozen        boolean NOT NULL DEFAULT false,  -- 拍板凍結;調整須人留痕(#15 不調鬆)
  source_ref    text NOT NULL,          -- 閾值出處(STAGE D 報告/deployment plan)
  note          text,
  PRIMARY KEY (policy_key, horizon),
  CONSTRAINT chk_track CHECK (track IN ('A_annotate','B_decay'))
);

-- 再驗證裁決(判停可稽核可回溯;no-AI:判詞由 ledger 機械算、非 AI 生成;provenance 全記)
CREATE TABLE revalidation_verdict (
  verdict_at        timestamptz NOT NULL DEFAULT now(),
  as_of_date        date NOT NULL,
  cell              text NOT NULL,       -- 部署 cell 識別(如 'ridge_H60_LO_asof')
  track             text NOT NULL,       -- 'A_annotate' | 'B_decay'
  state             text NOT NULL,       -- 三態:deploying_unestablished / suspected_decay_review / confirmed_decay_stop
  triggered_cond    text,                -- 觸發條件(軌B;軌A 為 NULL)
  metric_snapshot   jsonb NOT NULL,      -- {net_sharpe,hac_t,dsr,bench_sharpe,n} @ 此 as_of(機械快照、可 trace ledger)
  baseline_ref      text,                -- 軌B 比較之凍結 baseline 錨
  threshold_source  text,               -- judgestop_threshold 之 policy_key(閾值來源)
  universe          text NOT NULL DEFAULT 'asof_incumbent',  -- 部署全史齊;廣宇宙對照另列
  note              text,
  PRIMARY KEY (as_of_date, cell, track),
  CONSTRAINT chk_state CHECK (state IN ('deploying_unestablished','suspected_decay_review','confirmed_decay_stop')),
  CONSTRAINT chk_track2 CHECK (track IN ('A_annotate','B_decay'))
);
-- 隔離斷言(非 schema、屬碼):revalidate_verdict.py 禁 import 素養/advisor 層、禁回讀 prediction_values(部署稽核層、非預測管線)。
-- no-AI:verdict/state 由 ledger 機械規則算(閾值比對),非 AI 生成判詞——與 knowledge_derivation_method 精神一致。
```

## 4. 命門 / 不做什麼(明文,含 v2 校正)

1. **不重造** revalidate.py 的 B/C/D 重跑、deflate_headline_verdict 的 DSR 裁決、既有 #8 骨架(#12 複用)。
2. **DSR 絕不入判停觸發**(軌A 標註用):DSR<95% 是薄 edge 已知常態、非 decay;入判停=首輪誤殺(5 鏡共識)。
3. **判停 scoped 部署 cell + 同宇宙口徑 + 連續 k 輪**:不對整 B/C/D 矩陣 OR(gbdt/H120 現就破 bench)、不單點觸發(小樣本雜訊)、不跨宇宙比(incumbency 漂移誤當 decay)。
4. **N 反身性**:重跑同 config 不增 trial N(**已由 trial_ledger UNIQUE 鍵 + ON CONFLICT UPDATE 強制、實查確認、非新工作**);N 口徑維持 SOP G7(DISTINCT 鍵不含 as_of);「變嚴」靠 T 增非 N 增。
5. **口徑不放寬**:embargo(h+62td)/asof/cost 0.585%/non-overlap 同 SSOT。
6. **判停閾值凍結**:住 DB(#29b)但一旦拍板即凍結、調整須人留痕(不得為保 edge 調鬆,#15)。
7. **隔離**:verdict 禁 import 素養/advisor、禁回讀 prediction_values(部署稽核層非預測管線)。
8. **不自動下單/判停後人決策**(靈魂):附判停 runbook(判停→看哪些證據→退場/重估/擴宇宙 決策樹)。

## 5. 分階段 + 誠實時間表

- **P0(兩宇宙地板定錨)→ P1(deflation 整合)→ P2(兩軌三態判停)**:核心價值序。
- **P4(#8 build 閘)**:獨立可並行。**P3(排程)**:收尾。
- **⚠誠實時間表(critic)**:H60 ~4.7 非重疊期/年、H120 ~2.3 期/年 → **H120 定論門檻 n≥20 現 n=8、需 ~5 年**(且 deflation 後小樣本更難確立)。`--track` 應加「預估年」欄、明說「H120 近期定論或此週期不可達、改以 pan-historical 全史為主證」。軌B decay 偵測亦需累積 ≥k 輪錨才啟用。**現況(1 as_of)只能跑軌A 誠實標註,不假裝能判 decay**。

---

## 附註 — 5 鏡對抗審查(`whvklsrw2`)關鍵修正

| 鏡抓到 | v1 錯 | v2 修 |
|---|---|---|
| 判停 DSR<95% 誤殺(全 5 鏡) | DSR 入判停 OR 條件 | 兩軌分離、DSR 只入軌A 標註永不判停 |
| 判停二元/整矩陣/單點 | PASS/判停二元、任一 cell 觸發 | 三態、scoped 部署 cell、連續 k 輪、同宇宙鎖 |
| 無歷史序列(僅 1 as_of) | 驗收「對 73 列跑裁決」含 decay | 現況只軌A;軌B 需 ≥k 輪錨、誠實停用 |
| N 反身性(trial_ledger UPDATE) | 「N 隨時間增→變嚴」前提錯 | 去重同 config;變嚴靠 T 增非 N 增 |
| P1 per-period 落差 | 「加一列 dsr」當免費 | 抽共用 helper、重跑取序列、釘執行序 |
| P4 build vs predict 端 | 曖昧(易實作成掃 feature_values) | 明定 build 端 gate 測試、併 audit 領域 |
| 廣宇宙 1.00 才是真地板 | 主追全史齊 1.20 | P0 兩宇宙定錨、主追廣宇宙 1.00 |
| 時間表不誠實 | 只印「待累積」 | 明列 H120 ~5 年、可能不可達 |

*本計劃 plan-first(CLAUDE #20),實作前用戶拍板。真實 gap 小但**判停語義是命門**,v2 已據 5 鏡釘死兩軌三態。*
