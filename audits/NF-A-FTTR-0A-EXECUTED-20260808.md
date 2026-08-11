---
status: executed
series: s4_models
track: NF-A-FTTR
date: 2026-08-08
depends_on:
  - audits/NF-A-FTTR-0A-GO-20260808.md
  - audits/NF-A-FTTR-PLAN-ADOPTED-20260808.md
asof_pin: "2026-07-31"
paste: "NF-A-FTTR-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31"
viewpoint: 2026-08-08T00:55+08:00
self_reported: true
---

# EXECUTED｜NF-A-FTTR-0a · `RankFTTransformer`＋selftest

> RC=0 · selftest **13／13 通過** · 純 torch · **未**裝 pytorch-tabnet · 零 DB · 未 registry · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| 模組 | `src/augur/models/tab_transformer.py` |
| class | **`RankFTTransformer`** |
| 契約 | `(n,f)` fit／predict＝RankRidge 同構；train scaler 凍結 |
| 架構 | 特徵 token＋CLS · TransformerEncoder(1L／4H／d=16) · Linear |
| selftest | **全通過** |

未做：0b WF＠07-31／registry／serve／接 `ALL_FAMILIES` 熱路徑。

```text
NF-A-FTTR-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | no-promote | no-serve-swap | hold-#1
```

*完。*
