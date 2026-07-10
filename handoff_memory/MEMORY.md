# Memory Index

- [Git 身分在 .env](git_identity_in_env.md) — commit 遇身分未設時查 .env 的 `git config --global` 指令,不問用戶、不自設
- [augur 專案地圖](augur-project-map.md) — 治權 SSOT(憲章v1.20/CLAUDE v1.16)+ 程式地圖(含知識/哲學/顧問層)+ 市場層飽和里程碑 + 知識層 W5 前沿 + 兩機/dump/token 約束
- [知識三部曲+哲學顧問層](augur-knowledge-philosophy.md) — 八層金字塔、命門7條、隔離不變式、T/W 工具鏈、review_flag 三態、e5-small 嵌入口徑、版權雙軌、未實作債
- [augur 特徵值全貌](augur-feature-values.md) — 產生器地圖 + feature_values 35 特徵(八二/康波 8 存活+gross_margin_pctile 翻案) + headline + 已修盲點與殘留
- [三鏡頭研究報告](augur-three-lens-research.md) — 第一性/八二/康波思想根源精萃 + 各鏡頭關鍵教訓與批判(α≈1.16 才給80/20、康波實證最弱故數字最不可回流、Bessembinder 4%股造全部財富)
- [特徵發現工具鏈](augur-feature-toolkit.md) — 標準流程(探索→候選→四道漏斗→經濟驗證→穩健終關)工具用法 + 判準魔數 + 鐵律教訓(覆蓋假象/強單因子≠增量/已淘汰名錄)
- [Raw Data 定義字典](augur-raw-data-defs.md) — 全84表據實 profile + 跨表髒值/語意陷阱(財報單季/累計YTD/snapshot、停牌哨兵、PER=-1、發布日 gate 15日、月營收=元、Dividend 塌列)
- [改常駐服務後須重啟](restart-systemd-after-edit.md) — 改 serve_*.py/src 後須 systemctl restart 對應服務再實測(http.server 不熱更新;引經據典因 advisor 未重啟再現之教訓,CLAUDE #7 v1.18)
- [限額錯誤處置紀律](quota-error-discipline.md) — API 限額錯誤≠定論,先請用戶看儀表再下判斷;失誤成本實例 2026-07-04
- [跨機接續交接](cross-machine-handoff.md) — 現行 SSOT=repo HANDOFF.md;源碼 GitHub(main@b011099)、DB 靠 D碟 dump、記憶隨 repo 遷移(sync_memory)、v3 建構理解 20260710
- [本地接續工具](local-handoff-tooling.md) — 三支零-usage 工具(sync_from_github/read_handoff/sync_memory)+ 記憶隨 repo 遷移機制(export→commit→新機 restore),供跨機接續
