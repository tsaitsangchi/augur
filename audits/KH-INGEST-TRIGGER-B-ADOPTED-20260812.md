# KH-INGEST-TRIGGER-B-ADOPTED · 2026-08-12

date: 2026-08-12  
kind: plan_adopted  
phase: **B**（ingest-driven 觸發計畫）  
status: ADOPTED  
prior: `audits/KH-NAV-DECOUPLE-A-ADOPTED-20260812.md`  
plan: `reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md`  
next: **C** 碼／timer／hook —— **未開**；須明示 `KH-INGEST-TRIGGER-C-go`

## 決策
KH 波次觸發改為 **S0–S9 庫內訊號**（破口／入庫／eligible／游標／假拒／smoke／抬層債／域 pending…），**不依** tip／PriceAdj／星期。

## 本階範圍
- 計畫＋導航對齊 only  
- **不**改碼、**不**上 timer、**不**默開 AUTO-LIFT

## 導航更新
- r14 `#29` → A✅ B✅ C🔴  
- KH readout §1.1／§4 `#11` → 觸發 SSOT＝B 計畫

## 驗收
- [x] 計畫檔落地且無日曆觸發門檻  
- [x] C 介面僅預留  
- [x] 下一刀須 Steward「開 C」＋ GO 帳

## paste
```text
KH-INGEST-TRIGGER-B-ADOPTED | S0-S9 | no-calendar
| no-C-without-GO | yield-lock-to-B3
```
