# 擂台 A2 開賽提案包(2026-07-12 預擬;解凍 GATE evaluate pass 後生效)

> **這份是什麼**:A2 開賽的全部拍板材料一頁式——候選定版、六門 TTY 親核包、futility 凍結值、
> 排程、首週監看。**前提=unfreeze GATE evaluate pass**;fail 則本包全部凍結不動(回退依擂台計畫 §7)。
> 你只需照 §7 的句式回覆+貼指令,十分鐘開賽。

## §1 前置狀態核對(自動鏈,無需你動)

| 前置 | 狀態 |
|---|---|
| FREEZE 解凍修憲 | ✅(v1.9.0/v1.43.0,commit 7d337ec) |
| 33 天資料補檔+PriceAdj 修復+特徵四鏈至 07-09 | ✅ |
| 首個凍結後 panel(2026-06-30) | ✅(91,385 值) |
| E 債 | E1 等對帳(IP 癒合自動跑);餘全綠 |
| **unfreeze GATE evaluate** | ⏳ 對帳綠後自動扣扳機(G1-G5 原子) |
| arena 骨架(4 表 3 trigger/8 候選/adapters/live round/settle/scoreboard/pipeline) | ✅ 全數實測 |

## §2 候選定版提案(=A-3;拍板句見 §7-①)

8 列照 A0 註冊凍結;唯一未決=**timesfm 條件款**:權重下載屢因網路停滯——提案:**開賽日冒煙未過
即依凍結協定 operational 除名留痕(不阻開賽),日後補測通過=新候選入下一輪家族**。
立門 K=6 不變(own_daily/chronos/timesfm×D5+own_stack×H20/40/82;timesfm 若除名→其門以
`superseded` 留痕、家族句照 16 門序列如實揭露)。

## §3 六門 gate TTY 親核包(evaluate pass 後我跑 `--preregister-arena`,然後你貼)

```bash
python scripts/preregister_direction_gate.py --approve dgate_arena_own_daily_5  --approved-by hugo
python scripts/preregister_direction_gate.py --approve dgate_arena_chronos_5   --approved-by hugo
python scripts/preregister_direction_gate.py --approve dgate_arena_timesfm_5   --approved-by hugo
python scripts/preregister_direction_gate.py --approve dgate_arena_own_stack_20 --approved-by hugo
python scripts/preregister_direction_gate.py --approve dgate_arena_own_stack_40 --approved-by hugo
python scripts/preregister_direction_gate.py --approve dgate_arena_own_stack_82 --approved-by hugo
```

親核時你在確認的(每門 criteria 已凍,`--check` 可覆算 sha):α=0.05/6 綁定;樣本門檻自動觸發
(D≥250 已結算日 cluster、H≥36 月頻)零人為挑時點;**MDE/檢定力表機械凍入**(誠實定位=偵測可交易級
邊際,對 +1-2pp 微小邊際檢定力≈0 已明文);fail_path 禁「蓋棺」措辭;**approve=併簽 no-v3 相容句**
(「係真未來新實驗、不構成對凍結資料重試」——note 已預寫)。

## §4 futility 判停凍結值提案(=`direction_arena_policy` 兩列;拍板句見 §7-②)

| policy_key | 建議值 | 理據 |
|---|---|---|
| `futility_min_clusters` | **60** | ≈3 個月日 cluster;以歷史 sd(0.26)+LRV 膨脹(3.4)換算 se≈6pp——此門檻下唯**災難級**劣化(訊號反接/邏輯壞)觸發,邊際型雜訊不殺(對抗審查 S1:防均值回歸誤殺;futility=停止出新預測、ledger 仍全數入 gate) |
| `futility_z` | **1.645** | 單邊 95% 信賴上界<0 才 suspected;連續 2 輪才 confirmed |

```sql
INSERT INTO direction_arena_policy VALUES
  ('futility_min_clusters', 60, true, 'arena A2 提案包 §4;hugo 併核 <日期>'),
  ('futility_z', 1.645, true, 'arena A2 提案包 §4;hugo 併核 <日期>');
```

## §5 排程提案(cron 三行;拍板句見 §7-③)

```cron
30 22 * * 1-5 flock -n /tmp/arena_pipe.lock  /home/hugo/project/augur/venv/bin/python /home/hugo/project/augur/scripts/run_arena_daily_pipeline.py >> /home/hugo/arena_daily.log 2>&1
10 23 * * 1-5 flock -n /tmp/arena_settle.lock /home/hugo/project/augur/venv/bin/python /home/hugo/project/augur/scripts/settle_arena_labels.py --run >> /home/hugo/arena_settle.log 2>&1
0  8  1 * *   /home/hugo/project/augur/venv/bin/python /home/hugo/project/augur/scripts/arena_scoreboard.py --out /home/hugo/project/augur/reports/arena_monthly_$(date +\%Y\%m).md >> /home/hugo/arena_score.log 2>&1
```

理據:22:30=台股 EOD 資料(法人/融資/選擇權)已全數落檔且避開整點;pipeline 內建每日 ~20 requests
(#24 零壓力)+資料未到=誠實缺席 exit 0;23:10 settle 與 pipeline 錯開;flock 防重疊;月報首日 08:00
(`--check-report` 字串斷言隨跑)。**首日由我手動陪跑替代 cron(§6),次日起 cron 接手。**

## §6 首週監看(我做,#21/#25)

開賽日:手動跑首輪對局+驗 ledger 落列/反回填 trigger/各 adapter 出手數;D+1~D+7:每日檢查
pipeline log(缺席/quota/adapter 失敗)、settle 首批結算實證(UPDATE 路徑首次真列驗證——A0 時
無法測的最後一塊)、scoreboard 首份週讀數(review 級字樣機械斷言);任何 anomaly 立即回報。

## §7 一鍵拍板句(evaluate pass 通知後回覆)

1. 「**候選定版照 §2(含 timesfm 條件款)**」
2. 「**futility 凍結照 §4**」(或改值)
3. 「**排程照 §5**」(或改時刻)
4. 貼 §3 六行 approve 指令(TTY)

四項到齊=**開賽**。我隨即:policy INSERT→cron 掛載→首輪對局陪跑→首週監看。
