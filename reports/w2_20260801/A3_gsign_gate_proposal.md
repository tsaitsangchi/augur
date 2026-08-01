# [DRAFT 呈案] A3｜G-SIGN 入 GATE_IDS 四件套——完整呈案（未經拍板不得施作）

> **日期**：2026-08-01（六）下午｜**呈案人**：AI（W2 呈案批）｜**裁決**：專屬 Constitution Steward（`AUGUR-MC v1.6 §8.1`／L6.18(a)）
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，所涉之閘直接約束 AI 自身的自動晉升通道（方向為收緊而非放寬）；本檔僅為草擬與呈案，判準變更之核准權不在起草者。
> **設計 SSOT**：`reports/augur_problem_solution_register_20260801.md` §3-A3＋`reports/augur_steward_adjudication_sheet_20260801.md` A3 項＋`reports/augur_evolution_execution_plan_20260731.md` W3 節（四件、T3/T4 出處）。本呈案＝親驗 live 現況＋展開為可拍板全文，**不重新設計**。
> **親驗基準**：git HEAD `e00135c`（A1 sign 落帳 commit）；DB 現查時刻 2026-08-01 15:2x；所有數字出自 §2 之 SQL／指令輸出（#9/#10）。

---

## §0 摘要（30 秒版）

SUNSET (b) 逐字要求「每一新成員通過符號一致性檢查」，但符號尺 `verify_sign_consistency.py` 至今**未接進晉升閘**：`GATE_IDS` 七閘無 G-SIGN、`promotion_queue` 全庫 `gate_json ? 'G-SIGN'` 命中 **0 列**（§2 親驗）。A1 已於今日 14:55 補上兩現役的落帳（4 列全 PASS），(b) 首次可機械查證——但**閘本身仍缺**：APPLY 一旦開啟，未過符號檢查的候選可直接入 prodset。本呈案將 G-SIGN 以「四件套」釘進**判準單一住所** `src/augur/philosophy/evolution.py`（#12），並對既存 77 筆 `pending_auto`（親驗現查）呈三案處置。建議案＝**通過四件套＋UNJUDGEABLE⇒FAIL＋77 筆採乙案（重評＋遷移）**（承裁決呈案單 A3 項）。

---

## §1 問題與授權鏈

### 1.1 問題

1. **閘缺口**：`GATE_IDS =('G-ISO','G-MAP','G-PROM','G-ECON','G-ATTEST','G-KILL','G-NOEXEC')`（`src/augur/philosophy/evolution.py:26-34`）無 G-SIGN；`all_gates_green`（:263）與 `may_apply`（:333）因此**永遠不驗符號**。promote 之自動放行路徑上，符號一致性（SIGN-B-go 判式，hugo 2026-07-28 簽核）只存在於一支獨立腳本與一張今日才有 4 列的落帳表，**不在閘上**。
2. **住所風險**：若圖省事把符號檢查放在 APPLY 腳本（`apply_evolution_promotions.py`），會開出第二個閘住所＝#12 之病（執行計畫 W3 明文禁止；T3 之檢驗標的）。
3. **既存佇列**：G-SIGN 入 `GATE_IDS` 後，舊世代（七鍵）`gate_json` 之 `all_gates_green` 一律 False——77 筆 `pending_auto` 的去向須一併裁定，否則留下「兩種標準判出的列同時 pending」的帳本歧義。

### 1.2 授權鏈（L6.5-L6.8 四要件留痕）

| 要件 | 內容 |
|---|---|
| (a) 範圍 | 呈案文件撰寫；全程唯讀 repo 與 DB（唯一寫入＝scratchpad/w2/ 本檔）；不施作、不 commit、不 DDL |
| (b) 結束條件 | 本呈案完稿交回主 session；施作須另經 Steward 圈選 §7 |
| (c) 可撤銷 | Steward／主 session 隨時收回 |
| (d) 任務參照 | 登錄冊 A3（W2 波次）；上游裁決依據＝Steward 2026-07-31「(b) 射程 all_active、要回頭補」＋SIGN-B-go 判式簽核（2026-07-28）＋執行計畫 W3【Steward】 |

**裁決分工**：四件套之施作、UNJUDGEABLE 落點（FAIL vs SKIP）、77 筆處置案、施作時機＝**Steward 圈選**；圈選後之機械落地與回歸鎖＝AI 執行；`--record`／遷移 SQL 之執行由圈選文字明定歸屬。

---

## §2 現況親驗（2026-08-01 現查；勿沿用舊數）

### 2.1 閘與佇列

```sql
SELECT queue_status, count(*) FROM promotion_queue GROUP BY 1 ORDER BY 1;
--  applied 23 | pending_auto 77 | rejected_gate 452

SELECT count(*) FROM promotion_queue WHERE gate_json ? 'G-SIGN';   -- 0

SELECT action, gate_json->'G-PROM'->>'verdict', count(*)
FROM promotion_queue WHERE queue_status='pending_auto' GROUP BY 1,2;
--  demote  FAIL_SIGN 58
--  promote PASS      19
```

