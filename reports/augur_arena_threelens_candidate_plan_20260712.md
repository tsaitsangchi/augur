# 擂台新候選計畫:own_threelens_interact(三鏡頭直餵+跨鏡頭交互)

> **性質**:計畫先行(憲章第六部 v1.39.0)。用戶拍板方向(2026-07-12,引述核可):「三鏡頭特徵直餵+跨鏡頭
> 交互項的方向模型,凍結配方後在真未來上,跟 own_stack/timesfm/chronos 同場競技」。本計畫=該候選之
> 完整落地規畫,**待拍板後動工**。

## §0 三十秒:這個候選在賭什麼、憑什麼合法

**假說**:方向軸 v2 判死的一個殘留疑點——DirStackM 個股側只餵 7 個壓縮特徵(4 原始+3 個 `rank_pctile`
綜合分數),三鏡頭(第一性/八二/康波)35 特徵**只透過 rank_pctile 一個瓶頸**進方向軸,跨鏡頭交互
(康波相位×八二集中度、循環×動量)**從未直餵**。本候選把瓶頸拆掉:個股側 7→35 特徵直餵+先驗凍結的
跨鏡頭交互項,市場 context 與 DirStackM 完全同款——**delta 只有特徵寬度**,賭的是「壓縮丟掉了方向訊號」。

**合法性(no-v3 相容)**:不對凍結快照開任何新 gate。候選凍結配方→真未來擂台出預測→**新家族 A3**
預註冊 gate 裁決(先凍後跑)。歷史資料唯作**工程冒煙**(機率產得出、校準器落地),**不以歷史 hit-rate
調參或篩選**——性能裁決權 100% 讓給真未來(否則=偷跑 v3)。

**誠實工程量**:這不是接線。三鏡頭 35 特徵住 `feature_values` = **季頻面板**(36 panels,2007-12→
2026-06);方向軌需**月頻**(direction_stack_feature_monthly 有 113 個月 panel 但只 7 特徵)。
故需新建一條**月頻三鏡頭特徵鏈**(builder+表)——真缺口 = 1 表 + 3 支新 script + 1 adapter + 1 家族預註冊。

## §1 候選規格(凍結內容,=register 時寫入 spec jsonb)

| 項 | 值 |
|---|---|
| model_key | `own_threelens_interact` |
| team / track / gate_eligible | own / H / true |
| 個股特徵 | feature_values 35 特徵全餵(月頻重算)+ 交互項(§2) |
| 市場 context | 與 DirStackM 同款(MktLogit_v2 分量)——不變,隔離 delta |
| 模型 | GBDT 3-seed 平均 + isotonic purged 校準(同 own_daily_rolling 口徑) |
| horizons | 20/40/82(交易日;同 own_stack 三門) |
| refit_policy | per-month rolling;train_data_max_date 留痕 |
| conversion | 校準後機率直出 |

## §2 跨鏡頭交互對(先驗凍結;拍板點②;拍板後不得增刪改)

理據=三鏡頭研究(2026-06-27)之分工:第一性=資訊內容、八二=分布形狀、康波=時間結構——交互=「在循環
哪裡 × 誰在支配 × 流向哪裡」。每 panel 先橫斷面 z-score 再乘積,9 對:

| # | 交互(鏡頭) | 特徵對 |
|---|---|---|
| 1 | 康波×八二 | cycle_position_252d × volume_gini_60d |
| 2 | 康波×八二 | price_to_10yr × top_holders_pct |
| 3 | 康波×第一性 | gross_margin_pctile × momentum_60d |
| 4 | 康波×第一性 | cycle_position_252d × volatility_60d |
| 5 | 康波×第一性 | range_position_120d × momentum_120d |
| 6 | 八二×第一性 | volume_gini_20d × momentum_20d |
| 7 | 八二×第一性 | top_holders_pct × institutional_net_buy_ratio_20d |
| 8 | 八二×第一性 | volume_max_share_20d × turnover_mean_20d |
| 9 | 八二×康波 | inst_cumflow_position_120d × cycle_position_252d |

