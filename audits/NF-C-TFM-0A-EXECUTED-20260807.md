---
status: executed
series: s4_models
track: NF-C-TFM
date: 2026-08-07
depends_on:
  - audits/NF-C-TFM-0A-GO-20260807.md
  - audits/NF-C-TFM-PLAN-ADOPTED-20260807.md
asof_pin: "2026-07-31"
paste: "NF-C-TFM-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31"
viewpoint: 2026-08-07T21:35+08:00
self_reported: true
---

# EXECUTED｜NF-C-TFM-0a · `SeqTransformerSmall`＋selftest

> RC=0 · 零 DB · CPU-only · **無**預訓練權重下載 · no-train-prod · 未 registry · 未塞 B3 · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| 模組 | `src/augur/models/sequence_transformer.py` |
| class | **`SeqTransformerSmall`** · family 同名 |
| 實作 | Linear→sin PE→`TransformerEncoder`(1L/4H/d=32 預設)→mean-pool→Linear |
| 契約 | `(n,T,C)` fit／predict＝SeqLSTM 同構；train 統計凍結 |
| selftest | **全通過**（12／12） |

未做：庫內 0b WF＠07-31／registry／serve／冒充 LSTM 翻案。

```text
NF-C-TFM-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | no-promote | no-serve-swap | hold-#1
```

*完。*
