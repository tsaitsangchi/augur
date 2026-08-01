# [DRAFT 呈案] D3｜KH5 恆 ready → 逐 item 軸覆蓋證據（未經拍板不得施作）

> **性質**：W2 呈案批之一；設計 SSOT＝`reports/augur_problem_solution_register_20260801.md` §3-D3
> ＋`reports/augur_steward_adjudication_sheet_20260801.md`「D3」。本檔＝親驗 live 現況＋展開成可拍板全文。
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，標的是「AI 機械衍生之軸狀態」的收緊——收緊後 AI 自身
> 產出的 depth 晉升更難；所有數字附現查 SQL 可獨立重跑，建議附證偽條件，不以起草者自信為據。
> **裁決專屬 Steward**（§8.1／L6.18(a)）；本檔僅草擬與呈案。

---

## §1 問題與授權鏈

**問題**（r3 §五，`fd06c9b`）：KH5 判準已於 07-31 逐 item 化（讀 `knowledge_kh4_state.kh_axis_state`、
fail-closed），但上游 `kh4.py:89-94` 之軸狀態是**機械恆真式**——
`approval='active' ∧ domain 非空 ∧ (adapter∈CHANNEL_BY_ADAPTER ∨ source_key)` 即 ready。
`knowledge_item.domain` 零 NULL（`auto_admit.py:400` 註、07-31 實查）⇒ 全表 **161,900/161,900 恆 ready**
（今日親驗仍同，§2.1）＝逐 item 化尚未帶來鑑別力：KH5 層對任何 item 都自動 pass，「軸證據」三字無實。

**授權鏈**：同 D2——Steward「記錄後逐項解決」指示 → 登錄冊 D3（W2 呈案→Steward）→ 裁決單 D3
建議「照 agent 案：domain 落於映射工件才 ready、缺表 false」。本次授權＝唯讀親驗＋scratchpad 落檔；
期限＝本批；可撤銷；施作屬 W3。

---

## §2 現況親驗（2026-08-01 現查；不符處明標）

### 2.1 恆 ready 現況（live 再證）

```sql
SELECT kh_axis_state, count(*) FROM knowledge_kh4_state GROUP BY 1;
-- ready|161900        （100%；與 r3 同）
SELECT count(*) FROM knowledge_item;
-- 285204              ⚠ r3／auto_admit.py:400 註記 285,179 → 今日 285,204（+25 漂移；以現查為準）
SELECT count(*) FROM knowledge_item i LEFT JOIN knowledge_kh4_state k ON k.item_id=i.item_id WHERE k.item_id IS NULL;
-- 123304              （無 kh4_state 列之 item；§3.5 施作範圍之關鍵邊界）
SELECT answer_status, count(*) FROM knowledge_kh4_state GROUP BY 1 ORDER BY 2 DESC;
-- eligible|145954 ／ provisional|12459 ／ ineligible|2931 ／ blocked|556   （§6 驗收基線）
```

### 2.2 映射工件現況（「軸證據」的候選載體）

```sql
SELECT count(*), count(DISTINCT domain) FROM principle_domain_map;          -- 11 列｜3 域
SELECT count(*), count(DISTINCT openalex_field), count(DISTINCT augur_domain) FROM knowledge_domain_map;
                                                                            -- 25 列｜25 field｜16 域
```

- `principle_domain_map`（憲章 v1.47.0；人閘首案 hugo 核可；`migrate_principle_domain_map_ddl.py`）：
  域＝{ai_ml, business_mgmt, materials_rd}；每列帶 citation NOT NULL＋AI 生成硬擋＝**最強的軸證據載體**。
- `knowledge_domain_map`（harvest 治理閘；`harvest_knowledge.py:89-92`）：openalex_field→augur_domain，
  「未拍板 field 不建列、INNER JOIN 天然排除」＝**決策層拍板域的機械名冊**；納新域＝決策層 INSERT 一列（#29b）。

### 2.3 逐 item 軸覆蓋預估（新判準之直接後果）

