---
status: executed
series: local_ai_kh
kind: fill_auto_empty_fix
date: 2026-08-12
viewpoint: 2026-08-12T16:42+08:00
paste: "D-FillAuto-EMPTY-FIX | stale-advisor-restart | fill-pack-public | machine-gate"
---

# EXECUTED｜wsj02「知識庫中無此內容」修復

## 根因
1. **Advisor :8399 未重載**：程序 13:06 啟動，fill-auto readout（intent／alias）14:54 才入碼 → live 問「wsj02如何填寫?」不走 readout → 空檢索 → 固定句「知識庫中無此內容」。
2. **範例包 ACL**：1956038／39／40 原為 `local_private`；未登入必空。已改與 1956036 同軌：`public` + `public_domain` + `domain=local`（格式示範非客戶密鑰）。

## 處置
| 項 | 結果 |
|---|---|
| 重啟 `serve_advisor_openai.py :8399` | PID 見 `/tmp/kh-serve/advisor.pid` |
| UPDATE itext 1956038/39/40 → public | 有 `local` grant 即可 readout |
| `ensure_fill_kv_in_response` | 無 `欄位=值` 時注入；若模型誤吐無內容句則清掉再注入 |

## 驗
- `advise(..., scope=admin)` → cite **1956038**＋答含 `wsj02=10.1.2.30`
- `local` grant 非 owner → n=2
- 未登入 anon → 仍 n=0（RBAC 預期；Chat 須登入）

## 誠實
未登入／無 `local` 授權仍會「無此內容」。live LLM 慢時請等；檢索層已綠。
