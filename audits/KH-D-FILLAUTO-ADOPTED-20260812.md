---
status: adopted
series: local_ai_kh
kind: fill_auto_evolve
date: 2026-08-12
viewpoint: 2026-08-12T15:10+08:00
layer: "[I]"
paste: "D-FillAuto-ADOPTED | ask=wsj02如何填寫 | auto-cite-fill-example | no-filename-required | evolve-capability"
plan: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
fill_pack: item 1956038
fill_go: audits/EASYFLOW-FILL-EXAMPLE-EXECUTED-20260812.md
self_reported: true
---

# ADOPTED｜D-FillAuto · 設定填值自動告知（本地 AI 進化能力）

## Steward 要旨
直接問「wsj02如何填寫」——**不需**使用者先問檔名／範例包名稱；本地 AI **自動**告知可填的範例內容。此為閉環自我進化能力，非一次性客服腳本。

## 能力鏈（已落地）
1. **Intent**：設定／wsj／填寫題 → readout  
2. **Alias**：`wsj02`／站台 IP → `EasyFlow整合站台設定-填寫範例-wsj_file`（**1956038**）  
3. **Cite**：引文含 `wsj02=10.1.2.30`、`wsj04=EFGP_PROD` 等  
4. **Compact**：prompt 要求 `欄位=值`  
5. **機器閘（2026-08-12 補）**：弱模型若只寫「改 wsj02／目標 IP」而無 `欄位=值` → `ensure_fill_kv_in_response` 自凍引文**前置注入**範例塊（不靠模型守約）

## 驗收尺
| 尺 | 條件 |
|---|---|
| R1 | 問句僅「wsj02如何填寫」→ cite 含 **1956038** |
| R2 | 答文**必須**出現可照抄 `wsj02=…`／`wsj04=…`（機器閘保證） |
| R3 | **不要求**使用者先貼範例檔名 |
| R4 | 純步驟無值之答 → 出閘前被補上範例塊 |

## 誠實
範例＝格式示範；實機值以現場為準。未對全庫欄位字典批量造例。

## 禁
捏造客戶真 IP 當已核實；撤回 alias／填值 prompt 而無替代。
