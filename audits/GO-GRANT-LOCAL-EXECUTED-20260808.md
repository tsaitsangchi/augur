---
status: executed
series: local_ai_kh
kind: grant_local_domain
date: 2026-08-08
viewpoint: 2026-08-08T20:50+08:00
go: audits/GO-GRANT-LOCAL-20260808.md
prior: audits/H1-READOUT-INVESTIGATE-EXECUTED-20260808.md
log: /tmp/grant-local/run.log
paste: "GO-grant-local-EXECUTED | local authz=True | 經營管理層→local |非super+{local}→277948 | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜grant-local · 2026-08-08

```text
GO-grant-local | local→authz_boundary | grant 經營管理層→local | verify OK
```

## 結果

| 步 | 結果 |
|---|---|
| 升邊界 | `knowledge_domain.local.is_authz_boundary=True`（label=本機文件） |
| 授域 | `group_domain_grant`(group_id=1 經營管理層, domain=local, granted_by=cli) |
| 帳 | `knowledge_access_audit` #67 add_domain · #68 grant_domain |
| 非 super ∧ `{local}` | resolve **`[277948]`** · cites=**5** |
| 非 super ∧ `{biology}`／∅／None | **0**（fail-closed 仍在） |

## 誠實殘

- `user_group` 仍 **0**（admin 靠 super）；本授對**入組非 super** 生效。
- `granted_by=cli`＝既有 CLI 慣例（治權簽名殘議另冊）。

## 未動

市場 hold-#1；AUTO-LIFT 默開；KH8；設超管。

*完。*
