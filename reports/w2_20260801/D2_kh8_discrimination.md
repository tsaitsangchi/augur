# [DRAFT 呈案] D2｜KH8 鑑別力閘——MIN_MINORITY_MASS 質量門檻（未經拍板不得施作）

> **性質**：W2 呈案批之一；設計 SSOT＝`reports/augur_problem_solution_register_20260801.md` §3-D2
> ＋`reports/augur_steward_adjudication_sheet_20260801.md`「D2」。本檔＝親驗 live 現況＋展開成可拍板全文，非重新設計。
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，標的是「對 AI 自身產出（KH8 證據評分）之鑑別力監督閘」——收緊
> 或放寬皆直接影響 AI 產出被當成證據的門檻；故所有數字附現查 SQL 可獨立重跑，建議附證偽條件，不以起草者自信為據。
> **裁決專屬 Steward**（`AUGUR-MC v1.6 §8.1`／L6.18(a)）；本檔僅草擬與呈案。

---

## §1 問題與授權鏈

**問題**（r3 深化理解 §五，`fd06c9b`）：`population_discriminates`（`src/augur/knowledge/evidence.py:133`）
的兩道判準皆為**存在性**判準——(1) band 種類 ≥2、(2) 三分量 distinct ≥2。現況母體 146,354 列中非 high
僅 **396 列（0.27%）**，即以此尾巴同時滿足兩判準 ⇒ **閘實際是開的（親驗 ok=True，見 §2）**
⇒ KH9-first 排序生效中：depth≥7 之 **145,954 件**全排公版 works 前，而深帶內 99.996% 同深＝排序鍵退化。
0.27% 的尾巴不構成「母體具鑑別力」的證據——存在性判準擋不住質量退化。

**授權鏈**：
- Steward 指示「記錄所有問題的解決方式，之後依記錄逐項解決」→ 登錄冊 §1 表列 D2＝W2 呈案波次（呈案→Steward）。
- 裁決單 D2 建議案＝`MIN_MINORITY_MASS=0.05`（中庸），證偽條件已預載（§4 沿用）。
- 本次授權範圍＝**唯讀親驗＋呈案文件撰寫**（scratchpad 落檔）；期限＝本批（2026-08-01 W2 呈案批）；可撤銷；
  參照＝登錄冊 D2。**全程零寫入 repo／DB；施作屬 W3、須 Steward 圈選後另行。**

---

## §2 現況親驗（2026-08-01 現查；與登錄冊/r3 不符處明標）

### 2.1 band 直方圖（live）

```sql
SELECT confidence_band, count(*) FROM knowhow_evidence_weight GROUP BY 1 ORDER BY 2 DESC;
-- high  |145958   （99.7294%）
-- absent|   380   （ 0.2597%）
-- low   |    16   （ 0.0109%）
-- 合計 n=146,354；非眾數（非 high）＝396 列
```

⚠ **與 r3 不符**：r3 §五記「非 high 僅 402 件」→ 今日現查 **396 件**（母體亦有異動）；本呈案一律以現查為準。

### 2.2 exp(H) 與非眾數質量（live）

```sql
WITH h AS (SELECT confidence_band b, count(*)::float8 c FROM knowhow_evidence_weight GROUP BY 1),
 t AS (SELECT sum(c) n FROM h)
SELECT round(exp(sum(-(c/n)*ln(c/n)))::numeric,6), round((1-max(c)/max(n))::numeric,8), max(n)::bigint FROM h,t;
-- exp(H)=1.019342 ｜ band 非眾數質量=0.00270577 ｜ n=146354
```

exp(H)（band 分佈之有效類別數）＝**1.019342**——與登錄冊「1.019」一致；三種 band 名存，實際上等效 1.02 種。

### 2.3 三分量分佈（live）

```sql
SELECT 'terminal', components->>'terminal', count(*) FROM knowhow_evidence_weight GROUP BY 2
UNION ALL SELECT 'embed', components->>'embed', count(*) FROM knowhow_evidence_weight GROUP BY 2
UNION ALL SELECT 'kh4_ok', components->>'kh4_ok', count(*) FROM knowhow_evidence_weight GROUP BY 2;
-- terminal: 1.0×146,354（零變異；非眾數質量=0.0）
-- embed:    1.0×145,958／0.0×396（非眾數質量=0.00270577）
-- kh4_ok:   1.0×145,958／0.0×396（非眾數質量=0.00270577）
```

登錄冊「四案皆 fail」之親驗解讀：**band＋三分量共四個非眾數質量**（0.0027／0／0.0027／0.0027）
皆遠低於三選項中最寬鬆之 0.02 ⇒ 任一門檻下今日皆 ok=False。

