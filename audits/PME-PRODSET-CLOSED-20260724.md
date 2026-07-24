# PME PRODSET CLOSED — 生產特徵集真寫登錄 [I]（2026-07-24）

* Steward 約定：U7 DONE 後立刻開「PME 補生產集登錄」
* 輸入：U-PME **F-U-PME-7**／G-PME-PRODSET=partial；U7 **F-U7-2／5**（G-R7-1）
* 硬邊界：零 FinMind／FRED；不改 [N]；不自動下單；**不**把 PRODSET 假稱可交易／確立級
* 證據錨：本檔＋`src/augur/philosophy/evolution.py`＋`scripts/apply_evolution_promotions.py`＋`scripts/migrate_philosophy_evolution_ddl.py`＋`scripts/verify_roadmap_r7_gate.py`

---

## 1. 裁決：真寫（非消歧）

| 項 | 結論 |
|---|---|
| 方案 | **真寫**新表 `evolution_production_feature_set`（philosophy 域 allowlist） |
| 為何非既有表 | live 盤點：無 `production_features`／feature allowlist；僅 `model_registry`（模型身分證，非特徵登錄） |
| 為何非消歧 | 落點合理、DDL 冪等、APPLY 同交易寫入；**無需**改 [N]／預測熱路徑 |
| 語義邊界 | 登錄＝PME APPLY promote 之可查帳本；**≠**可交易／確立級／`canonical_features`／predict 自動納入 |

---

## 2. Schema／路徑

```text
evolution_production_feature_set
  feature PK
  set_status ∈ {active, removed}
  source_run_id / source_queue_id / apply_log_id / principle_id / last_action
COMMENT: PME 生產特徵登錄（philosophy 域）；≠可交易/確立級；≠predict 熱路徑自動納入
```

| 動作 | 寫入 |
|---|---|
| APPLY `promote` | UPSERT `set_status=active` ＋ `production_set_delta` 含 `table`／`set_status` |
| APPLY `demote` | UPSERT `removed`（路徑預留；本輪無 demote APPLY） |
| `freeze` | **不**寫 prodset |
| `--backfill-prodset` | 對已 `applied` 之 promote／demote 冪等補登錄 |

---

## 3. 親驗（零 API）

| 指令 | 結果 |
|---|---|
| `python -m augur.philosophy.evolution --selftest` | 全通過（DDL 六表＋prodset 純函式） |
| `python scripts/migrate_philosophy_evolution_ddl.py --selftest` | 全通過 |
| `python scripts/migrate_philosophy_evolution_ddl.py --run`／`--verify` | 表齊；kill 種子 OK |
| `python scripts/apply_evolution_promotions.py --selftest` | 全通過 |
| `python scripts/apply_evolution_promotions.py --backfill-prodset --run-id 5` | **n=2** |
| live `SELECT` prodset | `inst_cumflow_position_120d`／`volume_gini_60d` → **active**（run_id=5；q=98／127；apply_log=1／2） |
| apply_log delta | 含 `"table":"evolution_production_feature_set","set_status":"active"` |
| `verify_roadmap_r7_gate.py --selftest` | 全通過（含幽靈詞可抓） |
| `--check` P-PME | fail=0 |
| `import_isolation`／`pytest tests/test_philosophy_isolation.py` | exit 0／9 passed |

---

## 4. Gap

| ID | 後 | 說明 |
|---|---|---|
| **G-PME-PRODSET** | **none** | 真寫表＋APPLY／backfill；run5×2 已登錄；**仍禁**讀成可交易／Efull |
| **G-R7-1** | **doc-only**（縮小） | 禁語表已補「生產特徵集已登錄」「Dividend…完備」→ G-P9 FAIL；殘留＝結構哨兵≠語義／空殼四判準（U7 F-U7-1） |

---

## 5. 重放路徑

```bash
python scripts/migrate_philosophy_evolution_ddl.py --run
python scripts/apply_evolution_promotions.py --backfill-prodset --run-id 5
# 未來 pending_auto：python scripts/apply_evolution_promotions.py [--run-id N]
```

---

## 6. 建議下一句

* Steward 可採納本 CLOSED／G-PME-PRODSET=none  
* 可選：S4 顧問解讀；或靈魂措辭另案（G-PME-SOUL pending）  
* **禁**：解凍 FinMind／FRED；禁把 prodset active 說成確立級可交易
