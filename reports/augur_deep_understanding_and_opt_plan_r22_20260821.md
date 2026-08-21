---
title: augur 深化理解＋專案優化地基 r22
status: final
series: deep_understanding_and_opt
round: r22
date: 2026-08-21
viewpoint: 2026-08-21T14:10+08:00
layer: "[I]"
role: 現行理解地基；吸收 08-20 價進庫、八窗河、平行條件帳、FinMind P0、Sponsor 09-14；市場開工鎖改掛 r22 執行板
supersedes_as_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r21_20260820.md
inherits_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r21_20260820.md
  - reports/augur_deep_understanding_and_opt_plan_r20_20260819.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r22_20260821.md
exec_nav: reports/augur_opt_stepwise_all_problems_r22_20260821.md
exec_inherits: reports/augur_opt_stepwise_all_problems_r21_20260820.md
slim_plan: reports/augur_repo_slim_opt_plan_r20_20260819.md
ssot_index: reports/SSOT_READ_ORDER.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
path_opt_ops: reports/augur_path_timing_opt_ops_plan_r18_20260819.md
finmind_free: reports/augur_finmind_free_rankridge_plan_r21_20260821.md
hist_wf: reports/augur_hist_ridge_wf_plan_r21_20260820.md
archive_tip: archive-20260821-r21-w10-ma-finmind-p0
self_reported: true
---

# augur 深化理解＋專案優化地基 r22（2026-08-21 14:10）

> **性質**：[I]；**不創** [N]；不解凍；不 sim `--apply`；不假 B3＠**08-21**；不 promote；不改 L0。  
> **一句**：價／特徵／核心／八窗模型已到 **08-20**；日常出門庫仍停在 **08-18**（只 H20+H60）。日曆 08-21＝假 B3。路徑勝率河仍閉。本檔＝讀懂「世界超前兩日、名單沒寫」之後的理解地基；後續開工跟 **r22 執行板**。  
> **覆蓋誠實**：非整庫逐檔複讀。倉內約 **153** 支 `src/augur` Python、**405** 支 `scripts/*.py`、**482** 份 `reports/*.md`、**1189** 份 `audits/`。精要仍＝讀序 ≤15。長細節回 r16／r19／r21／治權檔／PATH-OPT／FinMind 計畫。  
> **疊用**：人話憲章 **r22** → 本檔理解 → 開工 **r22 執行板**（繼承 r21／r19 硬門）→ 精化 slim r20 → 心跳 r16 → 路徑 PATH-OPT → 知識 KH 20260813 → FinMind free 計畫（P0′ 未到）。

**精要入口**：[`reports/SSOT_READ_ORDER.md`](SSOT_READ_ORDER.md)。

---

## 第一部｜深化理解

### §1 專案是什麼（產品真相，未改）

**Augur**＝古羅馬「觀兆者」。「兆」只能是真實觀測，「預言」只能是帶不確定性的相對排序／機率。

> **只用真資料，誠實判斷台股誰比較強、知識庫裡到底寫了什麼；說得出依據，也說得出什麼時候該閉嘴。**

| 軸 | 白話 | 日常選刀 |
|---|---|---|
| **① 市場預測** | as-of → 特徵 → 宇宙 → 模型 → 日更名單／經濟尺 | **r22 執行板** |
| **② 知識素養＋顧問** | 可溯源文件；誠實檢索與作答 | **KH 20260813 板** |
| **③ 自反／演化** | 預註冊實驗、擂台、判準凍結 | 分屬兩板；**互不等待** |
| **①b 路徑／進出** | 長窗定方向、短窗管進出；條件帳 ≠ 下單 | **PATH-OPT**；勝率河 **PATH-HIT-LIFT 已停**；平行條件帳 W10／MA10／MA20／做空各表 |

它是／它不是：相對排序＋可信度，**不是**保證獲利、點位神算、自動下單、可融券可成交、短線高勝率機器。  
成功定義＝**扣來回成本後的經濟價值**＋知識側**可核引文**；不是裸 IC、不是 64／64、不是「四閘全過之後 30 日勝率 51%」、不是均線過齊。

### §2 倉庫地圖（相對 r21 只改仍變的數字）

