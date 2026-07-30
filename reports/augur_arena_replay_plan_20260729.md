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
| **作用域標注** | replay 門過＝「**replay-確立（作用域=歷史重演）**」——同 A′ scoped_established 哲學，不冒充 live 確立；**作用域標籤不得混算**（replay 樣本不計入 live 門樣本數、不與真未來賭注同表呈現） |
| **判死留檔** | 任一關不過＝`evaluated_fail` **判死留檔**、`display_tier=never_shown`（凍結列 `criteria.fail_path` 逐字「任一關不過=evaluated_fail 判死留檔」；實錄＝`dgate_replay_mc_bootstrap_5`／`dgate_replay_momentum_20_5` 2026-07-30 判 fail 留檔，`n_panels=2798`）；已重演但無預先凍結之門者，其數字亦不因「跑完了」取得任何地位——**無特權通道** |
| **W1/W2 凍結不動** | replay 對觀察名單只出**旁證報告**（明標、不計批次、不觸發 W2-a——修復觸發仍唯 live 批 2） |
| **帳本硬隔離** | replay 列住新表（§四），對 `direction_arena_prediction` **零寫入**；live 計分板/結算工具零改動 |
| **不翻舊案** | 方向軸 v2 家族判死是對「該家族」的歷史 OOS 終審——replay 隊伍（own_daily/mc/基準/外隊）皆非該家族，舊判決原封 |

> **本節三節點之總則依據（2026-07-30 對齊：大憲章新增之「普遍晉升路徑」條；文字引用，條號由該次修憲定、本檔不自創）**：上表之 **人閘**（§七 R0「你簽 `REPLAY-go`＋§附 門判準親核」；凍結列 `approved_by` 記 hugo 對話拍板、claude 繕打不冒充親簽）、**判死留檔**、**作用域標籤不得混算** 三項並非本計畫自訂之地方規則，而是該條「候選 → 預先凍結判準之證據通道（可證偽／樣本外／實效終審）→ 人類授權門 → 晉升或**判死留檔** → 後果回流為新觀測；**無特權通道**」對「**模型／隊伍**」行走者之落地——本檔僅得定其具體門檻（§附），**不得省略任一節點**。

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

**終審層級誠實註記（2026-07-30 對齊：親驗六門凍結列之 `criteria.econ_axis` 逐字＝「經濟終關=獨立標示軸不在 GATE 內;過門後另判」）**：本軌之凍結判準**明文把經濟終關排除於 GATE 之外**——故**本軌終審為統計級，非實效級——實效終審僅在認知候選線成立**（#14 經濟價值驗證為門外另判軸）。推論：過 replay 門 ≠ 經濟可用；引用門評結果時不得以「終審已過」姿態呈現，須同時標「statistical-only、經濟終關未判」。

**三處與凍結列之落差（2026-07-30 親驗；處置皆屬判準變更 → 呈 hugo 簽，本檔不代訂、不自行釘值）**：
- **窗起點未釘**：六門凍結列 `criteria.estimand.panel_window` 實查皆為 `null`，本節亦僅釘 `weights_cutoff_ok` 與 cluster 數——窗長成為事後可選之自由度（已評兩門實跑 `n_panels=2798`、`n_samples=1391406`、`pred_date` 實達 2015-01-05，遠逾 §三 表列之 2024-01→2026-06）。乾淨隊窗起點是否入 criteria、釘於何日，待簽。
- **majority 無門**：`direction_arena_replay` 實查已為 `majority` 寫入 1,391,879 列（2015-01-05→2026-06-30），但本節六門枚舉未含之、live 亦無 `dgate_replay_majority`——此隊既無預先凍結之門、亦無判死路徑。依 §二 之「無特權通道」與展示分級「未過 GATE=判死留檔、永不出 UI」之保守解釋，**在補門或明定其為不設門之基準臂前，其數字不得引為隊伍表現**；二案擇一（補門並入家族計數重算 alpha／明定為基準臂不設門）待簽。
- **cluster 門檻字面 ≥60 與凍結值不一致**：六門凍結列 `criteria.min_clusters` 實查皆為 **250**（`power_disclosure.threshold_clusters` 同值、`auto_trigger` 綁該值；判準器 `scripts/evaluate_direction_gate.py:112-117` 以之為「未達＝誠實拒判、回 REFUSE」之機械閘），而本節與下方補記仍逐字寫「≥60」並據此對三隊蓋 ✓——**字面與凍結列不符，補記之 ✓ 不得引為已達門檻之證據**。數字之逐字修正與「cluster < min_clusters 之終態」處置併他案（P8）呈簽，本檔不代改。

**待簽**：`REPLAY-go`（含附錄判準；改判準請註明）。

## 補記：R3 發布日親驗（2026-07-30，web/HF 查證非記憶）

| 隊 | 權重發布（親驗） | 合法窗（+1M 邊際） | 估 clusters |
|---|---|---|---|
| chronos_bolt_small | **2024-11-26**（HF 發布） | 2024-12-26 → 2026-06-30 | ~370 ✓ |
| moirai2_small（Moirai-2.0-R-small） | **2025-08** | 2025-09-15 → 2026-06-30 | ~195 ✓ |
| timesfm_25_200m（TimesFM-2.5） | **2025-09** | 2025-10-16 → 2026-06-30 | ~175 ✓ |

（2026-07-30 對齊：上表 ✓ 係對「≥60」蓋章，而凍結列 `min_clusters` 實查＝**250**——三隊之 ✓ 未經凍結門檻驗證，見 §附「三處與凍結列之落差」第三點；本表不代改、呈簽後一次修。）

三隊合法窗皆足 ≥60 不重疊 cluster——R3 重演可排程（TSFM CPU 推論重活、待車道；`--allow-pretrained`＋窗參數照上表）。
來源：huggingface.co/amazon/chronos-bolt-small、Salesforce/moirai-2.0-R-small、google/timesfm-2.5-200m-pytorch（發布敘述另證 marktechpost 2025-08-15/09-16）。
