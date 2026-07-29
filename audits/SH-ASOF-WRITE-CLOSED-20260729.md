# SH-ASOF-WRITE CLOSED — prediction_values 寫庫 @ 2026-06-30 [I]（2026-07-29）

> **性質**：[I] 執行收口；不創設 [N]。  
> **拍板**：`audits/THREE-FOLLOWUPS-APPROVED-20260729.md`（ASOF 寫庫補登）＋`FZ-keep`  
> **前置**：`audits/SH-ASOF-REFRESH-CLOSED-20260729.md`（dry-run 已綠；寫庫曾擋於 DELETE／ghost）  
> **硬邊界**：as-of=`2026-06-30`；禁 reval；禁部署切換；≠確立級／≠可交易／≠ direction_gate；零 FinMind／FRED。  
> **簽名誠實**：決策者＝hugo；本檔由 agent 繕寫登錄。

---

## 結果（一句）

**H20／H40／H60 `predict_asof --run --candidate` @ `2026-06-30` 已寫入 `prediction_values`（各 226 列／top10%=22；合計 678）。語意＝candidate；≠部署／≠確立級。**

---

## 1. 硬邊界遵守

| 禁／守 | 本輪 |
|---|---|
| 禁 reval／四關／deflation | ✅ 未跑；`revalidation_ledger` @ `2026-06-30`＝**0** |
| 禁部署切換 | ✅ 未改 registry deploy 標；未宣稱 in_portfolio＝已部署 |
| 禁確立級 | ✅ 未宣稱 |
| FZ-keep／零市場 API | ✅ 無 FinMind／FRED／sync |
| 預測⊥API | ✅ 庫內 as-of；僅 DB 寫 `prediction_values` |

---

## 2. 解阻（寫庫前置）

### 2.1 未登錄表 → 補登後 `--apply`

`setup_predict_role --apply` 原 fail-loud 於 **19** 張未登錄表。本輪全部歸 **forbidden**（非預測熱路徑；禁 fail-open）：

| 手段 | 表／前綴 |
|---|---|
| 新前綴 | `knowhow_`、`advisor_probe_`、`meta_replay_` |
| 明示 FORBIDDEN | `arena_replay_run`、`factor_direction_ruling`、`license_regime_map`、`source_license_whitelist`、`source_pacing_policy`、`raw_table_coverage_snapshot`、`steward_question_ledger`（＋既有 `knowhow_interaction_probe`） |

```bash
./venv/bin/python scripts/setup_predict_role.py --apply --confirm
# → REVOKE 125／GRANT 162；exit 0
# log=/tmp/augur_logs/setup_predict_role_apply_20260729.log
```

| 查詢 | 結果 |
|---|---|
| `has_table_privilege('augur_predict','prediction_values','DELETE')` | **True**（先前 False） |
| INSERT／SELECT | True |

### 2.2 Ghost artifact → registry.latest 跳過缺檔

H20／H40 registry 最新列 `3a4e66fa…` **缺 joblib**（仍有 2026-05-31 prediction_values FK，**未刪列**）。

**修正**：`augur.models.registry.latest` 依 `asof DESC, created_at DESC` 走訪，**跳過 `Path.is_file()` 為假**之 ghost，選下一 on-disk 列——未 retrain。

| H | serve model_id |
|---|---|
| 20 | `RankRidge_H20_2026-05-31_seed42_ce62866bb62de38b` |
| 40 | `RankRidge_H40_2026-05-31_seed42_ce62866bb62de38b` |
| 60 | `RankRidge_H60_2026-05-31_seed42_9a88039981b5a128`（prodset；本就最新且有檔） |

---

## 3. 指令矩陣（實跑）

```bash
./venv/bin/python scripts/predict_asof.py --run --candidate --asof 2026-06-30 --horizon {20,40,60}
# log=/tmp/augur_logs/sh_asof_predict_write_20260729.log
```

| H | exit | model | feature_source | n_rows | top10% |
|---|---|---|---|---|---|
| 20 | 0 | ce62866b… | canonical（凍結 28；漂移僅告警） | 226 | 22 |
| 40 | 0 | ce62866b… | canonical（同上） | 226 | 22 |
| 60 | 0 | 9a880399… | prodset（2 feats） | 226 | 22 |

**未跑**：`run_revalidation`／Stage B／D／R／`evaluate_direction_gate`／deploy 切換／retrain／FinMind／FRED。

---

## 4. Metrics（僅 DB／stdout）

| 鍵 | 值 |
|---|---|
| `prediction_values` @ `2026-06-30` | **678**（3×226） |
| per-model in_portfolio | 各 **22** |
| #1 score（stdout） | H20 2330 `+0.7402`；H40 2330 `+0.8697`；H60 3567 `+0.5491` |
| DELETE privilege | True |
| revalidation @ as_of | **0** |

事後核：`/tmp/augur_logs/sh_asof_write_postcheck_20260729.txt`

---

## 5. 變更檔

| 檔 | 作用 |
|---|---|
| `scripts/setup_predict_role.py` | 19 表補登 forbidden；`--apply` 放行含 DELETE 之 WRITABLE GRANT |
| `src/augur/models/registry.py` | `latest` 跳過缺檔 ghost；`--selftest` 鎖 `is_file` |
| 本檔／`THREE-FOLLOWUPS` §二 | 留痕 |

---

## 6. 仍未開

- **SH-REVAL**／四關重跑／確立級  
- 部署切換／`rewrite-all`（本輪僅 H20／40／60）  
- ghost `3a4e66fa` 列物理清理（FK 仍掛 2026-05-31 舊分；serve 已跳過）
