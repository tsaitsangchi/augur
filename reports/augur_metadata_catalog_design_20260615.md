# augur 元資料登錄（metadata-catalog）架構設計 — 2026-06-15

**性質**：詳細設計檔。**被憲章第三部「橫切 · catalog」元件引用**（憲章承載架構框架、本檔承載詳細設計，守憲章第六部 SSOT 分家 + 30 分鐘可讀）。
**clean-room（#16）**：只依 5 治權檔 + `docs/datasets_zh.md`（本 session 實證）+ live API 事實。
**緣由**：把「怎麼抓每個 dataset」的元資料從「邊探邊抓 / 散落 code / markdown」正規化為 **DB 登錄表**，作未來抓取的**單一驅動依據**——契合 #18（依 API 探測、可刷新、非硬編白名單）。

---

## 1. 一句話
把 `datasets_zh.md` + fetch-plan **正規化進 DB 的 2 張登錄表**，sync 引擎讀它驅動「怎麼抓」（最優模式/範圍/data_id/排除），人看的 `datasets_zh.md` 由表自動生成。**表＝SSOT、md＝視圖。**

---

## 2. 兩張登錄表 schema

### `dataset_catalog`（表級，每 dataset 一列）
| 欄位 | 型別 | 說明 |
|---|---|---|
| dataset | VARCHAR PK | FinMind/FRED dataset 名 |
| source | VARCHAR | `finmind` / `fred` |
| category | VARCHAR | 技術/籌碼/基本面/衍生/可轉債/其他/國際/總經/FRED |
| tier | VARCHAR | F / F(id) / B / S |
| endpoint | VARCHAR | `/data` / dedicated / `/series/observations` |
| excluded | BOOL | 是否排除（real-time/OUT_OF_UNIT）|
| excluded_reason | VARCHAR | 排除原因（#4 intraday / 規模物理不可行）|
| fetch_mode | VARCHAR | per-stock / by-date / by-dim-id / market / single-day（**動態重算、見 §3.3**）|
| data_id_source | VARCHAR | `/datalist` / roster / none / 文檔 |
| earliest_date | DATE | 實證最早日期（DB MIN 或 probe）|
| frequency | VARCHAR | daily / quarterly / monthly / event / snapshot |
| n_stocks | INT | per-stock universe（DB distinct stock_id 或估）|
| n_dates | INT | by-date 期數（DB distinct date 或估）|
| anti_leakage_note | TEXT | 公告時點欄 / as-of 錨（#8）|
| source_provenance | VARCHAR | earliest/mode 來源：DB / probe / 文檔 |
| last_verified | TIMESTAMP | 最近一次 builder 刷新時點（#15）|
| notes | TEXT | 特殊處理（單日型 end_date none、契約碼…）|

### `column_catalog`（欄級，每 (dataset,column) 一列）
| 欄位 | 型別 | 說明 |
|---|---|---|
| dataset | VARCHAR | 複合 PK |
| column_name | VARCHAR | 複合 PK；API 原欄名 |
| ordinal | INT | 欄序（依 API）|
| column_name_zh | VARCHAR | 中文名 |
| zh_source | VARCHAR | `FM`（/translation 官方）/ `金融`（專業用語）/ `派生` |
| inferred_type | VARCHAR | DATE/NUMERIC/VARCHAR/TEXT（augur `generic_schema` 推導）|
| size | VARCHAR | 大小（VARCHAR(255)/NUMERIC(20,6) 預設或 DB 實際）|
| is_pk | BOOL | 是否主鍵欄 |
| anti_leakage_flag | BOOL | 是否公告時點/as-of 欄（#8 金礦）|
| last_verified | TIMESTAMP | |

> 即 `datasets_zh.md` 之正規化：表級＝🔌+📅+tier+category；欄級＝逐欄中英+來源+型別。

---

## 3. 四個關鍵設計原則（做對、否則踩雷）

### 3.1 catalog = 可刷新快取/提示，**非鐵契約**（守 #18、不脆）
- FinMind 會改 dataset/欄/起訖 → 登錄會過時。
- 引擎用登錄模式抓；**登錄失效（回非預期/空）→ adaptive fallback 重 probe → 回寫更新 catalog**。
- 結果：planned（快+省）+ adaptive 退路（穩）——仍守 #18「問 API」，登錄只是 API 探測的**持久化**。