**pending_auto=77**（登錄冊「執行時現查」＝77，與 r3 一致；執行計畫 07-31 寫 67 已過期——run 20 灌入後 +10）。組成：

- **promote 19 列／3 特徵**：`inst_cumflow_position_120d`（2 列，run 3/4——**已是現役**，佇列殘影）、`cycle_position_252d`（16 列，run 11/12/15/16/17/18/19/20 各 2）、`lending_fee_rate_mean_30d`（1 列，run 20）。19 列 G-PROM∧G-ECON 皆 PASS、七鍵齊全（`?& array[七閘]` 缺鍵=0 列）。
- **demote 58 列／10 特徵**：全數 G-PROM=`FAIL_SIGN`（R3 自動除役通道）。`debt_ratio` 31、`gov_bank_net_buy_60d` 8、`top_holders_pct` 4、`volume_gini_20d/60d`·`volume_max_share_20d/60d` 各 3、`market_cap_log`·`momentum_5d`·`volume_surge_5_60` 各 1。其中 **7 特徵已是 prodset removed**（重複除役殘影）、3 特徵從未入 prodset。
- 閘口徑指紋：佇列中 `min_abs_hac_t` 僅一值 **2.0**（77 筆 pending 全帶 thresholds）。

### 2.2 sign 落帳與方向覆蓋

```sql
SELECT feature,h,direction,point_ic,n_panels,verdict,code_sha FROM feature_sign_check;
-- 4 列（A1 今日 13:57 落）：inst_cumflow_position_120d h20/h60 PASS(+0.0095/+0.0331, n=102/100)
--                        lending_fee_rate_mean_20d  h20/h60 PASS(−0.0755/−0.0831, n=22/20)
--                        code_sha=dc6e97a…（全 PASS——含 mean_20d，符號 PASS）
```

- `factor_direction_ruling` 存在、2 列（days_since_high_252d=−1、range_position_120d=+1）。
- 13 個 pending 特徵之 map 方向**全部單一**（n_dir=1、無 conflict、無 NULL）；`feature_values` panel 覆蓋 60–113 個——**重評時無結構性 UNJUDGEABLE 風險**（引擎窗 since 2021-01-01 之 IC 序列遠大於 6）。

### 2.3 時機要素（親驗）

| 檢查 | 結果 |
|---|---|
| heavy slot | `python -m augur.core.heavy_slot` → **持有中＝無** |
| 活引擎進程 | `pgrep -af "run_philosophy_evolution\|run_evolution_iteration\|apply_evolution_promotions"` → **rc=1（無）** |
| TWEVO 車道 | `evolution_iteration_ledger`：tw failed 1／halted 1／succeeded 2、**running 0** |
| `evolution_run` | **status='running' 有 9 列（run 11-19）——全為 07-30/31 殭屍**；run 20 succeeded（07-31→08-01 收）；B1 回填器已備、`--apply` 待裁 |
| kill switch | tw/lai/raw/global 全 clear |
| cron | TWEVO 一至五 23:00（下次触發＝週一 08-03 23:00）；週報週日 09:00；RAWEVO 週六 09:00 已過（不碰 promotion_queue） |

### 2.4 與登錄冊／執行計畫不符處（明標）

1. **「波及 7 呼叫端」**：`build_gate_json` 實際呼叫端＝**6 處**（grep 全 repo：`evolution.py:697`＋`run_philosophy_evolution.py:118/134/153/737/811`）；第 7 個波及點＝`apply_evolution_promotions.py:89-91` 之**手寫七閘 dict**（非 build_gate_json 呼叫，但 `all_gates_green` 改判 8 閘後其 selftest 必炸，同須改）。合計 7 個觸點成立，性質在此明辨。
2. **blast radius「67 筆」（執行計畫 07-31）已過期**：現查 **77**。
3. **「running=0」以 SQL 現查不成立**：`evolution_run` 有 9 筆殭屍 running。真實「無活引擎」須以 §2.3 三查（pgrep＋slot＋ledger）認定，或前置 B1-apply 後才可用 SQL 判（§4.4 時機案已納入）。

### 2.5 本呈案所讀之既有表 schema（#20 v1.39.0 (a)；不新建任何表）

- `promotion_queue`（DDL 住 `evolution.py:131-144`）：`queue_id·run_id·principle_id·feature·action(promote/demote/freeze)·gate_json JSONB·queue_status CHECK∈{pending_auto,applied,rejected_gate,halted}·decided_at·decided_by(default 'evolution_engine')·apply_log_id`。**無 note 欄**；遷移之 provenance 只能落 `decided_by`＋`decided_at`＋審計檔。
- `feature_sign_check`（DDL 住 `scripts/migrate_feature_sign_check_ddl.py:40-58`）：`feature·h·direction·direction_source·point_ic·boot_ics JSONB·n_panels·panels_first/last·verdict CHECK∈{PASS,FAIL,UNJUDGEABLE}·code_sha·checked_at`；append-only、無人簽欄。
- `evolution_run.config_json`（閘組態釘板）、`evolution_iteration_ledger`（gate_scale 快照消費端）。
- **結果落點**：四件套＝純 code（零 DDL）；乙案遷移＝`promotion_queue` 之 DML；run 21 重評新列落 `promotion_queue`＋雙寫 `feature_sign_check`。