```sql
WITH mapped AS (SELECT openalex_field AS d FROM knowledge_domain_map
                UNION SELECT augur_domain FROM knowledge_domain_map
                UNION SELECT domain FROM principle_domain_map)
SELECT (SELECT count(*) FROM knowledge_kh4_state),
       (SELECT count(*) FROM knowledge_kh4_state WHERE domain IN (SELECT d FROM mapped)),
       round(100.0*…, 3);
-- 161900 | 19454 | 12.016%
```

**逐域分解**（mapped=Y 合計 19,454；N 合計 142,446）：

| domain | 列數 | mapped | | domain | 列數 | mapped |
|---|---|---|---|---|---|---|
| erp_tiptop | **141,873** | **N** | | business_mgmt | 69 | Y |
| quant_finance | 15,361 | Y | | materials_science | 61 | Y |
| business_management_and_accounting | 1,315 | Y | | finance_mgmt | 60 | Y |
| economics_econometrics_and_finance | 942 | Y | | production_mgmt | 55 | Y |
| decision_sciences | 536 | Y | | organization_mgmt | 48 | Y |
| chemistry | 389 | Y | | mgmt_philosophy | 47 | Y |
| local | 330 | N | | environmental_science | 43 | N |
| accounting_mgmt | 205 | Y | | energy_materials | 43 | Y |
| solar_materials | 149 | Y | | rd_mgmt | 34 | Y |
| biology | 107 | Y | | investment_mgmt | 31 | Y |
| computer_science | 85 | N | | general | 15 | N |
| smoke_test | 78 | N | | erp_semantics | 14 | N |
| （其餘 4 域各 ≤6 列） | | | | solar_rd | 6 | N |

### 2.4 深帶（KH9-first 排序母體）之映射分佈

```sql
-- knowhow_auto_admit_state depth≥7 join kh4_state：
-- 7|mapped|3,513 ／ 7|unmapped|142,435 ／ 9|unmapped|6
-- depth 9 六件之域：local×4、smoke_test×2
```

深帶 145,954 件中僅 **3,513 件（2.4%）** 落於映射工件；**全庫最深的 6 件（depth 9）域＝local×4＋
smoke_test×2**——煙霧測試工件坐在知識金字塔頂端，恆 ready 之荒謬性的具體化。

---

## §3 方案（`kh4.py` 逐檔 diff 計畫；**零 DDL**——`migrate_kh4_state_ddl.py:30` CHECK 已含 'pending'）

### 3.1 `_select_sql` 全文替換（現行 `src/augur/knowledge/kh4.py:148-207`，親讀）

```python
def _select_sql(*, has_fulltext_status, has_import_qualification,
                has_principle_domain_map=False, has_knowledge_domain_map=False):
    # terminal_blocked＝有 status 終態帳且仍無全文（FT-COV：有 text≠不可答；
    # 僅因曾 skip_no_oa 等而留 status、後來已有 abstract/全文者不得誤擋 KH4）
    blocked_expr = (
        """(
          EXISTS (SELECT 1 FROM knowledge_fulltext_status f WHERE f.item_id=i.item_id)
          AND NOT EXISTS (SELECT 1 FROM knowledge_item_text x WHERE x.item_id=i.item_id)
        )"""
        if has_fulltext_status else "false"
    )
    qual_expr = (
        """(
          SELECT q.verdict
            FROM knowledge_import_qualification q
           WHERE q.item_id=i.item_id
           ORDER BY q.ingested_at DESC NULLS LAST, q.qualification_id DESC
           LIMIT 1
        )"""
        if has_import_qualification else "NULL::text"
    )
    # D3（KH5 恆 ready 收緊）：軸證據＝item.domain 落於決策層映射工件
    #（principle_domain_map.domain ∪ knowledge_domain_map.augur_domain/openalex_field）。
    # 工件表缺 → false（fail-closed：無工件即無軸證據）；納新域＝決策層 INSERT 一列（#29b 零改碼）。
    _axis_parts = []
    if has_principle_domain_map:
        _axis_parts.append(
            "EXISTS (SELECT 1 FROM principle_domain_map pm WHERE pm.domain = i.domain)")
    if has_knowledge_domain_map:
        _axis_parts.append(
            "EXISTS (SELECT 1 FROM knowledge_domain_map km "
            "WHERE km.augur_domain = i.domain OR km.openalex_field = i.domain)")
    axis_map_expr = ("(" + " OR ".join(_axis_parts) + ")") if _axis_parts else "false"
    return f"""
    SELECT
        i.item_id,
        i.source_key,
        i.domain,
        i.entity_type,
        ks.adapter,
        ks.protocol,
        COALESCE(ks.approval_status, 'missing') AS approval_status,
        COALESCE(
          (SELECT x.license
             FROM knowledge_item_text x
            WHERE x.item_id=i.item_id
            ORDER BY x.seq
            LIMIT 1),
          'unknown'
        ) AS license,
        EXISTS (SELECT 1 FROM knowledge_item_text x WHERE x.item_id=i.item_id) AS has_text,
        EXISTS (
          SELECT 1
            FROM knowledge_item_text x
            JOIN knowledge_sentence s ON s.itext_id=x.itext_id
           WHERE x.item_id=i.item_id
        ) AS has_sentence,
        EXISTS (
          SELECT 1
            FROM knowledge_item_text x
            JOIN knowledge_sentence s ON s.itext_id=x.itext_id
            JOIN knowledge_sentence_embedding e ON e.sent_id=s.sent_id
           WHERE x.item_id=i.item_id
        ) AS has_embedding,
        {blocked_expr} AS has_terminal_block,
        {axis_map_expr} AS axis_domain_mapped,
        EXISTS (
          SELECT 1 FROM knowledge_staging st
           WHERE st.status='promoted' AND st.source_key=i.source_key AND st.staging_id=i.staging_id
        ) AS staging_promoted,
        {qual_expr} AS qual_verdict
    FROM knowledge_item i
    LEFT JOIN knowledge_source ks ON ks.source_key=i.source_key
    """
```

