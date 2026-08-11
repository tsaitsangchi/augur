---
status: inventory
series: local_ai_kh
kind: problem_board_refresh
date: 2026-08-11
viewpoint: 2026-08-11T08:50+08:00
ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
prior_board: audits/KH-LOOP-BOARD-REFRESH-20260808.md
pdf_probe: /tmp/kh-pdf-inventory-20260811.json
paste: "KH-LOOP-board-refresh | FZ/GATE-keep | hold-#1@0811 | no-mass-ingest | PDF-inv-first"
self_reported: true
layer: "[I]"
---

# INVENTORY｜本地 AI·KH 閉環 · 全問題最佳下一步（2026-08-11）

> **SSOT**：`reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md`（`rev=readout-compact-raw-v2`）。  
> Steward：要問題板＋可先／∥，並「讀入所有 pdf」→ 選 **PDF inv_first**（**≠** 本窗全量 re-acquire）。  
> **正交**：市場 **hold-#1＠08-11**（watcher ALIVE；PriceAdj tip 仍 **08-10**）。

## PDF／匯入現況（2026-08-11 親查）

| 尺 | 值 |
|---|---|
| 磁碟 `~/.augur_uploads/**/*.pdf` | **306** 檔（約 **5** batch；三大 batch 各 **98**＝**檔名重複**） |
| 去重 basename | **≈105** 獨一份 |
| docx／doc | **719** |
| 倉內 `augur/**/*.pdf` | **0** |
| `knowledge_item` 標題／URL／external 含 `.pdf` | **114** |
| basename ∩ uploads | **105／105**（獨一份 basename 已能對上庫） |
| `domain=local` | **330**（有文路徑另計） |
| `knowledge_import_job` | **21** completed；近 job 多為小增量 ok |
| academic `fulltext_status` | `unattempted` **121k**（OA 池；**≠** 本地 upload 全失敗） |
| 計畫釘 | PDF **acquire 層已閉**；殘＝**PDF-C** 弱字層／OCR／有界補豐 |

→ 「讀入所有 PDF」若＝**再跑一遍全量 ingest**：現況顯示**多數本地 PDF 已入庫路徑在**；全量重掃多半 **dup／skip**，非默認最佳刀。補缺口→ **缺檔差異清單＋PDF-C 有界**，另 GO。

## 問題板（最佳下一步 · 可先／∥）

| # | 問題 | 最佳下一步 | 可先／∥？ | 狀態（08-11） |
|---|---|---|---|---|
| **1** | D-Data KH0 破口 | 守；`run_kh_chain --check` | — | ✅ 0 |
| **1c** | AUTO-LIFT 熱路徑 | 旗仍勿默開 systemd；可∥運維抽測 | ∥運維 | ✅ 試點閉／旗 off |
| **1h+** | local 授權／錨題 | grant 已落；live 抽測可∥ | ∥ | ✅／🟡 live |
| **1b** | D-Answer 地板 | live 抽測 | ∥1c | ✅ stub |
| **3** | 治權誤用 | 抽樣無 web／對話 approve | ∥隨時 | ✅ T0 抽樣 |
| **PDF** | 「讀入所有」 | **差異盤點**（disk∖庫）→ 僅補缺；禁默全量 | **可先文件／有界** | 🟡 inv 本窗 |
| **PDF-C** | 弱字層 OCR | P2／切句 embed 有界 | ∥；≠full-acquire | ✅ P0／可加深 |
| **4** | 他域 FT | domain 分隊＋另 GO | 閒時 | 🔴 |
| **5** | KH8 鑑別力 | E keep；**M3 pool-gate ✅**；A2 **L1+L2 ✅**；主 disc 仍 False；**禁抬 8**；L3／merge 另雙明示 | 加深前闸已绿；merge 未做 | 🟡 码闸绿／生产仍红 |
| **8** | C1／市場 | 讓 **hold-#1＠08-11** | 正交∥市場 | 讓位 |
| **9** | KH10 | — | **禁** | 禁 |
| **10** | 計畫入版控 | commit（另授） | ∥文件 | 📄 |

### 推薦排序（本視點）

1. **市場主軸不讓**：hold tip≥**08-11** → 站式 B3 20,60。  
2. **KH 可∥（不搶 tip）**：PDF **差異清單**（306→獨 105 已對上）確認是否尚有「在碟無庫」；有則 **有界补入 GO**，非全量。  
3. **可∥加深预备**：**A2-L3** 或 **merge-M3** 皆须双明示；现状推荐暂缓（与 tip 抢盘且 disc 投影仍 False）。  
4. **可∥运维**：#3 治權抽樣；#1c 勿默开。  
5. **PDF-C-P2** 有界 OCR／字层 — 若锚题弱字层。

## Paste

```text
KH-LOOP-board-refresh | FZ/GATE-keep | hold-#1@0811 | PDF-inv | no-mass-ingest
# 下一步候選（另授）:
PDF-DIFF-gap-go | basename∖DB | bounded-ingest-if-gap | ≠full-acquire
PDF-C-P2-go | bounded-sample
KH8-DISCRIM-merge-M3-go | dual-explicit | after Steward
A2-L3-go | dual-explicit | no-tip-contend
```

*完。inventory。*