| 區 | 作用 | 精化態度 |
|---|---|---|
| `constitution/` · `specs/` · `docs/` 三件套 · `CLAUDE.md` | [N]／靈魂 | **永不刪** |
| `src/augur/` | 預測 ⊥ 知識 | 少碰；禁為整理改邊界 |
| `scripts/` | 薄 CLI **405** py | 檔名入鏈=0 ≠ 未使用 |
| `reports/` | 計畫／理解 **[I]** **482** md | 精要＝讀序 |
| `audits/` | GO／EXECUTED **1189** | 禁默刪 |
| PostgreSQL `augur` | 唯一系統記錄 | 本檔不改庫 |
| GitHub | `https://github.com/tsaitsangchi/augur` · HEAD `237e13d` · tag `archive-20260821-r21-w10-ma-finmind-p0` | 封存已推 |

**H 軌 SSOT**：`src/augur/core/closed_horizons.py` — `H_TRACK = (5, 10, 20, 40, 60, 90, 120, 240)`。八窗可訓 ≠ 八窗出門（standing 仍 H20+H60）。

**取數與預測正交**：`train_ranker.py`／`predict_asof.py` **零 FinMind**。Token 降級只影響 L0 能不能把價／法人／借券日更進來。

### §3 S1→S5 × 硬邊界（2026-08-21 14:10）

| 階 | 一句 |
|---|---|
| **S1** | 價頂＝**2026-08-20**；08-21＝假 B3（rc=3） |
| **S2** | KH 分軌；`--check` 曾 FIRE；**未** `--apply`（繼承，本輪未重跑） |
| **S3** | fv／core＠**08-20**（37 欄、27 956 列、核心 **237**）；08-19 亦 ready（fv 27 955） |
| **S4** | 冠軍 **RankRidge**；**八窗模型登記已到 08-20**；出門庫 `prediction_values` 仍＝**08-18** 僅 H20+H60 各 286 |
| **S5** | **emit tip＝2026-08-18**；08-19 與 08-20＝世界已算、**名單未出門**（缺口從「一日」變成「兩日」） |
| **①b** | 條件帳平行產品已落地（v1／W10／MA10／MA20／做空）；PATH-HIT-LIFT **P5 墓碑仍閉** |
| **L0／API** | Sponsor 帳號頁到期 **2026-09-14**；P0 探針仍 0/6000、三張 by-date；**到期前不改 L0** |

硬門：

```text
no-fake-B3@08-21 | no-promote | no-SIM-apply | NF-pause | standing=20,60
| 分數／p_beat／p_mkt／p_up／路徑％／勝率／均線閘 ≠ 報酬％
| 觀察≠進場 | 條件≠可交易 | 兩檔≠宇宙 | 做空≠可融券
| PATH-HIT-LIFT 河閉 | 不放寬四閘 | 禁 OOS 最長持有當冠
| 禁 E5／倒 canonical 31／再送 E4 就緒 5
| 不改 L0 直到 P0′（錶≠6000）| 不第二支 HIST-WF --apply
| 平行條件帳不互覆寫
| 精化: 讀序≤15 | 禁默刪 [N]／heartbeat／GO | T5≠rm
```

### §4 LIVE 錨（2026-08-21 ≈14:10+08 · 親查）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-21 週五 14:10+08** |
| PriceAdj TAIEX max | **2026-08-20** |
| `check_asof_ready --date 2026-08-21` | **fake_b3 rc=3** |
| `check_asof_ready --date 2026-08-20` | **ready**；pack 8×8＋Daily3＋Mkt2＋DirStackM；at_tip |
| `check_asof_ready --date 2026-08-19` | **ready**；截面 8×8 |
| fv＠08-20 | 37 欄／**27 956** 列 |
| core＠08-20 | **237**（08-19 曾約 285；宇宙縮小＝真，不編造） |
| emit `prediction_values` max | **2026-08-18** RankRidge H20+H60 各 286 |
| RankRidge 八窗 `asof_snapshot` 近端 | **08-20、08-19、08-18…08-11** 皆 8H 齊 |
| RankRidge 模型列（asof≥2014） | **4337**（河在灌歷史日） |
| HIST-RIDGE-WF | 全交易日河仍跑；進度快照約 **528** 日完成、最後 **2016-03-03**、fail 0；鎖 `/tmp/augur_hist_ridge_wf.lock` |
| 條件帳 tip（buy/sell 表） | 做多 v1 max **08-14**（102 列）；做空 **08-20**（273）；W10 **0 列**；MA10 **08-20**（145）；MA20 **08-20**（662） |
| PATH-HIT-LIFT | **P5 停**（繼承） |
| FinMind | P0＠08-21：錶 **0/6000**；三張 by-date；到期 **2026-09-14** |
| E4b 鐘 | WAIT k=0；next≈**2026-11-13** |
| T5 複審鐘 | 最早≈**2026-11-17**；≠rm |
| 封存點 | tag `archive-20260821-r21-w10-ma-finmind-p0` · HEAD `237e13d` |

