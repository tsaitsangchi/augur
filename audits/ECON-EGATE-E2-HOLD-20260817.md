---
status: hold
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T08:56+08:00
paste: "E2-approve-go | gate=egate_H_60_ridge_LO_prodset_r17 | approved-by='hugo'"
paste_prior: "E2-approve-go | gate=egate_H_60_ridge_LO_prodset_r17 | approved-by=<名>"
gate: egate_H_60_ridge_LO_prodset_r17
approved_by_intended: hugo
self_reported: true
layer: "[I]"
---

# HOLD｜E2 核准未執行（簽名已指名 hugo；仍非 TTY）

第二句已把簽名填成 **hugo**。佔位符擋已解除。

本環境非 TTY；`--approve … --approved-by hugo` 本窗再跑一次 → **拒**（RC=1，`approve 唯決策層人`）。未用偽 TTY、未 SQL 直寫 `approved`。閘仍 **preregistered**。

請 Steward 在**自己的終端**執行：

```bash
cd /home/hugo/project/augur
./venv/bin/python scripts/preregister_econ_establishment_gate.py \
  --approve egate_H_60_ridge_LO_prodset_r17 --approved-by hugo
```

成功時應看到 `✓ … 已核准 by hugo`。把那一行貼回，我再寫 E2 EXECUTED。再把同一句貼到對話裡仍會被拒。
