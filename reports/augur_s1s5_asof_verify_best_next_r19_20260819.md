---
title: r16 閉環 × r19 LIVE——各段最佳下一步／可先／可同步＋其他模型驗証
status: final
series: s1s5_loop
round: r19
date: 2026-08-19
viewpoint: 2026-08-19T14:45+08:00
layer: "[I]"
role: 把 r16 運轉 SSOT 對到 r19 視點；列出全段最佳下一步／可先／可同步；V0＋V1＠價頂 08-18 已跑
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r19_20260819.md
other_verify: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
supersedes: archive/slim-t2/augur_s1s5_asof_verify_best_next_r18_20260817.md
go: audits/S1S5-OTHER-VERIFY-0818-GO-20260819.md
fired: audits/S1S5-OTHER-VERIFY-0818-FIRED-20260819.md
executed: audits/S1S5-OTHER-VERIFY-0818-EXECUTED-20260819.md
code:
  - scripts/run_asof_collect_train_verify.sh
  - scripts/verify_asof_families.py
  - src/augur/core/asof_ready.py
  - scripts/check_asof_ready.py
self_reported: true
---

# r16 閉環問題板（對齊 2026-08-19 14:40 LIVE）

> **一句**：閉環怎麼轉仍＝r16；開工順序＝r19。歷史 as-of **可以**收特徵／訓／驗——這是正門，不是假今天。  
> **LIVE 15:22**：價頂／fv／包／出門＝**08-18** H20+H60。**08-19＝假 B3**（rc=3）。**過去 as-of＝可以**（正門）。HIST＠**08-12／08-11 已齊 64／64**。下一未齊＝**08-10 缺 52**（已有 H5 窗）。V0＠08-18＝8×8 全綠。

## §1 過去 as-of：可以，而且是唯一合法做法

| 可以 | 不可以 |
|---|---|
| D ≤ PriceAdj TAIEX 價頂，且只用當時可見資料 | 把 **08-19** 當 as-of（價未進） |
| 截面族**共用** `feature_values`＠D | 拿 D+1 價回填 D 的特徵 |
| `check_asof_ready.py --date D` → ready 才 collect／訓 | 無價卻 `train_* --asof D` |
| 多 D walk-forward 當重覆驗（#11） | 同尺重掃 0812 NF 六族變綠 |
| `--track A`／`--track all`＠歷史 D（方向臂不覆寫） | promote／sim-apply／`--track other --apply`（rc=6） |

殼：

```text
python scripts/check_asof_ready.py --date 2026-08-18          # 價頂；ready；下一刀 verify_only
python scripts/check_asof_ready.py --fake-b3-date            # 現＝2026-08-19
python scripts/check_asof_ready.py --date 2026-08-19          # rc=3 假 B3
python scripts/check_asof_ready.py --scan                    # 建議下一未齊＝08-10 缺 52（已有 H5 窗）
# 08-11／08-12 已 apply：64／64。下一槍另貼 HIST-ASOF-apply | date=2026-08-10 | track=all
bash scripts/run_asof_collect_train_verify.sh --date 2026-08-18 --dry-plan --track other
# rc=0：V0 盤點；不訓。--apply --track other 仍 rc=6
python scripts/verify_asof_families.py --date 2026-08-07 --ic --oos
python scripts/verify_asof_families.py --walk --oos --horizon 5 --limit 6
python scripts/verify_asof_families.py --walk --oos --horizon 10 --limit 4
```

**pack_complete**：歷史 D＝截面 64 格；價頂才加 Daily3＋Mkt2＋DirStackM。`--track all`＠非價頂預設 `--skip-daily --skip-mkt --skip-stack`。

**其他模型**：共用 `feature_values`＠D 的只有截面 8 族。VECM／TCN／NB／RL 缺 adapter／額外張量，須點名 GO。0812 NF 六族禁同尺重掃。SeqLSTM 評測不寫庫。

---

## §2 r16 各段 × 現在最佳下一步／可先／可同步

**全專案最佳下一步**仍是 r19 決策卡：**候下一真收盤（刀 B）**；本路徑不取代心跳、不升格。