### §5 相對 r21 的理解增量（約 28 小時）

r21 正文寫於 08-20 10:11，當時價頂仍是 **08-19**、emit 08-18。不要再引用「08-20＝假 B3、價頂＝08-19」當現況。

| # | 增量 | 證據 |
|---|---|---|
| 1 | 價／fv／core／價頂 RETRAIN 包進到 **08-20** | `asof_ready` ready＠08-20 |
| 2 | 出門**仍** 08-18；缺口從一日變成 **兩日**（08-19 與 08-20 都沒寫 pv） | `prediction_values` max |
| 3 | 八窗 **模型**已登到 08-20（與出門庫不是同一件事） | `model_registry` 8H asof |
| 4 | 核心＠08-20＝**237**，小於 08-19 的 285 | `core_universe_asof` |
| 5 | HIST-RIDGE-WF 全交易日河在跑（約到 2016-03） | 進度 JSON；勿第二支 `--apply` |
| 6 | 平行做多 W10／MA10／MA20 與做空監看已入倉 | archive 20260821 |
| 7 | FinMind P0＝Sponsor 基線；到期 09-14；**不改 L0** | 探針 JSON＋帳號頁 |
| 8 | 單檔研究（2459）≠產品、≠可交易 | `reports/augur_2459_dunji_5y_finance_outlook_20260821.md` |

**本輪最重要的三本帳**：

1. **世界已到 08-20、名單還在 08-18。** 重訓／八窗模型齊 ≠ 站著兩窗已寫進 `prediction_values`。補帳須 **B3-go** 點名日期（08-19 與／或 08-20），**不准**把日曆 08-21 當 as-of。  
2. **路徑四閘不是短線優勢**（繼承 P5）。平行條件帳是「今天誰齊」的地圖，各表各鎖，**不互覆寫、不當下單**。  
3. **FinMind 改 free 是日曆題，不是今天改碼題。** 訓練程式不呼叫 API。到期前維持核 A。P0′＝錶不再是 6000。

### §6 知識／模型／路徑／取數結論（仍真的）

- 冠軍仍 **RankRidge**；L2／RETRAIN-ALL 跟價重訓 ≠ 換冠。  
- standing 仍兩窗；勿默改八窗出門。  
- tip≠經濟綠：H20 dead／H60 thin（繼承）。  
- 路徑：觀察≠進場；兩檔≠宇宙；做空≠可空；CHARGE-T5 扣成本 IS 負已量出；**PATH-HIT-LIFT 勝率河已死**。W10＝四閘＋路徑％帶；MA10／MA20＝均線堆疊＋價差帶。過齊 ≠ 可交易。  
- 知識：`--check` ≠ `--apply`；stop-at-7；禁放寬 θ。  
- 取數：預測 ⊥ API；`_quota_gate` 跟 `/user_info`；到期日 hardcode 進程式 **比跟錶更糟**。

### §7 綜合債表（r22）

