# 方向 Live 擂台計畫書(對抗審查後定稿・待拍板)

> **性質**:計畫先行文件(憲章第六部 v1.39.0)。初稿經 3 視角對抗審查(22 項發現、6 blocker)**全數採納重寫**;
> 發現表 §8。**審查改變了本計畫的承諾**(§0.1 粗體)——請先讀 §0 再拍板。

---

## §0 三十秒・誠實預期・雙留痕

### 0.1 三十秒(含審查後的承諾修正)

真未來是方向模型唯一乾淨的考場(市場基礎模型在凍結回測上有 pretrained-on-the-future 洩漏)。擂台=
多模型凍結參賽 → 每日/每月對真未來出方向機率 → 防篡改帳本 → 樣本達標自動評估。**但對抗審查親算檢定力
後,本計畫的可交付承諾必須改寫**:以歷史觀測的邊際量級(D 軌 +1.4pp),「確認」它需要 **12-29 年**資料
——**擂台不能在人類時間尺度上確認微小邊際**。擂台誠實能交付的是三件事:
1. **證偽「可交易級邊際」**:gate 以預先揭露的 MDE(最小可偵測邊際,如 ≥5pp)設計——數年內可誠實回答
   「有沒有『有用的』方向邊際」;fail=「在檢定力 X% 下未偵測到 ≥Y pp 邊際」,**禁用「終結爭論/蓋棺」措辭**;
2. **review 級 live 計分板**(觀察、非裁決、永標非交易訊號);
3. **新資料累積**——主要受益者是活著的相對軌(live 再驗證/軌B),擂台是搭便車。

### 0.2 AI 誠實留痕

1. **檢定力數字(審查親算,§0.4 溯源)**:D 軌日 panel excess sd=0.261、lag-1 自相關 0.695→LRV 膨脹
   3.37×,250 個已結算日 cluster 的有效 n≈74;α=0.05/K 下 80% 檢定力需邊際 ≥10pp 級。H 軌 36 月頻 panel
   有效 n≈17。**gate 對 +1~2pp 級邊際檢定力≈0——若真邊際只有那麼小,fail 是設計註定,計畫書如實承認**。
2. **方向軸可能三度證偽**(對可交易級 MDE 而言)——敗退路徑照樣先寫死(§4)。
3. **硬體邊界**:GTX 1650 4GB VRAM——市場模型限 small 級推論(`timesfm-2.5-200m`;2.0 版只有 500m、
   權重 >4GB 大概率塞不下,審查已糾正初稿型號名);塞不下=誠實除名。
4. **兩個現實硬前置(審查實測發現)**:①FinMind token **已過期降 Free tier**(/user_info 實測
   level=Free、sponsor 到期 2026-06-24;單股單日 fetch PriceAdj 已 400 拒)——**續訂=A1 硬前置、機械驗證**;
   ②PriceAdj 增量拼接損傷已有實錘(15 檔於 06-16 出現調整基準不一致)——結算標籤須走基準一致路徑(§5)。

用戶指示(2026-07-11):探索市場模型/自建模型解方向問題;成立條件=預註冊可證偽、真未來考場、敗退寫死。

### 0.3 拍板點總表

