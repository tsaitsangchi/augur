---
status: draft
series: c_track_structure
depends_on:
  - reports/augur_project_optimization_plan_r6_20260804.md
  - src/augur/execution/action_log.py
  - scripts/migrate_automation_action_ddl.py
---

# C 軌 P1 — `action_log` 三決策點接線盤點（2026-08-05）

> **性質**：[I] 盤點＋接線 plan-first（CLAUDE #20／r6 §C P1）。**本檔先讀碼定落點**；未授權前不改生產呼叫（`run_evolution_iteration` 之 `TEMP-RED-CHECK` 除外見 §3——屬已插入之未完成接線，修補仍須明示）。
> **self-reported（#32a）**。PC002 live 親查：`automation_action_log`／`authorization_grant` **表存在、皆 0 列**（2026-08-05）。

---

## 0. 一句話

**API 與 DDL 已在；三個「真改 Reality」決策點中，evolution I5 有自測絆線但生產路徑被 `TEMP-RED-CHECK` 掐斷（`action_id=None` 永不 `log_action`），`predict_asof`／`decide_sim_verdict` 仍零引用；且 `authorization_grant` 零列 → 即使接上 `log_action`，`authorization_ref` 也只能先 NULL（過渡）或先種子授權列。**

---

## 1. API 契約（既有，不改）

`src/augur/execution/action_log.py`：

| 函式 | 義務 |
|---|---|
| `log_action(cur, actor_identity, authorization_ref, knowledge_basis, action_type, target=None, expected_effect=None) → action_id` | 寫 `status='started'`；缺 actor／action_type → ValueError |
| `link_observed_effect(cur, action_id, attestation_result_id, status=..., ended_at=...)` | 收尾；允 UPDATE，禁 DELETE |

DDL SSOT＝`scripts/migrate_automation_action_ddl.py`（已 apply 本機）。

---

## 2. r6 指名三決策點 — 落點表

| # | 腳本 | 「真改 Reality」條件 | 建議插入點 | 現況 |
|---|---|---|---|---|
| **1** | `scripts/run_evolution_iteration.py` | I5 且非 dry-run 且 `allow_apply` 且外呼 `apply_evolution_promotions` rc 已知 | `_do_step`：在 `_run_cmd` **前** `log_action`；後 `link_observed_effect` | **半接線**：註解＋selftest 絆線在；生產 `action_id = None  # TEMP-RED-CHECK`（約 L334）→ **永不留痕**；表仍 0 列 |
| **2** | `scripts/predict_asof.py` | `--run` 且非 `--dry-run`，寫入 `prediction_values` 之 transaction 內 | `emit`／出單函式：DELETE+INSERT 成功前後 | **零** `action_log` import／呼叫 |
| **3** | `scripts/decide_sim_verdict.py` | `--apply` 且 verdict∈{killed,undecidable}，`_insert_verdict` 成功後 | `_insert_verdict` 返回後或包一層 | **零**引用；**promoted 路徑本就不寫**——留痕只應覆蓋 killed／undecidable |

**不在本三點、但歷史文件曾提**：`watchdog`／`selfheal`／`daily_maintenance`（CODE-MIGRATION Phase 5）——屬擴大範圍，本檔不納入 Phase 0，列殘餘。

---

## 3. 關鍵發現：I5 `TEMP-RED-CHECK`

```334:341:scripts/run_evolution_iteration.py
    action_id = None  # TEMP-RED-CHECK
    rec = _run_cmd(step, argv, dry)
    if step == "I5" and not dry and rec["rc"] == 0:
        rec["gate_ref"] = gate_ref
    if action_id is not None:
        action_log.link_observed_effect(cur, action_id, None,
                                        status="completed" if rec["rc"] == 0 else "failed")
```

- selftest（約 L792+）用 mock 斷言「I5 真寫時必呼 `log_action`」——**2026-08-05 親跑已驗紅**：`✗ I5 真寫時 log_action 有被呼叫` → 隨後 `IndexError`（`_al_calls` 空）。此為 #35「先驗紅」之正確狀態：絆線在、生產掐斷被抓到；**修接線後須再驗綠**。
- **修法方向**（授權後）：I5 ∧ ¬dry → `log_action(...)` 賦值 `action_id`；移除 `TEMP-RED-CHECK`；保持 dry-run／非 I5 零留痕（既有自測契約）；修後 `--selftest` 須全綠。

---

## 4. 前置：`authorization_grant` 種子

| 現況 | 含義 |
|---|---|
| grant 表 0 列 | 無結構化授權可 FK |
| `log_action` 允 `authorization_ref=None` | docstring：僅過渡期；自動行動精神上應有授權 |

**Phase 0a（建議先於／並行接線）**：Steward 明示至少一列 grant（例：scope＝`evolution_apply`／`predict_asof_write`／`sim_verdict_kill`，依據＝既有拍板碼如 `TWEVO-APPLY-go`／`predict-asof-write-go`）——**內容照錄、不代簽**。  
無種子時接線可先 `authorization_ref=None`＋`knowledge_basis` 記 `gate_ref`，但須在帳上標「過渡、待補 grant」。

---

## 5. (a) schema／(b) 程式規畫

| 項 | 規劃 |
|---|---|
| 新表 | **無** |
| `authorization_grant` | 種子 INSERT（admin／遷移腳本一次性；非 hand-patch 業務數值） |
| `run_evolution_iteration.py` | 去掉 TEMP-RED；I5 真寫路徑接 `log_action`＋`link` |
| `predict_asof.py` | import＋非 dry-run 寫庫成功後留痕（actor＝`predict_asof`／服務 identity） |
| `decide_sim_verdict.py` | `--apply` 寫 killed／undecidable 後留痕 |
| 回歸鎖 | 各檔既有 `--selftest` 擴下游絆線（#35：禁字面、先驗紅） |

**建議 `action_type` 字面（資料非邏輯；若頻繁增刪可後遷 DB）**：`evolution_apply`／`predict_values_write`／`sim_verdict_write`。

---

## 6. 分階段

| 階段 | 內容 | Gate | 另授權？ |
|---|---|---|---|
| **Phase 0（本檔）** | 盤點完成；親跑 I5 `--selftest` 記紅／綠 | 本檔＋stdout | 已做盤點 |
| **Phase 0a** | grant 種子列（Steward 內容） | `SELECT count(*)>0` | 是 |
| **Phase 1** | 修 I5 TEMP-RED＋兩點接線 | 自測綠；一次真實／dry 對照：dry 零列、真寫≥1 列 | 是 |
| **Phase 2** | watchdog／daily_maintenance（可選） | 另 plan | 是 |

---

## 7. 硬邊界

- 不因接線放寬 APPLY／promoted 人閘；`decide_sim_verdict` **仍拒寫 promoted**。
- 留痕失敗策略（待裁）：fail-loud 阻斷寫入 vs 寫入成功但 log 失敗告警——建議 **I5／predict 採 fail-loud**（六元組精神），sim kill 可同。
- skip-sync；不碰 FinMind／FRED。

---

## 8. 請 Steward 裁示

1. **inventory_ok** — 接受本盤點；下一步只修 I5 TEMP-RED（最小）
2. **wire_all_three** — 授權 Phase 0a 種子＋三點全接（推薦完整 C 軌 P1）
3. **grants_first** — 先只種子 `authorization_grant`，接線另句
4. **defer** — 表留 0 列，本輪不接

---

*定版（2026-08-05）。零 CPU 盤點完成；實作待上表裁示。*
