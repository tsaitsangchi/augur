---
status: executed
series: local_ai_kh
kind: aap_readout_fix
date: 2026-08-11
viewpoint: 2026-08-11T09:30+08:00
paste: "AAP-readout-fix | intent-strip-? | alias→應付帳款管理系統→aap.pdf | FZ/GATE-keep"
query: "tiptop 應付帳款系統說明?"
item_id: 277896
self_reported: true
layer: "[I]"
---

# EXECUTED｜應付帳款手冊假「無此內容」修復

## 根因（誠實）

1. PDF **已在庫**：`aap.pdf` item **277896**（≈670k 字、eligible、public）。  
2. 問句尾 **`?`** 使 `is_readout_intent=False` → 不走 readout，改 ANN；易濾空或假拒。  
3. 「應付帳款系統說明」未別名到文首產品名 **應付帳款管理系統**（裸「應付帳款」content-head 被雜件洗掉、aap 進不了掃描窗）。

## 修復（`readout.py`）

- 剝尾綴 `?`／`？` 再判 bare-title  
- `_resolve_hint_variants`：去 tiptop/erp 前綴＋手冊別名 → `應付帳款管理系統`  
- selftest 鎖上述個案  

## 驗收

```text
intent(tiptop 應付帳款系統說明?)=True
resolve → [277896]
advise_readout_citations → aap.pdf 有界原文（≠「知識庫中無此內容」）
```

**運維**：若 chat／advisor 仍舊答，**重啟**載入新碼之伺服行程。

*完。*
