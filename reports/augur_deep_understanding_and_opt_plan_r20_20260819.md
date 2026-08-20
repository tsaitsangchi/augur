---
title: augur 深化理解＋專案優化地基（倉精化）r20
status: final
series: deep_understanding_and_opt
round: r20
date: 2026-08-19
viewpoint: 2026-08-19T15:40+08:00
layer: "[I]"
role: 現行理解地基；本輪優化主題＝把倉合併為精要、逐步刪重複／未用；市場開工鎖仍＝r19
supersedes_as_understanding:
  - archive/slim-t2/augur_deep_understanding_and_opt_plan_r19_20260819.md
inherits_understanding:
  - archive/slim-t2/augur_deep_understanding_and_opt_plan_r19_20260819.md
  - archive/slim-t2/augur_deep_understanding_and_opt_plan_r17_20260817.md
  - archive/slim-t2/augur_deep_understanding_and_opt_plan_r15_20260813.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r19_20260819.md
exec_nav: reports/augur_opt_stepwise_all_problems_r19_20260819.md
slim_plan: reports/augur_repo_slim_opt_plan_r20_20260819.md
ssot_index: reports/SSOT_READ_ORDER.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
path_opt_ops: reports/augur_path_timing_opt_ops_plan_r18_20260819.md
archive_tip: archive-20260819-b3-hist-slim-r20
prior_archive: archive-20260819-path-opt-charge-t5-ridge
self_reported: true
---

# augur 深化理解＋專案優化地基 r20（2026-08-19 15:40）

> **LIVE 過期（2026-08-20）**：本檔寫於「08-19 還沒有價」。現行理解改跟 [`reports/augur_deep_understanding_and_opt_plan_r21_20260820.md`](augur_deep_understanding_and_opt_plan_r21_20260820.md)。精化計畫 slim r20 **仍有效**（T5 鐘未到）。

> **性質**：[I]；**不創** [N]；不解凍；不 sim `--apply`；不假 B3＠08-19；不 promote。  
> **一句**：在 r19 上吸收午後增量（B3＠08-18 已出門、HIST＠08-12／08-11 已齊、RIDGE-THEN-PB 多空 0／10），並把 Steward 要的「讀懂全倉 → 合併精要 → 逐步刪重複」收成**可執行的精化軌**；**不**把市場開工鎖從 r19 默換成 r20。  
> **疊用**：人話憲章 r19 → **本檔理解** → 市場／知識／路徑仍跟 **r19 執行板** → 精化跟 **slim r20** → 準則仍＝r16 心跳＋PATH-OPT＋KH 板。  
> **覆蓋誠實**：非整庫逐檔複讀（不可能也不誠實）。倉內約 **151** 支 `src/augur` Python、**17** 個領域 package、**414** 支 `scripts/`、**524** 份 `reports/*.md`、**1106** 份 `audits/`、**59** 份 `constitution/`、**14** 份 `specs/`、**30** 份 `tests/`、**18** 份 `docs/`、git 追蹤 `ops/` **67**（另有 gitignore 的 gpu-test-venv **1010** 檔，勿算進「專案源碼」）。本輪＝**結構地圖＋LIVE 親查＋入鏈圖＋精化選刀**；長細節仍回 r15／r16／r19／治權檔。

**精要入口**：[`reports/SSOT_READ_ORDER.md`](SSOT_READ_ORDER.md)（≤15 條現行讀序）。

---

## 第一部｜深化理解

### §1 專案是什麼（產品真相 · 繼承 r19）

**Augur**＝古羅馬「觀兆者」；「兆」只能是**真實觀測**，「預言」只能是**帶不確定性的相對排序／機率**。

> **只用真資料，誠實判斷台股誰比較強、知識庫裡到底寫了什麼；說得出依據，也說得出什麼時候該閉嘴。**

三軸＋一條路徑旁軌不變：

| 軸 | 白話 | 日常選刀 |
|---|---|---|
| **① 市場預測** | as-of → 特徵 → 宇宙 → 模型 → 日更名單／經濟尺 | **r19 執行板** |
| **② 知識素養＋顧問** | 可溯源文件；誠實檢索與作答 | **KH 20260813 板** |
| **③ 自反／演化** | 預註冊實驗、擂台、判準凍結 | 分屬兩板；**互不等待** |
| **①b 路徑／進出** | 長窗定方向、短窗管進出；dry-run | **PATH-OPT 手冊**（從屬 r19 開工順序） |

