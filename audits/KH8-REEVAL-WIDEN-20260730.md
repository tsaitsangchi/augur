# 留痕 — KH 深度重評 145,949 件 ＋ KH8 母體擴大（閘自解）2026-07-30

* **Steward 拍板**：「**重評 145,949 件**」→「**把 KH8 母體擴大（讓三分量真有變異、閘自動解除）**」（hugo，2026-07-30，兩則連續指示）
* **繕打／施作**：claude（Fable 5）〔不冒充親簽 `AUGUR-MC v1.6 §8.1`〕
* **起因**：獨立核驗（`wf_b9308bce-be4`）判 FAIL，證明 145,949 件之 `admit_depth=9` 係以**零變異之 KH8 橡皮章**取得（母體選擇效應致 `terminal`／`embed`／`kh4_ok` 恆 1.0、score 底線 0.72、必落 high band）。

---

## 一、重評（甲案；`scripts/reevaluate_kh_depths.py`）

| | 值 |
|---|---|
| 重評前分佈 | `[(3, 396), (7, 3), (9, 145949)]` |
| 重評後分佈 | `[(3, 396), (7, 145952)]` |
| 帳本列數 | `knowhow_depth_reevaluation` **145,949** 列（`depth_before=9 → depth_after=7`） |
| 理由（逐列記載） | `KH8 fail：母體無鑑別力（kh8_non_discriminating）→ 收斂至 7` |

**口徑（誠實界定）**：鑑別力檢定為**母體級**（全域一致），故逐 item 只讀其既存 weight 之 band 即可得新 verdict——**不重算輸入、不寫新 weight 列**（輸入未變、重算必得同值，且會使該表多 145,949 列冗帳）。**`depth 0–7` 之既有判定不重驗、亦不撤銷**；不刪任何列；`knowhow_evidence_weight`／`knowhow_synthesis_run` 未動（已發生之評估事實屬史料）。

**工具紀律**：`--selftest` 六項全綠，含**反向鎖**「有鑑別力＋band high＋depth9 → 保留 9」——確保它不是無條件降級器。批次 5,000、可續跑、逐列留帳（append-only，DDL 無 DELETE）。

⚠ **guard 缺口（誠實揭露）**：`knowhow_auto_admit_state` **無任何 trigger**，故本次 UPDATE 未受機械閘保護；帳本是唯一留痕。該表之 honesty guard 應補（列殘餘）。

## 二、母體擴大（治本；`compute_knowhow_evidence_weight.py --widen`）

**病灶**：原僅對 `min_depth=7` 之 item 加權（`list_candidate_item_ids(min_depth=7)`）⇒ 三分量對全母體恆 1.0 ⇒ **指標結構上不可能鑑別**。

**處置**：新增 `--widen`（取 `max_depth_lt=7`，即有原文但未終態／未嵌入／非 eligible 者）納入加權母體。**非放寬判準，而是讓判準所需之變異真實存在。**

**結果（實測）**：

| | 擴大前 | 擴大後 |
|---|---|---|
| 母體 n | 145,949 | **146,348** |
| bands | `['high']` | **`['high','absent','low']`** |
| 三分量變異數 | terminal=1／embed=1／kh4_ok=1 | terminal=1／**embed=2**／**kh4_ok=2** |
| `population_discriminates` | `ok=False` | **`ok=True`** |

**閘已自動解除**——如設計所預期之自癒（無人工旗標、無須再開會）。

⚠ **殘餘一（誠實）**：`terminal` **仍無變異**（1 種值）——閘是靠 `embed`／`kh4_ok` 之變異開的。判準為 `max(t,e,k) ≥ 2`，故成立，但「三分量皆有變異」尚未達成。
⚠ **殘餘二（更重要）**：**指標仍不鑑別「它所通過者」之間的差異**——145,949 件仍全為 `band=high`，僅 `cite_norm` 在動。「母體具鑑別力」≠「band=high 是強的 per-item 證據宣稱」。**故 depth 9 之回復僅代表「指標非結構性盲目」，不代表該 item 之證據強度已被證明。**

## 三、連帶效果與未做之事

- **乙之排序閘**（`set_kh_evidence_validity`）現回 `ok=True` ⇒ **深度優先排序已自動生效**（先前為關閉）。故並行 session 之 KH9-first 引文排序自此開始作用。
- **145,949 件現在 depth 7**，可經 `run_knowhow_auto_admit.py --until-empty --apply-up-to 9` 合法重新升至 9（此時 KH8 之 pass 有母體鑑別力為前提）。**本次未執行該再推進**——未經指示，且應由 Steward 決定何時放量。
- **P8 自毀條款之處置仍待裁**：補正雖已依核驗建議修正並經實測，但「認定失效之技術觸發」是否溯及、如何記錄，屬 Steward 事項。
- **第三次獨立核驗未做**：本批（乙＋丙＋重評＋擴大）尚未受核驗；前兩批一 FAIL 一 PASS-WITH-FINDINGS，故不以自測綠燈自稱已驗。

## 四、機械驗證

- `reevaluate_kh_depths.py --selftest` → GREEN（6 項）
- `evidence.py --selftest` → GREEN（含四項新增鑑別力自測）
- `migrate_kh_gate_guard_ddl.py --check` → PASS（機械閘就位；實測核驗者之繞過 UPDATE 已被擋）
- `check_cmd_matrix.py` → 全數通過
