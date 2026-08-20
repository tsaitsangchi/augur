---
title: augur 深化理解＋專案優化地基 r21
status: final
series: deep_understanding_and_opt
round: r21
date: 2026-08-20
viewpoint: 2026-08-20T10:11+08:00
layer: "[I]"
role: 現行理解地基；吸收 08-19 價進庫、路徑勝率墓碑、RIDGE-THEN-PB＠08-19；市場開工鎖改掛 r21 執行板
supersedes_as_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r20_20260819.md
inherits_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r20_20260819.md
  - archive/slim-t2/augur_deep_understanding_and_opt_plan_r19_20260819.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r21_20260820.md
exec_nav: reports/augur_opt_stepwise_all_problems_r21_20260820.md
exec_inherits: reports/augur_opt_stepwise_all_problems_r19_20260819.md
slim_plan: reports/augur_repo_slim_opt_plan_r20_20260819.md
ssot_index: reports/SSOT_READ_ORDER.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
path_opt_ops: reports/augur_path_timing_opt_ops_plan_r18_20260819.md
path_hit_lift: reports/augur_path_hit_lift_plan_r20_20260820.md
archive_tip: archive-20260820-r21-hist-wf-ridge-pb-close
self_reported: true
---

# augur 深化理解＋專案優化地基 r21（2026-08-20 10:11）

> **性質**：[I]；**不創** [N]；不解凍；不 sim `--apply`；不假 B3＠08-20；不 promote。  
> **一句**：r20 寫於「08-19 還沒有價」。現在價／特徵／核心宇宙已到 **08-19**，出門名單仍停在 **08-18**；日曆 08-20＝假 B3。路徑閘「加濾提高 30 日勝率」已在 P5 判死。本檔＝讀懂這筆帳之後的理解地基；後續開工跟 **r21 執行板**。  
> **覆蓋誠實**：非整庫逐檔複讀。倉內約 **151** 支 `src/augur` Python、**398** 支 `scripts/*.py`、**475** 份 `reports/*.md`、**1122** 份 `audits/`。精要仍＝讀序 ≤15。長細節回 r16／r19／r20／治權檔／PATH-OPT。  
> **疊用**：人話憲章 **r21** → 本檔理解 → 開工 **r21 執行板**（繼承 r19 硬門）→ 精化 slim r20 → 心跳 r16 → 路徑 PATH-OPT → 知識 KH 20260813。

**精要入口**：[`reports/SSOT_READ_ORDER.md`](SSOT_READ_ORDER.md)。

---

## 第一部｜深化理解

### §1 專案是什麼（產品真相）

**Augur**＝古羅馬「觀兆者」。「兆」只能是真實觀測，「預言」只能是帶不確定性的相對排序／機率。

> **只用真資料，誠實判斷台股誰比較強、知識庫裡到底寫了什麼；說得出依據，也說得出什麼時候該閉嘴。**

| 軸 | 白話 | 日常選刀 |
|---|---|---|
| **① 市場預測** | as-of → 特徵 → 宇宙 → 模型 → 日更名單／經濟尺 | **r21 執行板** |
| **② 知識素養＋顧問** | 可溯源文件；誠實檢索與作答 | **KH 20260813 板** |
| **③ 自反／演化** | 預註冊實驗、擂台、判準凍結 | 分屬兩板；**互不等待** |
| **①b 路徑／進出** | 長窗定方向、短窗管進出；dry-run | **PATH-OPT**；勝率河 **PATH-HIT-LIFT 已停** |

它是／它不是：相對排序＋可信度，**不是**保證獲利、點位神算、自動下單、可融券可成交、短線高勝率機器。  
成功定義＝**扣來回成本後的經濟價值**＋知識側**可核引文**；不是裸 IC、不是 64／64、不是「四閘全過之後 30 日勝率 51%」。

### §2 倉庫地圖（繼承 r20；只改仍變的數字）

| 區 | 作用 | 精化態度 |
|---|---|---|
| `constitution/` · `specs/` · `docs/` 三件套 · `CLAUDE.md` | [N]／靈魂 | **永不刪** |
| `src/augur/` | 17 pkg；預測 7pkg ⊥ 知識 | 少碰；禁為整理改邊界 |
| `scripts/` | 薄 CLI **398** py | 檔名入鏈=0 ≠ 未使用 |
| `reports/` | 計畫／理解 **[I]** **475** md | 精要＝讀序 |
| `audits/` | GO／EXECUTED **1122** | 禁默刪 |
| PostgreSQL `augur` | 唯一系統記錄 | 本檔不改庫 |
| GitHub | `https://github.com/tsaitsangchi/augur` · HEAD `3bd1a37` | 工作樹**髒**（T6／T7 mv、r21 文檔、路徑探針） |