它是／它不是：相對排序＋可信度，**不是**保證獲利、點位神算、自動下單、可融券可成交。  
成功定義＝**扣來回成本後的經濟價值**＋知識側**可核引文**；不是裸 IC、不是 64／64、不是兩檔格子好看。

### §2 倉庫地圖（讀檔導航 · 精化視角）

| 區 | 作用 | 精化態度 |
|---|---|---|
| `constitution/` · `specs/` | Layer 0–7 **[N]** | **永不刪**；不是膨脹 |
| `docs/` | 靈魂／原則／領域大憲章 | **永不刪**；版號以 `ls docs/` 現查 |
| `src/augur/` | **17 pkg**；預測 7pkg ⊥ 知識 | 精化＝少碰；禁為「整理」改 import 邊界 |
| `scripts/` | 薄 CLI **414** | T0 **不刪**；檔名入鏈=0 ≠ 未使用 |
| `reports/` | 計畫／理解 **[I]** | **精要＝讀序**；舊輪留繼承鏈 |
| `audits/` | GO／EXECUTED 紙本 | **禁默刪**；重複 JSON 可 T1 去別名 |
| `models_artifacts/` | joblib；**不進 git** | 不管 |
| PostgreSQL `augur` | 唯一系統記錄 | 不管本軌 |
| `ops/` | 機／runbook；git **67** | gpu-test-venv gitignore，勿當源碼 |
| `handoff_memory/` | 跨對話碎片 **82** | 不拼進精要；不刪（Agent 檢索） |
| `archive/` | 已退場腳本＋ **slim-t0** | 只進有證據的搬遷 |
| GitHub | `https://github.com/tsaitsangchi/augur` · HEAD `6341cab` | 工作樹**未乾淨**（r19 午後未入倉） |

**預測 7pkg（禁吸知識）**：`ingestion` · `features` · `universe` · `models` · `evaluation` · `catalog` · `audit`。  
**其餘**：`core` · `knowledge` · `philosophy` · `advisor` · `llm` · `identity` · `arena` · `evolution` · `deliberation` · `execution`。

**H 軌 SSOT**：`src/augur/core/closed_horizons.py` — `H_TRACK = (5, 10, 20, 40, 60, 90, 120, 240)`。八窗可訓 ≠ 八窗出門（standing 仍 H20+H60）。

### §3 S1→S5 × 硬邊界（運轉真相 · 08-19 15:40）

| 階 | 08-19 15:40 一句 |
|---|---|
| **S1** | 價頂＝**2026-08-18**；08-19＝假 B3（探針日＝價頂次一日曆日） |
| **S2** | KH 分軌；`--check` 曾 FIRE S0=63；**未** `--apply` |
| **S3** | 核心仍走 08-18 包；P6 H20／H60 凍＠**08-14**（缺口仍在） |
| **S4** | 冠軍 **RankRidge**；8×8 COMPLETE＠08-18／17／14／13／12／**11**／07／07-31；方向臂仍＠**08-18**（HIST 不覆寫） |
| **S5** | **emit tip＝2026-08-18** 僅 H20＋H60；H20＝dead、H60＝thin |
| **①b** | RIDGE-THEN-PB-v1 多空＠08-18：**可當進場 0／10 ＋ 0／10** |

硬邊界不變（市場／知識／路徑／分軌四列，見 r19 §3）。本輪多一列：

```text
精化: 精要＝讀序≤15 | 禁默刪 [N]／heartbeat／GO 紙本
    | 檔名入鏈=0 ≠ 未使用 | T0 只動 byte-identical 無引用
    | r20 理解 ≠ 取代 r19 開工鎖
```

### §4 LIVE 錨（2026-08-19 ≈15:40+08 · 親查）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-19 週三 15:40+08** |
| `TaiwanStockPriceAdj` max（TAIEX） | **2026-08-18**（`check_asof_ready --latest-date`） |
| 假 B3＠08-19 | **是**（探針日＝價頂+1 曆日；禁當 as-of） |
| 截面已齊 8×8（近） | 08-18、08-17、08-14、08-13、08-12、08-11、08-07、07-31 |
| 下一未齊 | **08-10 缺 52**（core=Y，H5 已實現）；其後 08-06／05／04（0／64） |
| 方向臂 | 仍鎖＠**08-18**（Daily3+Mkt2+DirStackM）；HIST apply **未**覆寫 |
| 出門 | **2026-08-18** H20+H60（刀 A 已閉） |
| #14 | H20＝**dead**；其餘 thin（H60 含） |
| P6 freeze | H20／H60 仍＠**08-14** vs 包＠08-18 |
| E4b 鐘 | WAIT k=0；next≈**2026-11-13** |
| RIDGE-THEN-PB-v1＠08-18 | 多 0／10、空 0／10；空≠可融券 |
| V0／V1＠08-18 | 已閉；`--track other --apply`＝rc=6；**no-promote** |
| 封存點 | tag `archive-20260819-b3-hist-slim-r20` · HEAD `63752bb` |
| git | `main` → `origin` `https://github.com/tsaitsangchi/augur` |
| crontab | 17 條；**無** cron B3；含 RETRAIN-ALL 21:40／09:20 |

