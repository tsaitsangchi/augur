#!/usr/bin/env python
"""augur 三鏡頭欄位地圖 build — 以第一性/八二/康波框架重檢 column_catalog 全數值欄、建 field_lens_map 表。

🎯 這支在做什麼(白話):把四份鏡頭報告(第一性/八二/康波/綜合)之框架,套到 `column_catalog` 全部數值訊號欄,
為每欄標註「三鏡頭特徵設計潛力」:**量**(第一性軸)× **形**(八二可做之集中度泛函)× **位**(康波可做之相位)。
依 dataset + 欄名 pattern 分類為 ~16 欄位類別,每類別有 doctrine 對映之三鏡頭標準映射(判準見 CATEGORIES)。

框架 SSOT:`reports/augur_first_principles_research`、`_pareto_principle_research`、`_kondratiev_cycle_research`、
`_three_lens_synthesis_20260627.md`(綜合:量×形×位三正交軸)。本表=「raw 欄位 → 三鏡頭特徵設計地圖」,供特徵生成參照。

邊界:唯讀 column_catalog、不改 raw;規則引擎本地計算、零 Claude usage(#28)。anti_leakage_flag 沿用 catalog(#8)。
分類保守、不確定標 generic + note;機械分類非定論,實際特徵仍須過漏斗(#11)。

守 #8(沿用 anti_leakage)· #9(鏡頭映射為連續泛函/相位、無硬編特定值)· #12(catalog SSOT)· #15(分類透明、不確定揭露)。
執行指令矩陣:python scripts/build_field_lens_map.py
"""
from __future__ import annotations

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

