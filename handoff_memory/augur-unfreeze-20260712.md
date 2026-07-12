---
name: augur-unfreeze-20260712
description: "FREEZE 已解除(2026-07-12 hugo 親核):live 增量維運、as-of'=滾動;no-v3 已入憲;殘餘前置=FinMind 續訂+E 債裁定"
metadata:
  type: project
---

**2026-07-12 hugo 親核拍板(聊天指令)四項**:①v2 結案報告親簽+**no-v3 入憲**(憲章 v1.43.0);②A5 D3/D4 措辭修正案(七片全 ✅);③擂台 A-1 核可(三小裁定照計畫);④**解凍**——FREEZE 子條解除(原則精華 v1.9.0),轉 live 增量維運、as-of'=滾動。修憲 commit=7d337ec(>unfreeze gate approved_at,G1(b) 滿足);CLAUDE v1.25/README/HANDOFF 全鏈對齊。

**解凍 GATE evaluate 前仍缺(依序)**:①**FinMind sponsor 續訂**(過期降 Free、fetch 400 實測;用戶付費動作)→②E 債裁定(E1 越線段重抓案、E2/E5/E7 除名——`--strict` 剩此 4 筆)→③分段 sync+build→④`preregister_unfreeze_gate.py --evaluate unfreeze_06dcb178267d --asof <日>`→⑤arena gate 預註冊(hugo TTY)→開賽。人裁佇列 6 單 red-line 演練單指令已備(拍板包 ①)。

擂台 A0 全落地:4 表 3 trigger、8 候選、chronos 冒煙過(VRAM 900MiB/4096);timesfm 權重下載未完(慢網,重試即可)。相關:[[augur-oracle-v2-plan]]。

**07-12 日間補記**:IP sustained ban 實錘(msg=ip banned;#24 已知現象、一夜 4,000+ requests 觸發)→ 自癒 runner(nohup+flock、30 分/發探測、癒合即自動對帳,log=~/audit_retry.log);settle factor 檢核鑑識定案=拼接與減資統計不可分→逐標的 unsettleable 揭露(批次熔斷唯時間旅行);L2 首自動日 15 confirmed/4 escalated(+5 人裁);特徵四鏈+TRI 至 07-09;首個凍結後 panel 2026-06-30;futility policy 建議值 min_clusters=60/z=1.645 待 A2 併核。

**A2 人閘全清(07-12 午)**:arena 六門 hugo TTY 全數 approved(criteria trigger 鎖死);futility policy 凍結(60/1.645);排程已核(cron 於開賽日掛、首日手動陪跑)。唯一待決事件=IP 癒合→對帳→E1→strict→unfreeze evaluate;pass 即開賽,fail 即原子回退。
