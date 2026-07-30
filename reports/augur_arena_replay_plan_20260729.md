# 歷史重演軌計畫（REPLAY）——arena 隊伍之 as-of 重演證據軌

> [I] 計畫書（#20；hugo 2026-07-29「REPLAY-plan」）。**拍板前零實作**；門判準先簽後跑（門柱紀律正用）。
> 動因（hugo 原話）：「你本來就可以 as-of 之前的日期來進行，不用等新交易資料，只要定義不偷看 as-of 之後的資料」——live 門的 60-cluster 累積是 live 之事，**證據生成不必等日曆**。

## 一、目標與三個直接效益

對每個歷史交易日 t：只用 ≤t 資料出單（`train_data_max_date=t` 斷言焊死）→ 用已知後續結算。效益：
1. **W2 病理持續性即刻可診**：own_daily_rolling 反排序是「一週雜訊」或「持續病理」——數十個歷史窗旁證，不必等 08-03；
2. **統計力**：own／mc_bootstrap／基準隊 2024-01→2026-06 ≈ **~600 clusters**（live 現況 2）；
3. **外隊真實力提早現形**（合法窗內，見 §三）。

## 二、效力邊界（本計畫的憲政核心，先於一切機制）

| 邊界 | 內容 |
|---|---|
| **live 門不吃 replay** | 既有 `dgate_arena_*` 判準明文「live 結算列」——**一字不動、一列不混**；live arena 仍是產品化唯一鑰匙 |
| **replay 走新門** | 另立 `dgate_replay_*` 預註冊（判準草案 §附；**你簽准後才准跑 evaluate**）；三關數學與既有 gate 同碼、僅樣本源不同 |
| **作用域標注** | replay 門過＝「**replay-確立（作用域=歷史重演）**」——同 A′ scoped_established 哲學，不冒充 live 確立 |
| **W1/W2 凍結不動** | replay 對觀察名單只出**旁證報告**（明標、不計批次、不觸發 W2-a——修復觸發仍唯 live 批 2） |
| **帳本硬隔離** | replay 列住新表（§四），對 `direction_arena_prediction` **零寫入**；live 計分板/結算工具零改動 |
| **不翻舊案** | 方向軸 v2 家族判死是對「該家族」的歷史 OOS 終審——replay 隊伍（own_daily/mc/基準/外隊）皆非該家族，舊判決原封 |

## 三、外隊權重污染表（合法窗）

預訓練模型在**發布日前**的歷史上重演＝權重藏未來（預訓練語料涵蓋該期），as-of 輸入紀律治不了。合法窗＝發布日＋1 個月安全邊際起：

| 隊 | 權重發布（**實作時以 HF model card 親驗**,下列為待核估值） | 合法窗（估） |
|---|---|---|
| chronos_bolt_small | ~2024-11（待核） | 2024-12 → 2026-06（~19 個月） |
| moirai2_small | ~2025（待核） | 發布+1M → 2026-06 |
| timesfm_25_200m | ~2025（待核） | 發布+1M → 2026-06 |
| own_daily_rolling／mc_bootstrap／momentum_20／majority | 規則式／逐日重訓，零預訓練 | **全期乾淨**（2024-01→2026-06） |

發布日**禁引記憶**——實作時逐模型查證入 spec、違窗列 `weights_cutoff_ok=false` 永不入門評。

## 四、(a) schema

```sql
CREATE TABLE arena_replay_run (          -- 重演批註冊(一批=一模型一窗)
    replay_run_id TEXT PRIMARY KEY, model_key TEXT NOT NULL,
    window_start DATE NOT NULL, window_end DATE NOT NULL,
    weights_cutoff_ok BOOLEAN NOT NULL,  -- §三合法窗判
    code_sha TEXT NOT NULL, spec JSONB NOT NULL, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE direction_arena_replay (    -- 重演出單+即結(鏡射 live 欄+replay_run_id)
    replay_run_id TEXT REFERENCES arena_replay_run,
    model_key TEXT, target_id TEXT, pred_date DATE, horizon_td INT,
    p_up NUMERIC, train_data_max_date DATE,   -- 斷言=pred_date(#8)
    y_up INT, realized_ret NUMERIC, settle_mode TEXT,
    PRIMARY KEY (replay_run_id, model_key, target_id, pred_date));
-- 隔離不變式:live 表零觸碰;交叉污染稽核=兩表 (model_key,pred_date) 交集必空於 live 開賽日前
```

