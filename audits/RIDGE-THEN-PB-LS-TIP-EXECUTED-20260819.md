---
status: executed
series: s4_s5_verify
track: RIDGE-THEN-PB
product_id: RIDGE-THEN-PB-v1
date: 2026-08-19
viewpoint: 2026-08-19T15:25+08:00
asof: "2026-08-18"
price_max: "2026-08-18"
family: RankRidge
k: 10
all_8h: true
long_entry: 0
short_entry: 0
wrote_prediction_values: false
standing_unchanged: true
go: audits/RIDGE-THEN-PB-LS-TIP-GO-20260819.md
fired: audits/RIDGE-THEN-PB-LS-TIP-FIRED-20260819.md
json: audits/RIDGE-THEN-PB-LS-0818.json
shell: scripts/probe_ridge_then_pb.py
paste: "請用最後交易日…八窗分數都要有…做多…做空…"
self_reported: true
layer: "[I]"
---

# EXECUTED｜RankRidge 八窗 · 相對強等回撤／相對弱等反彈＠2026-08-18

最後交易日＝庫裡 PriceAdj 頂 **2026-08-18**（08-19＝假 B3 rc=3）。dry-run 未寫庫。standing 20,60 未改。

**做多可當進場＝0／10。做空可當進場＝0／10。**  
做空欄＝條件排序，不是下單、不是可融券可成交。score ≠ 漲跌幅％。

進場閘＝UP-PULL 四閘 AND（做多 L-A…D／做空 S-A…D）。池不因未回撤／未反彈剔除。