**H 軌 SSOT**：`src/augur/core/closed_horizons.py` — `H_TRACK = (5, 10, 20, 40, 60, 90, 120, 240)`。八窗可訓 ≠ 八窗出門（standing 仍 H20+H60）。

### §3 S1→S5 × 硬邊界（2026-08-20 10:11）

| 階 | 一句 |
|---|---|
| **S1** | 價頂＝**2026-08-19**；08-20＝假 B3（rc=3） |
| **S2** | KH 分軌；`--check` 曾 FIRE S0=63；**未** `--apply` |
| **S3** | 核心／fv＠**08-19**（285 檔、37 欄、27 955 列）；P6 H20／H60 凍＠**08-14**（缺口拉大到 vs 08-19） |
| **S4** | 冠軍 **RankRidge**；出門庫 `prediction_values`／`prediction_probability` 仍＝**08-18** 僅 H20+H60 |
| **S5** | **emit tip＝2026-08-18**；08-19＝世界已算、**名單未出門** |
| **①b** | RIDGE-THEN-PB＠08-19：做多進場 **0／10**、做空 **1／10＝群光**（≠可融券）。PATH-HIT-LIFT **P5 墓碑** |

硬門：

```text
no-fake-B3@08-20 | no-promote | no-SIM-apply | NF-pause | standing=20,60
| 分數／p_beat／p_mkt／p_up／路徑％／勝率 ≠ 報酬％
| 觀察≠進場 | 條件≠可交易 | 兩檔≠宇宙 | 做空≠可融券
| PATH-HIT-LIFT 河閉 | 不放寬四閘 | 禁 OOS 最長持有當冠
| 禁 E5／倒 canonical 31／再送 E4 就緒 5
| 精化: 讀序≤15 | 禁默刪 [N]／heartbeat／GO | T5≠rm
```

### §4 LIVE 錨（2026-08-20 ≈10:11+08 · 親查）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-20 週四 10:11+08**（盤中） |
| PriceAdj TAIEX max | **2026-08-19** |
| 假 B3＠08-20 | **是** |
| `check_asof_ready --date 2026-08-19` | **ready**（core=Y） |
| fv max | **2026-08-19**（37 欄／27 955 列） |
| core＠08-19 | **285** |
| emit `prediction_values` max | **2026-08-18** RankRidge H20+H60 各 286 |
| 截面已齊 8×8（近） | 08-18、08-17、08-14、08-13、08-12、08-11、08-07、07-31 |
| 下一未齊 | **08-10 缺 52**（另句才補） |
| 方向臂 | 仍鎖＠**08-18**（HIST 不覆寫） |
| #14 | H20＝**dead**；其餘 thin |
| P6 freeze | H20／H60＠**08-14** vs 包／價 **08-19** |
| E4b 鐘 | WAIT k=0；next≈**2026-11-13** |
| RIDGE-THEN-PB＠08-19 | 多 0／10；空 1／10 群光；空≠可融券 |
| 全宇宙四閘＠08-19 | 做多 5（緯創／聯強／茂訊／飛捷／微星）；做空 5 |
| PATH-HIT-LIFT | **P5 停**：H30 四閘勝率 51.2%；加八窗 52.9%；分桶無同號 +3pp |
| T5 複審鐘 | 候選；最早≈**2026-11-17**；≠rm |
| 封存點 | tag `archive-20260820-r21-hist-wf-ridge-pb-close` · HEAD 回填 |

### §5 相對 r20 的理解增量（一夜＋今早）

r20 正文寫於 08-19 15:40，當時 **沒有** 08-19 價。不要再引用「08-19＝假 B3、價頂＝08-18」當現況。

| # | 增量 | 證據 |
|---|---|---|
| 1 | 價／fv／core 進到 **08-19** | `asof_ready` ready；fv 27 955 |
| 2 | 出門**未**跟到 08-19（pv／pp 仍 08-18） | `prediction_values` max |
| 3 | RIDGE-THEN-PB 重跑＠08-19：做多 0、做空群光 | `audits/RIDGE-THEN-PB-LS-0819.json` |
| 4 | 全宇宙四閘清單（H20 不擋）多 5／空 5 | 探針現算 |
| 5 | 2005–now 四閘 H30 勝率 ~51%；八窗 ~53% | PATH-HIT 回測 |
| 6 | PATH-HIT-LIFT P0 採納 → P1 診斷無同號桶 → **P5 墓碑** | `PATH-HIT-LIFT-P5-STOPPED-20260820.md` |
| 7 | 群光四閘過＝條件標，**不是**可融券 | 憲章鐵律 9 |

**本輪最重要的兩本帳**：

