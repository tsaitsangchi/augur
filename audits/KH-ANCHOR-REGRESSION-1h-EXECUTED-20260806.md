# KH 錨題回歸 #1h — EXECUTED 2026-08-06

```text
KH-ANCHOR-REGRESSION-1h-executed | FZ/GATE-keep | stub-llm | scope=admin-super
# 計畫 §4 #1h · SSOT readout-compact-raw-v2
# 錨 item=277948 國碩-ERP-GP_DR說明(20211007-4-rman)1
```

## 題組（機械 stub · 授權 scope）

| ID | 問句 | 結果 |
|---|---|---|
| Q1 | `…：請讀出具體內容` | ✅ readout=[277948] · compact · guard · 非 NO_K · prompt 含逐步 |
| Q2 | 純標題同檔名 | ✅ 同上 |
| Q3 | `…：請依引文用編號逐步條列…` | ✅ 同上 |
| Q4 | `國碩 ERP-GP DR：r-man 備份路徑從哪改到哪？` | ✅ hit=277948 · compact（無 readout meta，走 retrieve）· guard · 非 NO_K |

**總判**：`ALL_OK`（stub；不焼長 LLM 作為回歸帳本體）。

## 邊界

- 本帳驗證**管線**：Resolve／hit→freeze→compact→逐步指令在 prompt→非假「無此內容」。  
- **不**代替本機 LLM 直播品質帳（已另有 compact smoke／逐步條列 live）。  
- 未登入／無 local 仍應誠實空（RBAC；本帳未覆測 deny）。

## 計畫

§4 **#1h** → ✅ 機械回歸已寫帳；live LLM 抽樣屬運維可選。

*executed。*
