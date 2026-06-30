# 投資哲學框架層 — 規劃報告(相容靈魂版、2026-06-30)

> **性質**:重大方向規劃 + 入憲方案。把 augur 從「純量化」提升為「**有投資智慧理論骨架的量化顧問**」——投資哲學作為**特徵設計的理論指導 + 股票 context 分類層**,**非** AI 對話大師、**非**預測來源。
> **定位裁決(用戶 2026-06-30 directive)**:選「理論框架層(相容)」——故全程守靈魂三敵(#1 零幻像 / #8 anti-leakage / #15 誠實),哲學來源**真實權威文獻(非 AI 生成)**、預測**仍靠真實資料量化**、哲學假說**須過四道漏斗 + 經濟價值 #14 驗證活下來才算**。

---

## 〇、一句話

投資哲學框架層 = 把**人類投資大師的智慧(真實文獻)** 結構化為「**可證偽的因子假說 + 股票分類框架**」存入 DB,**指導特徵發現、解讀量化結果**;但「**大師**」的本質仍是 augur 靈魂——**只用真實資料誠實預測、有紀律的顧問、驗證活下來才算數**,哲學是骨架不是占卜。

## 一、為何相容靈魂(關鍵論證)

augur 三鏡頭(**第一性原理 / 八二法則 / 康波週期**)**本來就是投資哲學的操作化** —— 這個方向不是轉向,是把「隱性的三鏡頭」擴充為「**顯性、可考、可擴充的投資哲學框架庫**」。相容性三條鐵則:

1. **哲學是假說來源、非真兆**:哲學原則 → 可量化因子假說 → **過四道漏斗 + #14 經濟價值才採用**(靈魂「有用＝驗證活下來、非設計出來」)。巴菲特說的不算數,**out-of-sample 撐住才算數**。
2. **來源真實文獻、非 AI 生成**:哲學內容一律出自**真實權威文獻**(原典書籍 / 學術論文),策展引用、可溯源(#10);**禁從 AI 平台生成內容入庫當真兆**(違 #1/#16,零容忍)。
3. **context 分類靠真實量化、非主觀**:股票的哲學標籤(價值股/成長股…)由 **feature_values 量化判定 + as-of #8**,非人工主觀貼標。

## 二、投資哲學框架盤點(真實權威文獻 → 可量化)

| 學派 | 代表/原典 | 核心原則 | 可量化因子 → augur 特徵 |
|---|---|---|---|
| **價值投資** | Graham《證券分析》《智慧型投資人》| 安全邊際、均值回歸、低估 | pe_ratio / pb_ratio / price_to_10yr ✓ |
| **品質/護城河** | Buffett 股東信、Greenblatt | 高 ROE/毛利、穩定獲利 | gross_margin_pctile ✓ / ROE(待建)|
| **成長投資** | Fisher《非常潛力股》| 營收/盈餘成長動能 | monthly_revenue_yoy ✓ / **Δmonthly_revenue_yoy(加速度、驗證中)** |
| **動能** | Jegadeesh-Titman | 強者恆強(中期)| momentum_20/60/120/252d ✓ |
| **市場週期** | Howard Marks《投資最重要的事》/ 康波 | 鐘擺、位階、循環相位 | cycle_position / range_position / inst_cumflow_position ✓ |
| **逆向/情緒** | Dreman、行為財務 Kahneman | 過度反應反轉、極端情緒 | days_since_high / 極值 transform / CnnFearGreed(context)|
| **籌碼/聰明錢** | 法人追蹤 | 機構/外資動向 | institutional_net_buy / foreign_holding / gov_bank ✓ |
| **流動性/規模** | Fama-French SMB | 小型股溢酬、流動性 | market_cap_log / dollar_volume / turnover ✓ |
| **股息** | 股息折現、貴族股 | 殖利率、配息穩定 | dividend_yield ✓ |
| **因子投資** | Fama-French / AQR | value/size/momentum/quality/low-vol | 多數已有 ✓ + volatility_60d(low-vol)|

**觀察**:augur 35 feat **已覆蓋 8-9 大學派的核心因子**——哲學框架層的價值是**把這隱性對映顯性化、補缺口(ROE/低波/逆向)、系統化產生新假說**。

## 三、PostgreSQL schema 設計

守 augur 命名慣例(領域名詞)+ 可溯源(#10)+ as-of(#8)。**新增 6 表**(不動現有管線表):

```sql
-- 1. 投資學派(真實文獻為據)
CREATE TABLE philosophy_school (
    school_id    SERIAL PRIMARY KEY,
    name         VARCHAR(64) NOT NULL UNIQUE,      -- 'value' | 'quality' | 'momentum' | 'cycle' ...
    name_zh      VARCHAR(64),
    core_thesis  TEXT NOT NULL,                    -- 核心理念(策展自原典)
    proponents   TEXT                              -- 代表人物
);

-- 2. 可證偽原則(每學派之具體主張)
CREATE TABLE philosophy_principle (
    principle_id   SERIAL PRIMARY KEY,
    school_id      INTEGER NOT NULL REFERENCES philosophy_school,
    statement      TEXT NOT NULL,                  -- 原則陳述
    hypothesis     TEXT NOT NULL,                  -- 可證偽假說(→ 因子方向預測)
    status         VARCHAR(16) DEFAULT 'untested'  -- untested|validated|rejected(經四道漏斗+#14)
);

-- 3. 原則 → 量化因子 → augur 特徵 映射
CREATE TABLE principle_factor_map (
    map_id        SERIAL PRIMARY KEY,
    principle_id  INTEGER NOT NULL REFERENCES philosophy_principle,
    feature       VARCHAR(255),                    -- 對映 feature_values.feature(已有)或待建
    direction     SMALLINT,                        -- 預期 IC 方向 +1/-1
    validated_ic  DOUBLE PRECISION,                -- 實證 as-of IC(過漏斗後回填、可溯源)
    validated_econ TEXT                            -- 經濟價值結論(#14)
);

-- 4. 真實文獻來源(可溯源 #10、禁 AI 生成)
CREATE TABLE philosophy_source (
    source_id    SERIAL PRIMARY KEY,
    school_id    INTEGER REFERENCES philosophy_school,
    citation     TEXT NOT NULL,                    -- 書名/論文/作者/年(真實權威)
    source_type  VARCHAR(32) NOT NULL,             -- 'book'|'paper'|'shareholder_letter'(禁 'ai_generated')
    url_or_isbn  TEXT
);

-- 5. 股票哲學 context 分類(as-of、從量化判定、消 survivorship #8)
CREATE TABLE stock_philosophy_tag (
    as_of_date   DATE NOT NULL,
    stock_id     VARCHAR(255) NOT NULL,
    school_id    INTEGER NOT NULL REFERENCES philosophy_school,
    score        DOUBLE PRECISION NOT NULL,        -- 該股符合該學派之量化分數(橫斷面、from feature_values)
    PRIMARY KEY (as_of_date, stock_id, school_id)
);

-- 6. 哲學框架 build 出處(承 A1 provenance 精神、參數可考)
CREATE TABLE philosophy_build_meta (
    build_id     SERIAL PRIMARY KEY,
    committed_at TIMESTAMP NOT NULL DEFAULT now(),
    n_schools INTEGER, n_principles INTEGER, n_validated INTEGER
);
```

## 四、資料來源與入庫流程(守三敵、絕不違 #1/#16)

**入庫鐵則**:
1. **學派/原則/來源** = **人工策展自真實權威文獻**(原典、論文)→ 寫 philosophy_school/principle/source。**不從 AI 平台抓生成內容入庫**(#1 零幻像、#16 clean-room;AI 生成非真兆)。`source_type` 禁 `ai_generated`。
2. **可從網路抓的僅「書目/引用 metadata」**(ISBN/論文 DOI/作者年份等**事實**),**非抓「AI 對市場的觀點」**。事實 metadata = 真兆;AI 觀點 = 假兆。
3. **principle_factor_map.validated_ic / validated_econ** = **augur 自身管線實證回填**(過四道漏斗 + #14),非文獻宣稱、非 AI 估算(#9/#10 可溯源)。
4. **stock_philosophy_tag.score** = **從 feature_values 橫斷面量化判定**(如「價值分數」= pe/pb/price_to_10yr 之 as-of 橫斷面 z 合成),as-of #8、非主觀貼標。

## 五、哲學 → 特徵假說(連結現有管線、驗證活下來才算)

哲學框架層**接上現有四道漏斗**,不另立預測軌:
```
philosophy_principle.hypothesis → principle_factor_map(因子假說)
   → 紀律閘#1/#8/#9 → 五鏡#11 → purged walk-forward → 提拔關卡(as-of+HAC+多seed)
   → 經濟價值 #14 → status: validated / rejected
```
**靈魂鐵律不變**:哲學提供「**為什麼這因子可能有用**」(假說來源、可解釋性),但「**是否真有用**」仍由 **out-of-sample + 經濟價值**裁決。dealer_self/inter_fh 教訓重申:**IC 漂亮 ≠ 可交易**,哲學說得通也得過 #14。

## 六、股票 context 分類(真實量化、輔助人決策)

`stock_philosophy_tag` 對每 as-of panel 之核心股,用 feature_values 算各學派分數(價值/成長/品質/動能/週期…)→ **解讀層**:「此股屬高品質低估值 + 動能轉強」。**用途**:(a) 解讀量化選股結果(顧問可解釋性)(b) regime/風格輪動分析 (c) 人決策輔助。**不進預測管線**(避免主觀洩漏)、純 context。

## 七、入憲方案規劃(相容版、逐檔 #19、待用戶確認後實作)

| 治權檔 | 入憲內容 | 版本 |
|---|---|---|
| **靈魂**(系統核心思想)| 補「投資哲學框架層」定位段:augur 是「**有投資智慧理論骨架的量化顧問**」;哲學=假說來源+解讀層、**非預測來源非 AI 大師**;**三敵不因哲學鬆動**(來源真實文獻、預測靠真實資料、假說須驗證活下來)| v1.2.0→v1.3.0 |
| **憲章**(架構)| 第三部管線補「哲學框架層」(6 表 schema + 接四道漏斗);**明定禁 AI 生成內容入庫**(#1/#16 延伸)| v1.15.0→v1.16.0 |
| **方法論**| 補「哲學→因子假說→漏斗驗證」操作 | 新增段 |
| **原則精華**| 法律 20 條**不動**(哲學層是操作化、非新不可違反原則);僅第 5 行版本引用同步 | v1.7.1(不動)|
| **CLAUDE.md**| #16 clean-room 補一句「哲學框架來源限真實文獻、禁 AI 生成入庫」| v1.10→v1.11 |

**入憲前提鐵則(否則治權自我矛盾)**:新條文**明文從屬於三敵人** —— 任何哲學框架成分若與 #1/#8/#15 衝突,以三敵為準。哲學是「如何更聰明地用真實資料」,**不是**「可以用非真實資料」。

## 八、誠實邊界與風險(#15)

1. **最大風險 = 哲學變占卜**:若有人把「文獻宣稱」或「AI 觀點」當預測依據 → 違 #1。**防線**:`status` 須 validated(經 #14)才用於生產;`source_type` 禁 ai_generated。
2. **過擬合風險**:哲學可「事後合理化」任何因子 → 仍須 out-of-sample + 換宇宙穩健(inter_fh 局部教訓)。
3. **context 分類洩漏**:tag 須 as-of(#8)、從 ≤t feature_values 算。
4. **不可宣稱「AI 大師」**:augur 是顧問、人決策(靈魂);哲學層增強可解釋性,不改「系統建議、人拍板」。

## 九、實施 roadmap(從零開始)

| 階段 | 內容 | 守則 |
|---|---|---|
| **P1 schema + 策展** | 建 6 表 + 策展 ~10 學派/原則自真實原典(人工、可溯源)| #10/#16 |
| **P2 因子映射** | principle_factor_map 對映現有 35 feat + 標缺口(ROE/低波/逆向)| 實證 |
| **P3 假說驗證** | 缺口因子過四道漏斗 + #14、回填 validated_ic/econ | #11/#14 |
| **P4 context 分類** | stock_philosophy_tag 量化判定(as-of)| #8 |
| **P5 解讀層** | 量化選股結果 + 哲學標籤解讀(顧問可解釋性)| 靈魂 |

---

## 結論

此方向**相容且強化** augur 靈魂——把隱性三鏡頭擴為**顯性投資哲學框架庫**,作為**特徵假說來源 + 解讀層**。**「投資大師」的本質仍是「有紀律的量化顧問」**:哲學提供智慧骨架與可解釋性,但**預測靠真實資料、驗證靠 out-of-sample 經濟價值、決策靠人**。三敵人零容忍**不因哲學鬆動**:來源限真實文獻、禁 AI 生成入庫、假說須驗證活下來。入憲採相容版(靈魂補定位 + 憲章補架構 + 明文從屬三敵),逐檔呈用戶確認後實作(#19)。