| 段 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 14:40 |
|---|---|---|---|---|---|
| **S0** | 運轉契約 | 跟 r16；開工跟 r19 | — | — | 🟢 LOCKED |
| **S1** | 日更心跳 | 候 `PriceAdj≥08-19-close` → B3 20,60（載＠08-18 RankRidge） | **否**（無價） | 開火獨佔 | 🟢 出門＠08-18；下一 D WAIT |
| **S2** | KH | 記帳 63；drain 另貼 `KH-S0-apply-go` | check＝已做；apply＝否 | 避開 B3 | 🟡 S0 FIRE 63 |
| **S3** | 特徵 | 沿用 panel＠08-18；缺 D 才 collect | 文件 | P6 refit **另 GO** | 🟢 37 欄；P6 缺口 08-14 vs 08-18 |
| **S4 日更** | 邊界 A | 新價才 L2；禁無 GO 再 `--force` | 否 | 歷史 D 須 GO | 🟢 pack＠08-18 COMPLETE |
| **S4 普查** | 其他族 | **本窗 V0／V1 已閉**；殘格點名；禁 0812 | 再 walk＝等新實現窗 | 開新族＝否 | 🟢 V0＠08-18；V1 H5 已跑；H10 閘；V4❄ |
| **S5** | #14 | 披露 H20=dead／H60=thin；不塗綠 | 是 | evaluate＝否 | 🟢 形已誠實；emit 已跟價 |
| **S5 sim** | 風險形狀 | 禁 apply | 否 | 否 | 禁 |
| **C2** | 模型↔漲跌比 | 日更時披露；**不**因單 panel 正 IC 換冠 | 文件 | 重訓讓 B3 | 🟡 RankKNN 五 panel 均值略正 ≠ 確立 |
| **歷史 as-of** | 重覆驗 | 已齊近＝08-18／17／14／13／12／**11**／07／07-31；下一未齊 **08-10 缺 52**（已有 H5 窗） | scan＝是 | `--apply`＠08-10 須另句 | 🟢＠08-11／12 64／64 |
| **M28** | 確立 | E4b 鐘 WAIT k=0 next≈2026-11-13；不 E5 | 鐘可重讀 | 否 | 🟡 |

### 可先做（不等 08-19 價；本窗已做／還能做）

| 做 | 狀態 | 不要順便做 |
|---|---|---|
| `--scan`／`--track other --dry-plan`／V0＠08-18 | **已做** | `--track other --apply` |
| V1 `--walk --oos` H5／H10；`--ic --oos`＠08-07／07-31 | **已做** | 把 IC 當報酬％／升格 |
| KH `--check` | **已做**（14:13） | `--apply` drain 63 |
| P6 缺口文件；E4b 鐘重讀 | 可再讀 | refit／E5／evaluate |
| 08-12 `dry-plan --track all` | 可先盤點 | 無 GO 卻 `--apply`；`--force-direction` |

### 可同步做（與主軸 WAIT 並行；B3 開火則讓鎖）

- 上表「可先」列（巡檢、盤點、唯讀 walk、文件）。
- **不要**與下一槍 B3／L2 搶 `augur_llm.lock`。
- 開新族、NF 重掃、KH apply、HIST apply＠08-12、P6 重訓、路徑 P1／emit：**不可**假裝與本窗同步——各須自己的 GO。

### 必須等／另句

| 等什麼 | 為什麼 |
|---|---|
| PriceAdj ≥ 08-19 收盤 ＋ `B3-go` | 否則假 B3 |
| 再 4 個交易日（約）才可能讓 **08-07 實現 H10** | 現 n_after(08-07)=7；H10 要 ≥11 |
| `HIST-ASOF-apply \| date=2026-08-12 \| track=all` | 缺 32 格；本鎖不開 |
| `KH-S0-apply-go \| drain up_to=0 limit=63` | FIRE ≠ 授權套用 |
| P6 refit-go；殘格點名 GO；E5 | 各一槍 |

---

## §3 其他模型驗証（本窗已跑到哪）