### 2.4 現行閘 live 裁決（親跑，唯讀）

```
$ ./venv/bin/python -c "…population_discriminates(cur)…"   # 0.28s
{'ok': True, 'bands': ['high','absent','low'], 'n': 146354,
 'note': "band […]；三分量變異數 terminal=1／embed=2／kh4_ok=2（n=146354）"}
```

**確認：今日閘開（ok=True）**——396 列尾巴同時解開判準(1)（band≥2）與判準(2)（embed/kh4_ok distinct=2）。
⚠ **與 code 註不符**：`auto_admit.py:134` 記全表掃「實測 4.9–7.7s」（07-30）→ 今日親測 **0.28s**（warm cache）；
不改判準，但 §3.4 之 TTL 論證一併按新實測校準。

### 2.5 尾巴的身分（誰是那 396 列）

```sql
SELECT w.confidence_band, st.admit_depth, k.domain, count(*) FROM knowhow_evidence_weight w
LEFT JOIN knowhow_auto_admit_state st ON st.target_kind='item' AND st.target_id=w.item_id::text
LEFT JOIN knowledge_kh4_state k ON k.item_id=w.item_id
WHERE w.confidence_band <> 'high' GROUP BY 1,2,3 ORDER BY 4 DESC;
-- absent|3|chemistry|377 ／ low|3|chemistry|5 ／ low|3|finance_mgmt|4 ／ low|3|organization_mgmt|3
-- absent|3|biology|3 ／ low|3|business_mgmt|2 ／ low|3|biology|2      （合計恰 396）
```

396 列全是 **admit_depth=3 的未嵌入批**（chemistry 為主）——現有「變異」來源＝嵌入進度落差，
**非** score 層的語意鑑別。母體選擇效應（只評「已終態＋已嵌入＋已 eligible」項）未解，質量門檻正是對此設防。

### 2.6 排序端現況（advisor 影響基底）

```sql
SELECT admit_depth, count(*) FROM knowhow_auto_admit_state WHERE target_kind='item' GROUP BY 1 ORDER BY 1;
-- 3|396 ／ 7|145948 ／ 9|6      （deep band＝depth≥7＝145,954，與 r3 同）
```

---

## §3 方案（函式全文草稿＋逐檔 diff 計畫；**零 DDL**）

### 3.1 新常數與純函式（`src/augur/knowledge/evidence.py`，插於 :114 `MIN_DISCRIMINATING_BANDS` 之後）

```python
# ── D2（2026-08-01 呈案）：存在性判準 → 質量判準 ─────────────────────────────
# 病灶（r3 §五）：判準(1)(2) 皆「存在性」——band 種類≥2、分量 distinct≥2，可被
# 0.27% 尾巴（396/146,354，皆 depth-3 未嵌入批）同時滿足 ⇒ 結構上仍不可鑑別的
# 母體開著 KH9-first 閘。強化：band 與分量之**非眾數質量**各須 ≥ MIN_MINORITY_MASS。
MIN_MINORITY_MASS = 0.05  # 【呈裁值；三選項 0.02/0.05/0.10——Steward 圈選後定版，未拍板不得入 repo】


def minority_mass(counts) -> float:
    """非眾數質量＝1 − 眾數計數/總數；空集回 0.0（無質量＝無鑑別力）。純函式。"""
    vals = [int(c) for c in counts if int(c) > 0]
    total = sum(vals)
    if total <= 0:
        return 0.0
    return 1.0 - (max(vals) / total)


def discrimination_verdict(band_counts, comp_minority_masses, *, min_minority_mass=None):
    """KH8 母體鑑別力裁決——純函式（免 DB；真輸入由 population_discriminates 現查餵入）。

    ok ⇔ (1) band 種類 ≥ MIN_DISCRIMINATING_BANDS
       ∧ (1′) band 非眾數質量 ≥ 門檻（擋「加一列 low 即解閘」——存在性判準之洞、F-bypass-1 同族）
       ∧ (2′) 三分量（terminal/embed/kh4_ok）至少一者非眾數質量 ≥ 門檻
              （擋母體選擇效應：分量恆 1.0 時 band 變異只是公式常數平移）。
    恰在門檻上＝過（≥ 語意）。空母體／零質量 → ok=False（fail-closed）。
    回傳鍵向後相容：ok/bands/n/note 必在（reevaluate_kh_depths.py:83、run_kh_chain.py:83 只讀此四鍵）。
    """
    mm = MIN_MINORITY_MASS if min_minority_mass is None else float(min_minority_mass)
    counts = {str(b): int(c) for b, c in dict(band_counts).items() if int(c) > 0}
    bands = sorted(counts, key=counts.get, reverse=True)
    n = sum(counts.values())
    comp = {str(k): float(v or 0.0) for k, v in dict(comp_minority_masses).items()}
    base = {"bands": bands, "n": n, "band_minority_mass": 0.0,
            "comp_minority_masses": comp, "min_minority_mass": mm}
    if n == 0:
        return {**base, "ok": False, "note": "KH8 母體為空（排除受判列後）"}
    bmm = minority_mass(counts.values())
    base["band_minority_mass"] = round(bmm, 8)
    if len(bands) < MIN_DISCRIMINATING_BANDS:
        return {**base, "ok": False, "note": f"判準(1)不過：{n} 列僅 {bands} 一種 band"}
    if bmm < mm:
        return {**base, "ok": False,
                "note": f"判準(1′)不過：band 非眾數質量 {bmm:.6f} < {mm}"
                        f"（{n} 列；尾巴不構成鑑別力）"}
    cmax = max(comp.values(), default=0.0)
    if cmax < mm:
        return {**base, "ok": False,
                "note": f"判準(2′)不過：三分量非眾數質量皆 < {mm}（{comp}）"
                        "——母體選擇效應未解，band 變異不足以證明鑑別力"}
    return {**base, "ok": True,
            "note": f"band {bands}；band 非眾數質量 {bmm:.4f}；分量非眾數質量 {comp}（n={n}）"}
```