---

## §3 方案：四件套逐檔 diff 計畫（單一 commit、缺一不可）

> 行號錨＝HEAD `e00135c` 現行行號。全程零 DDL。#20 (b) 之程式規畫即本節。

### 3.1 件一＋件二：`src/augur/philosophy/evolution.py`（判準單一住所）

**(a) `GATE_IDS`（:26-34）**：尾端加 `"G-SIGN"` → 八閘（順序無語意消費者；置尾使 diff 最小，Steward 可改置 G-PROM 後）。

**(b) `judge_sign` 移居（自 `scripts/verify_sign_consistency.py:38-44` 原文搬入，逐字不改判式）＋新常數**：

```python
# —— G-SIGN(SIGN-B-go 判式簽核 hugo 2026-07-28;自 scripts/verify_sign_consistency.py 移居=#12 單一住所) ——
SIGN_BOOT_SEEDS = 5     # panel block bootstrap 席數（儀器釘死;verify_sign_consistency 同源引用）
SIGN_SEED0 = 42
SIGN_MIN_SERIES = 6     # IC 序列下限;未達=不可判（樣本不足非證據）


def judge_sign(point_mean, boot_means, direction):
    """判式(SIGN-B-go):sign(點估計)==direction 且全部 bootstrap 均值同號才 PASS。純函式。
    0 均值視為不同號(無方向證據≠方向正確);direction ∈ {+1,-1}。"""
    if direction not in (1, -1):
        return "UNJUDGEABLE"
    vals = [point_mean] + list(boot_means)
    return "PASS" if all(v * direction > 0 for v in vals) else "FAIL"
```

**(c) `evaluate_g_sign_from_evidence` 函式全文草稿**（與 `evaluate_g_prom_from_evidence` 同型；純函式、IO 在呼叫端）：

```python
def evaluate_g_sign_from_evidence(
    evidence: Mapping[str, Any],
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """由符號一致性證據裁決 G-SIGN（純函式；判式＝judge_sign，SIGN-B-go 簽核原文）。

    evidence 鍵：
      direction (int|None|'conflict')   — 正典方向（factor_direction_ruling 優先於 map 共識；
                                          呼叫端以 verify_sign_consistency.map_direction 取得）
      direction_source (str)
      point_ic (float|None)             — as-of IC 點估計（**raw 未乘方向**口徑，與 feature_sign_check 同）
      boot_ics (list[float]|None)       — panel block bootstrap 均值（raw 口徑；SIGN_BOOT_SEEDS 席）
      n_series (int)                    — IC 序列長度
      skipped_reason (str|None)         — 整閘無法算（如 coverage_class 非 mapped）時誠實 SKIP

    不可判（無方向／衝突／n_series<門檻／判式輸入不全）之 verdict 落點由
    cfg gates.G-SIGN.unjudgeable_verdict 釘定（預設 'FAIL'＝fail-closed 人閘；Steward A3 拍板欄）。
    一律附 unjudgeable=True 旗標——與「證據俱在而判負」之 FAIL 可機械區分，不混統計。
    **禁用 'FAIL_SIGN' 字串**：該值屬 G-PROM R3 除役通道之保留字（執行計畫 W3 第 3 件）。
    """
    gcfg = dict((cfg or DEFAULT_GATE_CONFIG).get("gates", {}).get("G-SIGN", {}))
    min_series = int(gcfg.get("min_series", SIGN_MIN_SERIES))
    n_boot = int(gcfg.get("n_boot_seeds", SIGN_BOOT_SEEDS))
    unj = str(gcfg.get("unjudgeable_verdict", "FAIL")).upper()

    skip = evidence.get("skipped_reason")
    if skip:
        return {"verdict": "SKIP", "reason": str(skip),
                "evidence": dict(evidence), "thresholds": gcfg}

    def _unjudgeable(reason: str) -> dict[str, Any]:
        return {"verdict": unj, "unjudgeable": True, "reason": reason,
                "judge": "UNJUDGEABLE", "evidence": dict(evidence), "thresholds": gcfg}

    direction = evidence.get("direction")
    if direction not in (1, -1):
        return _unjudgeable(f"direction={direction!r} 非 ±1（無方向/衝突＝fail-closed 人閘）")
    n = int(evidence.get("n_series") or 0)
    if n < min_series:
        return _unjudgeable(f"IC 序列 n={n} < {min_series}（樣本不足非證據）")
    point = evidence.get("point_ic")
    boots = evidence.get("boot_ics")
    if point is None or boots is None or len(boots) < n_boot:
        return _unjudgeable("point_ic/boot_ics 不全（儀器未跑完整判式）")

    v = judge_sign(float(point), [float(b) for b in boots], int(direction))
    return {
        "verdict": v,                      # 此處 v∈{PASS,FAIL}（±1 已前置檢查）
        "judge": v,
        "reason": ("sign consistent: 點估計+全 bootstrap 同號==direction" if v == "PASS"
                   else "sign inconsistent: 點估計或任一 bootstrap 與 direction 異號"),
        "direction": int(direction),
        "direction_source": evidence.get("direction_source"),
        "point_ic": float(point),
        "n_series": n,
        "evidence": dict(evidence),
        "thresholds": gcfg,
    }
```

