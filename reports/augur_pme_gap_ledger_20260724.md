# PME Gap 帳本 [I]（2026-07-24）

* 掛接：`reports/augur_philosophy_market_evolution_loop_plan_20260724.md`
* 狀態留痕：`audits/PME-S012-STATUS-20260724.md`；**E123**：`audits/PME-E123-STATUS-20260724.md`
* 性質：[I]；**不**創設 [N]

| ID | 前 | 後 | 說明 |
|---|---|---|---|
| **G-PME-KILL** | absent | **none** | kill-switch 表＋CLI＋A5 live；env OR |
| **G-PME-AUTO-PATH** | absent → partial | **none** | E123：真綠 APPLY×2（`inst_cumflow_position_120d`／`volume_gini_60d`→validated） |
| **G-PME-COV** | absent | **none** | S1 覆蓋可重跑；dividend＝blocked_div |
| **G-PME-ECON** | open／SKIP | **partial** | E123 本地 #14 真跑：PASS=15／FAIL=21／SKIP=6（map 列）；非 skeleton |
| **G-PME-PROM** | open／SKIP | **partial** | E123 本地三關真跑：PASS=2／FAIL=34／SKIP=6；非 skeleton |
| **G-PME-STATUS** | known／open | **partial** | validated=2（原 0）；untested=24；其餘 desync 待後續真綠 |
| **G-PME-SOUL** | — | **pending** | 靈魂措辭另案；本輪不改 [N] |
| **G-PME-U** | — | **open** | U-PME 未開（A11 SKIP） |
