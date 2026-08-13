---
status: executed
series: pred_kh
kind: rel_prob_dual_board
date: 2026-08-13
viewpoint: 2026-08-13T08:35+08:00
paste: "REL-PROB-BOARD-FIX | dual-H20+H60 | top+bottom | intersect-lists | no-LLM | no-dup | no-blocked-caveat"
---

# EXECUTED｜相對機率雙窗看板修正

## 病灶（Steward 貼的本地 AI 回覆）
- 只回 **H60**、表頭 `Top10/H60 H60`
- 個股**逐列重複**
- 缺跌幅 Top10、缺兩窗交集
- 出現「白話解讀未過機械閘」

## 根因
1. `_horizon_from_query` 遇「20天與60天」先命中 60 → 單窗  
2. 弱 LLM 複誦真兆表 → 重複／丟序號；guard fail → 擋白話

## 處置
| 項 | 作法 |
|---|---|
| `rel_prob_board_intent` | 雙窗或漲+跌 TopN → 看板 |
| `build_rel_prob_board_payload` | 確定性 H20/H60 強／弱＋交集條列 |
| `advise`／`oai_compat` | 看板路徑**免 LLM**、guard pass |
| `_render_picks_table` | 優先 `board_text`；單窗去重、勿疊 H |

## 驗
同問句 → H20+H60 強／弱 Top10＋兩窗皆在強／弱條列；無重複複誦；無「白話未過」。
