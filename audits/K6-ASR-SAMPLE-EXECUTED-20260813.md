---
status: executed
series: local_ai_kh
track: K6
date: 2026-08-13
viewpoint: 2026-08-13T10:45+08:00
kind: optional_sample
log: /tmp/kh-k6-asr-sample-0813/sample.log
prior_k4: audits/K4-PRIVATE-SMOKE-EXECUTED-20260813.md
paste: "K6-ASR-sample-EXECUTED | n=5items/6rows | via-mark=seq1 | owned_local | spot=1818835 | no-retranscribe | PDF-C-no-ASR"
self_reported: true
layer: "[I]"
---

# EXECUTED｜K6 ASR via／對聽 · 可選抽樣 · 2026-08-13

> 唯讀抽樣；**未**重跑 faster-whisper／未入庫。

## 庫內

| 尺 | 值 |
|---|---|
| `source_type=asr_transcribe` | **5** items／**6** text 列 |
| license | 皆 **owned_local** |
| S0 mark `<!-- via=asr_transcribe -->` | **seq=1 皆有**；`1818838` seq=2＝續段無前綴（預期） |
| 對聽錨 | **1818835** 開頭為口語 ASR 文（非 PDF-C） |

## 抽樣對聽（readout）

`WebService程式撰寫(I).avi：請讀出具體內容` · scope=super → 命中 **1818835** 且 cite 含 via 標記（同 K4 矩陣）。

## 判定

**✓ 可選抽樣綠** · 續守 ASR＝owned_local＋via；**≠** PDF-C；未默重轉。

*完。*
