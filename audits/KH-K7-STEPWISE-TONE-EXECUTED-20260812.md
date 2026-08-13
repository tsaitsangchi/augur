# KH-K7-STEPWISE-TONE-EXECUTED · 2026-08-12

date: 2026-08-12  
kind: executed  
status: EXECUTED  
go: `audits/KH-K7-STEPWISE-TONE-GO-20260812.md`  
log: `/tmp/kh-k7-stepwise-tone/`  
prior: `audits/KH-K7-ANCHOR-LIVE-EXECUTED-20260812.md`

## 碼／設定
| 項 | 內容 |
|---|---|
| `compact_answer._normalize_cite_bullets` | 支援無冒號 `- [N] …` → `N. …` |
| `prompt.build_compact_knowhow_prompt` | 問句含「逐步／操作步驟」→ **強制操作步** out_hint |
| 試跑 env | `AUGUR_COMPACT_NUM_PREDICT=960` · `CITE_CHARS=3500` · `CITE_N=4` · `STEPWISE=1` |

## LIVE（錨 Q2 逐步操作）

| 模型 | 秒 | hit | guard | 編號步 | 動詞步 | 判 |
|---|---:|:---:|:---:|---:|---:|---|
| **qwen3:8b** | 385 | ✅ | pass | **25** | **18** | **達標**（1.…25. 可執行步） |
| qwen3:4b | 373 | ✅ | pass | 0 | 0 | 未達（點列摘要＋尾想題洩） |

## 判讀
- 逐步口吻加強：**8b＋960 predict＋強制操作 hint** 有效。  
- 4b 仍不夠穩；產品若要「每行一步」建議 readout／步驟題預設 **8b** 或至少提高 predict。  
- 未默改 systemd model；本帳為抽樣＋小碼。

## 選刀
K7：🟡→**管線綠＋8b 口吻達標**；4b 仍殘。

## paste
```text
KH-K7-STEPWISE-TONE-EXECUTED | 8b=25steps guard=pass | 4b=fail-tone
| cite-bullet-normalize | ops-out-hint | num_predict=960
```