| ID | 債 | 狀態 |
|---|---|---|
| **R22-01** | 08-19 **與** 08-20 世界已算、emit 仍 08-18 | 🟡 候 `B3-go` 點名 D；禁假 B3＠08-21 |
| **R22-02** | 08-21 收盤尚未進庫 | 🟡 刀 B：WAIT PriceAdj≥08-21-close |
| **R22-03** | HIST-RIDGE-WF 未灌到價頂 | 🟡 河在跑；禁第二 `--apply`；不聲稱已完 |
| **R22-04** | FinMind P0′（free 終局） | 🟡 等錶≠6000（約 09-14／15）；此前不改 L0 |
| **R22-05** | 核心＠08-20 縮到 237 | 🟡 記實；不 zero-fill；P3 宇宙閘另 GO |
| **R21-03** | 路徑閘短線勝率 | 🟢 P5 墓碑；不准再開 P2／P3／P4 |
| R21-01／02 | 原「08-19 出門／等 08-20 價」 | 價已到 08-20；出門缺口 **升級**為 R22-01 |
| R20-07 | HIST＠08-10 缺 52 | 🟡 另句；無新 GO 不跑 |
| R20-08 | P6 freeze 08-14 vs 現價 08-20 | 🟡 文件可先；訓另 GO |
| R20-09 | KH S0 FIRE | 🟡 `--apply` 另句 |
| R20-11 | T5 複審鐘 | 🟡 最早≈2026-11-17；≠rm |
| R19 其餘 | 見 r21／r19 板繼承列 | **不因本檔假關**；開工看 r22 板 |

已閉、勿再當開問題：R19-01 B3＠08-18；PATH-HIT-LIFT 勝率優化；08-20 **價**進庫（出門仍開）；FinMind P0 Sponsor 基線探針；W10／MA 產品入倉（≠可交易）。

---

## 第二部｜優化計畫（選刀對齊）

> **後續優化執行 SSOT＝** `reports/augur_opt_stepwise_all_problems_r22_20260821.md`（繼承 r21 全板硬門，刷新 LIVE）。  
> **精化執行 SSOT 仍＝** `reports/augur_repo_slim_opt_plan_r20_20260819.md`。  
> **FinMind 降級＝** `reports/augur_finmind_free_rankridge_plan_r21_20260821.md`（P1 另 GO）。

### §8 讀序

```text
人話憲章 r22
  → 精要讀序 SSOT_READ_ORDER
    → 本檔理解 r22
      → 問「現在做哪槍」→ r22 執行板
      → 問「怎麼瘦倉」→ slim r20（T5 鐘未到）
      → 問心跳 → r16
      → 問路徑 θ → PATH-OPT（HIT-LIFT 已停）
      → 問知識 → KH 20260813
      → 問 FinMind 掉級 → free 計畫（P0′ 未到不改 L0）
```

### §9 最佳下一步（摘要）

此刻（週五午後）**有** 08-20 價與世界，**沒有** 08-21 價，**沒有** 08-19／08-20 兩窗出門。

| 角色 | 內容 |
|---|---|
| **全專案最佳下一步** | 等 Steward 點名：**補出門＠08-19 與／或 08-20**（世界已在），或等 08-21 收盤後的整鏈。三槍都另句。 |
| **路徑** | HIT-LIFT 停。平行條件帳可監看、不當交易系統優化 |
| **八窗河** | 讓它跑；不要搶鎖 |
| **FinMind** | 到期前不改碼 |
| **精化** | T5 未到；不默刪 |
| **KH** | 守 check；不 apply |
| **禁** | 假 B3＠08-21；P2／P3／P4；promote；sim-apply；第二支 WF apply；改 L0 |

### §10 驗收

- [x] 覆蓋誠實（非整庫逐檔）  
- [x] LIVE：價 08-20／emit 08-18／假 B3＠08-21／核心 237  
- [x] 八窗河、平行條件帳、FinMind P0、Sponsor 09-14 寫進理解  
- [x] 優化計畫改掛 r22 執行板  
- [x] 人話憲章 r22  
- [x] 不創 [N]、不開訓、不假 B3、不代 commit  

```text
paste（採納為導航／理解地基，不是 B3-go）:
  DEEP-UNDERSTANDING-R22-OPT-PLAN-adopt | FZ/GATE-keep | dual-ssot | nav-only | no-fake-B3@08-21
```

開工鎖：Steward「後續依此進行」＝已採 `OPT-R22-ALL`（見執行板 §1／§1b）。**不是** B3-go。

*完。[I] · self-reported · r22。*
