---
status: executed
series: s4_s5_verify
track: RIDGE-THEN-PB
product_id: RIDGE-THEN-PB-v1
date: 2026-08-20
viewpoint: 2026-08-20T07:55+08:00
asof: "2026-08-19"
price_max: "2026-08-19"
family: RankRidge
k: 10
all_8h: true
long_entry: 0
short_entry: 1
wrote_prediction_values: false
standing_unchanged: true
go: audits/RIDGE-THEN-PB-LS-TIP-GO-20260820.md
fired: audits/RIDGE-THEN-PB-LS-TIP-FIRED-20260820.md
json: audits/RIDGE-THEN-PB-LS-0819.json
shell: scripts/probe_ridge_then_pb.py
paste: "請用最後交易日…八窗分數都要有…做多…做空…"
self_reported: true
layer: "[I]"
---

# EXECUTED｜RankRidge 八窗 · 相對強等回撤／相對弱等反彈＠2026-08-19

最後交易日＝庫裡 PriceAdj 頂 **2026-08-19**（日曆 08-20＝假 B3 rc=3）。dry-run 未寫庫。standing 20,60 未改。

宇宙 285／有路徑 282；八窗分數 20／20 齊。

**做多可當進場＝0／10。做空可當進場＝1／10（2385 群光）。**  
做空欄＝條件排序，**不是下單、不是可融券可成交**。score ≠ 漲跌幅％。

進場閘＝UP-PULL 四閘 AND（做多 L-A…D／做空 S-A…D）。池不因未回撤／未反彈剔除。