**(d) `build_gate_json` 新簽名全文（:273-295）**——`g_sign` 為**必填** keyword-only（漏改呼叫端即 `TypeError` fail-loud）：

```python
def build_gate_json(
    *,
    g_iso: Mapping[str, Any],
    g_map: Mapping[str, Any],
    g_prom: Mapping[str, Any],
    g_econ: Mapping[str, Any],
    g_attest: Mapping[str, Any],
    g_kill: Mapping[str, Any],
    g_noexec: Mapping[str, Any],
    g_sign: Mapping[str, Any],
) -> dict[str, Any]:
    """組裝 gate_json（鍵＝GATE_IDS）。g_sign 必填無預設——漏改呼叫端即 TypeError（fail-loud）。"""
    out = {
        "G-ISO": dict(g_iso), "G-MAP": dict(g_map), "G-PROM": dict(g_prom),
        "G-ECON": dict(g_econ), "G-ATTEST": dict(g_attest), "G-KILL": dict(g_kill),
        "G-NOEXEC": dict(g_noexec), "G-SIGN": dict(g_sign),
    }
    for gid in GATE_IDS:
        out[gid].setdefault("verdict", "FAIL")
    return out
```

**(e) `_selftest`（:682 起）**：`len(GATE_IDS)==7` → `==8`＋`"G-SIGN" in GATE_IDS`；:697 green 補 `g_sign={"verdict":"PASS"}`；新增回歸鎖見 §6.2。模組尾公開入口串（:816-819）補 `judge_sign / evaluate_g_sign_from_evidence`。

### 3.2 件四：`DEFAULT_GATE_CONFIG`（:83-103）＋`_gate_scale` 閘集指紋

**(a) `DEFAULT_GATE_CONFIG.gates` 增**（隨 `cfg=dict(DEFAULT_GATE_CONFIG)` 自動釘入每 run 之 `evolution_run.config_json`——「同 run 禁事後改寫」既有紀律不變，故新舊 run 之 config 內容天然分家）：

```python
        "G-SIGN": {
            "n_boot_seeds": 5,
            "seed0": 42,
            "min_series": 6,
            "unjudgeable_verdict": "FAIL",  # Steward A3 拍板落點：FAIL=fail-closed；改 'SKIP' 即乙案
        },
```

並於頂層加 `"gate_set_rev": "8g-sign-v1",`（閘集版本字串；入 config_json 供 provenance／sha 派生）。

**(b) `scripts/run_evolution_iteration.py:131-148 `_gate_scale``**——指紋納閘集，**舊列字串完全不變**（歷史輪對之可比性保留；新舊閘集相鄰輪自動 incomparable）：

```python
    # 兩處 SELECT 皆改為：
    SELECT gate_json->'G-PROM'->'thresholds'->>'min_abs_hac_t', (gate_json ? 'G-SIGN')
    FROM promotion_queue WHERE gate_json ? 'G-PROM' [AND run_id=%s] ORDER BY queue_id DESC LIMIT 1
    # 回傳改為：
    r = cur.fetchone()
    if not (r and r[0]):
        return "unset"
    return f"min_abs_hac_t={r[0]}" + ("|gates=8+G-SIGN" if r[1] else "")
```

跨閘集不可比之機制**已存在**：`src/augur/philosophy/iteration.py:87 compare_gain` 對 `gate_scale` 不等硬回 `(None,'incomparable')`、`next_no_gain_count` 對 incomparable **原地不動**（:110-114）——指紋一變即自動生效，停損計數不受污染，無須改該檔。

### 3.3 件三：`build_gate_json` 之 7 個觸點逐一列（漏一即 selftest/TypeError 紅）