（相對現行差異僅三處：簽名加二 kwarg（:148）；`_axis_parts`／`axis_map_expr` 區塊（插於 :167 後）；
select list 加 `{axis_map_expr} AS axis_domain_mapped` 一行（插於 :199 後）。其餘逐字不動。）

### 3.2 `derive_states` 軸分支（`kh4.py:89-94` 替換）

```diff
     if approval != "active":
         axis_state = AXIS_BLOCKED
-    elif domain and (adapter in CHANNEL_BY_ADAPTER or row["source_key"]):
+    # D3：ready 須逐 item 軸覆蓋證據（axis_domain_mapped＝domain 落於映射工件）；
+    # 未映射→pending（誠實「軸證據未落」），**不是** blocked——標籤不作答閘（KH-XDOM-S01），
+    # answer_status 之 eligible 路徑不受 pending 影響（derive_answer_status 僅擋 BLOCKED）。
+    elif row.get("axis_domain_mapped") and (adapter in CHANNEL_BY_ADAPTER or row["source_key"]):
         axis_state = AXIS_READY
     else:
         axis_state = AXIS_PENDING
```

（`row.get(...)`＝舊呼叫端／fixture 缺鍵時預設 False＝fail-closed。）

### 3.3 evidence 溯源鍵（`kh4.py:125-136` evidence dict 加一行）

```diff
         "has_terminal_block": has_terminal_block,
+        "axis_domain_mapped": bool(row.get("axis_domain_mapped")),
         "qual_verdict": qual_verdict,
```

### 3.4 `refresh_items` 取數參數（`kh4.py:213-216` 替換）

```diff
     sql = _select_sql(
         has_fulltext_status=_table_exists(cur, "knowledge_fulltext_status"),
         has_import_qualification=_table_exists(cur, "knowledge_import_qualification"),
+        has_principle_domain_map=_table_exists(cur, "principle_domain_map"),
+        has_knowledge_domain_map=_table_exists(cur, "knowledge_domain_map"),
     )
```

### 3.5 selftest 改動（`kh4.py:280-349`；先驗紅）

