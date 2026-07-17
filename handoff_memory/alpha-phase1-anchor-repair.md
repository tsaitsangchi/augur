---
name: alpha-phase1-anchor-repair
description: alpha Phase 1 錨修復鏈全程(2026-07-17):PriceAdj 修復→新錨 1.1321→judgestop 相對式條款(hugo 三裁);多發踩雷教訓
metadata: 
  node_type: memory
  type: project
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

**alpha 計畫 Phase 1 開工日(2026-07-17)全鏈**:P0 診斷包(8 項實算)→§0 驚雷=headline 錨 1.1972 不可再現(同配方 1.1321)→hugo 拍 A(修復重定錨)→修復→DDL(1-1)→重定錨→verdict 條款修復。**現行錨(KPI SSOT=N=32 保守口徑,hugo 拍板)**:`ridge_H60_LO/asof_incumbent` net Sharpe **1.1321**、超額 +0.372、HAC-t 6.70、DSR 47.9%、deflated −0.021;pit_broad 0.9896/DSR 32.7%;`revalidation_baseline` 已 re-freeze(07-17)、state=`deploying_unestablished`。

> ⚠️ **2026-07-17 本機 dry-run 對帳(重要,深讀 agent 未跑此對帳)**:本機 DB 為 07-16 快照(不含 07-17 重定錨,DB 不隨 git),`revalidate_baseline.py --dry-run` 實算=net **1.1302**/超額 +0.3772/HAC-t 6.945/DSR **34.3%**/deflated **−0.155**;pit_broad 0.9890/DSR 20.9%。
> - **net 1.1302 vs 簽核 1.1321 差 0.0019**:唯一成因＝`TaiwanStockPriceAdj` live sync 逐日改寫史(07-16 快照 vs 07-17 快照);錨不可再現的病**沒好、只變小**(1.1972→1.1321 Δ0.065 → 1.1321→1.1302 Δ0.0019),`repair_priceadj_basis.py:9` 自承「live 維運每逢除息必復發、過渡工具」。
> - **DSR「47.9%」查無來源(材料性可疑)**:全 repo 156 報告搜 47.9/0.479 零命中;P0 報告 §5 實跑=**34.5% @ N=32**(`deflate_headline_verdict.py`),本機 dry-run 34.3% 與之吻合(差 0.002)。且本則同時寫「N 維持 33、headline 1.1302 不動」(:23)——**1.1321 與 1.1302 兩數並存於同一則**。DSR 是帳本狀態相依量(N=16→75.8%/N=32→40.9%),引用**必帶 `@N=,as_of=` 戳記**(P0 紀律),此處 47.9% 無戳記＝疑誤植。
> - **待新 dump 定案**:hugo 決定從簽核那台機器搬正確 dump 覆蓋(唯一能兩機一致之路)。驗收基準應為 1.1321 / DSR≈34.5%@N=32(**非 47.9%**) / deflated≈−0.09。以簽核值 1.1321 為錨,本機 1.1302 為快照差異、不另立錨。

**修復定性**:PriceAdj「216 檔受損」大幅高估——真拼接損傷僅 41 檔(重抓修復);175 檔=**合法除息跳點被 `FACTOR_TOL` 誤標**(1109 五筆跳點×除息日精確對齊實證;repair 掃描工具未排除除息日=backlog)。錨降 0.065=修復讓地板變真、非變差。

**judgestop 條款修訂(hugo (i) 2026-07-17)**:`deflated_floor_zero`(絕對零線)在 N=32 口徑下 baseline 自身=−0.021→**恆觸發失鑑別力**(重定 baseline 治不了絕對條款!)。修=新 frozen 列 `deflated_decay_margin=0.10`(U6 簽核留痕)+`revalidate_verdict.evaluate` 改相對式(`da < bda−margin`;margin 未凍時 fallback 舊零線);舊列 note 退役史料。**judgestop 快照連動**:新增 frozen B_decay 列→舊 gate(admission/unfreeze)criteria 快照≠現值——皆終態不再 evaluate、無實害,--check 顯分叉屬預期。

**踩雷教訓(一天四型)**:
1. **verdict 重跑墊 streak**:revalidate_verdict 無參數=算+寫入(非唯讀!),每跑一次 INSERT 一列;suspected 狀態下重跑=streak 累積,k=2 下差一步自動判停。**探測 verdict 一律 --dry-run**。
2. **revalidate_baseline 無參數=直接凍結**(非印矩陣)——「無參數 graceful=唯讀」慣例(#29a)並非每支舊 script 都守;**不確定的工具先 Read 檔頭再跑**。
3. **pipe 截斷四連發**:`| tail`/`| head` 吃 exit code+截輸出(revalidate 崩點被掩、deflate N=32 段被截)——背景/驗證命令**不包 pipe**。
4. **pkill/pgrep -f 自匹配自殺 ×2**(exit 144):kill 前先 pgrep 列 PID 檢查,或用不含關鍵字的模式。
5. **DDL 遷移消費端要掃「寫入端」**:trial_ledger UNIQUE 擴 8 欄後 `migrate_trial_ledger_ddl.BACKFILL` 的 ON CONFLICT(7 欄)炸——selftest 只鎖了讀取端 N 口徑;修+回歸鎖(arbiter 8 欄斷言)。

**Phase 1 全落定(2026-07-17)**:1-3 P1 buffer 判死(雙宇宙判準攔 asof 假象;組合構建候選 pit 非可選項)、1-4 P4 vol-target 無靶不啟用(Cederburg 2020 反證台股重現;能力清償)、**1-6~1-9 D2+D3 7 候選全滅無一抵經濟終關**(opus-4-8 resume;Fable 額度上限=模型級、切 opus 續)——預診放棄 3(size/vol 代理)、死 IC 3(x_foreign_streak_60d=iid −2.22 越線 HAC −1.78 崩=G8 教科書)、死增量 1(x_limitup_reversal_5d Δ−0.049 帶稀疏宇宙混淆→S1 拍板)。**N 維持 33、headline 1.1302 不動、生產表全淨**——「大部分候選會死=功能非缺陷」教科書輪。9 拍板點待 hugo(重點 C2=DSR 重算涵蓋修 N=32/33 陳舊斷鏈)。報告=reports/alpha_phase1_tail_verdict_20260717.md。1-8/1-9=純盤點草案(零 API 零 code)。
**Phase 1 早段**:1-0 P0 ✅、1-1 recipe DDL ✅(32 列 plain/8 欄 UNIQUE)、1-5 全鏈刷新 ✅(ledger 140+64 dsr 列/baseline re-freeze/verdict 回穩/econ_verdict thin 維持未變向/fail-closed triggers 全在)。**次=1-2 P2 turnover 權重修正**。dump=C:\database\augur_pgdump_20260718_Fd.tar(修復後乾淨快照)。見 [[arena-g1g5-admission-plan]]、[[augur-validation-master-plan]]。