| # | 檔:行 | 性質 | 改法 |
|---|---|---|---|
| 1 | `src/augur/philosophy/evolution.py:697` | selftest green | 補 `g_sign={"verdict":"PASS"}` |
| 2 | `scripts/run_philosophy_evolution.py:118` | selftest skeleton | 補 `g_sign={"verdict":"SKIP","reason":"skeleton"}` |
| 3 | `scripts/run_philosophy_evolution.py:134` | selftest local green | 補 `g_sign={"verdict":"PASS"}` |
| 4 | `scripts/run_philosophy_evolution.py:153` | selftest FAIL_SIGN 路 | 補 `g_sign={"verdict":"PASS"}`（驗 FAIL_SIGN 通道不被 G-SIGN 干擾） |
| 5 | `scripts/run_philosophy_evolution.py:737` | dry-run 組閘 | `g_sign=g_sign_f`（見 3.4 wiring） |
| 6 | `scripts/run_philosophy_evolution.py:811` | live 落佇列 | 同上 |
| 7 | `scripts/apply_evolution_promotions.py:89-91` | **手寫七閘 dict（非 build_gate_json 呼叫）** | tuple 補 `"G-SIGN"` 成八閘；另加「七鍵 green 不放行」紅鎖（§6.2 R6） |

### 3.4 引擎 wiring：`scripts/run_philosophy_evolution.py`（G-SIGN 證據之產生與雙寫）

執行計畫 W3 第 2 件：「複用 judge_sign／build_sign_rows，**同時**寫 gate_json 與 feature_sign_check」。逐段：

1. **import（:35-49）**：evolution import 塊加 `evaluate_g_sign_from_evidence`；檔內 `import verify_sign_consistency as vss`（同目錄 script 互 import，先例＝`run_meta_replay.py:98`）。
2. **`_compute_feature_gates`（:309-）改回三元組 `(g_prom, g_econ, g_sign)`**：
   - 函式已算出 `ic_by_panel`（**已乘 direction 口徑**，:348 preds×direction）。G-SIGN 段：`ics` 序列 ≥6 時以 `SIGN_SEED0+k`（k<5）panel block bootstrap 取 5 席均值；**還原 raw 口徑落證據**：`point_ic = point_adj × engine_dir`、`boot_ics = [b × engine_dir]`（engine_dir＝IC 乘用之方向）。
   - **正典方向另取**：`d, src = vss.map_direction(cur, feature, with_source=True)`（裁決表優先、conflict 偵測——**不得**沿用 :712 `int(m["direction"] or 1)` 之 None→1 硬默認，那會偽造方向）；evidence 同時記 `engine_direction`（IC 乘用值）與 `direction`（正典判定值），二者不一致時如實入 evidence 供稽核。
   - `g_sign = evaluate_g_sign_from_evidence(sign_ev, cfg)`。
3. **`_prom_econ_skeleton`（:245）與 coverage 短路（:698-705）**：改回三元組，第三元＝`{"verdict":"SKIP","reason":"skeleton; sign not evaluated"}`／`{"verdict":"SKIP","reason":f"coverage_class={cls}; G-SIGN not evaluated"}`（skeleton 誠實 SKIP 之既有語意不變）。
4. **`gates_for`（:694）**回三元組；cache 三元組；dry-run 印列（:751-756）加 `SIGN=`；`verdict_tally`（:799,:810,:852）加 `"G-SIGN"`。
5. **雙寫 `feature_sign_check`（僅 live、非 dry-run）**：g_sign 非 SKIP 時，以 `vss.build_sign_rows(feature, d, src, [(h, g_sign["judge"], point_raw, n, boots_raw)], panels, sha)`＋`vss._record_rows` 落一列（判定欄寫 `judge` 三值含 UNJUDGEABLE——表 CHECK 相容；閘 verdict 之 FAIL/SKIP 折算不進表，表存判式原始輸出）。append-only；每 run 每 mapped 特徵 1 列（run 20 口徑≈51 列/run）。
6. **不動之處（明示）**：`FAIL_SIGN` 字串、R3 demote 通道（`decide_queue_status:326`／`may_apply:352-355`——demote 分支**不經** `all_gates_green`，故 G-SIGN 入閘**不影響**既存與未來之 FAIL_SIGN 自動除役）、G-PROM/G-ECON 判式、`--control-arms`。

### 3.5 `scripts/verify_sign_consistency.py`（判式回指單一住所）

- `judge_sign`（:38-44）刪本體，改 `from augur.philosophy.evolution import judge_sign`（模組層 re-export——`run_meta_replay.py:147` 之 `vss.judge_sign` 屬性引用**零改動**即續通）；`N_BOOT_SEEDS/SEED0`（:34-35）改自 library 引用（`SIGN_BOOT_SEEDS/SIGN_SEED0`）。
- selftest（:195-208）既有判式鎖照跑（行為級、餵真輸入，搬家後必須仍綠＝判式逐字未變之證明）；加一鎖：`judge_sign.__module__ == 'augur.philosophy.evolution'`（單一住所斷言，行為級非字面）。
- `--record` 路徑、`map_direction`、`build_sign_rows` 全不動。

---

## §4 選項與建議案

### 4.1 裁點一：UNJUDGEABLE（無方向／衝突／n<6／判式輸入不全）⇒ FAIL 還是 SKIP？

機械後果表（逐消費路徑；兩案在「promote 放行」上**零差異**，差在帳面語意與催辦力）：

