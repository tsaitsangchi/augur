# FT-COV-DASH＋FT-COV-EMBED CLOSED（2026-07-28）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/FT-COV-DASH-EMBED-APPROVED-20260728.md`（Steward 原文 `FT-COV-DASH`＋`FT-COV-EMBED`；近程計畫採納僅 P0＋P1）  
> **計畫**：`reports/augur_knowledge_fulltext_coverage_plan_20260728.md`  
> **不含**：`HAR-ext`／pending 放量／猛抓全文／FinMind／FRED 解凍／他域進化閉環

## 一、做了什麼

| 階段 | 狀態 | 摘要 |
|---|---|---|
| **P0 DASH** | ✅ | `scripts/report_knowledge_fulltext_buckets.py`（`--selftest`／矩陣／`--json`）；`serve_admin_console._gov_data`／`gov_dashboard_html` 改 §3.2 四欄＋可答%／終態%＋舊 length>200 對照；標題去「至可檢索終態」誤導 |
| **P1 EMBED** | ✅ | `ft_no_sent=0`（勿重切）；`embed_knowledge --gap-fill` 掃 CLEAN 未嵌句→**全 junk 排除入 ledger**；erp 已 100% answerable **未假重嵌全庫** |
| **admin** | ✅ | `systemctl --user restart augur-admin`（ActiveEnterTimestamp 2026-07-28 09:42:30 CST）；函式路徑實測與腳本數字一致（登入牆外 HTTP 僅確認服務 up） |

## 二、儀表前後差異（真兆）

| domain | 舊 headline（length>200／items） | 新 **可答%**（answerable／items） | 新 **終態%** | blocked | pending |
|---|---:|---:|---:|---:|---:|
| **erp_tiptop** | **7%**（10,652／141,873） | **100%**（141,873／141,873） | 100% | 0 | 0 |
| medicine | 0% | 0% | 0% | 0 | 12,262 |
| chemistry | ~1%（92） | 0%（ans=7） | 0% | 61 | 8,994 |
| computer_science | ~1%（85） | 1% | **97%** | 7,079 | 187 |

解讀（對齊計畫 §0）：erp「7%」＝短文門檻假低，非未抓；medicine 等 0%＝**pending 未做**；computer_science 終態高＝大量 `skip_no_oa`／`skip_license`（誠實不可答，**不得灌全文**）。

## 三、EMBED 補洞數字

| 指標 | 數值 | 出處 |
|---|---|---|
| `ft_no_sent`（有 text 無句） | **0** | `build_sentences` 待切／buckets gaps |
| CLEAN `sent_no_emb` 掃過（en） | 7,111 處理／**0 新嵌**／junk 7,111 | `knowledge_embed_ledger` ledger_id=86；note=`FT-COV-EMBED-gap-fill junk=7111 embedded=0` |
| CLEAN `sent_no_emb` 掃過（zh） | 31／**0**／junk 31 | ledger_id=87 |
| 殘餘 raw `sent_no_emb`（含非 CLEAN） | 13,238 | book／compound／material 等 **語意層 entity 排除**＋junk 短句／超長段——**正確不嵌** |
| chemistry 可答 | 仍 **7** | 有 text 389 中 382＝material／compound（CLEAN 排除）；非漏嵌 |
| erp | 可答 **100%** | 禁止整庫假重做；殘餘 junk 句已 ledger |

驗收對照計畫 V1／V3：gov 四欄可見；CLEAN 可嵌池＝0（junk／CLEAN 排除已入帳）。

## 四、硬邊界核對

| 項 | 本輪 |
|---|---|
| 零 FinMind／FRED；不解凍 | ✅ |
| 不把 skip_*／blocked 灌成全文 | ✅ |
| 不開太陽能↔儲能他域進化閉環 | ✅ |
| 素養層不進預測管線 | ✅ |
| #1／#8／全文三軌 | ✅ |

## 五、下一步（仍待另碼）

- **清 pending／有界 OA**：需 **`HAR-ext`**（± `FT-COV-BATCH`）；本輪**未**開。  
- medicine／social_sciences／engineering 等仍全 pending——儀表現已誠實標示，**不是**儀表 bug。  
- 可選：超長「一句」切句品質（junk>1000）另案，非本輪範圍。