## 五、(b) 程式規畫

| 檔 | 職責 |
|---|---|
| `scripts/migrate_arena_replay_ddl.py`（新） | 上表＋隔離稽核 `--check`；`--apply/--dry-run/--selftest` |
| `scripts/run_arena_replay.py`（新） | 重演引擎：`--model --from --to`；複用 `arena/adapters.py`（#12），逐日 as-of 出單＋即結；**斷言**：`train_data_max_date==pred_date`、標籤只取 >pred_date 已實現日；逐日 commit resume；`--probe-one`（#25 單日先行）`--dry-run/--selftest`；nice 離峰 |
| `preregister_direction_gate.py`（既有） | 註冊 `dgate_replay_*`（判準=§附草案、你簽） |
| `evaluate_direction_gate.py`（擴一模式） | `--replay-source`：同三關數學、樣本改讀 replay 表（判準碼零改） |
| `verify_arena_watchlist.py`（擴一模式） | `--replay-adjunct`：W1/W2 同口徑排列檢定於歷史窗——**輸出恆標「旁證/不計批次/不觸發」** |
| `settle_arena_labels.py` 等 live 工具 | **零改動**（隔離） |

## 六、算力與排程

own_daily 逐日重訓 ~600 日＝**過夜級**（nice、逐日 resume、與 LLM 臂 flock 錯開）；mc/momentum/majority 輕；外隊推論=第二波過夜。全部**排在今晚 A′ 批收槍後**，不與現役三重活搶道。

## 七、分階段・驗收・停損

| 階段 | 內容 | 驗收 | 停損 |
|---|---|---|---|
| R0 | 你簽 `REPLAY-go`＋**§附門判準親核** | 簽核碼 | 未簽不動 |
| R1 | DDL＋引擎＋selftest＋單日 probe → 乾淨隊全窗重演（過夜） | as-of 斷言零違例；抽 3 日對帳已知價格 | 任一斷言破=停+報 |
| R2 | replay 計分板＋W2 旁證報告＋乾淨隊門評 | 交叉污染稽核=空；門評引用凍結判準 sha | — |
| R3 | 外隊發布日親驗→合法窗重演→門評 | 違窗列 0 入評 | 查不到可靠發布日=該隊不跑（誠實棄） |

**明確不做**：replay 餵 live 門；改 live 工具；重演死亡 v2 家族；用 replay 觸發 W2-a。

## 附：`dgate_replay_*` 判準草案（待你親核；核可即凍結）

沿用既有 direction gate 三關逐字（(i) hit−base HAC Eff-t 單尾 p<0.05；(ii) OOS Brier < p̄(1−p̄)；(iii) ECE≤凍結上限＋十分位單調），樣本源改「`direction_arena_replay` 之 `weights_cutoff_ok=true` 列、≥60 不重疊 cluster」；每隊一門（own_daily_rolling／mc_bootstrap／momentum_20／chronos_bolt／moirai2／timesfm）；作用域標注=「replay-確立」。

**待簽**：`REPLAY-go`（含附錄判準；改判準請註明）。

## 補記：R3 發布日親驗（2026-07-30，web/HF 查證非記憶）

| 隊 | 權重發布（親驗） | 合法窗（+1M 邊際） | 估 clusters |
|---|---|---|---|
| chronos_bolt_small | **2024-11-26**（HF 發布） | 2024-12-26 → 2026-06-30 | ~370 ✓ |
| moirai2_small（Moirai-2.0-R-small） | **2025-08** | 2025-09-15 → 2026-06-30 | ~195 ✓ |
| timesfm_25_200m（TimesFM-2.5） | **2025-09** | 2025-10-16 → 2026-06-30 | ~175 ✓ |

三隊合法窗皆足 ≥60 不重疊 cluster——R3 重演可排程（TSFM CPU 推論重活、待車道；`--allow-pretrained`＋窗參數照上表）。
來源：huggingface.co/amazon/chronos-bolt-small、Salesforce/moirai-2.0-R-small、google/timesfm-2.5-200m-pytorch（發布敘述另證 marktechpost 2025-08-15/09-16）。