### 3.2 `population_discriminates` 改為薄取數層（`evidence.py:133-177` 全段替換）

```python
def population_discriminates(cur, *, exclude_item_id: int | None = None) -> dict[str, Any]:
    """KH8 母體是否具鑑別力——取數後委派 discrimination_verdict（判準全文見該函式）。

    `exclude_item_id`：排除正在受判之 item（防自證污染，原語意不變）。
    表未建／空表 → ok=False（fail-closed，原語意不變）。
    """
    cur.execute("SELECT to_regclass(%s)", ("public.knowhow_evidence_weight",))
    if not cur.fetchone()[0]:
        return {"ok": False, "bands": [], "n": 0, "note": "KH8 表未建"}
    where = "" if exclude_item_id is None else "WHERE item_id <> %s"
    args: tuple = () if exclude_item_id is None else (exclude_item_id,)
    cur.execute(
        f"SELECT confidence_band, count(*) FROM knowhow_evidence_weight {where} GROUP BY 1 ORDER BY 2 DESC",
        args,
    )
    band_counts = {r[0]: int(r[1]) for r in cur.fetchall()}
    # 三分量非眾數質量（單趟；回一列三 float，與舊「一列三 distinct 數」同形——FakeCur 相容）
    cur.execute(
        f"""WITH src AS (SELECT components->>'terminal' AS t, components->>'embed' AS e,
                                components->>'kh4_ok' AS k
                           FROM knowhow_evidence_weight {where})
            SELECT (SELECT 1.0-max(c)::float8/sum(c) FROM (SELECT count(*) c FROM src GROUP BY t) x),
                   (SELECT 1.0-max(c)::float8/sum(c) FROM (SELECT count(*) c FROM src GROUP BY e) y),
                   (SELECT 1.0-max(c)::float8/sum(c) FROM (SELECT count(*) c FROM src GROUP BY k) z)""",
        args,
    )
    t, e, k = ((float(x) if x is not None else 0.0) for x in cur.fetchone())
    return discrimination_verdict(band_counts, {"terminal": t, "embed": e, "kh4_ok": k})
```

**上游不動**：`frozen_population_verdict`（:125-130 批次凍結）、`evaluate_item_evidence`（:279-324）、
`synthesis.py:134`（KH9 同凍結判準）、`auto_admit.py:123/:157` 皆原樣消費 `ok` 鍵——**單點改、全鏈生效**。

### 3.3 selftest 改動（`evidence.py:356-393`；絆線＝真直方圖雙向紅）

- 既有 `_FakeCur` scripted 第三查詢由「一列三 distinct 數」改「一列三質量 float」：
  d1/d2 用 `(0.0, 0.0, 0.0)`、d3 用 `(0.0, 0.23, 0.0)`（band 30/130=0.23 質量、應 ok）、d4 `(0.0, 0.0, 0.0)`。
