---
name: cheap-scale-first
description: 昂貴掃描前先跑便宜尺寸 preview 打熟引擎;07-29~30 preview 23-cutoff 抓 3 bug 省 73h 白算
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-30T01:10:56.487Z
---

meta-replay 密網格月頻掃（100 cutoff、估 73h）前，先以現網格 23 個季頻 cutoff 跑 preview——連抓三 bug（bootstrap 卡空 falsy、靜態錨空集=差值序列全癱、44 分/cutoff 成本主刀→ladder 快取）；帳本按 proc_sha 自然分家、壞家族留檔考古零污染。同型先例：#25 單倉/單日/單 panel probe。

**Why**：昂貴尺寸上炸 bug＝小時~天級白算＋污染風險；便宜尺寸炸＝分鐘級＋決策 JSON 可驗屍。

**How to apply**：任何 >數小時的掃描/重演/建置，先問「有沒有 1/5~1/10 尺寸的 preview 路？」——有就先跑；程序身分（sha）須含會影響結果的一切輸入（碼+參數+資料池+**網格**），preview 與正式自動分家。收 preview 時**讀帳本決策明細**驗屍、別只看 console 摘要（console 印錯過一次：空集顯示 bootstrap）。