### §5 相對 r19 的理解增量（同日午後）

r19 正文寫於 ≈14:05，當時 R19-01（B3＠08-18）與 R19-27（HIST 08-12）仍開。**不要再引用那兩條當現況。**

| # | 增量 | 證據 |
|---|---|---|
| 1 | B3 出門＠**08-18** H20+H60 EXECUTED | `audits/OPS-B3-20260818-EXECUTED-20260819.md` |
| 2 | HIST-ASOF **code**（`asof_ready.fake_b3_probe_date`；缺 core 仍 `build_core`） | `HIST-ASOF-CODE-EXECUTED` |
| 3 | HIST apply＠**08-12** 64／64；無 `--ic`（n_after=4＜6） | `HIST-ASOF-0812-EXECUTED` |
| 4 | HIST apply＠**08-11** 64／64；無 `--ic`（n_after=5＜6） | `HIST-ASOF-0811-EXECUTED` |
| 5 | S4 other V0＝64／64；V1 H5 六片 KNN 均值弱、Ridge 負；**no-promote** | `S1S5-OTHER-VERIFY-0818-EXECUTED` |
| 6 | RIDGE-THEN-PB 改多空產品；進場門＝L-A…D／S-A…D 全過；結果 0／10＋0／10 | `RIDGE-THEN-PB-LS-TIP-EXECUTED`＋JSON |
| 7 | 精要讀序＋slim 計畫；T0 搬走一份無引用的 byte-identical CSV | 本檔＋`archive/slim-t0/` |

**本輪最重要的兩本帳**（在 r19 兩本之外）：

1. **「讀完全倉」做不到、也不該假裝做到。** 精化的誠實動作＝標出 **≤15 條現行入口**，讓 524 份 reports 退成繼承鏈，而不是再開一篇與 r19 等長的複述。  
2. **檔名沒被別的檔提到 ≠ 可以刪。** 入鏈圖在排除 reports／audits 後有 169 支「零命中」，加上紙本後只剩 **16** 支；其中 `migrate_horizon_{5,10,240}` 是活窗 DDL，**列零命中仍是 KEEP**。

### §6 知識／模型／路徑結論（繼承；只寫仍真的）

- 冠軍仍 **RankRidge**；L2／RETRAIN-ALL 跟價重訓 ≠ 換冠。  
- 訓到價頂 **已**出門到價頂（08-18）；下一缺口是**下一真收盤**，不是再補 08-18。  
- standing 仍兩窗；勿默改八窗出門。  
- tip≠經濟綠：H20 dead／H60 thin。  
- 路徑：觀察≠進場；兩檔≠宇宙；做空≠可空；CHARGE-T5 宇宙扣成本 IS 負已量出。  
- 知識：`--check` ≠ `--apply`；stop-at-7；禁放寬 θ；有引文禁假「無此內容」。

### §7 綜合債表（r20）