| 消費路徑 | UNJ⇒**FAIL**（建議） | UNJ⇒SKIP（替代） |
|---|---|---|
| `all_gates_green`→promote 放行 | 擋（非 PASS） | 擋（SKIP≠PASS）——**同** |
| `decide_queue_status` | rejected_gate | rejected_gate——**同** |
| demote FAIL_SIGN 通道 | 不經 G-SIGN——**同**（無影響） | 同 |
| 週報 (b)／tally 顯示 | **紅**：無方向＝待策展、被催辦 | 灰：像「還沒跑」；無方向特徵永遠灰＝**silent skip 成穩態**（v2 明訓） |
| 證據統計（偽陽率／穩定度） | `unjudgeable=True` 旗標分開統計，不污染真 FAIL 分母 | SKIP 與「儀器沒跑」混一桶 |
| 與 SIGN-B-go 簽核原文對齊 | 「UNJUDGEABLE＝fail-closed 人閘」逐字落地 | 弱化為「缺料再說」 |
| 與 G-PROM 對稱性 | 不對稱（G-PROM 樣本不足=SKIP）——以 `unjudgeable` 旗標保留可區分性補償 | 對稱，但代價＝上兩列 |

**建議＝FAIL**（承裁決呈案單 A3：「FAIL 免與『誠實缺資料 SKIP』混義——符號判不出來不該被當成『先放行』」）。落點做成 `unjudgeable_verdict` 單一 config 鍵（§3.2）：Steward 若改採 SKIP，改一鍵、不改判式。

### 4.2 裁點二：既存 pending_auto 77 筆三案

先釘兩個機械事實（親驗）：G-SIGN 入閘後——
(i) **58 筆 demote/FAIL_SIGN 不受影響**（demote 放行不經 `all_gates_green`），APPLY 一開仍會照舊自動除役；
(ii) **19 筆 promote 成死列**：下次 APPLY 掃到即因缺 G-SIGN 鍵被 `may_apply` 拒、被引擎翻成 `rejected_gate`，reason＝`gates not all PASS`——**把「缺鍵未評」誤記成「閘判不過」**。

| 案 | 內容 | 寫入 | 後果 | 帳本語意 |
|---|---|---|---|---|
| **甲 惰化** | 全不動，等 APPLY 自然淘汰 | 0 | (i)(ii) 照發：19 promote 死列以錯誤 reason 收場；殭屍 run 碎片（run 11-19 之列）長存 pending；debt_ratio 31 重複 demote 屆時灌 31 筆 apply_log | 差：兩世代混雜、死因失真 |
| **乙 重評＋遷移【建議】** | 一筆 DML 把 77 筆收斂（`decided_by='gate_set_migration_gsign'`——engine 欄機器標記、**非人簽**，不觸「不代打人簽」）＋四件套落地後跑 run 21 全量重評（八閘、雙寫 sign 表） | 77 列 UPDATE | 舊佇列一次歸零、死因如實（閘集遷移非閘判）；run 21 產新世代列（含 G-SIGN verdict）；殭屍碎片同時出清 | 好：單一世代、可回滾 |
| **丙 只重評** | 跑 run 21，舊 77 筆不動 | 0（run 21 照常寫） | 新舊兩代同時 pending；APPLY 會**混世代消費**（舊 58 demote 以舊證據自動除役、舊 19 promote 以錯誤 reason 死）；同特徵新舊列並存 | 差：歧義最大 |

**乙案遷移 SQL 全文**（DML 非 DDL；仍帶 lock_timeout 保底；謂詞冪等——只收舊閘集列，重跑零效果；**於四件套 commit 之後執行**）：

```sql
BEGIN;
SET LOCAL lock_timeout = '5s';
UPDATE promotion_queue
   SET queue_status = 'rejected_gate',
       decided_at   = now(),
       decided_by   = 'gate_set_migration_gsign'
 WHERE queue_status = 'pending_auto'
   AND NOT (gate_json ? 'G-SIGN');
-- 預期 UPDATE 77（執行當下以 §6.1-V5 前查現數為準）
COMMIT;
```

（`gate_json` 一字不碰——證據禁事後改寫；`queue_status` 詞彙表無 'superseded'，新增值＝DDL，已評估後**不採**：3c 統一 DDL 窗已滿載，`decided_by` 標記足以機械區分。）

**回滾 SQL**（標記唯一可辨識，可全量還原）：

```sql
BEGIN;
SET LOCAL lock_timeout = '5s';
UPDATE promotion_queue
   SET queue_status = 'pending_auto', decided_at = NULL, decided_by = 'evolution_engine'
 WHERE decided_by = 'gate_set_migration_gsign'
   AND queue_status = 'rejected_gate' AND apply_log_id IS NULL;
COMMIT;
```

### 4.3 裁點三：施作時機