| # | 拍板 | 性質 |
|---|---|---|
| A-1 | ✅ **已核(hugo 2026-07-12,聊天指令「擂台計畫 A-1 核可(含三小裁定照計畫)」)**:新閉集字彙+另表+TAIEX 內部分量三裁定照計畫生效 | 已結 |
| A-2 | ✅ **解凍已拍(hugo 2026-07-12,牆前 §1 建議式:as-of'=滾動)**;修憲已執行(原則精華 v1.9.0/憲章 v1.43.0);**殘餘前置=FinMind 續訂+E 債裁定**(A1 硬前置) | 已拍、待前置 |
| A-3 | 候選清單定版(§2.1 枚舉表;依據限合成冒煙+VRAM+授權,**禁用凍結資料表現**) | A0 完成時 |
| A-4 | ~~預註冊~~ → **evaluate 扣扳機前之最終確認**(gate 於 A2 已預註冊凍結;evaluate 由樣本門檻自動觸發) | 未來 |
| A-5 | (預設不觸)freeze_manifest P4-1 | 唯實證缺口 |

### 0.4 實查來源(#9/#10)

檢定力親算=審查輪 attack:統計(daily_direction_oos_sample/direction_oos_sample LRV 口徑重算);FinMind
Free tier=/user_info+單股單日 fetch 實測;PriceAdj 15 檔拼接損傷=core_universe_asof×adj/raw factor SQL;
raw 表現況 max(date)(多數至 2026-06-17/18,實際缺口≈3.3 週且逐表異質)=逐表實查;GTX 1650 4GB+
timesfm/chronos 未裝=nvidia-smi/pip list;解凍 GATE U1-U6 已凍結=DB prediction_unfreeze_gate 實查。

## §1 治權前置:兩道門+一個時序裁定

**門一(資料層)=解凍 GATE** `unfreeze_06dcb178267d`(U1-U6 已由 hugo 2026-07-11 12:08 親簽凍結,不需再拍):
①**A-2 修憲(完整清單,#19 一處改全鏈對齊)**:原則精華 L74/L76/L77(FREEZE 子條明文解除→轉 **live 增量
維運**模式+新 as-of';不是只改日期——保留「不追新資料/不為此掛排程」語意則擂台每日 sync+cron 全違法)
+憲章 L132(三不動②)/L200+CLAUDE.md L26 同步;commit 時間>gate approved_at(G1(b) 機械檢核)。
②增量 sync(**硬前置:FinMind sponsor 續訂,/user_info level 機械驗證**;現況盤點:多數 raw 表已有至
06-17/18 之越線資料——處置與 06-01 後 PriceAdj 段重抓列入 A1;分段 resume-safe #24/#25;FRED 走獨立
sync_fred)→ build panels。③`--evaluate --asof <as-of'>` G1-G5 原子裁決。

**門二(輸出層)=arena direction_gate**——**時序裁定(A-2 併裁;審查 blocker)**:憲章 v1.42 要求「判準
先寫死才產生」,v2 fail_path 凍結句要求「新資料累積」後才另立 gate。**本計畫採審查建議解法:解凍後、
首輪對局前(A2)即預註冊全部 arena gate(criteria 含 §4 判準/MDE/樣本門檻/K 枚舉,status=approved 凍結),
evaluate 唯樣本門檻自動觸發後執行**——先凍後跑滿足 v1.42;hugo 於 gate note 簽核「prereg-now-evaluate-later
係對真未來資料之新實驗、不構成對凍結資料重試、不違 no-v3 本旨」以解字面張力。

**FREEZE 內(現在)可做**:本計畫拍板、DDL+adapters 骨架、**合成序列冒煙**(§2.2;不碰凍結真實價格、
不產生任何真實股票之 p_up——機械 grep 驗收);**不可做**:新資料 sync、live 對局、對凍結資料的任何
dry-run(=又一次觀看,踩 no-v3 本旨)。

## §2 擂台設計

### 2.1 候選枚舉表(A-3 定版;**每 (model_key×track×horizon) 一門**,K=立門列總數)

| model_key | 隊 | track×horizon | 立門? | 說明 |
|---|---|---|---|---|
| `own_daily_rolling` | 自家 | D×5 | ✓ | **凍結配方+滾動 refit** 類:凍 spec+code_sha+訓練窗政策+seed,weights_hash=null,ledger 逐列記 `train_data_max_date`(§2.2;審查 blocker 修正——自家模型無單一 artifact 可 hash) |
| `own_stack_rolling` | 自家 | H×20/40/82 | ✓×3 | 同上(DirStackM 配方+MktLogit_v2 分量) |
| `own_v2_frozen` | 自家 | D×5 | **✗ 對照列** | v2 凍結配方=已兩敗之同 spec 假說,**不佔 K、不立門**(防殭屍稀釋 α);計分板誠實對照 |
| `timesfm_25_200m` | 市場 | D×5(點預測→機率轉換) | ✓ | 本地推論;provenance=HF repo+revision+sha256+license 白名單;**離線單測必過**(predict 零網路);`conversion_selection_log`(試過的全部轉換變體+選擇準則)隨 spec 凍結;校準層唯得 fit 於開賽後 burn-in 段(該段不入結算窗) |
| `chronos_bolt_small` | 市場 | D×5 | ✓ | 同上 |
| `majority`/`momentum_20`/`mc_bootstrap` | 基線 | D、H 各列 | **✗ 不立門** | 依構造不可過關(majority excess≡0),立門=純稀釋 α;僅為計分板地板與 gate 內比較基準;參數(20d/52w)=慣例值、隨 spec 凍結 |

K(草案)=1(D own)+3(H own)+2(D 市場)=**6 門**;A2 預註冊時以實際枚舉凍結。中途加入者**不進本家族**、
累至下一輪新 gate(新家族新 K),計分板標「非本 gate 家族」。

### 2.2 凍結協定(防重訓到贏;審查修正版)

- candidate insert-only(trigger:唯 status+retire_note 可單次寫);換版/換轉換口徑=新候選新列且**歷代
  版本全數計入 K**(封 iterate-until-win 通道);
- 滾動 refit 類:refit 政策(頻率/窗)凍入 spec,逐列 `train_data_max_date` 留痕——滾動 refit 依凍結政策
  執行**不算**換版;
- **表現型判停(futility)只停止「出新預測」,其既有 ledger 仍全數入 gate**(審查 blocker:除名不得把
  資料丟出家族=optional stopping);除名唯限 operational 事由(缺席/OOM/依賴失效);
- A0 冒煙一律合成序列;真實資料推論唯 A2 後。

### 2.3 對局規則

- D 軌每交易日收盤後、H 軌每月最後交易日,cron 產出;產出僅落 ledger,不進 payload/UI;
- **反回填機械鎖(審查 major)**:BEFORE INSERT trigger 強制 `pred_date ≥ (created_at AT TIME ZONE
  'Asia/Taipei')::date − 1`(容當日盤後)——「時戳貼緊出手日」,堵 horizon 內補插偷看;斷檔=無列,
  同一 trigger 拒逾期插入;
- `label_due_est` 僅供排程提示(未來交易日曆不可知);**實際結算日=settle 腳本以已實現日曆數
  pred_date 後第 h 個交易日動態判定**;
- 停牌/下市(審查 major):label 日起 N 日無成交→`settle_mode='last_trade'` 以最後成交價結算,或標
  `unsettleable` 入分母統計與缺席率並列——**標的消失的誠實**,防 live 倖存者偏差。

### 2.4 計分與判停(futility,非 decay;新閉集=A-1 拍板項)

- scoreboard 唯讀,月報固定含字串集「review 級・觀察中・非裁決・非交易訊號」,由 `--check-report`
  機械斷言(審查 minor:驗收可執行化);
- **futility 判準(取代誤植的 decay 語意——revalidate_verdict 係為「曾確立」模型設計)**:累積已結算
  cluster≥X 且 excess 單邊 95% 信賴上界<0 → suspected;連續 2 輪 → confirmed(=停出新預測、ledger 留家族);
  X 與 α 隨 spec 凍結;
- verdict 三態 `observing/suspected_futility/confirmed_stop_entries` =**新閉集**(A-1 拍板);
- 閾值住 **arena 自己的 `direction_arena_policy` 表**(不動 judgestop_threshold 的 CHECK;審查 major)。

## §3 Ledger Schema(v1.39.0 (a);住 `migrate_direction_arena_ddl.py`;唯一既有表變更=無)

```sql
CREATE TABLE IF NOT EXISTS direction_arena_candidate (
  model_key text PRIMARY KEY,
  team text NOT NULL CHECK (team IN ('own','market','baseline')),
  track text NOT NULL CHECK (track IN ('D','H')),          -- 跨軌基線=每軌一列(枚舉表已反映)
  gate_eligible boolean NOT NULL,                          -- 立門與否(§2.1;凍結)
  spec jsonb NOT NULL,        -- 配方/轉換口徑/conversion_selection_log/refit 政策/provenance(repo+revision+license)
  code_sha text NOT NULL, weights_hash text,               -- 滾動 refit 類=null
  registry_model_id text REFERENCES model_registry(model_id),   -- 自家隊溯源;市場/基線 NULL
  frozen_at timestamptz NOT NULL DEFAULT now(),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','stopped','retired')),
  retire_note text);
-- trigger:除 status/retire_note(單次)外 UPDATE 一律 RAISE

CREATE TABLE IF NOT EXISTS direction_arena_prediction (
  model_key text NOT NULL REFERENCES direction_arena_candidate(model_key),
  target_id text NOT NULL,            -- 個股;'TAIEX'=內部分量列(永不申請展示,A-1)
  pred_date date NOT NULL, horizon_td int NOT NULL,
  p_up double precision NOT NULL CHECK (p_up BETWEEN 0 AND 1),
  train_data_max_date date,           -- 滾動 refit 留痕
  created_at timestamptz NOT NULL DEFAULT now(),
  label_due_est date,                 -- 排程提示;實際結算日 settle 動態判定
  y_up smallint CHECK (y_up IN (0,1)), realized_ret double precision,
  settle_mode text CHECK (settle_mode IN ('normal','last_trade','unsettleable')),
  settled_at timestamptz, git_sha text NOT NULL,
  PRIMARY KEY (model_key, target_id, pred_date, horizon_td));
-- trigger①(反回填):INSERT 斷言 pred_date ≥ created_at 台北日 −1
-- trigger②(不可篡改):p_up/pred_date/created_at/train_data_max_date 禁改;結算欄僅 NULL→值一次

CREATE TABLE IF NOT EXISTS direction_arena_policy (        -- 判停閾值(不動 judgestop_threshold)
  policy_key text PRIMARY KEY, threshold double precision NOT NULL,
  frozen boolean NOT NULL DEFAULT true, source_ref text NOT NULL);

CREATE TABLE IF NOT EXISTS direction_arena_verdict (
  as_of_date date NOT NULL, model_key text NOT NULL,
  state text NOT NULL CHECK (state IN ('observing','suspected_futility','confirmed_stop_entries')),
  metric_snapshot jsonb NOT NULL, threshold_source text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (as_of_date, model_key));
```

所讀既有表:`TaiwanStockPrice`+除權息事件表(**標籤自建單一基準調整報酬**——PriceAdj 增量拼接損傷實錘,
§5)、`core_universe_asof`(解凍後續建)、`model_registry`(FK)、`direction_gate`(arena 門)。

## §4 Confirmatory Gate(A2 預註冊凍結;evaluate 自動觸發)

- 三關結構沿憲章 v1.42(hit vs 全局多數類 HAC/Brier/ECE+單調);**α=0.05/K(K=§2.1 立門枚舉數,含
  歷來曾立門者)綁定入 criteria**;
- **MDE 與檢定力機械揭露(審查 blocker 的核心修正)**:預註冊時附機械計算表——per-panel sd、LRV 膨脹
  係數、有效 n、各 α 下 80%/50% 檢定力可偵測邊際;**gate 的誠實定位=偵測「可交易級邊際」(MDE≈5-10pp,
  預註冊寫死),對 +1-2pp 級微小邊際明文聲明檢定力≈0**;
- **evaluate 觸發零裁量(審查 major)**:「第一個滿足『已結算 cluster ≥X(D 軌 X=250)/月頻 panel ≥36(H 軌)』
  的月末**自動觸發**,結算窗=開賽日至觸發日全部已結算列、無裁剪」——寫入 criteria 凍結,防看盤挑時點;
- estimand 凍結:model_key+聚合口徑+結算窗定義全文(v2 estimand 引擎複用);
- **敗退寫死**:全體 fail=「在檢定力 X% 下未偵測到 ≥MDE 邊際」結案(**不稱「證偽所有邊際」**);方向軸
  維持研究態;部分 pass=該候選研究級展示+econ 終關另判(預期照舊 dead);
- 逐日價格點位/路徑/單股準確率=永久除外,擂台不碰。

## §5 Python 程式規畫(v1.39.0 (b))

| 檔(新) | 職責 |
|---|---|
| `migrate_direction_arena_ddl.py` | §3 四表+三 trigger(冪等;負向單測×3) |
| `register_arena_candidate.py` | 凍結協定(provenance 必填、離線單測、insert-only) |
| `run_arena_daily_pipeline.py` | **每日管線編排(審查 major 補)**:sync_all_by_date+sync_fred→derive_market_iv(參數化 as-of)→build 特徵(builders 移除 FREEZE 常數、加 --until)→universe as-of 續建→資料可用性檢查(無新列=誠實缺席)→`run_arena_round` |
| `run_arena_round.py` | 逐 active 候選出手;adapter 統一介面;市場模型輸入 spec(表/欄/context≤2048 點/缺值政策)住 spec |
| `arena_adapters/` | own_daily/own_stack(滾動 refit 依凍結政策)/timesfm/chronos(離線)/baseline |
| `settle_arena_labels.py` | 動態判定實際 label 日(數已實現交易日);**單一基準標籤**:TaiwanStockPrice+事件表庫內自建調整報酬(或同次抓取窗內同錨計算);停牌分支(last_trade/unsettleable);PriceAdj factor 單調性機械檢核(不過禁結算——可入 deliberate oracle) |
| `arena_scoreboard.py` | 計分板+futility 判停+`--check-report`(review 級字串集斷言) |
| (既有)`preregister_direction_gate.py` | A2 擴 arena 門模板(estimand=arena ledger+MDE/power 表) |

前置修復(A1):PriceAdj 06-01 後段重抓+15 檔拼接損傷修復(改 writer+重抓,#12 不 hand-patch)。

## §6 分階段・驗收

| 階段 | 內容 | 硬前置 | 驗收 |
|---|---|---|---|
| **A0 骨架** | DDL+adapters+register+**合成序列**冒煙 | A-1 | trigger 負向單測×3;離線單測;VRAM 實測(合成輸入);「零真實股票 p_up 輸出」grep 斷言 |
| **A1 解凍** | A-2 修憲(完整清單)→ **FinMind 續訂(/user_info 機械驗證)**→ 越線資料盤點+PriceAdj 修復 → 分段 sync → build → unfreeze GATE evaluate | A-2、token 續訂 | G1-G5 原子;fail=回退 §7 |
| **A2 開賽** | 候選定版(A-3)+register → **arena gate 全數預註冊+hugo TTY 親核(先凍後跑)** → cron → 首週緊盯 | A1 pass | criteria 含 MDE/power 表斷言;首週 ledger 逐日列;反回填 trigger 實測 |
| **A3 觀察** | 每日管線+每月 scoreboard/futility | — | 月報 `--check-report` 過;缺席率/unsettleable 揭露 |
| **A4 判決** | 樣本門檻**自動觸發** evaluate → econ 終關 | 門檻達標 | 依凍結 criteria;結案措辭依 §4 敗退句 |

## §7 風險與回退

unfreeze fail=原子回退、擂台順延、不鬆 U 判準;FinMind 未續訂=A1 硬停(標籤源不存在);市場模型 OOM/
依賴失效=operational 除名留痕(ledger 入家族);拼接污染=factor 檢核不過禁結算;最壞情境=在檢定力邊界
內未偵測到可交易級邊際——成本≈每日 20 requests+本地算力,新資料同步餵飽相對軌,邊際成本近零。

## §8 對抗審查發現表(3 視角 22 項全採納;裁處=本定稿)

| # | 視角 | 發現(摘) | 裁處 |
|---|---|---|---|
| D1(blocker) | 治權 | A2 產生→A-4 才預註冊違「先凍後跑」;與 no-v3 字面雙面受夾 | §1 時序裁定:A2 預註冊+evaluate 自動觸發;hugo note 簽核相容性(A-2 併裁) |
| D2(major) | 治權 | created_at<label_due=假保證(horizon 內補插不被擋) | §2.3/§3 反回填 INSERT trigger |
| D3(major) | 治權 | judgestop CHECK 擋 'ARENA';verdict 新字彙≠既有閉集;「複用」自述不實 | §2.4/§3:閾值另表;新閉集列 A-1 拍板;明註語意鏡射非 import |
| D4(major) | 治權 | as-of' 入憲清單不完整;修憲實質(FREEZE→live 維運)未指明 | §1 完整修憲清單 |
| D5(major) | 治權 | A0 dry-run 碰凍結資料=再觀看;VRAM 時點三處矛盾 | §1/§6:合成序列統一;禁凍結資料表現入圈選 |
| D6-D8(minor) | 治權 | TAIEX 輸出形不在閉集;K 凍結矛盾;市場權重治權定位無槽 | 內部分量永不展示;家族封閉規則;provenance+離線單測 |
| S1(blocker) | 統計 | 判停除名→倖存者 K=FWER 失效;decay 語意誤植;iterate-until-win 通道 | §2.2/§2.4:K 含歷來全體;futility 只停新預測;歷代版本全計 K |
| S2(blocker) | 統計 | **檢定力自欺**:250 日 cluster 有效 n≈74,確認 +1.4pp 需 12-29 年;「蓋棺」措辭不誠實 | §0.1 承諾改寫;§4 MDE/power 機械揭露;敗退句改「未偵測 ≥MDE」 |
| S3-S8(major) | 統計 | K 不可執行/基線佔門;觸發時點=可選停;轉換口徑=閘外多重測試;v2 殭屍佔額;no-v3 論證含糊;judgestop CHECK | §2.1 枚舉表+基線不立門;§4 自動觸發;conversion_log 凍結;own_v2_frozen 降對照列;§1 時序裁定;另表 |
| S9(minor) | 統計 | 基線參數非零參數 | 慣例值凍結+變體列計分板 |
| F1(blocker) | 可行 | 自家模型無 artifact 可 hash,「原樣參賽」未定義 | §2.1/§2.2:滾動 refit 類+train_data_max_date 留痕 |
| F2(blocker) | 可行 | **FinMind 已降 Free tier(實測 400 拒)**;PriceAdj 拼接損傷 15 檔實錘 | §0.2/§6:續訂=A1 硬前置機械驗證;§5 單一基準標籤+factor 檢核+修復 |
| F3(blocker) | 可行 | label_due 未來日曆不可知;NOT NULL 強迫寫猜測值 | §3 label_due_est nullable+settle 動態判定 |
| F4-F9(major/minor) | 可行 | 斷言證明力不足;每日資料管線整段缺席;K 不一致;停牌倖存偏差;現況與 DB 不符(越線資料);型號名錯;FK 未落實;驗收不可執行 | §2.3 反回填;§5 run_arena_daily_pipeline;§2.1 枚舉;§2.3 settle_mode;§0.4/§1 現況盤點;timesfm-2.5-200m;registry_model_id 欄;--check-report |

---

**結語(審查後誠實版)**:擂台不承諾「終結爭論」——它承諾**把「可交易級方向邊際存不存在」放進唯一
乾淨的考場,在預先揭露的檢定力邊界內給出可覆算的答案**,同時讓新資料餵飽活著的相對軌。
下一步=**A-1**(本計畫)與 **A-2**(解凍+修憲,本計畫最大的一顆;含 FinMind 續訂的現實前置)。
