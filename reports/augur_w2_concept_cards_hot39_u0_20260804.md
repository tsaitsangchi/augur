# W2 概念卡圈選包｜熱路徑 binding **39** ＋ U0 六條（2026-08-04）

> **位階**：[I] 備料／圈選單（CLAUDE #16）。**非** [N]；AI **不代簽** `decided_by`／不執行寫庫 SQL。  
> **授權**：Steward 本輪明示「**圈選熱路徑 39＋U0 六條概念卡**」（承接甲案 triage 建議第 3 項）。  
> **上游**：  
> - triage：`reports/augur_w2_65_triage_20260804.md`  
> - U0 底稿：`reports/augur_w2_phase1_concept_unblock_prep_20260803.md` §3  
> - 形制：`reports/augur_w2_undefined_concept_unblock_plan_20260803.md` §1.3  
> - 抽樣：`reports/augur_w2_source_column_reconcile_sampling_20260803.md` §2  
> - 親簽 SQL 形制先例：`reports/wm_channel_registration_draft_20260803.md` §7  
> **WM.36**（constitution-mcp）：登錄項最低七欄＝世界概念／歸類／通道映射／權威表徵／通道時間雙宣告（含跨市場軸若適用）／provenance／定案性述語；消費須以概念為鍵。  
> **硬紀律**：本檔 **零** `INSERT`/`UPDATE` Registry；**零**假 mapped；概念卡 ≠ 登錄完成。API 解凍（若已成立）**不**授權本批寫概念庫。

---

## 0. 本包範圍與驗收

| 項 | 內容 |
|---|---|
| **圈選集合** | **7** 張卡＝HP-39（`TaiwanStockBlockTrade`）＋ U0-1…U0-6（binding 7／37／50／65／80／97） |
| **本輪交付** | 可勾選圈選單＋七欄草稿＋共病旗標＋寫庫閘清單 |
| **本輪不做** | 親簽 SQL 執行、`source_column` 填滿、權威採認、改消費端直綁、FinMind sync |
| **驗收（文件）** | Steward 於 §5 每列勾選（登錄／改名／俟 Q-R*／不登錄）；勾完＝「圈選完成」≠「已寫庫」 |
| **驗收（寫庫）** | **另句**：`Q-R1` 形制＋`honesty_write` 明示＋hugo 親打 `decided_by`／`decided_at` |

---

## 1. 為何這 7 條（triage 對齊）

| 優先 | binding | 表 | 桶 | 一句理由 |
|---|---:|---|---|---|
| **P1 熱** | **39** | `TaiwanStockBlockTrade` | 需新卡_熱路徑 | vendor 直綁仍在消費（`field_correlation.py` `block_money`←`sum(trading_money)`） |
| U0 | 7 | `TaiwanStockConvertibleBondInfo` | 需新卡_U0抽樣 | 抽樣已提案鍵；概念空白 |
| U0 | 37 | `JapanStockPrice` | 同上 | 跨市場＋derived 同表 |
| U0 | 50 | `GoldPrice` | 同上 | 單欄最乾淨樣本 |
| U0 | 65 | `TaiwanOptionInstitutionalInvestorsAfterHours` | 同上 | 多欄流量＋列鍵 |
| U0 | 80 | `TaiwanStockSplitPrice` | 同上 | 同表兩概念（W2-5） |
| U0 | 97 | `TaiwanFuturesDaily` | 同上 | 全 PK／值欄偵測失效（W2-6） |

**刻意不進本包**：緩登 13、out 候補 8、其餘需新卡 37、草案殘 20（另刀）。

---

## 2. 概念卡（形制＝§1.3；self-reported 提案鍵）

> 欄位：`concept_key`｜`category`｜`identity_one_liner`｜`candidate_binding_ids`｜`proposed_source_columns[]`｜`co_morbid`｜`knows_consumption?`｜`draft_ref`  
> **禁假 concept**：不得用表名充 Identity；不得為覆蓋率 INSERT 空殼。