執行計畫 W3 前置**已全滿足**（親驗）：W1 結輪（run 20 succeeded 08-01）∧ W2-‖A 完成（sign 表 4 列）。硬約束＝**不得於輪進行中改**（同輪兩種標準＋config 與 baseline 不符）。

建議窗口與順序：

1. **窗口＝現在（週六下午）至週一 08-03 23:00 TWEVO cron 前**。親驗：slot 空、pgrep 無活引擎、ledger 零 running、kill 全 clear。
2. 「running=0」判準**明訂為**：pgrep 空 ∧ heavy slot 無持有 ∧ ledger 無 running（`evolution_run` 之 9 筆殭屍 running 為帳面殘影，屬 B1-apply 案；**不阻塞本案**，但若 Steward 先裁 B1-apply，則本判準可簡化為純 SQL）。
3. 順序：拍板 → 四件套單 commit（回歸鎖先驗紅）→ 乙案遷移 SQL → 手動跑 run 21（`--local-gates`，heavy slot 內）→ T3/T4 檢核 → 週報 08-02 09:00 自動反映。**APPLY-go 必在其後另案**（裁決呈案單：G-SIGN 落地 ∧ A1 verdict 出爐 ∧ 該候選 PASS 三條件齊才開；本呈案不開 APPLY）。
4. 週報時序註記：乙案遷移使 pending_auto 77→0，週日 09:00 週報之佇列數字將如實反映——屬預期，不是異常。

### 4.4 建議案（一句話）

**通過四件套（§3）＋UNJUDGEABLE⇒FAIL（§4.1）＋77 筆採乙案（§4.2）＋窗口即本週末（§4.3）。**

### 4.5 證偽條件（預先凍結；出處＝執行計畫 T3/T4，數字校正為現查口徑）

- **T3（住所選對了嗎）**：落地後**第一次 APPLY** 起，若出現「prodset 新 active 成員，其來源 queue 列 `gate_json->'G-SIGN'->>'verdict'` ≠ 'PASS'」——閘住所選錯，回頭檢討（機械檢核 SQL 見 §6.1-V8）。
- **T4（重評代價可接受嗎）**：run 21 中 G-PROM∧G-ECON 雙 PASS 之列，若 **>50% 僅因 G-SIGN 而落 rejected_gate**——加閘破壞性被低估，回報並回頭改甲案惰化（裁決呈案單 A3 證偽原文；機械檢核 SQL 見 §6.1-V9）。

---

## §5 風險與回滾

| # | 風險 | 緩解／回滾 |
|---|---|---|
| 1 | 漏改呼叫端 | 設計上 `TypeError` fail-loud（必填 kwarg）；7 觸點 §3.3 逐列；全 repo grep 無第 8 觸點（tools/ops/augur_proxy 零命中，親驗） |
| 2 | 誤動 FAIL_SIGN／R3 除役通道 | 執行計畫明文禁改；回歸鎖 R5 行為級鎖死（含「舊列無 G-SIGN 鍵時 demote 仍放行」） |
| 3 | 指紋改變使首輪 incomparable | 刻意保守設計：舊列指紋字串**逐字元不變**，只有新閘集列帶後綴；跨界那一輪 `compare_gain→(None,'incomparable')`、停損計數原地不動（iteration.py:110-114 親驗）——一輪量測空窗是誠實成本 |
| 4 | 乙案遷移錯標／需反悔 | 謂詞冪等＋`decided_by` 標記唯一；回滾 SQL §4.2 全量還原；`gate_json` 零觸碰 |
| 5 | run 21 成本 | local_gates 全量本就要跑（重評＝正常輪）；G-SIGN 增量≈對 ≤113 長度序列做 5 次 bootstrap/特徵，可忽略；sign 表增量≈51 列/run，append-only |
| 6 | 週報 (b) 「最新列」口徑：引擎單 h（60）列成為 latest，可能遮住 A1 之 h20 列 | **殘留、不在本案射程**：`report_triple_evolution_week.py:151` 之 `DISTINCT ON (feature)` 宜改 per-(feature,h) 全 PASS 口徑——列為 follow-up 一行修，另案過目 |
| 7 | 新增 selftest 觸發假斷言閘（pre-commit 第四閘） | 全部回歸鎖採行為級（餵真輸入呼叫函式），零字面自我匹配；commit 前四閘本地全跑 |
| 8 | 引擎方向與正典方向不一致（ruling vs map 漂移） | evidence 雙記 `engine_direction`／`direction`，不一致如實入帳供稽核；判定以正典為準 |
| 9 | code 回滾 | 四件套單 commit → `git revert` 一刀；DB 側四件套零寫入（遷移與 run 21 各自獨立可回滾／可判 invalid） |

---

## §6 驗收判準（機械可判）

### 6.1 驗收指令（全過才勾登錄冊）