| ID | 債 | 狀態 |
|---|---|---|
| **R20-01** | 倉膨脹：reports 524 md／audits 1106／scripts 414；讀者無單一精要 | 🟢 讀序＋T0–T4 已做；audits 紙本故意留 |
| **R20-02** | scripts 冗餘（原 R19-09／M14） | 🟢 T1 已封存五支；其餘不默刪 |
| R20-03 | 三份 identity mismatch CSV 兩份重複 | 🟡 T0 已搬 **20260718**；留 0801＋0722_gb10 |
| R20-04 | RIDGE JSON 兩檔 byte-identical、審計各引一名 | 🟢 T1：0818＝指針；LS＝內容；EXECUTED 正文路徑未改 |
| R20-05 | r19 LIVE 段（14:05）過期 | 🟢 以本檔 §4 為準 |
| R20-06 | 下一真收盤心跳＠**≥08-19 收盤** | 🟡 WAIT · 禁假跑（原 R19-02） |
| R20-07 | HIST＠**08-10** 缺 52 | 🟡 另句 `HIST-ASOF-apply`；無新 GO 不跑 |
| R20-08 | P6 freeze 08-14 vs 包 08-18 | 🟡 文件可先；訓另 GO |
| R20-09 | KH S0 FIRE 63 | 🟡 `--apply` 另句 |
| R20-10 | 工作樹 r19／r20 未入倉 | 🟢 已封存 `archive-20260819-b3-hist-slim-r20` |
| **R20-11** | 封存檔要不要到期刪 | 🟡 T5＝90 天**複審鐘**候選（最早≈**2026-11-17**；產清單預設 KEEP；**≠rm**） |
| **R20-12** | PME 0724 local-backup leftover | 🟢 T6：`git mv` → `archive/slim-t6/`；正式 0724 留 reports/ |
| **R20-13** | sim 專章 draft leftover | 🟢 T7：`git mv` → `archive/slim-t7/`；final 留 reports/ |
| R19-03…26 其餘 | 見 r19 債表 | **不因本檔假關**；開工仍看 r19 板 |

已閉、勿再當開問題：R19-01 B3＠08-18；R19-27 之 08-12／08-11（下一未齊改掛 R20-07）。

---

## 第二部｜優化計畫（選刀對齊）

> **市場／知識／路徑後續優化執行 SSOT 仍＝** `reports/augur_opt_stepwise_all_problems_r19_20260819.md`。  
> **本輪新增執行 SSOT（只管精化）＝** `reports/augur_repo_slim_opt_plan_r20_20260819.md`。

### §8 讀序與操作協議

```text
人話憲章 r19
  → 精要讀序 SSOT_READ_ORDER
    → 本檔理解 r20
      → 問「現在市場做哪槍」→ r19 執行板
      → 問「怎麼瘦倉」→ slim r20（T0–T4＋T6＋T7 已做；T5＝90 天複審鐘候選）
      → 問心跳細節 → r16
      → 問路徑 → PATH-OPT
      → 問知識 → KH 20260813
```

1. 缺 GO → 停。精化 T1 刪腳本／搬 superseded 長文 **必須另句點名**。  
2. 勿重掃假綠；勿把精化當藉口改 standing／promote／假 B3。  
3. 重大市場收斂 → 刷新 r19 板；不必每次重寫理解長文。精化收斂 → 刷新 slim 計畫 T#。

### §9 最佳下一步（摘要）

此刻（週三午後）**沒有** 08-19 價。

| 角色 | 內容 |
|---|---|
| **市場主軸** | 刀 B：WAIT `PriceAdj≥2026-08-19` 收盤進庫。**禁**假 B3＠08-19 |
| **精化主軸（本檔）** | T0–T4＋T6＋**T7 已做**。T5＝90 天複審鐘**候選**（未開火；≠rm） |
| **路徑** | 各未閉槍仍另句；RIDGE-THEN-PB ≠ 可交易 |
| **KH** | 守 `--check`；不開 K9／放寬 θ／本鎖 drain S0 |
| **禁** | 假 B3；sim-apply；promote；`--track other --apply`；無 GO 補 08-10；默刪 scripts／audits |

```text
market: no-fake-B3@08-19 | knife-B=WAIT | standing=20,60 | no-promote
slim:   T0=done | T1=done | T2=done | T3=done | T4=done | T5=review-clock-candidate | T6=done | T7=done | never-delete-[N]-heartbeat-GO | no-calendar-ttl-delete
kh:     check≠apply | E-keep | stop-at-7
path:   0/10+0/10 ≠ 進場
```

### §10 驗收

- [x] 覆蓋誠實（非整庫逐檔）  
- [x] LIVE 刷新到 B3＠08-18／HIST 08-11／12／下一未齊 08-10／RIDGE-THEN-PB 多空  
- [x] 精要＝讀序，不是拼接 1800 份 md  
- [x] 優化計畫指向 slim r20；**不**默奪 r19 開工鎖  
- [x] T5 寫成 90 天複審鐘候選（≠開火、≠rm）  
- [x] T6 搬 1 份 PME local-backup（正式 0724 未搬）  
- [x] T7 搬 1 份 sim 專章草案（final 未搬）  
- [x] 不創 [N]、不開訓、不假 B3、不代 commit  

*完。[I] · self-reported · r20。*
