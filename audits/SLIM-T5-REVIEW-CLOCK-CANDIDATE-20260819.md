---
status: candidate
series: repo_slim
track: slim-t5
kind: review_clock_candidate
date: 2026-08-19
viewpoint: 2026-08-19T16:43+08:00
plan: reports/augur_repo_slim_opt_plan_r20_20260819.md
paste: "把「90 天複審鐘」寫進 slim 計畫當 T5 候選"
epoch_tag: archive-20260819-b3-hist-slim-r20
epoch_date: 2026-08-19
earliest_review: 2026-11-17
self_reported: true
layer: "[I]"
---

# CANDIDATE｜倉精化 T5 · 90 天複審鐘（未開火）

Steward 要將「90 天複審鐘」寫進 slim 計畫當 **T5 候選**。已寫入 `reports/augur_repo_slim_opt_plan_r20_20260819.md` §0／§4 T5。

## 是什麼

對已 `git mv` 進 `archive/slim-t0`…`t4/`、且已在 annotated tag 的檔：滿 **90** 天列入可審清單。清單預設 **KEEP**。

epoch＝`archive-20260819-b3-hist-slim-r20` 之日 **2026-08-19**。最早可審≈**2026-11-17**。

## 不是什麼

- **不是** GO、不是「執行 T5」、不是授權 `rm`／`git rm`
- **不是** cron 到期自動刪
- **不是** 生成物磁碟 TTL（dump／`models_artifacts` 另軌）
- 日曆滿 90 天 **≠** 未用

## 開火仍須另句

`執行 T5` **且** 日曆 ≥ 2026-11-17 → 只產 `SLIM-T5-REVIEW-LIST-*`。鐘未到則寫未到期帳，仍不刪。清單之後若要再瘦＝**T5b 另句**。
