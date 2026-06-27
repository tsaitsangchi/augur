# 三鏡頭欄位地圖 — raw 欄位定義 × 量 × 形 × 位(2026-06-27)

> **性質**:以四份鏡頭報告之框架,重檢 `column_catalog` 全部數值訊號欄、為每欄標註「三鏡頭特徵設計潛力」,整理成 DB 表 `field_lens_map` + 本報告。**參考層**(特徵設計地圖、非生產特徵;實際特徵仍須過漏斗 #11)。
> **框架 SSOT(四報告)**:`augur_first_principles_research`、`augur_pareto_principle_research`、`augur_kondratiev_cycle_research`、`augur_three_lens_synthesis_20260627.md`(綜合:**量 × 形 × 位**三正交軸)。
> **產物**:表 `field_lens_map`(342 欄)、CLI `scripts/build_field_lens_map.py`(規則引擎、可重跑)。本地計算、零 Claude usage(#28)。

---

## 一、方法

**命題(承綜合報告)**:任何 raw 欄位都可由三正交軸描述——**量**(第一性/資訊內容)× **形**(八二/分布集中度)× **位**(康波/時間相位)。本地圖即把 342 個數值訊號欄各自定位於此三軸。

**做法**:四鏡頭框架對映到 **21 個欄位類別**(依 dataset + 欄名 pattern 分類);每類別有 doctrine 推導之三鏡頭標準映射。規則引擎(`build_field_lens_map.py`)4-pass 分類(ds+col 皆具者須兩者皆中,解同表混型如 Price.close→價格 / volume→量能)。

**表 schema** `field_lens_map`:`dataset, column_name, column_name_zh, field_category, first_principle(量), pareto_lens(形), kondratiev_lens(位), anti_leakage(P-lag), note`,PK(dataset, column_name)。

---

## 二、21 類別 × 三鏡頭映射(★=該軸強適用)

| 類別 | 欄數 | 量(第一性) | 形(八二) | 位(康波) |
|---|---|---|---|---|
| **價格** | 57 | ★水位/動能/缺口 | ★報酬集中 skew/kurt/Gini(rolling \|日報酬\|) | ★range-position/drawdown/共振(C2 存活軸) |
| 衍生品 | 42 | 衍生品部位/避險 | 多空部位集中 | 未平倉 range-position |
| 證金擔保 | 34 | 信用/證金放款籌碼 | 放款結構集中 | 放款餘額 range-position(信用循環) |
| 借券放空 | 34 | 空方籌碼/擁擠度 | 空方力量集中(借券vs融券) | 空方循環相位 |
| **法人資金流** | 32 | 籌碼流(誰在買賣) | ★HHI/max-share(跨法人玩家集中) | ★累計淨流 range-position(吸籌/派發、C4 存活軸) |
| 一般數值 | 25 | 水位(待判) | (視窗/橫斷面可構) | range-position(自身歷史) |
| **量能** | 24 | ★流動性/量能 | ★量能時間集中 Gini/max-share(P3 存活軸) | ★量能相位/量價相位差 |
| 股利配息 | 21 | ★股利政策/品質 | — | —(政策事件、P-lag) |
| 可轉債 | 21 | 信用/可轉債部位 | — | 發行/流通餘額 range-position |
| 融資券餘額 | 11 | 個股槓桿(信用循環) | — | ★融資餘額 range-position/增減速(Minsky) |
| 外資持股 | 8 | 結構性少數關鍵者籌碼 | 外資 share/距上限空間 | 外資持股 range-position |
| **宏觀指數** | 7 | 宏觀景氣(context) | — | ★景氣循環相位/減速/領先-同時背離(C1) |
| 匯率 | 6 | 匯率(資金潮汐 context) | — | ★台幣循環相位(C1) |
| **估值** | 5 | ★估值缺口 | 橫斷面估值分散(regime) | ★估值 range-position(再評價動能) |
| 人數計數 | 3 | 參與廣度 | (若分布)集中度 | 參與度 range-position |
| **營收基本面** | 3 | ★基本面品質 | 營收佔產業 share/季節熵 | ★YoY 動能+減速/基期結構(C3、P-lag) |
| 財報科目 | 3 | 基本面品質 | 獲利佔產業 share(品質馬太) | ★庫存/capex/margin 循環(Kitchin/Juglar、P-lag) |
| 利率利差 | 2 | 宏觀資金成本(context) | — | ★利率循環相位/倒掛深度(C1) |
| **持股分級分布** | 2 | 籌碼結構(誰擁有) | ★Gini/HHI/熵(級距分布)+Δ集中度 | 集中度循環相位 |
| 情緒 | 1 | 情緒(context) | — | ★情緒循環極值距離(C1) |
| 市值規模 | 1 | ★規模(size) | 市場集中(市值佔全市場 share) | 規模 range-position |

---

## 三、整體覆蓋

| 指標 | 值 |
|---|---|
| 數值訊號欄 | **342** |
| 八二可做(有分布集中度結構) | **273 / 342**(80%) |
| 康波特化相位(非預設 range-position) | **317 / 342**(93%) |
| P-lag(發布日 gate、#8) | 36(營收/財報/股利/宏觀/利率) |
| 一般數值(未明確分類) | 25(7%) |

**核心特徵管線 12 表 100% 分類**(Price/PriceAdj/法人/持股分級/估值/融資券/外資/營收/借券/短賣/官股/市值,0 generic)。

---

## 四、重點解讀

1. **量能、法人流、價格是多鏡頭最富欄位**(三軸皆★)——本 session 存活特徵正出自此三類(量能集中 P3、流相位 C4、價格相位 C2),地圖事後印證。
2. **康波幾乎全適用(93%)**:任何時序欄都可做 range-position 相位——時間結構是最普適鏡頭(但須防 apophenia,見綜合報告)。
3. **八二需「分布結構」**(80%):跨成分(法人玩家、持股級距)或跨時窗(量/報酬)才有集中度可做;單一純量(估值/利率)無。
4. **P-lag 36 欄**:營收/財報/股利/宏觀/利率須發布日 gate——**catalog 之 `anti_leakage_flag` 未填、本地圖由鏡頭框架已知補正**(#8)。
5. **context 類(宏觀/匯率/利率/情緒)= 康波 C1 景氣循環素材**——X 類、與個股相位交互(綜合報告之跨鏡交互)。

---

## 五、Caveats(#15)

- **機械分類非定論**:依 pattern 規則,供特徵設計**起點參照**;某欄真正有用之軸仍須過五鏡 + 提拔關卡(#11)裁決。
- **25 generic 為邊陲**:國際股(歐/日/英/美)、期權子欄、漲跌限、減資參考價、處置、權證彙總——非台股單股特徵標準源,給預設 量×位 fallback。
- **★ 為「適用」非「有效」**:標★表示該軸**可做**,不保證有 alpha(本 session 12 軸只 4 軸存活即證)。
- **anti_leakage 由 doctrine 補**:catalog flag 原為空,本地圖按類別補 P-lag;非欄位級逐一實證,實作時仍須查發布時點。

---

## 六、如何用

特徵設計時 query 此表為起點:
- `SELECT * FROM field_lens_map WHERE first_principle LIKE '★%'` → 第一性強欄(直接資訊內容)
- `WHERE pareto_lens LIKE '★%'` → 可做集中度泛函之欄(八二)
- `WHERE kondratiev_lens LIKE '★%'` → 可做特化相位之欄(康波)
- **跨鏡交互前沿**(綜合報告):同欄之 形×位(集中度×相位)、量×位(水位×相位)乘積=未開採特徵空間。

> 紀律不變:地圖只**提示生成**;市場(漏斗)才**裁決有效**(綜合報告精華⑦)。

---

## 來源
- 框架:四鏡頭報告(`augur_first_principles_research` / `_pareto_principle_research` / `_kondratiev_cycle_research` / `_three_lens_synthesis_20260627.md`)
- 資料:`column_catalog`(751 欄、95 dataset);本地圖取其 342 數值訊號欄
- 工具:`scripts/build_field_lens_map.py`;表 `field_lens_map`
