# SH-ASOF-REFRESH CLOSED — universe＋predict @ 2026-06-30 [I]（2026-07-29）

> **性質**：[I] 執行收口；不創設 [N]。  
> **拍板**：`SH-ASOF-REFRESH-yes`（as-of=`2026-06-30`；禁 reval；禁部署切換）＋`FZ-keep`  
> **依據**：`audits/WAVE2-SIX-TRACK-APPROVED-20260729.md`；M2＝`reports/augur_short_horizon_timeliness_clarify_20260729.md` §4  
> **硬邊界**：零 FinMind／FRED；庫內 as-of；**未**重跑四關／revalidate；**未**改 deploy／確立級宣稱；**未**開 `SH-REVAL`。  
> **簽名誠實**：決策者＝hugo；本檔由 agent 繕寫登錄。

---

## 結果（一句）

**`core_universe_asof` @ `2026-06-30` 已建（226 股）；H20／H40／H60 `predict_asof` 候選分數 dry-run 全綠（各 226 列／top10%＝22 檔）。寫庫 `prediction_values` 未落——`augur_predict` 缺 DELETE；首輪 `--run` 寫入撞權限／ghost artifact。≠可交易／≠確立級／≠ direction_gate。**

---

## 1. 硬邊界遵守

| 禁／守 | 本輪 |
|---|---|
| 禁 reval／四關／deflation | ✅ 未跑 `run_revalidation`／Stage B／D／R／`evaluate_direction_gate` |
| 禁部署切換 | ✅ 未改 registry deploy 標；未宣稱 in_portfolio＝已部署 |
| 禁確立級 | ✅ 未宣稱 |
| FZ-keep／零市場 API | ✅ 無 FinMind／FRED／sync／`daily_maintenance` |
| 預測⊥API | ✅ 庫內 as-of |

---

## 2. 指令矩陣（實跑）

```bash
# 1) universe（參數對齊既有 build_meta：liquidity_pct=25＋金融月營收豁免）
./venv/bin/python scripts/build_core_universe.py \
  --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof
# → EXIT=0；log=/tmp/augur_logs/sh_asof_universe_20260729.log

# 2) 首輪寫庫嘗試（誠實失敗）
./venv/bin/python scripts/predict_asof.py --run --candidate --asof 2026-06-30 --horizon {20,40,60}
# → H20/H40：FileNotFoundError（registry latest＝ghost 3a4e66fa… 缺 joblib）
# → H60：InsufficientPrivilege DELETE on prediction_values（augur_predict）
# → log=/tmp/augur_logs/sh_asof_predict_20260729.log

# 3) 交付路徑＝dry-run＋跳過缺檔 artifact（未改 train／未開 reval）
#    （stdin wrapper；registry 跳過 missing joblib → 用 on-disk ce62866b／9a880399）
# → ALL_OK=True；log=/tmp/augur_logs/sh_asof_predict_dryrun_20260729.log
```

| 步 | 指令／動作 | exit | log |
|---|---|---|---|
| 1 | `build_core_universe.py … --asof` | 0 | `/tmp/augur_logs/sh_asof_universe_20260729.log` |
| 2 | `predict_asof --run --candidate` H20／40／60 | 1 | `/tmp/augur_logs/sh_asof_predict_20260729.log` |
| 3 | dry-run＋artifact-pick H20／40／60 | 0 | `/tmp/augur_logs/sh_asof_predict_dryrun_20260729.log` |
| — | `setup_predict_role --apply --confirm`（試刷新 DELETE） | 拒跑 | 19 未登錄表；`predict_DELETE` 仍 False |
| — | retrain H20／40／`rewrite-all`／GRANT DELETE | **SKIP** | 出本軌／審批擋 |

**未跑**：任何 sync／FinMind／FRED；`run_evaluation`／revalidate／方向門；deploy 切換。

---

## 3. Metrics（僅 stdout／DB；零臆造）

### 3.1 Universe

| 鍵 | 值（真兆） |
|---|---|
| 指令 stdout | `74 面板（2014-12-31..2026-06-30）`；as-of 核心數 `219..703`；pan-hist 190 股／38 特徵 |
| `core_universe_asof` @ `2026-06-30` | **226** 列 |
| 全表 | 28492 列；min=`2014-12-31` max=`2026-06-30` |
| build_meta（最新 asof） | panel_end=`2026-06-30`；panel_count=74；core_count=226；feat_count=38；liquidity_pct=25 |

### 3.2 Predict dry-run（asof=`2026-06-30`）

| H | model_id | feature_source | n_feats | n_rows | top10% 檔 | #1 score |
|---|---|---|---|---|---|---|
| 20 | `RankRidge_H20_2026-05-31_seed42_ce62866bb62de38b` | canonical | 28 | 226 | 22 | 2330 `+0.7402` |
| 40 | `RankRidge_H40_2026-05-31_seed42_ce62866bb62de38b` | canonical | 28 | 226 | 22 | 2330 `+0.8697` |
| 60 | `RankRidge_H60_2026-05-31_seed42_9a88039981b5a128` | prodset | 2 | 226 | 22 | 3567 `+0.5491` |

H20／H40：registry 最新列 `3a4e66fa…` **缺檔** → 跳至 on-disk `ce62866b…`；canonical 漂移僅告警、仍以 frozen feats serve。  
H60：用 N1-RETRAIN prodset model（`inst_cumflow_position_120d`＋`lending_fee_rate_mean_20d`）。

### 3.3 寫庫／reval 現況（事後核）

| 查詢 | 結果 |
|---|---|
| `prediction_values` WHERE `panel_date=2026-06-30` | **0**（dry-run 未寫） |
| `revalidation_ledger` @ `2026-06-30` | **0** |
| `augur_predict` DELETE on `prediction_values` | **False** |

---

## 4. Write vs dry-run（誠實）

| 意圖 | 結果 |
|---|---|
| 偏好 `--candidate` 寫 `prediction_values`（refresh OK） | **未寫成** |
| 原因 | (a) H20／H40 ghost artifact；(b) predict role 無 DELETE（`predict_asof` 冪等＝DELETE+INSERT）；(c) `setup_predict_role --apply` 因 19 未登錄表 fail-loud 拒跑 |
| 代碼留痕 | `scripts/setup_predict_role.py` WRITABLE 已補 `DELETE`（待表分類補登後 `--apply` 才生效） |
| 本輪交付 | **dry-run 候選分數**（stdout／log）；語意＝candidate top-frac，**≠部署** |

---

## 5. 仍未開

- **`SH-REVAL`**（M3 四關重跑）— 未拍／未開  
- **`SH-GBDT-REG`** — 未拍  
- 寫庫 refresh／ghost artifact 清理／predict GRANT 表分類補登 — 另令  

---

## 6. 證據索引

| 來源 | 用途 |
|---|---|
| `/tmp/augur_logs/sh_asof_universe_20260729.log` | universe stdout |
| `/tmp/augur_logs/sh_asof_predict_20260729.log` | 寫庫失敗真兆 |
| `/tmp/augur_logs/sh_asof_predict_dryrun_20260729.log` | H20／40／60 scores |
| `/tmp/augur_logs/sh_asof_postcheck.txt` | DB 事後核 |
| `audits/WAVE2-SIX-TRACK-APPROVED-20260729.md` | 拍板 |
| clarify M2 | `reports/augur_short_horizon_timeliness_clarify_20260729.md` §4 |
