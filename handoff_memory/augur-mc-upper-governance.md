---
name: augur-mc-upper-governance
description: "augur 已受外部上位憲章 AUGUR-MC v1.3 約束(Layer 0 lex superior)——四治權檔 Layer 登錄、Steward 裁決 2026-002、AUD-02 critical(#7 違憲)、補正期 2026-10-14、三條未併 remediation 分支;憲章原文不在本機故本機無法驗證合憲性"
metadata: 
  node_type: memory
  type: project
  originSessionId: aac75e63-bffa-4a09-be73-f8f4937ad7f1
---

**2026-07-17 認知**:hugo 於另一會話建立 `augur-constitution` repo,augur **不再是自身治權的最高權威**——五治權檔之上有 **AUGUR-MC v1.3(Layer 0 lex superior,§0.6)**。日後任何治權工作都須認知此上位體系存在。植入點=單一 commit `493fd73`「憲章從屬聲明 + SSOT 正名(RULING-2026-002 主文五交辦)」,tag `augur-mc-v1.3-compliance-seal`。

**Layer 登錄(Steward 裁決第 2026-002 號 / Amendment Log AL-2026-006)**——2026-07-17 實查各檔檔頭 `grep AUGUR-MC`:

| 檔 | Layer | 實測 |
|---|---|---|
| `docs/系統核心思想_v1.8.0.md` | **Layer 1(World Model)** | 命中 1;兼 AUGUR-WM v1.0 領域前身文件(§WM.6) |
| `docs/原則精華_v1.9.1.md` | **Layer 4(Knowledge System)** | 命中 1 |
| `CLAUDE.md` v1.29 | **Layer 6(Agent Runtime)** | 命中 1 |
| `docs/系統架構大憲章_v1.46.0.md` | **Layer 7(External Interface/Infra)** | 命中 2;**自稱「最高承載文件」已被限縮**於 augur 領域架構、位階受 MC 約束(牴觸即無效 §0.6(a)) |
| `README.md` | **(無檔頭)** | **命中 0**——⚠ `HANDOFF.md:80` 稱「5 治權檔已加從屬聲明」,實測**只 4 檔有、README 無**。差一檔,係漏做或不需要待確認。 |

**AUD-02(critical)=一部宣稱「20 條皆不可違反」的法律,自承其中一條違憲**:
- 原則精華 **#7**(correction＝`ON CONFLICT DO UPDATE` 覆蓋為當前值＝**last-write-wins**) **牴觸 `AUGUR-MC v1.3 §P4.E5`**(明禁 last-write-wins;§8.4 **不可豁免**)。
- `docs/原則精華_v1.9.1.md:3` **檔頭主動掛「⚠️ 已知緊張」自曝**(誠實,非被抓包)。補正方案＝`docs/remediation/AUD-02-raw-supersede-log.md`(#7 條文改「新版本入庫、舊版標 superseded」,**須 Steward 拍板、code 不先行**)。
- **更深一層(修完 AUD-02 仍不合規)**:`sync_by_date` 每日 resume 自 `max(date)` 重抓,經主路徑無痕覆寫;補它須違反已拍板之「主路徑一 byte 不動」硬約束 → HANDOFF **誠實升 Steward(事項 A)** 而非假裝修好。
- **T5 順序悖論**:#7 現行條文命令「無獨立修正程式:correction＝重跑正常 sync」;`raw_supersede_log` 一 apply,heal 路徑就不再只是「重跑正常 sync」→ **須先改 #7 條文、後 apply**,反序則 apply 當下即技術性違反 #7 字面。

**⚠ 本機不可驗證(最重要的誠實揭露)**:`/home/hugo/project/augur-constitution` **不在本機**(2026-07-17 實查 ls 不存在)。**一切關於 §P4.E5／§0.6／§8.4／§WM.9／RULING-2026-002 之敘述,來源皆為 augur 自身文件之轉述、非原文**。→ **本機無人能真正驗證合憲性**;要動治權須先取得 constitution repo。本地僅見 AUD-02 全文(`docs/remediation/AUD-02-raw-supersede-log.md`),AUD-01/03..25 內容與級別未知。合規聲明補正期 = **2026-10-14**(四檔檔頭皆載);⚠ 合規聲明**本體**目前不存在(檔頭只一行從屬聲明,原則精華:3/憲章:3 稱「由本檔合規聲明載明」但兩檔內未見該本體,待補或存外部 repo)。

**三條未併 remediation 分支**(2026-07-17 實查 `git branch -a`,皆在 `remotes/origin/`):
`remediation/aud-02-consolidated` / `remediation/aud-02-raw-supersede-log` / `remediation/impl-2026-07-17`
- 實作(含 main 上不存在的 `src/augur/identity/`、`execution/` 兩 package + 9 張新表)受四步部署閘(#7 實測→#19 逐檔→owner≠應用角色→P5 拍板);
- ⚠ 分支可能仍持有舊檔名 `docs/原則精華_v1.9.0.md` → 合併時注意別讓 v1.9.0 復活成第二份法律(違 #12 單一住所)。

**How to apply**:治權工作(改判準/升版/合規宣稱)一律先問「這條有沒有上位 MC 對應條款?」;**判準值變更＝Steward 裁決事項,AI 不得改任一側**。關聯 [[arena-g1g5-admission-plan]] [[augur-project-map]]。