### 卡 HP-39｜binding **39** `TaiwanStockBlockTrade`（本輪新增）

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.block_trade.print`（提案；平行既有籌碼／流量命名） |
| **category** | `event`（逐筆鉅額成交列；替代讀：把日加總金額當 `quantity`＝**仍待裁**） |
| **identity_one_liner** | 台股個股鉅額交易盤之逐筆成交（類別／價／量／金額），非日報彙總表 |
| **candidate_binding_ids** | `[39]`（**不**併 binding **42** `TaiwanStockBlockTradingDailyReport`——該表 triage＝B0 緩登、無實體表） |
| **proposed_source_columns[]** | **入（消費實證）**：`trading_money`（現直綁加總）；**同事件伴隨**：`price`,`volume`；**列維度（非事實載體）**：`trade_type`（`單一型`／`逐筆交易`／`配對交易`——Q-R2 味） |
| **co_morbid** | 多值／列篩選（`trade_type`）；W2-1 若堅持單 text `source_column`；與 B0 日報表語意分離 |
| **knows_consumption?** | **yes**——`src/augur/audit/field_correlation.py:75`（`block_money`）；衍生 `block_share`（同檔 :120） |
| **draft_ref** | triage §需新卡_熱路徑；FinMind／欄走查：`date,stock_id,trade_type,price,volume,trading_money`（`reports/augur_full_column_walkthrough_20260629.md` §TaiwanStockBlockTrade）；schema 目錄 6 欄 |
| **WM.36 七欄草擬（未採認）** | ①鍵＝上；②event；③映射＝39＋欄集；④權威＝建議 39；⑤ts＝交易日／盤後可得（法定公開規則型，表內無公告欄——**人裁**）；跨市場＝N/A；⑥provenance＝本檔＋消費點路徑；⑦finality＝建議「當日值於次一交易日收盤後定案」（A.37 例示語——**人裁**） |

### 卡 U0-1｜binding **7** `TaiwanStockConvertibleBondInfo`

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.convertible_bond.terms` |
| **category** | `state`（條款狀態；替代 `entity` **仍待裁**） |
| **identity_one_liner** | 台股可轉債之發行／轉換條款（金額與轉換起迄），非日頻成交列 |
| **candidate_binding_ids** | `[7]` |
| **proposed_source_columns[]** | `IssuanceAmount`, `InitialDateOfConversion`, `DueDateOfConversion`（**出**候補：`cb_name`） |
| **co_morbid** | W2-1 |
| **knows_consumption?** | unknown（P1 全掃未做） |
| **draft_ref** | prep §3 U0-1；抽樣 §2 #1 |

### 卡 U0-2｜binding **37** `JapanStockPrice`

| 欄 | 值 |
|---|---|
| **concept_key** | `jp.daily_bar`（**Q-R8 仍待裁**） |
| **category** | `quantity` |
| **identity_one_liner** | 日本市場個股日頻 OHLCV 觀測（原始價通道） |
| **candidate_binding_ids** | `[37]`（建議另拆 **derived** 承 `Adj_Close`） |
| **proposed_source_columns[]** | `Open`,`High`,`Low`,`Close`,`Volume`；**出／第二概念**：`Adj_Close`（W2-3） |
| **co_morbid** | W2-3、Q-R8、A.35 跨市場軸 |
| **knows_consumption?** | unknown |
| **draft_ref** | prep §3 U0-2；抽樣 §2 #4 |

### 卡 U0-3｜binding **50** `GoldPrice`

| 欄 | 值 |
|---|---|
| **concept_key** | `cm.gold.spot_price`（**Q-R8 仍待裁**） |
| **category** | `quantity` |
| **identity_one_liner** | 黃金現貨／報價水準（單一價格觀測；單位／幣別不在 schema） |
| **candidate_binding_ids** | `[50]` |
| **proposed_source_columns[]** | `Price`（抽樣：機械自動配對＝True） |
| **co_morbid** | 結構輕；欄 1／5／單位語意仍人裁 |
| **knows_consumption?** | unknown |
| **draft_ref** | prep §3 U0-3；抽樣 §2 #5 |

### 卡 U0-4｜binding **65** `TaiwanOptionInstitutionalInvestorsAfterHours`

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.option.institutional_flow.after_hours` |
| **category** | `quantity` |
| **identity_one_liner** | 台股選擇權盤後時段法人多空成交量／金額流量 |
| **candidate_binding_ids** | `[65]` |
| **proposed_source_columns[]** | `long_deal_amount`,`long_deal_volume`,`short_deal_amount`,`short_deal_volume` |
| **co_morbid** | W2-1；M-W4 列鍵；盤後 ts 語義 |
| **knows_consumption?** | unknown |
| **draft_ref** | prep §3 U0-4；抽樣 §2 #7 |

### 卡 U0-5｜binding **80** `TaiwanStockSplitPrice`

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.corporate_action.split`（平行既有 `tw.corporate_action.ex_dividend`） |
| **category** | `event` |
| **identity_one_liner** | 股票分割公司行動（恢復買賣日為 ts；分割前後參考價與類型） |
| **candidate_binding_ids** | `[80]`＋**建議第二 binding** 承漲跌停參考態（A.26） |
| **proposed_source_columns[]** | **入**：`before_price`,`after_price`,`type`；**出／第二概念**：`max_price`,`min_price`,`open_price`（W2-5） |
| **co_morbid** | W2-1、W2-5 |
| **knows_consumption?** | unknown |
| **draft_ref** | prep §3 U0-5；抽樣 §2 #8 |

