---
title: KH 進化 ingest-driven 觸發計畫（階 B）
status: adopted
series: kh_loop_evolve
phase: B
date: 2026-08-12
viewpoint: 2026-08-12T10:30+08:00
layer: "[I]"
role: KH 自我進化「何時開刀」契約——依庫內資料擴大／破口／命中缺口，**不依市場日曆**
ssot_code: KH-INGEST-TRIGGER-B-20260812
parent_nav:
  - reports/augur_opt_stepwise_best_next_plan_r14_20260811.md
  - reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
prior_phase: audits/KH-NAV-DECOUPLE-A-ADOPTED-20260812.md
adopted: audits/KH-INGEST-TRIGGER-B-ADOPTED-20260812.md
next_phase: C＝碼／timer／hook（須另明示 GO；本檔不授權開碼）
inherits_boundaries:
  - FZ/GATE-keep · no-SIM-apply · no-cron-B3
  - KH-nav≠tip-calendar（階 A）
  - PDF-C-no-ASR · ASR=owned_local+local_private only
  - T0 禁 web／對話 approve · T2 機械 system 可
  - KH8 stop-at-7 生產；加深另 plan
  - 禁把本計畫當「每天必跑進化」
self_reported: true
---

# KH 進化 ingest-driven 觸發計畫（階 B · 2026-08-12）

> **一句**：KH 波次何時開，看**庫內訊號**（入庫擴大、破口、eligible／游標／假拒／抬層債），**不看** tip／PriceAdj／星期幾。  
> **性質**：[I] 觸發契約；**不開碼**。落地自動化＝階 **C**＋明示 GO。  
> **階梯**：A 導航解耦 ✅ → **本檔 B** → C 碼／timer（未開）。

---

## §0 護欄

```text
KH-INGEST-TRIGGER-B | no-calendar-trigger | no-market-axis
| S0-S9 | apply=opt-in | KH-SPLIT
```

| 是 | 不是 |
|---|---|
| 資料／品質訊號達門檻 → **建議**對應波次 | 固定 cron「每日進化」無訊號也跑 |
| Steward／agent 依本表選刀 | 自動 SERVE／升格／改 tip |
| 事件驅動（ingest 後、回歸失敗後） | 綁 2026-08-xx 才准跑 KH |
| C 階實作本表 | 本檔＝已授權改碼／上 timer |

---

## §1 訊號目錄（ingest-driven）

> 門檻為 **B 契約預設**；C 開碼前可 AskQuestion 微調，但不得改成「純日曆」。

| ID | 訊號（量什麼） | 建議門檻（預設） | 建議波次／刀 | 優先 |
|---|---|---|---|---|
| **S0** | `kh0_breach`（`run_kh_chain --check` 口徑） | **>0** | Drain／A.1／KH0 補評（D-Data） | P0 立刻 |
| **S1** | 新 `knowledge_item`（自上次 KH 帳） | **≥1** 有可理解內容 | QUAL→state→（可）embed；有界 reingest 收尾 | P1 |
| **S2** | 新／升 `answer_status=eligible` | **≥1** 批（或單批 job 完成） | concordance／游標追；readout 錨抽 1 | P1 |
| **S3** | concordance／items 游標 pending | **>0**（zh 或 en） | cursor catch-up；禁假稱命中綠 | P1 |
| **S4** | 解析 skip（缺 parser／no_text／ASR fail-closed） | 同族 **≥3** 或 Steward 點名 | 補工具／有界 reingest（Writer／ASR 窄切） | P2 |
| **S5** | readout／advise **假拒**（庫內有件卻「無此內容」） | **≥1** 可複現 | resolve／RBAC／compact 回歸 | P0 |
| **S6** | AUTO-LIFT 旗開且 `lift_log` 異常（該抬未抬／誤抬） | 抽測失敗 | 關旗或修尺；**不**默抬 | P1 |
| **S7** | 私有／ASR smoke 矩陣回歸 | 任一格 FAIL | `KH-PRIVATE-SMOKE`／via 抽樣 | P1 |
| **S8** | domain FT pending／unattempted 上升 | Steward 選域＋另 GO | KH3／終態分隊（K-04） | P3 閒時 |
| **S9** | depth 宣佈 ≥8／物種進化 | **永不**單靠本表 | 必先 KH8 discrim plan＋GO | 阻塞 |

