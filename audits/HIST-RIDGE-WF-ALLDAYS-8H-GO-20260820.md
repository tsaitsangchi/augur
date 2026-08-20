---
status: go
series: s1s5_loop
track: HIST-RIDGE-WF
product_id: HIST-RIDGE-WF-v1
phase: P2-train-asof-D
date: 2026-08-20
from: "2014-01-02"
until: "2026-08-19"
layer: "[I]"
self_reported: true
paste: 從2014-01-02到現在，依當時交易日產生當日特徵與核心，定錨產出當天 RankRidge 八窗（同 2014-08-19）
---

# GO｜全交易日 asof=D 八窗

每個交易日 D∈[2014-01-02, 價頂]：特徵＋核心＠D → RankRidge 八窗 asof=D（標出場≤D）→ 八窗分數。已有八窗分數的日跳過（含 2014-08-19）。不改 standing、不重建 tip 核心、不假 B3＠08-20。單日失敗繼續。月尾 collect 河併入本河。