| # | 指令 | 通過判準 |
|---|---|---|
| V1 | `venv/bin/python -m augur.philosophy.evolution --selftest` | rc=0，含「GATE_IDS 八閘」✓ |
| V2 | `venv/bin/python scripts/run_philosophy_evolution.py --selftest` | rc=0 |
| V3 | `venv/bin/python scripts/apply_evolution_promotions.py --selftest` | rc=0 |
| V4 | `venv/bin/python scripts/verify_sign_consistency.py --selftest` | rc=0（判式鎖搬家後仍全綠＝逐字未變） |
| V5 | 遷移後：`SELECT count(*) FROM promotion_queue WHERE queue_status='pending_auto' AND NOT (gate_json ? 'G-SIGN')` | =0（執行前先查現數留檔） |
| V6 | run 21 後：`SELECT count(*) FROM promotion_queue WHERE gate_json ? 'G-SIGN'` | >0（執行計畫 W3 驗收原文） |
| V7 | run 21 後：`SELECT count(*) FROM feature_sign_check WHERE checked_at > '<run21 started_at>'` | ≥ run 21 之 mapped 特徵數（引擎雙寫落地） |
| V8 | **T3 常置檢核**：`SELECT p.feature FROM evolution_production_feature_set p JOIN promotion_queue q ON q.queue_id=p.source_queue_id WHERE p.set_status='active' AND p.last_action='promote' AND q.gate_json ? 'G-SIGN' AND q.gate_json->'G-SIGN'->>'verdict' <> 'PASS'` | 0 列（每次 APPLY 後跑） |
| V9 | **T4 檢核**：run 21 之 `SELECT count(*) FILTER (WHERE 僅 G-SIGN 非 PASS 且其餘六閘 PASS 且 G-PROM∧G-ECON PASS) * 1.0 / NULLIF(count(*) FILTER (WHERE G-PROM∧G-ECON PASS),0)`（展開式隨施作附） | ≤0.5；>0.5 觸證偽→回報 Steward |
| V10 | pre-commit 四閘（治權引用／指令矩陣／#8 AST／假斷言） | 全綠 |

### 6.2 回歸鎖清單（**凡新鎖必先驗紅**——對 HEAD 舊碼跑必 FAIL 才收）

| 鎖 | 住所 | 內容（行為級、餵真輸入） |
|---|---|---|
| R1 | evolution.py selftest | `len(GATE_IDS)==8` ∧ `"G-SIGN" in GATE_IDS` |
| R2 | evolution.py selftest | 七鍵全 PASS 之 gate_json → `all_gates_green(...)==False`（舊世代列不可放行） |
| R3 | evolution.py selftest | `build_gate_json(七參數)` 拋 `TypeError`（try/except 行為測） |
| R4 | evolution.py selftest | `evaluate_g_sign_from_evidence` 五路：PASS／FAIL(一 bootstrap 翻號)／FAIL+unjudgeable(direction=None)／FAIL+unjudgeable(n_series=5)／SKIP(skipped_reason)；另 `unjudgeable_verdict='SKIP'` 之 cfg 覆蓋路 |
| R5 | evolution.py＋apply selftest | FAIL_SIGN 通道不變：`decide_queue_status(demote,FAIL_SIGN)=='pending_auto'`；**七鍵**（無 G-SIGN）gate_json 之 demote FAIL_SIGN 經 `may_apply` 仍放行（舊列相容） |
| R6 | apply selftest | 八閘 green 放行；七閘 green 拒（`gates not all PASS`） |
| R7 | verify_sign_consistency selftest | `judge_sign.__module__=='augur.philosophy.evolution'`＋既有判式六鎖照跑 |
| R8 | run_meta_replay | import smoke：`vss.judge_sign` 可解析（Ｖ4 附帶） |
| R9 | run_evolution_iteration selftest | `_gate_scale` 假 cur 行為測：`('2.0', True)`→`'min_abs_hac_t=2.0\|gates=8+G-SIGN'`；`('2.0', False)`→`'min_abs_hac_t=2.0'`（與現行逐字元同） |
| R10 | iteration.py selftest（既有檔） | `compare_gain({'gate_scale':'min_abs_hac_t=2.0',...},{'gate_scale':'min_abs_hac_t=2.0\|gates=8+G-SIGN',...})==(None,'incomparable')`（跨閘集邊界鎖；現碼已通過——此鎖為凍結防回歸，不驗紅、標明既綠收錄） |

---

## §7 Steward 決定欄（留白）

| 裁點 | 選項 | 決定 |
|---|---|---|
| A3-1 四件套 | 通過／退回 | ☐ |
| A3-2 UNJUDGEABLE 落點 | FAIL【建議】／SKIP | ☐ |
| A3-3 既存 77 筆 | 甲惰化／**乙重評＋遷移【建議】**／丙只重評 | ☐ |
| A3-4 時機 | 本週末窗口【建議】／另定 | ☐ |
| A3-5 遷移 SQL 執行者 | 拍板後 AI 執行／hugo 親跑 | ☐ |

簽核：＿＿＿＿＿＿＿＿（hugo TTY）　日期：＿＿＿＿＿＿＿＿
