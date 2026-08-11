---
status: go
series: local_ai_kh
kind: grant_local_domain
date: 2026-08-08
viewpoint: 2026-08-08T20:55+08:00
board: audits/KH-LOOP-BOARD-REFRESH-20260808.md
prior: audits/H1-READOUT-INVESTIGATE-EXECUTED-20260808.md
paste: "GO-grant-local | FZ/GATE-keep | promote authz_boundary | grant→經營管理層 | no-set-super | hold-#1"
self_reported: true
layer: "[I]"
---

# GO｜grant-local（g1 經營管理層）

Steward 選：升 `local` 為授權邊界＋授 **經營管理層**（group_id=1）。

| 准 | 禁 |
|---|---|
| `--add-domain local --authz-boundary`（升邊界） | 設新超管／假開 insecure-loopback |
| `--grant-domain --group 經營管理層 --domain local --confirm` | 全群組亂授；改 item.domain |
| 驗非 super + `allowed={local}` 可讀 277948 | 撤他域既有 grant |

誠實：現 `user_group=0`（admin 僅靠 super）→ 本授對**未來入組之非 super** 生效；admin 本已全見。