- **新增（先驗紅）**：
```python
    # D2 真直方圖雙向紅：live 直方圖（2026-08-01 現查凍結為 fixture）於三選項下必 fail；
    # 合成有鑑別力分佈必 ok——雙向都得動，防字面斷言假綠。
    live_bands = {"high": 145958, "absent": 380, "low": 16}
    live_comp = {"terminal": 0.0, "embed": 0.00270577, "kh4_ok": 0.00270577}
    for th in (0.02, 0.05, 0.10):
        chk(f"live 直方圖 θ={th} → fail",
            discrimination_verdict(live_bands, live_comp, min_minority_mass=th)["ok"] is False)
    chk("合成有鑑別力分佈 θ=0.05 → ok",
        discrimination_verdict({"high": 90000, "low": 10000},
                               {"terminal": 0.0, "embed": 0.10, "kh4_ok": 0.0},
                               min_minority_mass=0.05)["ok"] is True)
    chk("band 質量夠但分量全平 → fail（判準 2′）",
        discrimination_verdict({"high": 90000, "low": 10000},
                               {"terminal": 0.0, "embed": 0.0, "kh4_ok": 0.0},
                               min_minority_mass=0.05)["ok"] is False)
    chk("恰在門檻上 → ok（≥ 語意）",
        discrimination_verdict({"a": 95, "b": 5}, {"embed": 0.05},
                               min_minority_mass=0.05)["ok"] is True)
    chk("回傳鍵向後相容", {"ok", "bands", "n", "note"} <=
        set(discrimination_verdict({"high": 1}, {})))
```
- **先驗紅程序**（回歸鎖三規則）：施作時先只加測試、跑舊碼——「live 直方圖必 fail」在舊判準下（bands=3、
  distinct=2 → ok=True）**必紅**；貼紅色輸出入 commit message 後才落新碼轉綠。

### 3.4 TTL 政策修正（`src/augur/knowledge/auto_admit.py`；D2 落地後的必要配套）

現行 :149 `_ttl = _OK_TTL_SEC if cache.get("ok") else _FAIL_TTL_SEC`——FAIL 短 TTL（30s）原為
「DB 瞬斷不得永久關閘」而設；D2 生效後閘將**以資料為據長期 False**，若沿用則 advisor 每 30s 重掃一次
全表（今日實測 0.28s，但屬無謂重算且 cache 冷時仍會回到秒級）。改為**按裁決來源分壽**：

```diff
--- src/augur/knowledge/auto_admit.py:149
-        _ttl = _OK_TTL_SEC if _kh_evidence_valid_cache.get("ok") else _FAIL_TTL_SEC
+        # 資料為據之裁決（ok True/False 皆然）＝長 TTL；唯 error fail-closed（取不到）＝短 TTL
+        _ttl = _FAIL_TTL_SEC if _kh_evidence_valid_cache.get("error_closed") else _OK_TTL_SEC
--- src/augur/knowledge/auto_admit.py:159-165（exception 路徑 disc dict 內加一鍵）
         disc = {
             "ok": False,
+            "error_closed": True,
             "bands": [],
```

### 3.5 順帶觀察（不在本案射程、留檔）

`src/augur/philosophy/retrieval.py:408`：`retrieve_all` 內 `set_kh_evidence_validity(cur)` 之 `cur`
**在該作用域不存在**（模組亦無同名全域）→ NameError 被 :409 `except: pass` 吞＝死碼。無害
（`kh_evidence_valid()` 已自足），但正是 07-30 已判過的「except 吞 fail-open」同型；建議另案清理。

---

## §4 選項與建議案（MIN_MINORITY_MASS 三選項後果表）

**三選項今日後果相同**：band 非眾數質量 0.0027 ＜ 0.02 ＜ 0.05 ＜ 0.10 ⇒ 皆 ok=False、閘關。
差異只在**未來重開閘所需的最少非眾數質量**（眾數 145,958 固定下之推算；含既有 396）：

| 選項 | 門檻 θ | 今日裁決 | 重開所需非眾數列數（現有 396） | 後果與風險 |
|---|---|---|---|---|
| 甲（寬） | **0.02** | fail | ≥ **2,979**（再 +2,583） | 最早重開；風險＝2% 尾巴仍可能全是「嵌入落差批」（absent/low，見 §2.5）而非 score 層真鑑別——閘重開時鑑別力未必真到位 |
| **乙（中庸，裁決單建議）** | **0.05** | fail | ≥ **7,682**（再 +7,286） | KH9-first 退回相似度序＝誠實（深度鍵本來就退化）；重開須母體結構實質改變（如 KH0/D1 補齊後未嵌入批大量入帳） |
| 丙（嚴） | **0.10** | fail | ≥ **16,218**（再 +15,822） | 最保守；風險＝「真有鑑別力」的分佈（少數帶質量 3–5% 且確有語意）也被關在外，閘變同義於永關 |

