# PME A7 CLOSED — status 對齊規則（非假綠）[I]（2026-07-24）

* Steward 事先約定：U-PME 後立刻「**PME 補 A7（非假綠）**」
* 輸入：`audits/PME-ULTRACODE-20260724.md` F-U-PME-5；計畫驗收 A7；Gap `G-PME-STATUS`
* **硬邊界**：零 FinMind／FRED；不改 [N]；**禁**把 desync／missing／blocked_div／閘紅靜默翻 `validated`
* **CLOSED 含義**：A7 **抽樣／分類規則釘死**＋違規＝0＋可機械 heal 路徑就位；**≠** 全量原則已 validated、≠ PRODSET、≠ PME-Efull、≠ 可交易

---

## 1. 前後對照（親驗）

| 指標 | 前（U-PME） | 後（本輪） |
|---|---|---|
| `principle_status` | untested=24／validated=2 | **同**（未假翻） |
| `raw_desync(untested∩validated_*)` | **21** | **21**（保留為粗指標） |
| A7 細類 | 未釘 | `map_evidence_gate_rejected`=21／`aligned_validated`=2／`coverage_blocked_or_missing`=3 |
| `a7_violations`（fake_validated∨apply_lag） | （未定義） | **0** |
| `a7_closed` | partial | **True** |
| `--apply` heal | — | syncable=0；healed=0（無假綠可回滾、無 apply_lag） |

指令（零 API）：

```text
./venv/bin/python -m augur.philosophy.evolution --selftest
./venv/bin/python scripts/sync_philosophy_principle_status.py --selftest
./venv/bin/python scripts/sync_philosophy_principle_status.py
./venv/bin/python scripts/audit_philosophy_feature_coverage.py --inventory
```

---

## 2. 規則摘要（釘死）

1. **`status=validated` ⇔ 存在 promote APPLY 證據**（`promotion_queue`＋`evolution_apply_log`）；僅 map `validated_*` **不足**。
2. **raw desync**（untested∩validated_*）在 **閘紅 `rejected_gate`** 下 → 類別 `map_evidence_gate_rejected`＝**誠實殘留**，**≠** A7 違規，**禁**翻 validated。
3. **A7 違規**僅：`fake_validated`（無 APPLY 卻 validated）／`apply_lag`（已 APPLY 未翻 status）。
4. **機械收斂**（`--apply`）只允許：`apply_lag→set_validated`、`fake_validated→rollback_untested`；對 gate_rejected／pending／blocked／missing → **No-op**。
5. **blocked_div／missing** → `coverage_blocked_or_missing`；禁冒充已對齊 validated。

落地：

| 檔 | 角色 |
|---|---|
| `src/augur/philosophy/evolution.py` | `classify_status_alignment`／`sync_action_for_alignment`／`is_a7_violation` |
| `scripts/sync_philosophy_principle_status.py` | 審計＋可選 heal |
| `scripts/audit_philosophy_feature_coverage.py` | S0 印 A7 細類 |

---

## 3. 驗收 A7

| ID | 結果 | 證據 |
|---|---|---|
| **A7** | **PASS（CLOSED）** | 規則釘死；violations=0；21 筆誠實分類為 gate_rejected；validated=2 皆有 promote APPLY；未假翻 |

**不膨脹**：多數 G-PROM 仍 FAIL（帳本 G-PME-PROM partial）；PRODSET／靈魂／U7 另案。

---

## 4. Gap

| ID | 後 | 說明 |
|---|---|---|
| **G-PME-STATUS** | **none** | A7 規則＋違規＝0；raw=21＝gate_rejected 知情殘留 |
| G-PME-PROM／ECON | 維持 partial | 多數閘紅＝為何仍 untested |
| G-PME-PRODSET | 維持 partial | 本輪未做（F-U-PME-7） |

---

## 5. 建議下一句

「**PME 補生產集登錄（消歧或真寫）**」或「**開 U7**」（靈魂措辭另案；FZ-keep）。
