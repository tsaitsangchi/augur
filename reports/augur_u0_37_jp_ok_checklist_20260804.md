# U0-37｜`jp.daily_bar` jp-ok 備料 checklist（prep only · 2026-08-04）

> **位階**：[I]。**依據**：`audits/U0-STRUCT-378097-20260804.md`＋`reports/augur_u0_struct_next_paths_20260804.md`。  
> **2026-08-04 11:23+08**：Steward `Q-R8=jp-ok` → **unlocked**（`audits/U0-37-JP-OK-20260804.md`）。  
> **2026-08-04 ≈11:34+08**：平行 SYNC4 收完整 `REGISTRY-GO` → **EXECUTED**（`audits/U0-37-REGISTRY-EXECUTED-20260804.md`）；honesty **已消費**。

---

## 1. 欄位切分（文件定錨）

| 通道 | 欄 | 角色建議 |
|---|---|---|
| binding **37** observation | `Open`,`High`,`Low`,`Close`,`Volume` | `channel_role=observation`；concept＝`jp.daily_bar` |
| **第二** binding（未建／未授） | `Adj_Close` | `channel_role=derived`（W2-3／WM.15）；concept 建議 `jp.daily_bar.adj_close` 或並列 derived 鍵——**人裁** |

- 台股對照：原始／還原分表（binding 75／81）→ 日股同表雙通道才需拆列。  
- 本檔**不**發 dry SQL COMMIT；若日後 dry＝`BEGIN…ROLLBACK` only。

---

## 2. Q-R8 呈案稿（供 Steward 一句）

**問題**：非 `tw.` 命名空間（`jp.*`）是否放行跨市場軸（A.35）。

**建議裁句（擇一貼）**：

```text
Q-R8=jp-ok
```

等價敘事：允許 `jp.daily_bar`（及必要時 derived 鍵）進入 Registry 命名空間；**仍須**另句：

```text
REGISTRY-GO: binding=37 + honesty=37 + decided_by=hugo
```

（STRUCT **未**預發 honesty／COMMIT。）

---

## 3. Prep checklist（本輪狀態）

| # | 項 | 狀態 |
|---|---|---|
| 1 | observation vs `Adj_Close` 出欄整理 | ✅ 本檔 §1 |
| 2 | 第二 binding／derived 通道註記 | ✅ 本檔 §1（文件層） |
| 3 | Q-R8 一句呈案 | ✅ 本檔 §2 |
| 4 | Steward `Q-R8=jp-ok` | ✅ **unlocked**（`audits/U0-37-JP-OK-20260804.md` @11:23+08） |
| 5 | dry SQL（W2／OHLCV；`Adj_Close` 出欄；ROLLBACK） | ✅ unlock §4＋`audits/U0-37-DRY-SQL-20260804.md` |
| 6 | `REGISTRY-GO`＋honesty＝37 | ✅ **EXECUTED／已消費**（`audits/U0-37-REGISTRY-EXECUTED-20260804.md`） |

**binding 37**：無需再貼 REGISTRY-GO（已綠）。`Adj_Close` 第二通道仍人裁殘。

---

*完。jp-ok unlocked；Registry EXECUTED。*
