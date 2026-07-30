---
name: same-scale-precheck
description: 任何 A vs B 比較前的同尺四查——覆蓋/網格/重名/慣例欄;07-28~30 六發尺陷阱歸納
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-30T01:10:44.426Z
---

2026-07-28~30 三天內六發「不同尺互比」陷阱（全部在便宜處自攔、零污染入帳）：雙 verb URL、候選短史覆蓋假象（Δ=-0.055 假）、canonical 重名（feats 含同名兩次→交集恆 0）、建置中網格飄移（econ 兩跑 17 vs 14 期）、`run_ladder(feats=[])` falsy 退全 canonical、estimand `settled_at` 慣例欄缺。

**Why**：對照組與實驗組讀到不同的 panel/fold/股集時，Δ 是兩把尺的差、不是效應——而且**方向常常誘人**（假 Δ 更漂亮）。

**How to apply**：跑任何 A/B 前四查——①兩側特徵**覆蓋 panel 集**相同？（稀疏特徵→顯式 `--panels-list` 釘死）②網格建置中？（釘 `--until`/清單＋**印 panel hash 兩側自證**）③加特徵前查它是否已在 canonical（重名→交集歸零）④空集/None 走到 `x or default` 會不會靜默換語意。相關：[[slow-but-precise]]、[[guard-mechanisms-that-silently-fail]]。
