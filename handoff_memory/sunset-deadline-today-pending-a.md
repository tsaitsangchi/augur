---
name: sunset-deadline-today-pending-a
description: "【已結案 2026-07-31 19:45】V2-SUNSET-r2 經 Steward 親簽裁 evaluated_pass（basis=R1）、三軸續命；R1 使 (a) 於凍結瞬間即滿足且永遠滿足 ⇒ 未來閘沿用 (a) 現行文字即無鑑別力"
metadata: 
  node_type: memory
  type: project
  originSessionId: b877d307-e736-407a-aa6a-200f3758f684
  modified: 2026-07-31T11:47:49.184Z
---

## ⚖ 已結案（2026-07-31 19:45:26，Steward hugo TTY 親簽）

```
V2-SUNSET-r2  status=evaluated_pass  ruled_by=hugo  ruling_basis=R1  consequence_executed=false
```

**裁 (a) 達成 ⇒ SUNSET 1/3 ⇒ 三軸續命。** 該列已終態、trigger 拒絕一切後續 UPDATE。
AI 之證據整備結論（傾向 R2/R3＝未達成）與裁決不同，**二者一併留檔不予刪改**——
證據是證據、裁決是裁決（`reports/augur_sunset_a_ruling_evidence_20260731.md`，commit `234ea33`）。

**⚠ 前瞻（下次開停損閘必讀）**：R1 之依據含 2026-07-11 那批 `evaluated_fail` 之
`result_snapshot`，該等快照為**不可變史料** ⇒ **任何沿用 (a) 現行文字之未來閘，
其 (a) 分支於凍結瞬間即滿足且永遠滿足**、停損失去鑑別力。新閘判準須改寫。

**⚠ consequence 仍無機械載體**：`evolution_kill_switch` 四 scope 全 clear；
`run_evolution_iteration.py`（tw）與 `run_raw_evolution_iteration.py`（raw）對其**引用各 0 處**；
無封存／halt 腳本。⇒ 即使日後裁 fail，「三軸整體停止」也只停在文字上，須先實作。

**工具**：`scripts/settle_sunset_gate.py`（兩路徑、強制 TTY、settle-fail 另需逐字確認、
`--basis` 必填記讀法）；`scripts/gate_raise_sunset_deadline.py`（GATE-raise 開新列＋supersede）。

---

## 以下為裁決前之經過（史料）

**2026-07-31 19:05 hugo 親簽落地**（DB 實查）：

```
V2-SUNSET     superseded   deadline=2026-10-31   （史料）
V2-SUNSET-r2  approved     deadline=2026-07-31   approved_by=hugo
兩列 evaluated_at 皆 NULL —— **未結算、無任何軸停止**
```

指示原話：「**92 天後還是會撞到。改今天**」——等待不使判準歧異消失，只使其在更趕的時點爆發。
（同日曾一度撤回後重新指示；沿革如實記於 `scripts/gate_raise_sunset_deadline.py` 檔頭。）

## 現在到期而未決的事：(a) 之解釋

(b)(c) 今日實查**皆明確未達成**（prodset active 仍＝2、基線 2；複現臂＝無）
⇒ **分數完全繫於 (a) 一條**。

⚠ **「凍結原文 vs 程式」是誤 framing，已於同日推翻**（AI 原持此框架並建議「(a) 達成」，
經 7 路對抗審議＋親驗後**自我推翻**）。實為**三種讀法**：

| | 讀法 | 判定 |
|---|---|---|
| R1 | 任一 `direction_gate` 列有可讀之數 | 達成 |
| **R2** | **arena 之**方向門產出可評之數 | **未達成** |
| **R3** | 程式：`status='evaluated_pass' > 0` | **未達成** |

**R2 與 R3 今日結論相同**（差集筆數＝0），故「嚴尺未走 GATE-raise」之程序爭點翻不動結論。

**R1 之決定性反證（親驗）**：六個 `dgate_arena_*` 之 `evaluated_at`／`result_snapshot` **全 NULL**；
那 12 個有數字的 `evaluated_fail` **無一為 arena 門**（10 個係 07-11 已判死之舊門、2 個係 replay 軌）；
且 `audits/V2-ADOPTED-SUNSET-20260726.md:32` 於簽字當日逐字寫「『方向門有可讀數』**未達**」，
**而那 10 門連同 snapshot 當時就已在庫** ⇒ 簽字者明知其存在仍判未達。

⇒ **(a) 未達成、0/3。**

**但 0/3 ≠ 程式沒有產出**（本案最具行動性之發現，親驗）：
- **(b) 之失敗係治理吞吐失能**——`cycle_position_252d` **自 run 11 起連續十輪** G-PROM ∧ G-ECON 雙綠
  （run 20：`hac_t=3.52`／`mean_ic=0.088`／`hit_rate=0.78`／`n_panels=64`／三 seed_delta 全正），
  但**從未 APPLY**：I5 預設 `apply_allowed=false`，人閘碼 **`TWEVO-APPLY-go` 從未開啟**（須 hugo 親跑）。
  ⚠ (b) 尚要求「符號一致性檢查」，其實作位置 **UNKNOWN**（`G-PROM.checks` 只有 hac_t／asof_ic／multi_seed_delta）。
- **(c)** 部分歸因於 07-31 始修之機械故障鏈。**(a)** 非「評估後不合格」，是 arena 門**從未被評估**。

**結算在機械層做不到**：`evolution_kill_switch` 四 scope **全 clear**；
`run_evolution_iteration.py`（tw）與 `run_raw_evolution_iteration.py`（raw）對 kill_switch **引用各 0 處**
（僅 PME 3 處）；**無封存／halt 腳本**；無依 deadline 自動動作之 code。
**且終態不可逆**——trigger 對 `evaluated_*`／`superseded` 之列拒絕**全欄 UPDATE**、連 supersede 亦不可能
⇒ 設 `evaluated_fail` ＝以最大不可逆性換取零機械效果。

**此屬 `AUGUR-MC §8.1` 條文解釋，專屬 Steward。AI 不得代判、不得寫 `evaluated_at`。**
全文＝repo `reports/augur_sunset_a_ruling_evidence_20260731.md`（commit `c920373`、標籤 `sunset-a-evidence-20260731`）。

## 結構缺口（比本案本身更值得記住）

`prereg_gate_no_goalpost` trigger 守的是 **DB 列**（DELETE／終態列／`criteria_sha`），
**守不到「解釋 criteria 的那支程式」**。故程式得以私自實作一把與凍結文字不同的尺，
而無任何機械紅燈。**往嚴改亦是挪門柱**；本專案有明文程序（升嚴走 GATE-raise 開新列），
該較嚴之尺**從未走過**。

⇒ 判斷句：**「凍結了判準文字，有沒有一併凍結解釋它的那支程式？」**
見 [[guard-mechanisms-that-silently-fail]] 型態 7。

## 相關

- 全文留痕＝repo `scripts/gate_raise_sunset_deadline.py` 檔頭；commit `a21fd35`；標籤 `sunset-deadline-today-20260731`。
- [[augur-self-evolution-plan-map]]（V2 總控地貌；其中 SUNSET 三條件之描述早於本次 GATE-raise，deadline 欄已過期）
- [[eval-boilerplate-floor]]（(c) 之量尺問題：零知識 robot 臂曾過地板）
