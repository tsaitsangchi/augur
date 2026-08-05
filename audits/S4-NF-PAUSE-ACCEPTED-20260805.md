---
status: accepted
series: s4_models
depends_on:
  - reports/augur_s4_next_family_adapter_plan_20260805.md
---

# ACCEPT｜S4 下一族 **NF-pause** · 2026-08-05

> **授權**：Steward `docs_first`（清單 3–9 之一部＝項 6 書面暫停）。  
> **性質**：[I] 書面接受；**不開訓、不寫新族 adapter**。  
> **self-reported（#32a）**。

## 1. 裁示

採 **`NF-pause`**：暫停開新 S4 模型族（不選 NF-E／NF-B-VAR；亦不默授 ARIMA Phase 1＝清單 #4）。

## 2. 生效邊界

| 是 | 否 |
|---|---|
| 下一族 adapter 設計／Phase 0 擱置 | 撤回既有 RankRidge／RankGBDT／Wave 已 EXECUTED |
| CPU／聊天／WM36／閉環文件可優先 | 自行解讀為可開 ARIMA P1 或 GNN 0b |
| 重新開族須新句 `NF-*-go-plan` 或 `S4-ARIMA-P1-go` | 把本檔當 train GO |

## 3. 交叉

- 計畫書：`reports/augur_s4_next_family_adapter_plan_20260805.md` → status＝`nf_pause_accepted`
- ARIMA Phase 1／β2 `#11` 仍須各別 GO（本 pause 不解凍）

## 4. Paste-ready（若日後撤 pause）

```
NF-E-go-plan
# 或
NF-B-VAR-go-plan
# 或
S4-ARIMA-P1-go + GATE-keep + skip-sync + no-SIM-apply
```