TABLE = "field_lens_map"
DDL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    dataset          VARCHAR(255) NOT NULL,
    column_name      VARCHAR(255) NOT NULL,
    column_name_zh   VARCHAR(255),
    field_category   VARCHAR(64)  NOT NULL,   -- 欄位類別(價/量/流/分布/估值/利率/宏觀…)
    first_principle  VARCHAR(128) NOT NULL,   -- 第一性「量」:資訊軸
    pareto_lens      VARCHAR(128) NOT NULL,   -- 八二「形」:適用集中度泛函(或 —)
    kondratiev_lens  VARCHAR(128) NOT NULL,   -- 康波「位」:適用相位 transform(或 —)
    anti_leakage     BOOLEAN,                 -- P-lag(沿用 catalog #8)
    note             TEXT,
    PRIMARY KEY (dataset, column_name)
)"""

# ── 欄位類別 → 三鏡頭映射(判準;依四鏡頭報告框架。優先序:特定 → 一般,首中即取)──
# 每項:(類別, [dataset 關鍵字], [欄名關鍵字], 第一性軸, 八二泛函, 康波相位, note)
# 八二「—」= 單一純量、無分布結構可做集中度(除非跨時窗/跨橫斷面,於特徵層另構)。
CATEGORIES = [
    ("持股分級分布", ["HoldingSharesPer"], [],
     "籌碼結構(誰擁有)", "★Gini/HHI/熵(級距 percent 分布)+ Δ集中度", "集中度循環相位",
     "八二本命表:級距分布天然可做集中度泛函(P1)"),
    ("法人資金流", ["InstitutionalInvestors", "ForeignDealer", "GovernmentBank", "Dealer"], ["buy", "sell"],
     "籌碼流(誰在買賣)", "★HHI/max-share(跨法人別 |淨買|、玩家集中)", "★累計淨流 range-position(吸籌/派發相位)",
     "多玩家結構→集中度;累計→相位(P2/C4)"),
    ("借券放空", ["SecuritiesLending", "ShortSale", "DailyShortSale", "SBL"], ["short", "lending", "fee", "sbl", "borrow"],
     "空方籌碼/擁擠度", "空方力量集中(借券 vs 融券結構)", "空方循環相位(餘額 range-position)",
     "借券費率=空方擁擠價格訊號"),
    ("證金擔保", ["LoanCollateral"], [],
     "信用/證金放款(籌碼)", "放款結構集中", "放款餘額 range-position(證金信用循環)",
     "證金擔保放款=信用循環另一面"),
    ("可轉債", ["ConvertibleBond"], [],
     "信用/可轉債部位(內嵌轉換權 context)", "—", "發行/流通餘額 range-position",
     "內嵌轉換選擇權;發行/流通量相位"),
    ("股利配息", ["Dividend"], [],
     "★股利政策/品質(配息配股)", "—", "—",
     "P-lag:除權息/股利公告;政策事件非連續循環"),
    ("融資券餘額", ["MarginPurchase"], ["margin", "balance"],
     "個股槓桿(信用循環)", "—", "★融資餘額 range-position/增減速(Minsky 信用循環)",
     "槓桿循環=Minsky 個股版(C3)"),
    ("外資持股", ["Shareholding"], ["foreign", "ratio", "shares"],
     "結構性少數關鍵者(外資)籌碼", "外資 share 與距上限空間", "外資持股 range-position(籌碼循環相位)",
     "外資=結構性少數關鍵者(P1/C4)"),
    ("估值", ["PER", "ValuationRatio"], ["per", "pbr", "dividend", "yield"],
     "★估值缺口(價格-價值)", "橫斷面估值分散(市場 regime)", "★估值 range-position(再評價動能相位)",
     "估值水位=alpha 主源;自身百分位=再評價(C2)"),
    ("市值規模", ["MarketValue"], ["market_value", "capital"],
     "★規模(size 因子)", "市場集中(個股市值佔全市場 share)", "規模 range-position",
     "市值佔比=支配地位本身(P1/P6)"),
    ("營收基本面", ["MonthRevenue"], ["revenue"],
     "★基本面品質(營收)", "營收佔產業 share / 季節 entropy", "★YoY 動能+減速(營收循環、基期結構 C3)",
     "P-lag:發布日 gate 必須"),
    ("財報科目", ["FinancialStatements", "BalanceSheet", "CashFlows"], [],
     "基本面品質(獲利/資產/現金)", "獲利佔產業 share(品質馬太)", "★庫存/capex/margin 循環相位(Kitchin/Juglar C3)",
     "P-lag:發布日 gate 必須"),
    ("利率利差", ["InterestRate", "Bonds", "GovernmentBonds"], [],
     "宏觀資金成本(context)", "—", "★利率循環相位/倒掛深度/方向(信用循環 C1)",
     "FRED vintage 警語(#8);ds-dominant 整表"),
    ("宏觀指數", ["fred", "BusinessIndicator", "Macro"], [],
     "宏觀景氣(context)", "—", "★景氣循環相位/減速度/領先-同時背離(C1)",
     "國發會/FRED 發布滯後 → 發布日 gate;ds-dominant 整表"),
    ("情緒", ["FearGreed", "Vix", "Sentiment"], [],
     "情緒(context)", "—", "★情緒循環位置(極值距離 C1)", "情緒循環相位"),
    ("匯率", ["ExchangeRate", "Currency"], [],
     "匯率(外資資金潮汐 context)", "—", "★台幣循環相位(C1)", "外資資金潮汐相位"),
    ("衍生品", ["Futures", "Option", "OpenInterest"], ["futures", "option", "oi", "open_interest", "未平倉"],
     "衍生品部位/避險", "多空部位集中", "未平倉 range-position(部位循環)", "衍生品部位相位"),
    ("鉅額/當沖", ["BlockTrade", "DayTrading"], ["block", "day_trading", "daytrading"],
     "交易中的少數關鍵/投機", "★鉅額/當沖佔總成交 share(P3)", "佔比 range-position",
     "block=大資金少數關鍵;當沖=投機少數"),
    ("量能", ["Price"], ["volume", "money", "turnover", "trading_volume", "trading_money"],
     "★流動性/量能", "★量能時間集中 Gini/max-share(rolling 窗 P3)", "★量能相位/量價相位差(C2)",
     "量集中少數日=事件/主力(P3 存活軸)"),
    ("價格", ["Price", "TotalReturn", "TAIEX", "Index"], ["close", "open", "max", "min", "price", "spread", "change", "taiex", "index", "加權"],
     "★水位/動能/缺口", "★報酬集中 skew/kurt/Gini(rolling |日報酬| P4)", "★range-position/drawdown/共振(C2 存活軸)",
     "價格=多鏡頭核心;相位/共振為康波本命(C2)"),
    ("人數計數", [], ["people", "count", "筆數", "人數", "家數", "number"],
     "參與廣度", "(若分布)集中度", "參與度 range-position", "計數類=參與/廣度"),
]
DEFAULT = ("一般數值", "水位(待判)", "(視窗/橫斷面可構)", "range-position(自身歷史)",
           "未明確分類:預設量×位;實際軸待逐欄判")


def classify(dataset, col, zh):
    """4-pass:ds+col 皆具者須兩者皆中(最具體、解同表混型如 Price.close→價格/volume→量能)→
    僅 ds 類別(整表同類)→ 僅 col 類別 → ds 未中但欄名中(跨表欄名)→ generic。"""
    hay_ds = (dataset or "").lower()
    hay_col = (col or "").lower() + " " + (zh or "")
    dsh = lambda kw: any(k.lower() in hay_ds for k in kw)
    colh = lambda kw: any(k.lower() in hay_col for k in kw)
    for c, dk, ck, fp, pa, ko, nt in CATEGORIES:          # pass1:ds+col 皆具且皆中
        if dk and ck and dsh(dk) and colh(ck):
            return c, fp, pa, ko, nt
    for c, dk, ck, fp, pa, ko, nt in CATEGORIES:          # pass2:僅 ds 類別、ds 中
        if dk and not ck and dsh(dk):
            return c, fp, pa, ko, nt
    for c, dk, ck, fp, pa, ko, nt in CATEGORIES:          # pass3:僅 col 類別、col 中
        if ck and not dk and colh(ck):
            return c, fp, pa, ko, nt
    for c, dk, ck, fp, pa, ko, nt in CATEGORIES:          # pass4:ds 未中但欄名中(跨表 close/volume…)
        if ck and colh(ck):
            return c, fp, pa, ko, nt
    return ("一般數值", *DEFAULT[1:])


def main():
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute(DDL)
            cur.execute(f"TRUNCATE {TABLE}")
            cur.execute("SELECT dataset, column_name, column_name_zh, is_pk, anti_leakage_flag "
                        "FROM column_catalog WHERE inferred_type='NUMERIC' AND COALESCE(is_pk,false)=false "
                        "ORDER BY dataset, ordinal")
            rows = cur.fetchall()
            P_LAG = {"營收基本面", "財報科目", "股利配息", "宏觀指數", "利率利差"}   # 鏡頭框架已知之 P-lag 類別(catalog flag 未填、由 doctrine 補 #8)
            data = []
            for ds, col, zh, _pk, leak in rows:
                cat, fp, pa, ko, note = classify(ds, col, zh)
                plag = bool(leak) or cat in P_LAG
                data.append((ds, col, zh, cat, fp, pa, ko, plag, note))
            from psycopg2.extras import execute_values
            execute_values(cur, f"INSERT INTO {TABLE} "
                           "(dataset, column_name, column_name_zh, field_category, first_principle, pareto_lens, kondratiev_lens, anti_leakage, note) VALUES %s",
                           data)
        # 報告用統計
        with db.transaction(conn) as cur:
            cur.execute(f"SELECT field_category, count(*) FROM {TABLE} GROUP BY field_category ORDER BY count(*) DESC")
            cats = cur.fetchall()
            cur.execute(f"SELECT count(*) FROM {TABLE} WHERE pareto_lens<>'—'")
            pareto_n = cur.fetchone()[0]
            cur.execute(f"SELECT count(*) FROM {TABLE} WHERE kondratiev_lens NOT LIKE 'range-position(自身%%'")
            ko_special = cur.fetchone()[0]
            cur.execute(f"SELECT count(*) FROM {TABLE} WHERE field_category='一般數值'")
            generic = cur.fetchone()[0]
            cur.execute(f"SELECT count(*), count(*) FILTER(WHERE anti_leakage) FROM {TABLE}")
            tot, leak_n = cur.fetchone()

    print(f"field_lens_map 建立:{tot} 數值欄")
    print(f"\n類別分布({len(cats)} 類):")
    for c, n in cats:
        print(f"  {c:14s} {n:>4d}")
    print(f"\n八二可做(分布集中度)欄: {pareto_n}/{tot}")
    print(f"康波特化相位(非預設)欄: {ko_special}/{tot}")
    print(f"未明確分類(generic): {generic}/{tot}")
    print(f"anti_leakage(P-lag)欄: {leak_n}/{tot}")


if __name__ == "__main__":
    main()
