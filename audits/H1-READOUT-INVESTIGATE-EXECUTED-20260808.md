---
status: executed
series: local_ai_kh
kind: readout_1h_investigate
date: 2026-08-08
viewpoint: 2026-08-08T20:45+08:00
board: audits/KH-LOOP-BOARD-REFRESH-20260808.md
prior_false_alarm: audits/AUTO-LIFT-1C-PILOT-EXECUTED-20260808.md
paste: "1h-READOUT-investigate | FZ/GATE-keep | root=RBAC-scope | resolve-OK@super | no-title-regression | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜#1h 錨題 readout 空 cite 調查 · 2026-08-08

```text
1h-READOUT-investigate | root=RBAC fail-closed | 277948 resolve OK @super | ≠title bug
```

## 結論（一句）

AUTO-LIFT 試點看到的 `citations=[]`／「知識庫中無此內容」＝**未帶身分 scope** 的預期 deny，**不是**標題 resolve／277948 損毀。

## 證據

| 條件 | 結果 |
|---|---|
| `advise_readout_citations(Q, scope=None)` | **0** cite |
| `scope=(True, ∅, user_id=1)` admin super | **5** cite · ids=`[277948]` |
| `advise(..., scope=super, compact)` | `readout.item_ids=[277948]` · guard pass · **非**「無此內容」 |
| `advise(..., scope=None)` | cites=0 · 答「知識庫中無此內容」（advise 內無 HTTP 層「未授權」） |
| item 277948 | title 命中 · has_text · kh4 `answer_status=eligible` |
| `clean_item_sql` @非 super∧空域 | 片段含 **`AND false`**（corpus 預設 deny；設計如此） |
| `group_domain_grant` 含 `domain=local`？ | **無**（非 super 即有他域授權也讀不到 local 庫） |
| curl `:8500` 無身分 | 「未授權」 |
| curl `:8399` 無正確 model | tier 名錯（另）；systemd unit **曾 inactive**，現有進程在聽 8399 |

## Ρ0 對照

計畫釘「未登入／無 local → 誠實空」＝**仍成立**。  
「登入後 cite 277948」＝**super／admin 下成立**。

## 非修（本窗）

- 未改 resolve SQL／未假開 RBAC  
- 未 `group_domain_grant` 加 `local`（另 GO）  
- 未默開 insecure-loopback-admin  

## 殘刀候選（另授）

1. **GO-grant-local**：把 `domain=local` 授給 steward 群（非 super 亦可讀本地檔）  
2. **ops**：`systemctl --user start augur-advisor`＋登入後 live 錨題驗 Ρ0  
3. hold｜等 08-10 B3  

*完。*
