---
status: executed
series: s4_models
track: NF-D-PATCH
date: 2026-08-08
depends_on:
  - audits/NF-D-PATCH-0A-GO-20260808.md
  - audits/NF-D-PATCH-PLAN-ADOPTED-20260808.md
asof_pin: "2026-07-31"
paste: "NF-D-PATCH-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31"
viewpoint: 2026-08-08T18:48+08:00
self_reported: true
---

# EXECUTED｜NF-D-PATCH-0a · `SeqPatchTSTSmall`＋selftest

> RC=0 · selftest **全通過（13／13）** · 零 DB · CPU-only · **無**預訓練權重 · no-train-prod · 未 registry · 未塞 B3 · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| 模組 | `src/augur/models/sequence_patchtst.py` |
| class | **`SeqPatchTSTSmall`** · family 同名 |
| 實作 | 非重疊 patchify（截斷尾段）→ Linear → `TransformerEncoder`(1L/4H/d=32 預設)→mean-pool→Linear |
| 契約 | `(n,T,C)` fit／predict＝SeqLSTM／TFM 同構；train 統計凍結 |
| selftest | **全通過** |

未做：庫內 0b WF＠07-31／registry／serve／塗綠 TFM·TimesFM。

```text
NF-D-PATCH-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | no-promote | no-serve-swap | hold-#1
```

*完。*