### 3.2 存 provenance + last_verified（守 #15）
- 每個 earliest/mode/中文/型別都標來源（DB 真值 / probe / 文檔 / FM 官方 / 金融用語）+ 驗證時點。
- 誠實可審：型別/中文是 **augur 推導/策展、非 FinMind 權威**（FinMind 不給型別）→ 明標、不當 gospel。

### 3.3 存原料、**動態重算最優模式**（不凍結會變的值）
- `fetch_mode` 不寫死——存 `earliest_date / n_stocks / n_dates / frequency` 原料，由引擎/plan 產生器**即時算** `min(per-stock=N_stocks, by-date=N_dates, …)`。
- 因新表 by-date 期數會隨時間長 → 凍結會失準（如 2024 表今年 by-date 1500、明年 1800）。

### 3.4 refresh 程式定期刷新
- builder 於建構期 + 定期（或大 sync 前）重 probe → 更新 catalog（新 dataset/欄/最早日期/n_dates）。
- 刷新本身遵 #17 三層限速 + #25 最小單位探測。

---

## 4. 如何驅動 sync（對映 optimization plan 三階段）
```
階段 P 計畫（0 API）：SELECT dataset_catalog → 每表動態算最優模式+呼叫數 → token 預算/排序
階段 F 抓取（限流內）：依 catalog 模式/範圍/data_id 抓；失效→adaptive fallback 回寫
階段 A 證明（輕量）：對帳/attestation 獨立（catalog 不負責「資料對」，只負責「怎麼抓」）
```
詳見 `reports/augur_sync_optimization_plan_20260615.md`；token 預算實證見 `augur_sync_plan_budget_20260615.md`（最優 ~128k calls、6/24 充裕）。

---

## 5. builder（怎麼填表）
- 一支 `scripts/build_catalog.py`（未來、需授權）：
  1. dataset 全集：`sync.daily_datasets()` + FRED series。
  2. 欄位/型別：最小單位 probe `/data`（每表 1 列）→ `generic_schema.infer_schema`（已落地表讀 DB schema 真值）。
  3. 中文：`/translation`（FM 官方 9 表）+ 金融用語（其餘）。
  4. 最早日期：DB MIN（已落地）/ wide-probe（未落地）。
  5. tier/排除/data_id 來源：`/user_info` + `/datalist` + #18 階層。
  6. 寫入 2 表 + `last_verified`。
- **本 session 已手做一遍**（datasets_zh.md + 各 /tmp JSON）→ builder＝其自動化版。

---

## 6. 與 `datasets_zh.md` 的關係
- **表＝SSOT**；`datasets_zh.md` 改由 `SELECT catalog → 產 markdown`（人看視圖、可重生）。
- 過渡：現行手做的 `datasets_zh.md` 先當種子；builder 上線後反向由表生成。

---

## 7. 對映原則
| 原則 | 對映 |
|---|---|
| #18 抓取依 API 探測 | catalog ＝探測結果之**持久化 + 可刷新**（非硬編白名單，仍問 API）|
| #3 純通用 ingestion | 無 dataset 白名單；catalog 由 API 全集自動填 |
| #2 API 即權威 | 欄名/型別/起訖以 API 探測為準 |
| #15 誠實 | provenance + last_verified + 型別非 FinMind 權威明標 |
| #7 對帳 | **獨立**——catalog 驅動「怎麼抓」、不保證「資料對」 |

---

## 8. 誠實 caveats（#15）
- catalog **驅動「怎麼抓」，不取代對帳/attestation**（資料正確性仍獨立守 #7）。
- type/中文 = augur 推導/策展，非 FinMind 提供 → 明標 provenance。
- 登錄會過時 → 必須 adaptive fallback + refresh，否則脆。
- 動態重算最優模式（別凍結 n_dates 這種會變的值）。

---

## 9. 落地步驟（未來、每步需授權）
1. 建 2 表（explicit DDL、屬「計算型內部表」走各自 builder，憲章第五部第三種建法）。
2. `build_catalog.py` 填表（建構期一次 + 定期 refresh）；本 session 手做版為種子。
3. sync 引擎改讀 catalog 驅動（optimization plan 階段 F）；保 adaptive fallback。
4. `datasets_zh.md` 改由表生成。
5. 每步小範圍試 + 對帳 PASS 才放量。

> 本檔為**設計計畫**；建表/builder/改引擎均屬動 code + 放量，依治權協議須用戶授權。