```python
    # D3 紅先驗：erp_tiptop 真實形狀 fixture（live 2026-08-01：kh4_state 141,873 列、無任何映射工件列）
    axis_fx = {
        "approval_status": "active", "has_text": True, "has_sentence": True,
        "has_embedding": True, "has_terminal_block": False, "entity_type": "paper",
        "license": "owned_local", "domain": "erp_tiptop", "adapter": "local_files",
        "qual_verdict": None, "staging_promoted": True, "source_key": "local_files_local",
        "axis_domain_mapped": False,
    }
    erp = derive_states(axis_fx)
    chk("未映射域 → axis pending（舊邏輯下本斷言必紅）", erp["kh_axis_state"] == AXIS_PENDING)
    chk("未映射域不動作答閘（KH-XDOM-S01）", erp["answer_status"] == ANSWER_ELIGIBLE)
    mapped = derive_states({**axis_fx, "domain": "quant_finance", "axis_domain_mapped": True})
    chk("映射域 → axis ready", mapped["kh_axis_state"] == AXIS_READY)
    chk("缺映射工件表 → SQL 落 false（fail-closed）",
        "false AS axis_domain_mapped" in _select_sql(has_fulltext_status=False,
                                                     has_import_qualification=False))
```
先驗紅程序：先只加測試跑舊碼——「未映射域 → pending」在舊邏輯（domain 真值即 ready）**必紅**，
貼紅輸出後才落新碼。既有五則 selftest 案例不動（其 fixture 缺新鍵→.get False→axis pending，
但既有斷言只驗 answer_status／status_reason，親讀確認全部仍綠）。

### 3.6 施作範圍護欄（W3 runbook；⚠ 本呈案親驗發現的關鍵邊界）

`retrieval.py:251-254` `_ITEM_JOIN` **INNER JOIN knowledge_kh4_state**——今日有 **123,304 件 item 無
state 列＝檢索不可見**。若 W3 用無參數 `refresh_kh4_state.py` 全量刷，會**替這 123,304 件新建列**，
其中衍生 eligible 者將**新進 advisor 檢索**＝超出 D3 範圍的行為變更。故 runbook 限定：

1. 落碼＋selftest（§6-1）。
2. **scoped 重刷（只碰既有 161,900 列、不擴母體）**：`refresh_kh4_state.py` 加 `--existing-only`
   旗標（`SELECT item_id FROM knowledge_kh4_state` 分批 5,000 餵 `kh4.refresh_items(cur, item_ids=…)`；
   冪等、可中斷續跑），或等價一次性批次；**禁用無參數全量刷**。
3. 驗收 §6；advisor 常駐服務 restart（CLAUDE #7）。

（`refresh_items` 之 10 個既有呼叫端——auto_admit:380、ingress_kip:571、promote_knowledge:209、
acquire_local_files:63/79、advance_knowledge_terminal:207 等——均為 item-scoped，自然沿用新判準，零改動。）

---

## §4 選項與建議案（含 ready 率變化預估）

| 案 | 內容 | kh4_state ready 率預估 | 評註 |
|---|---|---|---|
| **甲（建議；登錄冊＋裁決單案）** | §3 diff 原樣：mapped＝pdm.domain ∪ kdm.augur_domain ∪ kdm.openalex_field；缺表 false | **100% → 12.016%**（161,900 → 19,454 ready；142,446 → pending） | 軸證據回到「決策層拍過板的域」之機械名冊；erp_tiptop（87.6%）、local、smoke_test 誠實轉 pending |
| 乙（甲＋後手資料補列） | 甲落地後，Steward 對其認可之域**親自 INSERT 映射列**（如 `INSERT INTO knowledge_domain_map VALUES ('erp_tiptop','erp_tiptop')`） | 每補一域即恢復該域（僅 erp_tiptop 即 12.0%→**99.66%**） | 零改碼（#29b）＝甲案設計特性而非獨立方案；⚠ 若一次補回 erp_tiptop，ready 率 >99% 將**當場觸發本案證偽條件**——補列須逐域附理由、非批發恢復 |
| 丙（維持現狀） | 不動 | 100% 恆 ready | 否決理由＝KH5 層對結果貢獻恆 0、「軸證據」名不符實（r3 佇列 #10） |

**建議案**：**甲**。乙不作為獨立選項呈裁，而作為甲的**後手治理閘**呈告知：任何域的 ready 恢復
＝Steward 一列 INSERT（決策留痕在 DB、非 code）；erp_tiptop 是否該有軸證據屬**另一次逐域裁決**
（若裁「是」，建議以 `principle_domain_map` 型帶 citation 載體或專用軸註冊表承載，勝過裸 2 欄恆等列）。

