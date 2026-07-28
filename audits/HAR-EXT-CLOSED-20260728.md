# HAR-ext＋FT-COV-BATCH CLOSED（2026-07-28）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/HAR-EXT-APPROVED-20260728.md`（Steward `HAR-ext`＋可選 `FT-COV-BATCH`；`FZ-keep`）  
> **計畫**：`reports/augur_knowledge_fulltext_coverage_plan_20260728.md`（P2／P3）  
> **日誌**：`logs/har-ext-20260728/`（p2／batch／build_sentences／embed）  
> **不含**：無 limit 全域放量；FinMind／FRED 解凍；他域進化閉環；把 blocked 洗成全文

## 一、做了什麼

| 階段 | 狀態 | 摘要 |
|---|---|---|
| **拍板登錄** | ✅ | `HAR-EXT-APPROVED-20260728.md` |
| **P2 煙測** | ✅ | 8 域各 `--limit 3`；**無熔斷、無 429、error=0**（出版商 403→`skip_fetch_error` 落帳） |
| **FT-COV-BATCH** | ✅ | 同 8 域各 `--limit 50`；**無熔斷、當日未因 429 停**；全文落地 **4** 筆 |
| **sentences／embed** | ✅ | `build_sentences --scope items`：5 段→93 句；`embed_knowledge` items en：**90 新嵌**／junk 3 |
| **分桶對照** | ✅ | `report_knowledge_fulltext_buckets.py` before／after |
| **FZ-keep** | ✅ | 零 FinMind／FRED |

## 二、P2 數字（每域 limit 3）

| domain | fetched | skip_no_oa | skip_license | skip_pdf | skip_short | error | 備註 |
|---|---:|---:|---:|---:|---:|---:|---|
| medicine | 0 | 2 | 1 | 0 | 0 | 0 | |
| social_sciences | 0 | 3 | 0 | 0 | 0 | 0 | |
| engineering | 0 | 1 | 0 | 0 | 1 | 0 | 另 1×出版商 403→`skip_fetch_error`（總 blocked=3） |
| physics | 0 | 2 | 0 | 0 | 0 | 0 | 另 1×404→`skip_fetch_error` |
| arts_and_humanities | 0 | 3 | 0 | 0 | 0 | 0 | |
| electronics | 0 | 1 | 1 | 0 | 0 | 0 | 另 1×出版商 403→`skip_fetch_error` |
| biochemistry_genetics_and_molecular_biology | 0 | 3 | 0 | 0 | 0 | 0 | |
| agricultural_and_biological_sciences | 0 | 2 | 1 | 0 | 0 | 0 | |
| **合計** | **0** | | | | | **0** | 熔斷＝否 |

**P2 判決**：健康 → 放行 BATCH。

## 三、FT-COV-BATCH 數字（每域 limit 50）

| domain | fetched | skip_no_oa | skip_license | skip_pdf | skip_short | error | circuit |
|---|---:|---:|---:|---:|---:|---:|---:|
| medicine | 0 | 41 | 9 | 0 | 0 | 0 | 0 |
| social_sciences | 0 | 37 | 6 | 3 | 1 | 1 | 0 |
| engineering | 0 | 33 | 8 | 1 | 0 | 0 | 0 |
| physics | 0 | 43 | 3 | 2 | 0 | 0 | 0 |
| arts_and_humanities | 0 | 34 | 12 | 2 | 0 | 0 | 0 |
| electronics | 0 | 48 | 0 | 0 | 0 | 1 | 0 |
| biochemistry_genetics_and_molecular_biology | **2** | 23 | 10 | 13 | 0 | 1 | 0 |
| agricultural_and_biological_sciences | **2** | 22 | 18 | 4 | 1 | 0 | 0 |
| **合計** | **4** | **281** | **66** | **25** | **2** | **3** | **0** |

解讀（對齊計畫 §0／§4）：本批主產物是 **終態帳（skip_*）↑**，非 gov 全文％暴衝；白名單 HTML 全文僅 4 筆屬 OA／license 現實，**非漏抓**。

### 新全文終態鏈（有界）

| item_id | domain | license | sentences | embedded |
|---|---|---|---:|---:|
| 34394 | biochemistry… | cc-by | 2 | 1 |
| 34398 | biochemistry… | cc-by | 7 | 7 |
| 25102 | agricultural… | cc-by | 38 | 38 |
| 25143 | agricultural… | public_domain | 46 | 44 |

（junk 短句 3 筆入 ledger、正確不嵌。）

## 四、gov 分桶前後（真兆；腳本 JSON）

| domain | before ans／blocked／pending | after ans／blocked／pending | Δblocked | Δpending | Δans |
|---|---|---|---:|---:|---:|
| medicine | 0／0／12262 | 0／53／12209 | +53 | −53 | 0 |
| social_sciences | 0／0／12252 | 0／52／12200 | +52 | −52 | 0 |
| engineering | 0／0／9568 | 0／53／9515 | +53 | −53 | 0 |
| physics | 0／0／4586 | 0／53／4533 | +53 | −53 | 0 |
| arts_and_humanities | 0／0／4350 | 0／53／4297 | +53 | −53 | 0 |
| electronics | 0／0／4259 | 0／52／4207 | +52 | −52 | 0 |
| biochemistry… | 0／0／3634 | **2**／50／3582 | +50 | −52 | **+2** |
| agricultural… | 0／1／4869 | **2**／52／4816 | +51 | −53 | **+2** |

每域嘗試 ≈53（P2×3＋BATCH×50）；pending→terminal_blocked 為主，可答僅 +4（兩域）。

## 五、硬邊界核對

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 禁止無 limit 全域放量 | ✅（上限 50／域） |
| blocked 不灌假全文 | ✅ |
| 403／429 不重試風暴 | ✅（無 429；出版商 403 落 skip；暫態 error≤1／域、無連續熔斷） |
| `UNPAYWALL_EMAIL` | ✅（值不入本檔） |

## 六、下一步建議（決策層）

1. **有界續啃 pending**：同批域再 `--limit 200`（或分日）——預期仍以 skip_* 為主；**勿**訂 gov 全文％ KPI。  
2. **PDF 另軸**：本批 `skip_pdf` 25（BATCH）——若要提高「可答」分子，須另拍 PDF 解析案（非本 CLOSED）。  
3. **件 B harvest**：仍另授權；本輪未開。  
4. **市場 API**：仍凍（`FZ-keep`）。