1. **世界已到 08-19、名單還在 08-18。** 這是「重訓／算特徵 ≠ 出門」的又一次實例。補帳須 **B3-go＠08-19**，不是把日曆 08-20 當 as-of。  
2. **路徑四閘不是短線優勢。** 加窗、加回撤甜區、加流動性，在 IS／OOS 雙尺下抬不起勝率。條件地圖可以留著當「現在齊不齊」；不要再當成可優化的交易勝率引擎。

### §6 知識／模型／路徑結論（仍真的）

- 冠軍仍 **RankRidge**；L2／RETRAIN-ALL 跟價重訓 ≠ 換冠。  
- standing 仍兩窗；勿默改八窗出門。  
- tip≠經濟綠：H20 dead／H60 thin。  
- 路徑：觀察≠進場；兩檔≠宇宙；做空≠可空；CHARGE-T5 宇宙扣成本 IS 負已量出；**PATH-HIT-LIFT 勝率河已死**。  
- 知識：`--check` ≠ `--apply`；stop-at-7；禁放寬 θ。

### §7 綜合債表（r21）

| ID | 債 | 狀態 |
|---|---|---|
| **R21-01** | 08-19 世界已算、emit 仍 08-18 | 🟡 候 `B3-go`＠08-19；禁假 B3＠08-20 |
| **R21-02** | 08-20 收盤尚未進庫 | 🟡 刀 B：WAIT PriceAdj≥08-20-close |
| **R21-03** | 路徑閘短線勝率 | 🟢 P5 墓碑；不准再開 P2／P3／P4 |
| R20-06 | 原「等 08-19 價」 | 🟢 價已到；轉成 R21-01 出門缺口 |
| R20-07 | HIST＠08-10 缺 52 | 🟡 另句；無新 GO 不跑 |
| R20-08 | P6 freeze 08-14 vs 現價 08-19 | 🟡 文件可先；訓另 GO |
| R20-09 | KH S0 FIRE 63 | 🟡 `--apply` 另句 |
| R20-11 | T5 複審鐘 | 🟡 最早≈2026-11-17；≠rm |
| R20-12／13 | T6／T7 搬檔 | 🟢 工作樹已 mv；**未**入這次 archive tag |
| R19 其餘 | 見 r19 板繼承列 | **不因本檔假關**；開工看 r21 板 |

已閉、勿再當開問題：R19-01 B3＠08-18；PATH-HIT-LIFT 勝率優化；RIDGE-THEN-PB 探針＠08-18／08-19（emit 仍另句）。

---

## 第二部｜優化計畫（選刀對齊）

> **後續優化執行 SSOT＝** `reports/augur_opt_stepwise_all_problems_r21_20260820.md`（繼承 r19 硬門與全板，刷新 LIVE）。  
> **精化執行 SSOT 仍＝** `reports/augur_repo_slim_opt_plan_r20_20260819.md`。

### §8 讀序

```text
人話憲章 r21
  → 精要讀序 SSOT_READ_ORDER
    → 本檔理解 r21
      → 問「現在做哪槍」→ r21 執行板
      → 問「怎麼瘦倉」→ slim r20（T5 鐘未到）
      → 問心跳 → r16
      → 問路徑 θ → PATH-OPT（HIT-LIFT 已停）
      → 問知識 → KH 20260813
```

### §9 最佳下一步（摘要）

此刻（週四盤中）**有** 08-19 價，**沒有** 08-20 價，**沒有** 08-19 出門。

| 角色 | 內容 |
|---|---|
| **全專案最佳下一步** | 等 Steward 點名：**08-19 真 B3 出門**（世界已在），或等 08-20 收盤後的整鏈。兩槍都另句。 |
| **路徑** | HIT-LIFT 停。名單／條件探針可另句 dry-run；不當交易系統優化 |
| **精化** | T5 未到；不默刪 |
| **KH** | 守 check；不 apply |
| **禁** | 假 B3＠08-20；P2／P3／P4；promote；sim-apply；無 GO 補 08-10 |

### §10 驗收

- [x] 覆蓋誠實（非整庫逐檔）  
- [x] LIVE：價 08-19／emit 08-18／假 B3＠08-20  
- [x] PATH-HIT-LIFT P5 寫進理解  
- [x] 優化計畫改掛 r21 執行板  
- [x] 人話憲章 r21  
- [x] 不創 [N]、不開訓、不假 B3、不代 commit  

```text
paste（採納為導航／理解地基，不是 B3-go）:
  DEEP-UNDERSTANDING-R21-OPT-PLAN-adopt | FZ/GATE-keep | dual-ssot | nav-only | no-fake-B3@08-20
```

開工鎖另貼 `OPT-R21-ALL`（見執行板 §1）。

*完。[I] · self-reported · r21。*