交互對清單存於凍結 spec jsonb(insert-only trigger 保凍;#29b 資料住 DB)。**誠實註**:GBDT 本身能學
交互,顯式乘積的增量主要在降低樹深需求+讓 35 特徵直餵不被壓縮——若真未來證明無增量,判死留檔即是答案。

## §3 Table Schema(v1.39.0(a))

**新表**(鏡射 direction_stack_feature_monthly;DDL 住 `migrate_threelens_ddl.py`):

```sql
CREATE TABLE IF NOT EXISTS direction_threelens_feature_monthly (
  panel_date date NOT NULL,          -- 月末 as-of(對齊 stack 表 113 panels 窗)
  target_id  text NOT NULL,
  feature    text NOT NULL,          -- 35 原始 + 9 交互(interact__ 前綴)
  value      double precision,
  git_sha    text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (panel_date, target_id, feature));
```

**所讀既有表**:`feature_values`(季頻,僅對帳驗證用)、特徵 generator 之上游 raw 表(同 feature_values
建置口徑,#8 as-of 純淨)、`direction_arena_candidate`(+1 凍結列)、`direction_gate`(+3 門 A3)。
**結果落**:`direction_arena_prediction`(既有,反回填/不可改 trigger 已在)。

## §4 Python 程式規畫(v1.39.0(b))

| 檔 | 職責 |
|---|---|
| `scripts/migrate_threelens_ddl.py`(新) | §3 DDL 冪等+現況唯讀 |
| `scripts/build_threelens_monthly.py`(新) | 以既有特徵 generator 於**月頻** as-of 重算 35 特徵+9 交互→落新表;resume-safe(DB-driven)、`--until` 滾動;**T1 驗收含與 feature_values 同 as-of byte 對帳**(同 generator 同日必同值,防兩套口徑) |
| `scripts/train_direction_threelens.py`(新) | walk-forward 工程冒煙(月頻 purge、3-seed、isotonic;輸出僅供機械驗收:出得了 p_up/校準器 provenance 落地;**一次跑、不迭代調參**) |
| `src/augur/arena/adapters.py`(改) | +`OwnThreelensInteract`(rolling refit,鏡射 OwnStackRolling;讀新表+凍結 spec 交互對) |
| `scripts/register_arena_candidate.py`(跑) | INSERT own_threelens_interact 凍結列(insert-only 合法) |
| `scripts/preregister_direction_gate.py`(改/跑) | +A3 家族 3 門 `dgate_arena_threelens_{20,40,82}`:α=0.05/**3**、min_clusters=36 月頻、MDE/檢定力機械凍入、fail_path 禁蓋棺、no-v3 相容句 |
| `scripts/run_arena_daily_pipeline.py`(驗) | 驗證自動納入新候選;若候選清單有 hardcode 即改 DB 驅動(#29b) |

風險預告:若特徵 generator 發現有季頻排程假設寫死(非以 as-of 參數化),T1 須先參數化(屬「改正確」執行層)。

## §5 統計誠實(先講死,承憲章 v1.44.0 輸出契約)

- **家族 A3**:K=3,Bonferroni α=0.05/3≈0.0167;**跨家族多重性**依 v1.44.0 條款全序列揭露
  (v1 六門+v2 四門判死+A2 六門+A3 三門=**19 門全列**,不得單挑活門講故事)。
- **min_clusters=36 月頻**≈3 年才裁決——與 own_stack 三門同鐘;MDE 誠實定位同 A2(偵測可交易級
  邊際;+1-2pp 微小邊際檢定力≈0,機械凍入 criteria)。
- **先凍後跑**:A3 三門於候選首筆預測落 ledger **前**完成 preregister+hugo TTY approve;
  凍後 spec/交互對/模型碼 code_sha 綁死,改版=新候選新家族。

## §6 分階段・驗收・拍板點

| 階段 | 內容 | 驗收(#7 實測) |
|---|---|---|
| **T0** | 本計畫拍板(①計畫②交互對§2) | — |
| **T1** | DDL+月頻 builder 全量回建 | 113 月 panel×(35+9) 特徵落表;與 feature_values 同 as-of 抽樣 byte 對帳 0 差異 |
| **T2** | trainer 工程冒煙 | OOS p_up 產出+校準器 provenance;一次跑不迭代 |
| **T3** | adapter+register 凍結 | 合成冒煙(SYNTH_*)出手;candidate 列 frozen |
| **T4** | A3 三門預註冊→**hugo TTY 親核**(拍板點③) | criteria sha 可覆算;approve 前零預測 |
| **T5** | 併入每日 pipeline 陪跑 | 首月預測落 ledger;反回填 trigger 實證 |

**時序**:T1-T3 與解凍 GATE/A2 開賽鏈零衝突(純本地零 usage,可平行);T4-T5 依「先凍後跑」在首筆
預測前完成即可,不擋 A2 開賽。

**成本**:全鏈本地(DB+Python),零 Claude usage、零 FinMind 新負載(讀既有 raw)。

## §7 一鍵拍板句

1. 「**候選計畫照 T0(含 §2 交互對凍結)**」→ 我開工 T1-T3;
2. T4 時我產三門 criteria,你貼 TTY approve 三行(屆時給指令)。