| 軌 | 本窗 | 下一步 |
|---|---|---|
| **V0** | **EXECUTED**＠08-18：截面 8 族 × 8 窗＝64／64；pack=True；方向臂活鎖仍＝價頂。`--track other --dry-plan` rc=0。`--date 2026-08-19` rc=3。0812 六族／VECM／TCN／NB／RL／SeqLSTM 登錄 n=0＝預期 | 當帳；不開訓 |
| **V1 H5** | **EXECUTED** walk 6 panel（新→舊）：**08-10（新實現）全族正 IC**；08-07／06／05／04 近 0／偏負；07-31 OOS＝no_model | **不升格**。候 08-11／12 的 H5 窗；或另 HIST 補未齊日 |
| **V1 H10** | **EXECUTED** 4 panel 全 no_model（07-31／06-30／05-31／04-30）。最早完整且 H10 已實現＝07-31，同日 stamp 被 `--oos` 排除；08-07 後僅 7 日＜11 | 候價蓋過使 08-07 實現 H10；或另 HIST＠更早 D 再 walk。勿 `--force-direction` |
| **V1 單日** | `--ic --oos`＠08-07＝僅 H5（n_after=7）；數字＝walk 同列。＠07-31＝H5+H10 全 no_model。＠08-18＝無已實現窗（略過，不是假綠） | 下一可 IC 的完整 8×8 日＝等 08-13 的 H5（尚差交易日） |
| **V2** | 殘格：VECM／TCN／NB／RL 登錄＝0 | `--track other --apply` rc=6；**點名**才 0a |
| **V3** | 08-07 已跑過；本窗重跑 OOS 不寫庫 | 新 asof 回饋另句；讓 B3 |
| **V4** | 0812 六族 EVIDENCE no-promote | **禁重掃** |
| **V5** | H20 dead、H60 thin、其餘 thin | 不修綠 |

### V1 H5 OOS 數字（dry-run；stamp < panel；n≈282–284）

| panel | n_after | 包 | 均值 IC | 最高族 | RankRidge |
|---|---|---|---|---|---|
| **2026-08-10** | 6 | 未齊 12／64 | **+0.150** | RankKNN +0.272 | +0.092 |
| 2026-08-07 | 7 | 64／64 | −0.031 | RankKNN +0.018 | −0.085 |
| 2026-08-06 | 8 | 0／64 | −0.116 | RankKNN +0.052 | −0.155 |
| 2026-08-05 | 9 | 0／64 | −0.071 | RankGBDT −0.020 | −0.092 |
| 2026-08-04 | 10 | 0／64 | −0.055 | RankKNN +0.066 | −0.080 |
| 2026-07-31 | 12 | 64／64 | no_model | — | — |

五 panel 有模型時，族均值：RankKNN **+0.069**；其餘皆負（RankRidge **−0.064**）。拿掉 08-10 後 KNN 均值只剩 **+0.019**，其餘更負。

**讀法**：08-10 是價頂 08-18 才剛夠 H5 的**第一個新 panel**，而且當日 8×8 **未齊**。單日全綠 ≠ 確立、≠ 報酬％、≠ 換冠軍。Standing 仍＝RankRidge H20+H60。

JSON：`/tmp/v1-oos-walk-h5.json`、`/tmp/v1-oos-walk-h10.json`、`/tmp/v1-asof-2026-08-07-oos.json`。

---

## §4 本窗改了哪些檔

| 檔 | 改什麼 |
|---|---|
| `src/augur/core/asof_ready.py` | `fake_b3_probe_date`（價頂+1，勿寫死）；`hist_next_action`／`format_hist_next_action` |
| `scripts/check_asof_ready.py` | `--fake-b3-date`；`--scan` 建議下一未齊；`--date` 印下一刀 |
| `scripts/run_asof_collect_train_verify.sh` | 自測假 B3 跟價頂次日；有 panel 缺 core 仍 `build_core`；08-12 dry 列入自測 |
| `scripts/verify_asof_families.py` | 註解：08-18＝價頂 V0，假 B3 用 `--fake-b3-date` |
| r16 §3 | LIVE 殼改指 hist 薄殼；08-12 不再寫成「不要」 |
| 本檔／r19 執行板 | 閉環問題板；M18 記帳 |
| `audits/HIST-ASOF-CODE-*-20260819.md` | GO／FIRED／EXECUTED |

未改 standing 20,60；未解 NF；未 promote；未寫 `prediction_values`；未 KH `--apply`；**未** HIST `--apply`＠08-12。

下一未齊 **08-10** 另貼 `HIST-ASOF-apply | date=2026-08-10 | track=all`；禁 `--force-direction`。08-11 已閉：`audits/HIST-ASOF-0811-EXECUTED-20260819.md`。08-12 已閉：`audits/HIST-ASOF-0812-EXECUTED-20260819.md`。