### 卡 U0-6｜binding **97** `TaiwanFuturesDaily`

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.futures.daily_bar` |
| **category** | `quantity` |
| **identity_one_liner** | 台股期貨契約日頻行情與未平倉（含結算／價差／量） |
| **candidate_binding_ids** | `[97]` |
| **proposed_source_columns[]** | 事實載體：`open`,`max`,`min`,`close`,`settlement_price`,`spread`,`spread_per`,`volume`,`open_interest`；鍵＝`futures_id`,`contract_date`,`date`,`trading_session` |
| **co_morbid** | **W2-6／Q-R7**（值欄機械偵測＝0） |
| **knows_consumption?** | unknown |
| **draft_ref** | prep §3 U0-6；抽樣 §2 #10 |

---

## 3. 寫庫前硬閘（勾選≠放行）

| # | 閘 | 狀態（2026-08-04） | 擋誰 |
|---|---|---|---|
| G1 | **Q-R1** unmapped→mapped：(a) UPDATE vs (b) supersede+INSERT | **仍待裁** | 全部寫庫 SQL 形狀 |
| G2 | **W2-1** 多欄 `source_column` 形制 | **仍待裁** | 7／65／80／39（多欄入） |
| G3 | **Q-R8** 非 `tw.` 命名空間 | **仍待裁** | 37／50 |
| G4 | **W2-3／W2-5／W2-6** 結構債 | 文件已知 | 37／80／97 |
| G5 | `SET LOCAL augur.honesty_write='on'` 明示同意 | 未本輪授 | UPDATE binding |
| G6 | hugo 親打 `decided_by`／`decided_at` | 未填 | 版本列採認 |
| G7 | 消費端改繫概念鍵（解除直綁） | **另授權** | HP-39 解直綁≠本包 |

**建議最小可寫子集（若 Steward 要先試一刀）**：僅 **U0-3 GoldPrice**（單欄＋自動配對 True）——仍須 G1＋G5＋G6；且 **Q-R8** 若堅持全 `tw.` 則先改名。

**熱路徑優先寫庫序（建議）**：HP-39 → U0-3 → U0-1 → U0-4 → U0-5 → U0-6 → U0-2（跨市場最後）。

---

## 4. 與 API 解凍／預測之正交

| 軸 | 本包 |
|---|---|
| Registry 概念卡 | **本檔** |
| FinMind／FRED 取數 | **不**因本圈選自動開跑；解凍另見 `audits/API-THAW-20260804.md`（若已生效） |
| 預測熱路徑 | 仍庫內 as-of；**不**把本卡當可交易／確立級 |

---

## 5. Steward 圈選單（已定案）

> **定案**（2026-08-04）：Steward「**直接回**」＝採示例句  
> `CIRCLE-39-U0: 登錄 HP-39+U0-3；其餘俟 Q-R*`  
> **確認**：同日 Steward「**提案批准**」＝上列圈選提案層正式通過。  
> **語意**：概念卡層批准登錄提案；**≠** 寫庫授權（仍須 G1–G6＋另句）。

| # | concept_key（提案） | binding | 圈選 |
|---|---|---:|---|
| HP-39 | `tw.block_trade.print` | 39 | ☑ **登錄**（寫庫前仍須 Q-R2／W2-1 形制可解析） |
| U0-1 | `tw.convertible_bond.terms` | 7 | ☑ **俟** W2-1（本句「其餘俟 Q-R*」） |
| U0-2 | `jp.daily_bar` | 37 | ☑ **俟** Q-R8／W2-3 |
| U0-3 | `cm.gold.spot_price` | 50 | ☑ **登錄**（寫庫前仍須 Q-R8 或改名裁定） |
| U0-4 | `tw.option.institutional_flow.after_hours` | 65 | ☑ **俟** W2-1／列鍵 |
| U0-5 | `tw.corporate_action.split` | 80 | ☑ **俟** W2-5 |
| U0-6 | `tw.futures.daily_bar` | 97 | ☑ **俟** W2-6／Q-R7 |

**同批附裁（本輪未裁＝維持「本包不裁／不授」）**

| 項 | 圈選 |
|---|---|
| Q-R1 形制 | ☑ 本包不裁 |
| honesty_write 通行證 | ☑ 本包不授 |
| 下一步 | ⏳ 待 Steward：備最小寫庫 SQL／只凍結／改開他刀 |

---

## 6. 複核指令（寫庫前／圈選後可跑；唯讀）

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
venv/bin/python scripts/reconcile_channel_columns.py --survey
# 確認 7 個 binding 仍 unmapped／concept_key IS NULL：
venv/bin/python - <<'PY'
from augur.core.db import connect
ids = [39, 7, 37, 50, 65, 80, 97]
with connect() as c:
    cur = c.cursor()
    cur.execute("""
      SELECT binding_id, source_table, concept_key, mapping_status, source_column
      FROM world_channel_binding
      WHERE binding_id = ANY(%s) AND superseded_at IS NULL
      ORDER BY 1""", (ids,))
    for r in cur.fetchall():
        print(r)
PY
rg -n 'TaiwanStockBlockTrade' src --glob '*.py'
```

---

## 7. 未做／誠實邊界

- 本輪 **未** live 重查七表列數／as-of（沿用 08-03 抽樣＋欄走查＋code 消費點；寫庫前建議重跑 §6）。  
- 提案鍵與七欄草擬＝**self-reported**（CLAUDE #32a），非「世界如此」。  
- 未改 `field_correlation.py` 直綁；未碰 `world_concept*`。

---

*完。零 DB 寫入、零 commit。*
