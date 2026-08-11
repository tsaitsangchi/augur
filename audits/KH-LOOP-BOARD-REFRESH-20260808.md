---
status: inventory
series: local_ai_kh
kind: problem_board_refresh
date: 2026-08-08
viewpoint: 2026-08-08T20:35+08:00
ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
prior_plan: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806.md
market_nav: reports/augur_opt_stepwise_best_next_plan_r13_20260808.md
paste: "KH-LOOP-board-refresh | FZ/GATE-keep | hold-#1 | no-mass-ingest | inventory-only"
self_reported: true
layer: "[I]"
---

# INVENTORY｜本地 AI·KH 閉環 · 全問題最佳下一步（2026-08-08）

> **SSOT**：`reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md`（`rev=readout-compact-raw-v2`）。  
> **本窗**：盤點＋選刀板刷新；**≠** 全量 PDF 再 ingest（Steward 選 inventory_plan）。  
> **正交**：市場 **hold-#1＠08-10**；KH 可∥但共享 LLM／CPU 時**讓日更**。

## PDF／匯入現況（誠實）

| 尺 | 值 |
|---|---|
| 磁碟 `~/.augur_uploads/**/*.pdf` | **≈306**（另有 docx 等） |
| 倉內 `augur/**/*.pdf` | **0**（PDF 不在 git tree） |
| `knowledge_item` 標題／URL 含 `.pdf` | **114** |
| `local_files` import jobs | **19** completed；累計 scanned 多、**ok 常低／skip 高**（重掃≠必新入） |
| fulltext 例 | `unattempted` 仍大（學術 OA 池；≠本地 upload 全失敗） |
| 計畫釘 | PDF **acquire 層已閉**；殘＝**PDF-C** 弱／掃描字層 OCR（非再全量 acquire） |

→ 「讀入所有 PDF」若指**再跑一遍全量 ingest**＝**本窗不授**；現況＝盤點確認 uploads 已存在＋歷史 job 已跑過；缺口改走 **PDF-C／QUAL** 有界刀。

## 問題板（最佳下一步 · 可先／∥）

| # | 問題 | 最佳下一步 | 可先／∥？ | 狀態 |
|---|---|---|---|---|
| **1** | D-Data KH0 破口 | 守；`run_kh_chain --check` | — | ✅ **2026-08-08 補齊 93→0**（`KH0-93-PATCH-EXECUTED`） |
| **1c** | AUTO-LIFT 熱路徑 | 試點 `AUGUR_KH0_ANSWER_AUTO_LIFT=1`＋lift_log | **∥運維；KH 現可開** | ✅ 試點閉（`AUTO-LIFT-1C-PILOT-EXECUTED`；**勿默開 systemd**） |
| **1h+** | local 域授權 | grant→經營管理層 | — | ✅ `GO-GRANT-LOCAL-EXECUTED`（仍須入組才對非 super 生效） |
| **1b** | D-Answer 地板 | 可續 live 抽測 | ∥1c | ✅ stub |
| **3** | 治權誤用 | 抽樣無 web／對話 approve | ∥隨時 | ✅ 抽樣閉 `KH3-GOV-SAMPLE-EXECUTED`（T0 守） |
| **PDF-C** | 弱字層 PDF | P0 已；可選 P2／切句 embed（有界） | ∥；**≠全量 acquire** | ✅ P0／可選加深 |
| **4** | 他域 FT | domain 分隊＋另 GO | 閒時 | 🔴 |
| **5** | KH8 鑑別力 | E＋A2＋A1；影全 T2；**M3** 准併方向（闸後才併） | — | ✅ M3 adopted；主仍 False；實驗∪ True；抬 8 禁 |
| **8** | C1／市場 | 讓 **r13 hold-#1** | 正交∥市場 | 讓位 |
| **9** | KH10 | — | **禁** | 禁 |
| **10** | 計畫入版控 | commit（另授） | ∥文件 | 📄 |
| **市場** | A→B3＠08-10 | watcher WAIT | **主軸市場**；KH 不搶 | hold |

### 推薦排序（本視點）

1. **市場主軸不讓**：hold-#1＠08-10（已 armed）。  
2. ~~可先地板：KH0 93 補評~~ → **已閉**（破口 0）。  
3. **KH 可∥運維**：**#1c** AUTO-LIFT 試點∥ **#3** 治權抽樣。  
4. **可先文件**：KH8 **go-plan**（#5）——`--check` 仍釘 **KH8 不具鑑別力**；深層綠禁。  
5. **PDF**：維持「不重全量」；上傳根 **306 pdf／701 docx**；import 累計 ok≈88／skip≈320。補豐→ `PDF-C-P2-go` 有界，非「讀入所有」。

## Paste

```text
KH-LOOP-board-refresh | FZ/GATE-keep | hold-#1 | inventory-only | no-mass-ingest
# 下一步候選（另授；推薦順序）:
KH0-93-patch | run_kh_chain --phase advance 有界 | FZ/GATE-keep
AUGUR_KH0_ANSWER_AUTO_LIFT=1 試點 | lift_log
KH8-DISCRIM-go-plan | FZ/GATE-keep | no-fake-depth8
PDF-C-P2-go | bounded-sample | ≠full-acquire
```

*完。inventory-only。*
