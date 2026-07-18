---
name: augur-oracle-v2-plan
description: 方向軸 v2 復活計畫已寫好待拍板(K=4 門;D1 hiIV 撤門;先凍後跑;v1 證據保全)
metadata: 
  node_type: memory
  type: project
  originSessionId: b066145f-886c-4e08-a8ce-952b36c108ab
---

2026-07-11 應用戶指示(ultracode 多視角)產出 `reports/augur_oracle_direction_v2_revival_plan_20260711.md`(對抗審查後定稿、**待拍板點①**)。要點:

- **K=4 門**:dgate_D_5_v2(主;purged isotonic+籌碼五族;family 預鎖 DailyGBDT_cal)、dgate_H_40_v2(主;月頻 panel 方案 A/B 窗待親核)、dgate_H_20_v2/H_82_v2(次;**α=0.01 綁定+pass=provisional**)。
- **撤門**:D1 高 IV 條件門——對抗審查代跑 PIT trailing 口徑 p=0.108 前提不成立+post-hoc regime selection+條件輸出形不在憲章閉集。
- **v1 關鍵解剖**(v2 依據):H 軌評測誤用千里眼基線(修正後仍全敗、H40 變近失 p≈0.105);D5 p=0.038 含 best-of-2 未校正;5 個 lag-1 市場特徵 0 列被消費(未試非死);D 軌零 purge;estimand 未釘死;trainer DELETE/upsert 會毀 v1 證據(v2 一律新 model_id+scoped DELETE+P0 備份)。
- **階段**:P0 修繕保全→P1 特徵→**P2 預註冊+TTY 親核(先凍後跑)**→P3 訓練→P4 裁決→P5 econ→P6 呈現(唯 pass;含 produce_direction_probability 生產腳本+advisor 短路句改 DB 驅動)。
- **敗退寫死**:全家族死→二次證偽結案、**不開 v3**(入 criteria 凍結)至解凍後新資料。
- 靈魂 v1.6/憲章 v1.42 已含預言機軸,v2 零修憲;「每日預測股價」永久除外不變。

相關:[[augur-oracle-direction-verdict]]、[[augur-oracle-pivot]]。

**2026-07-11 深夜終局:v2 全家族判死(二次證偽)**。四門全 evaluated_fail/never_shown:D5_v2 hit p=0.072(修 purge+校準後自 v1 的 0.038 退化=灌水懷疑實證)、Brier 四門全敗、ECE 全過(校準誠實、無訊號);econ 標示軸 H82 名目 alive(Sharpe 差 0.027 雜訊級)。fail_path 執行:**方向軸凍結至解凍+新資料、不開 v3**(criteria 凍結句)。結案報告=reports/augur_oracle_direction_v2_verdict_20260711.md(待 hugo 親簽=拍板點③,含 no-v3 入憲與否)。advisor 誠實句已更新「十道關卡」並重啟驗證。commits:2430b15(P0-P2)+b3b709e(判決)⚠**2026-07-17 實查:兩者皆已在 origin/main、非「未 push」**。

**Live 擂台計畫(2026-07-11 深夜)**:reports/augur_direction_live_arena_plan_20260711.md(對抗審查 22 項/6 blocker 全採納定稿、**待拍板 A-1/A-2**)。核心:真未來擂台(自家滾動 refit+timesfm-2.5-200m/chronos 本地推論+基線不立門)、K 枚舉 Bonferroni 綁定、A2 預註冊+evaluate 自動觸發(先凍後跑)、反回填 trigger。**審查改寫承諾**:檢定力親算=確認 +1.4pp 需 12-29 年→gate 誠實定位=偵測「可交易級 MDE(5-10pp)」、禁「蓋棺」措辭。硬前置:A-2 解凍修憲(完整清單:原則精華 L74/76/77+憲章 L132/L200+CLAUDE L26)+**FinMind 續訂(已過期降 Free tier、fetch 400 實測)**+PriceAdj 拼接損傷 15 檔修復。檔案未 commit(待用戶授權)。
