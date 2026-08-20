---
status: go
series: s1s5_loop
track: HIST-RIDGE-WF
product_id: HIST-RIDGE-WF-v1
phase: P1-collect
date: 2026-08-20
viewpoint: 2026-08-20T10:55+08:00
layer: "[I]"
self_reported: true
paste: |
  先補月尾（2014 起約 152 個月底，其中約 88 個還沒特徵）——模型 walk-forward 靠這條
  再補月中每一個交易日——只用「該日可見、最近一次月尾」的模型打八窗分數
  分數夠了、且 30 日已實現，才拿 RIDGE-THEN-PB 對全宇宙路徑閘，看 Ridge 池會不會較準
---

# GO｜HIST-RIDGE-WF 月尾河 P1-collect

Steward 鎖三步。本紙只授權 **P1-collect**：2014-01…2026-07 已結束月尾、缺特徵的 **88** 日，特徵＋增量核心。不訓、不打分、不改 standing、不假 B3＠08-20、不重建 core＠08-19。

08-19＝8 月月中／價頂，**不**當月尾重訓。P1-train／P2／P4 另過。

```text
python scripts/run_hist_ridge_wf_batch.py --month-ends --collect-only --apply
```
