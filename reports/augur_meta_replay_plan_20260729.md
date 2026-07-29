# 程序重演軌計畫（META-REPLAY）——自我迭代程序本身的 walk-forward 驗證

> [I] 計畫書（#20；hugo 2026-07-29「META-REPLAY-plan」）。**拍板前零實作**；meta 門判準先簽後跑。
> 動因（hugo 原話）：「as-of 2026-01-05，之後自我迭代 2026-01-06，以此類推」——重演的不是模型，是**挑選程序**。回答的問題：**這套程序逐期執行，OOS 有沒有增益？**（TWEVO 軸的終極驗證形態）

## 一、估計量（estimand，一句話）

對每個 cutoff T_k：用**凍結的現行程序**與 ≤T_k 資料選出 prodset_k → 量測 T_k→T_{k+1} 期間「prodset_k 模型」vs「**靜態基準**（起點 prodset 凍住不動）」之次期實績差——差值序列過 HAC 檢定＝**程序適應力有無真增益**。

## 二、三刀（宣稱域邊界，每份輸出強制蓋章）

| 刀 | 內容 | 處置 |
|---|---|---|
| **工具箱後見之明** | 35 產生器、判準門檻、宇宙構造、map 方向皆為看過全史者所設——治不好 | 宣稱域鎖死＝「**固定現行工具箱與判準之程序歷史逐期 OOS 增益**」；禁「當年就會賺」措辭；每份報告/門評printout 首行蓋此章 |
| **資料地板** | `core_universe_asof` 起 2014-12；特徵回看窗+首個 cutoff 須 3 年統計史 | cutoff 窗＝**2018-01 → 2026-05**（~101 月）；**2008 明確不做** |
| **算力** | 每 cutoff 全漏斗=數週級 | **增量式**：cutoff k 只評「非現任成員」候選；增量 ladder 僅 prodset 變動期跑；seeds 降 2（**偏離現行程序之處誠實列表**）；先季頻粗掃（34 cutoff）、有訊號才月頻細化 |

## 三、程序凍結（「程序」的逐字定義，proc_sha 鎖）

每 cutoff 依序（全部僅用 ≤T_k 資料）：
1. **單因子關**：候選池＝35 產生器特徵（as-of 可算者）；HAC |t|≥2（panels ≤T_k）；
2. **增量關**：對 prodset_{k-1} 之多 seed（2）ladder 增量 >0 穩定；
3. **符號關**：實現 IC 符號 == 今日 map 方向（後見之明已在 §二蓋章）；
4. **進出規則**：三關過→入；現任成員符號被拒（同 R3 sign-refuted 精神）→ 出；
5. prodset_k 落 meta 帳本（決策全 JSON 可溯）。程序碼 hash＝`proc_sha`——**中途改程序＝新家族重跑，禁原地改**。

## 四、(a) schema

```sql
CREATE TABLE meta_replay_cutoff (
    proc_sha    TEXT NOT NULL, cutoff_date DATE NOT NULL,
    prodset     JSONB NOT NULL,        -- 該期選定集
    decisions   JSONB NOT NULL,        -- 逐候選三關結果(可溯)
    computed_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (proc_sha, cutoff_date));
CREATE TABLE meta_replay_perf (
    proc_sha TEXT, cutoff_date DATE, model TEXT,      -- B2_ridge/M1_gbdt
    ic_next NUMERIC, ic_next_static NUMERIC,          -- 程序集 vs 靜態基準之次期 IC
    n_stocks INT, PRIMARY KEY (proc_sha, cutoff_date, model));
-- meta 門=direction_gate 新列 dgate_meta_replay(判準 §附;先簽後評)
```

## 五、(b) 程式規畫

| 檔 | 職責 |
|---|---|
| `scripts/migrate_meta_replay_ddl.py`（新） | 上兩表＋`--apply/--check/--selftest` |
| `scripts/run_meta_replay.py`（新） | 逐 cutoff 執行凍結程序：`--from/--to/--step {quarter,month}/--probe-one/--run/--selftest`；複用 `vcp._asof_ic_series`/`baseline.run_ladder`/`verify_sign_consistency.judge_sign`（#12）；panels 子集斷言 ≤cutoff；逐 cutoff commit resume |
| `scripts/evaluate_meta_replay_gate.py`（新） | 預註冊判準機械評（§附）；輸出首行蓋 §二宣稱域章 |

## 六、meta 門判準草案（§附；核可即凍）

樣本＝(ic_next − ic_next_static) 之 cutoff 序列（≥60 期、雙模型分列）；三關：(i) 差值序列 HAC Eff-t 單尾 p<0.05（程序增益>0）；(ii) 程序集次期 IC 之絕對水準 ≥ 靜態基準之 90%（防「贏在基準爛掉」）；(iii) 換手揭露：prodset 逐期異動率併報（適應成本可見）。過門＝「**meta-確立（作用域=固定工具箱程序重演）**」。

## 七、分階段・驗收・停損

| 階段 | 內容 | 驗收 | 停損 |
|---|---|---|---|
| M0 | 你簽 `META-REPLAY-go`＋§六判準親核 | 簽核碼 | 未簽不動 |
| M1 | DDL＋程序凍結模組（proc_sha）＋selftest＋單 cutoff probe（#25） | ≤cutoff 斷言零違例；probe 決策 JSON 人眼可核 | 斷言破=停 |
| M2 | 季頻粗掃 34 cutoff（過夜×2-3、nice、與 replay/臂錯開） | 帳本 34 期滿；資源自律 | 任一 cutoff 崩=resume 不重來 |
| M3 | meta 門評＋報告（蓋章） | 判準 sha 凍結在先 | — |
| M4（條件） | 月頻細化（101 cutoff） | 季頻有訊號才開 | 季頻無訊號=誠實停,不細化找訊號(防 p-hacking) |

**明確不做**：2008；中途改程序；**meta 結果自動回饋 live prodset 決策**（讀了結果想改程序＝下一版程序、新 proc_sha 新家族——防 Goodhart 循環）；月頻細化作為「找訊號」手段。

**待簽**：`META-REPLAY-go`（含 §六判準；改判準請註明）。
