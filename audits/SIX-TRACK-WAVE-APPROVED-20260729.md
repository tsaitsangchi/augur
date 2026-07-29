# 六軌並行開工拍板（2026-07-29）

> **性質**：[I] 拍板登錄；不創設 [N]。  
> **Steward 原文組合**：`開 KH4-heal + KH7-rejudge + n1-retrain + IMPORT-QUAL-S2 + SH-CAL-yes + SH-CLOSE-yes + FZ-keep`  
> **確認**：IMPORT-QUAL-S2＝最小可用面板／讀寫補齊（不另立長計畫）。  
> **簽名誠實**：決策者＝hugo；本檔由 agent 繕寫登錄。

## 一、效力

| 碼 | 含義 | 本輪 |
|---|---|---|
| **KH4-heal** | depth≈3 卡住項：embedding／KH4 eligibility heal（不假抬 admit） | ✅ 開工 |
| **KH7-rejudge** | 解 ungrounded／再跑 eligibility（不假綠；approve 仍唯人） | ✅ 開工 |
| **n1-retrain** | prodset active n=1（`inst_cumflow_position_120d`）庫內 train／predict；`--skip-sync` | ✅ 開工 |
| **IMPORT-QUAL-S2** | S1 之上最小 `/gov` 或等價讀寫面板；不另立長計畫 | ✅ 開工 |
| **SH-CAL-yes** | 採納日曆對映：P30←H20、P60←H40；H60≠「60 天」 | ✅ |
| **SH-CLOSE-yes** | 原 short-horizon 計畫結案＋HANDOFF 改標 | ✅ |
| **FZ-keep** | 零 FinMind／FRED | ✅ |
| SH-ASOF-REFRESH | — | **未拍**（預設 no） |
| SH-REVAL／SH-GBDT-REG | — | **未拍**（預設 no） |
| NHC-CONSTITUTE／PME-XDOM-SOLAR／PME S4 | — | **未拍** |

## 二、硬邊界

- 預測⊥API；庫內 as-of；禁 live sync 當熱路徑入口。
- `approve`／`activate` 仍唯人；KH7 `eligibility_pass` ≠ 可交易。
- 不因本拍板解凍市場 API；不開第二支 admit drain／全表 local-gates。

## 三、留痕（執行中填入）

| 軌 | CLOSED／交付 |
|---|---|
| KH4-heal | ✅ CLOSED · `audits/KH4-HEAL-CLOSED-20260729.md` · buckets {3:2994→504, 6:143280→145770}；advanced=2490；殘留 396 ineligible＋108 provisional（不假抬） |
| KH7-rejudge | ✅ `audits/KH7-REJUDGE-CLOSED-20260729.md`（run_id=6：3 pass／1 fail；layer7 可 pass；≠approve；FZ-keep） |
| n1-retrain | **CLOSED** `audits/N1-RETRAIN-CLOSED-20260729.md` — live active n=2（cumflow＋lending_fee；拍板敘 n=1 已漂移）；`train_ranker`＋`predict_asof --dry-run` as-of 2026-05-31 綠；model=`RankRidge_H60_2026-05-31_seed42_9a88039981b5a128`；**≠可交易／≠direction_gate** |
| IMPORT-QUAL-S2 | ✅ `audits/IMPORT-QUAL-GATE-S2-CLOSED-20260729.md`（`/gov` 唯讀 job＋qualification；無 approve／activate） |
| SH-CAL／SH-CLOSE | ✅ `audits/SH-CAL-CLOSE-APPROVED-20260729.md`；HANDOFF §1／§4.5 已改標 |

## 四、六軌收束

全部 CLOSED（2026-07-29）。可另令：`--until-empty --apply-up-to 7`（仍非 KH10；KH8／9 UNBUILT）；`NHC-CONSTITUTE`／`PME-XDOM-SOLAR`／SH-ASOF-REFRESH。