**建議案（沿裁決單）**：`MIN_MINORITY_MASS = 0.05`。
**證偽條件（沿裁決單，原文）**：若 0.05 使閘在「真有鑑別力」的分佈下也關（少數帶質量 3–5% 且確有語意），降 0.02。
補充機械化：屆時以當日直方圖＋人工抽 20 件少數帶 item 驗語意，兩者留檔佐證後再降。

### advisor 行為變更說明（拍板任一選項即發生）

1. **排序端**（`auto_admit.py:200` → `rank_item_citations` fail-closed 分支）：KH9-first **整體停用**——
   `retrieve_all` 回 works/public/private 三路 `zip_longest` 交錯原序截 k；`_finalize_items_kh_first`
   回 Qdrant/pgvector 相似度原序截 k。**deep band 145,954 件不再自動排公版 works 前**；
   works 取回交錯位。深帶內 99.996% 同深（145,948/145,954 皆 7），帶內本就靠 −score，故實際變化
   集中在「深 item vs works」之先後，非 item 間互換。
2. **准入端零變化**：鑑別力閘只作用**排序**，不是檢索濾網——`retrieval.py:254` 之
   `JOIN knowledge_kh4_state k4` ＋ `answer_status='eligible'` 條件原樣；引文集合、RBAC、相關度閘、
   guard 全不動。**答案內容不變，只有引文先後變。**
3. **晉升端**：`evaluate_item_evidence`（KH8 層）對每件回 `fail｜kh8_non_discriminating`、
   KH9 層回 `kh9_blocked_by_invalid_kh8` ⇒ **閘關期間不再新增 depth 8/9**（帳仍寫、可溯源）；
   既有 depth（含 6 件 depth 9）因 upsert `GREATEST` 不降——**存量再膨脹屬 D4 案**，本案不動。
4. **恢復路**：不需改碼——當母體真的出現 ≥θ 非眾數質量（如 D1 補旗標後未嵌入批被評、或真實 low/medium
   帶成規模），閘自動重開（`compute_knowhow_evidence_weight.py:64` 之「隨之自動解除」語意保留）。

---

## §5 風險與回滾

- **零 DDL、零資料變更**：純常數＋純函式＋一處 TTL 政策；不碰 `knowhow_evidence_weight` 任何列。
- **回滾**＝`git revert` 單 commit，行為即回今日現狀（閘開）；無狀態殘留（進程快取 TTL≤900s 自然換血，
  重啟 advisor 服務即全新）。⚠ 改後須 `systemctl --user restart` advisor 相關常駐服務再實測（CLAUDE #7）。
- **殘餘風險**：(a) 閘長關使 KH8/KH9 晉升凍結——此為**設計意圖**（無鑑別力之證據不得晉升），非副作用；
  (b) 三 script 消費端（`reevaluate_kh_depths.py:83`／`run_kh_chain.py:83/:291`）只讀 ok/bands/n/note
  四鍵，回傳超集向後相容，已逐一親查；(c) `_FakeCur` 形狀相容（第三查詢仍一列三值）。
- **不動之邊界**：判準(1) `MIN_DISCRIMINATING_BANDS=2` 保留；exclude_item_id 防自證污染保留；
  批次凍結（frozen_population_verdict）保留。

## §6 驗收判準（機械可判）

1. `python -m augur.knowledge.evidence --selftest` RC=0，且 commit 內含**先驗紅**輸出
   （新測試在舊碼下 FAIL 之貼文）。
2. `python -m augur.knowledge.auto_admit --selftest` RC=0（連鎖跑 kh8/kh9 selftest）。
3. live 唯讀複跑：`population_discriminates(cur)` 回 `ok=False` 且 note 含「判準(1′)」、
   `band_minority_mass` 與 §2.2 SQL 現查值一致（誤差 <1e-6）。
4. 回傳鍵斷言：`{"ok","bands","n","note"} ⊆ keys`（selftest 內建）。
5. advisor 重啟後行為探針：同一 query 之引文序＝相似度序（不再 deep-first）；
   `journalctl` 無 30s 週期之全表掃（TTL 修正生效）。
6. `python scripts/run_kh_chain.py`（preflight 唯讀段）印出 `kh8_discriminates ok=False` 不裸 traceback。

## §7 Steward 決定欄

- MIN_MINORITY_MASS：☐ 0.02 ／ ☐ 0.05（建議） ／ ☐ 0.10 ／ ☐ 另定＿＿＿
- TTL 配套（§3.4）：☐ 准 ／ ☐ 駁
- retrieval.py:408 死碼另案清理：☐ 開案 ／ ☐ 不理
- 簽署：＿＿＿＿＿＿＿＿（hugo TTY 親簽；日期＿＿＿＿）