**證偽條件（沿裁決單，原文）**：改後若 ready 率仍 >99%，代表映射工件本身覆蓋過寬，問題上移。
（甲案預估 12.016%，遠離觸線；乙案批發補列會觸線——此即其護欄。）

### 對 KH5／深帶／advisor 的傳導（與 D2 互補）

- **KH5 層（`auto_admit.py:411-423`，零改動）**：未映射 item 之 depth 5 評估 `fail｜kh_axis_state=pending`
  ⇒ **未來** progressive 重評時未映射者 depth 封頂 4；可續往 7+ 衝者只剩 mapped 3,513＋後續映射域新件。
- **存量深帶不自動消滅**：upsert `GREATEST`（`auto_admit.py:260`）使既有 145,954 件 depth≥7 原地不動
  ——存量降級屬 **D4 案**（再晉升鎖）射程；D3 只封「未來繼續機械晉升」之路。
- **advisor**：D3 本身**不改**檢索准入（answer_status 不變，§6-3 為此設驗收）也不改排序（排序閘在 D2）；
  D2＋D3 合力＝排序端立即誠實（D2）＋晉升端從源頭要證據（D3）。

## §5 風險與回滾

- **零 DDL**：`kh_axis_state` CHECK（`migrate_kh4_state_ddl.py:30`）已含 'pending'；純 code＋scoped 重刷。
- **answer_status 不變式**：pending 不進 `derive_answer_status` 的 blocked 分支（`kh4.py:61` 親讀）——
  161,900 列之 answer_status 在重刷後應**逐值不變**（§6-3 機械驗）；標籤不作答閘（KH-XDOM-S01）維持。
- **回滾**：revert commit ＋ 同法 scoped 重刷一次＝全表回 ready（derive 是純函數、重刷冪等）；無不可逆狀態。
- **殘餘風險**：(a) 重刷與驗收若不同日，底層事實（新嵌入等）自然漂移會污染 §6-3 對照——驗收限同日窗口；
  (b) `knowledge_domain_map` 被賦予「軸證據」第二語意（原為 harvest 排程閘）——語意過載已在 §4 乙案
  註明，長期正解為專用軸註冊表（另案）；(c) 122 件 mapped 但 approval/channel 缺者理論上存在
  （現查 ready 全 161,900 → mapped 19,454 全在 ready 中，故預估數即 19,454，無此殘差）。

## §6 驗收判準（機械可判；施作同日執行）

1. `python -m augur.knowledge.kh4 --selftest` RC=0，commit 含**先驗紅**輸出（§3.5 程序）。
2. scoped 重刷後：
   `SELECT kh_axis_state, count(*) FROM knowledge_kh4_state GROUP BY 1;`
   ＝ `ready|19454 ／ pending|142446`（±施作日 item-scoped 刷新自然增量；總數仍 161,900 除非入庫事件）。
3. **answer_status 直方圖前後逐值相同**：
   `eligible|145954 ／ provisional|12459 ／ ineligible|2931 ／ blocked|556`（§2.1 基線；如漂移須逐因說明）。
4. 抽測：`SELECT kh_axis_state FROM knowledge_kh4_state WHERE domain='erp_tiptop' LIMIT 1` → pending；
   `…WHERE domain='quant_finance' LIMIT 1` → ready。
5. KH5 行為探針（唯讀 dry-run）：對任一 erp_tiptop item 跑 `progressive_item(…, up_to=5, apply=False)`
   → layer 5 verdict=fail、note 含 `kh_axis_state=pending`；對 quant_finance mapped item → pass。
6. `SELECT count(*) FROM knowledge_kh4_state` 不得超過施作前值＋當日正常入庫量（防誤跑全量刷擴母體）。

## §7 Steward 決定欄

- 方案：☐ 甲（建議） ／ ☐ 甲＋指定域補列（列出域與載體：＿＿＿） ／ ☐ 丙維持 ／ ☐ 另定＿＿＿
- `refresh_kh4_state.py --existing-only` 旗標新增：☐ 准 ／ ☐ 駁（改用一次性批次）
- erp_tiptop 軸證據是否另案逐域裁決：☐ 開案 ／ ☐ 暫緩
- 簽署：＿＿＿＿＿＿＿＿（hugo TTY 親簽；日期＿＿＿＿）