**市場訊號不進本表**：PriceAdj、tip、B3、econ——**永不**作為 KH 觸發或禁止條件（`KH-SPLIT-FROM-MARKET-AXIS-ADOPTED`）。

---

## §2 波次對照（開哪把刀）

| 波次 | 當 S* | 動作摘要 | 產出帳 |
|---|---|---|---|
| **Κ-Data** | S0／S1 | KH0／QUAL／Drain | `*-EXECUTED` 或 check 綠 |
| **Κ-Hit** | S2／S3 | embed／concordance／cursor | catch-up 帳 |
| **Κ-Read** | S5／S7 | readout／私有／via | smoke 表 |
| **Κ-Parse** | S4 | Writer／ASR／OCR 有界（守 PDF-C-no-ASR） | reingest 帳 |
| **Κ-Lift** | S6；可選試點 | `AUGUR_KH0_ANSWER_AUTO_LIFT` 運維 | lift_log 抽測 |
| **Κ-Deep** | S8／S9 | 他域 FT／KH8 | **另 GO**；禁假綠 |

同一時刻多訊號：**P0 > P1 > P2 > P3**；同優先則 **S0→S5→S3→S2→S1→S7→S4→S6→S8**。

---

## §3 執行協議（人／agent · 階 B）

```text
1) 量訊號（SQL／既有 check 腳本；勿發明假綠）
2) 對 §1 表取最高優先 S*
3) 開對應波次；寫 GO（若寫庫／訓模／大批）→ EXECUTED
4) 重測該 S* 是否回落；更新 r14 #29／readout §4
5) 與 B3 搶 lock → 暫停 KH 重 LLM，讓收盤窗
```

**Steward 手動覆蓋**：可點名波次，但須在帳註「override＝…／原 S*＝…」。

---

## §4 階 C 介面（已落地 · 見 C-EXECUTED）

Steward 已明示 **`KH-INGEST-TRIGGER-C-go`** → 實作見：

| C 元件 | 狀態 | 落點 |
|---|---|---|
| ingest hook | ✅ 預設 check | `acquire_local_files` → `hook_after_ingress` |
| 門檻 CLI | ✅ | `scripts/kh_ingest_trigger.py --check`／`--apply` |
| 輪詢腳本 | ✅ 可選；**未默裝** | `scripts/kh_ingest_trigger_watch.sh` |
| AUTO-LIFT | 仍要旗 | C **不**因 timer／hook 開抬層 |

帳：`audits/KH-INGEST-TRIGGER-C-GO-20260812.md` · `audits/KH-INGEST-TRIGGER-C-EXECUTED-20260812.md`

---

## §5 與 r14／readout 對齊

| 檔 | 角色 |
|---|---|
| KH 選刀專檔 | `reports/augur_kh_opt_stepwise_best_next_plan_20260812.md` |
| r14 市場板 | **不**編排本表；KH 已遷出 |

---

## §6 驗收（本計畫 B）

- [x] 訊號全為資料／品質／回歸，無 tip 日期門檻  
- [x] 每訊號有波次與優先  
- [x] 明文禁日曆假進化；C 須另 GO  
- [x] 資源讓位規則保留  
- [x] ADOPTED 帳落地  

## §7 Paste

```text
KH-INGEST-TRIGGER-B-ADOPTED | ingest-driven | no-calendar
| S0-S9 | P0=breach/false-decline | next=C-only-with-GO
```

*完。[I] · 階 B 觸發契約 · 不開碼。*
