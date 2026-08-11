---
status: executed
series: local_ai_kh
kind: kh8_a2_sim
date: 2026-08-08
viewpoint: 2026-08-08T21:25+08:00
go: audits/KH8-DISCRIM-A2-SIM-GO-20260808.md
log: /tmp/kh8-a2-sim/run.log
paste: "KH8-DISCRIM-A2-sim-EXECUTED | no-write | proj-ok=False | E-keep | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜KH8 A2-sim · 2026-08-08

```text
KH8-DISCRIM-A2-sim | sample=1000 + full-pop投影 | no-write | ok仍False（誠實）
```

## 草案公式（僅模擬）

```text
plumbing = 0.12*T + 0.12*E + 0.11*K     # 舊齊備頂 0.65 → 現 0.35
cite     = 0.50 * min(cite_n/8, 1)
interact = 0.15 * E * cite_norm
cap: cite_n≤1 ⇒ score≤0.55；cite_n=0 ⇒ ≤0.35
```

## 結果

| 尺 | legacy | A2 draft |
|---|---|---|
| 1k band（本抽） | high=1000 | medium=946 · high=54 |
| 1k minority | 0 | **0.054**（樣內剛過） |
| 1k score p50 | 0.72 | 0.431 |
| **全庫投影 band** | （live high 主導） | high 3060 · **medium 143352** · low11 · absent385 |
| **全庫投影 disc** | ok=False | **仍 ok=False**（band 非眾數 **0.0235＜0.05**） |
| 分量 | terminal 全1 | **未變**（公式不改分量源）→ 2′ 壓力仍在 |

## 判讀

1. A2 方向**有效**：打破 0.72→high 牆，分數／band 真展開。  
2. **未達標**：全庫 minority 僅≈2.4%，距 5% 仍差一截；且 terminal 無變異。  
3. **E 仍適用**；不得因「樣內剛過」宣佈 KH8 綠。  
4. 下一刀候選：A2-sim2（更陡／更深引文信號）∥ A1 擴薄項母體；仍 no-write 先。

## 未動

主表重算、θ、depth≥8、hold-#1。

*完。*
