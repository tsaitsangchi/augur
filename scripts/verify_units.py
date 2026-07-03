#!/usr/bin/env python
"""augur 欄位單位交叉驗 — 用「跨源一致性」據實定單位(股vs張、元vs千元),非推測。

🎯 這支在做什麼(白話):單位之前是推斷。本支用跨源交叉一致性據實驗:
- money ≈ close×volume? → 確認 trading_money=元、volume=股、close=元
- 月營收(千元?)×3 ≈ 季財報 Revenue(元?) → 同時定兩源單位
- 融資餘額 vs 發行股數比例 → 融資單位是股或張(千股)
- HoldingSharesPer unit 加總 vs 發行股數 → 持股單位是股或張

唯讀、本地、零 usage(#28)。守 #15(交叉驗、據實定單位)。
執行指令矩陣:python scripts/verify_units.py
"""
import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

STK = "2330"


def q1(cur, sql, p=()):
    cur.execute(sql, p)
    r = cur.fetchone()
    return r


def main():
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            print(f"單位交叉驗(以 {STK} 為主)\n")

            # A1: money ≈ close × volume(定 money=元、volume=股、close=元)
            r = q1(cur, 'SELECT "Trading_money", close, "Trading_Volume" FROM "TaiwanStockPrice" '
                   'WHERE stock_id=%s AND close>0 AND "Trading_Volume">0 ORDER BY date DESC LIMIT 1', (STK,))
            money, close, vol = float(r[0]), float(r[1]), float(r[2])
            ratio = money / (close * vol)
            print(f"A1 money/(close×volume) = {ratio:.3f}  → {'✅ money=元/volume=股/close=元(比≈1)' if 0.5 < ratio < 2 else '⚠️ 單位不符 '+str(ratio)}")

            # A2: 季財報 Revenue vs 月營收×3(定兩源單位)
            fr = q1(cur, "SELECT date, value FROM \"TaiwanStockFinancialStatements\" WHERE stock_id=%s AND type='Revenue' "
                    "AND date='2023-03-31'", (STK,))
            mr = q1(cur, "SELECT sum(revenue) FROM \"TaiwanStockMonthRevenue\" WHERE stock_id=%s "
                    "AND date>='2023-01-01' AND date<'2023-04-01'", (STK,))
            if fr and mr and mr[0]:
                fin_rev, mon_rev = float(fr[1]), float(mr[0])      # 兩源皆元(ledger 0628 裁定、2330 實證)
                r2 = fin_rev / mon_rev                             # 同單位(元) → 比≈1
                print(f"A2 財報季Rev / 月營收和 = {r2:.3f}  → {'✅ 財報=元、月營收=元(同單位、比≈1)' if 0.8 < r2 < 1.25 else '⚠️ 比='+f'{r2:.2f}'+'(單位待究)'}")

            # A3: 融資餘額 vs 發行股數(定融資單位 股/張)
            mb = q1(cur, 'SELECT "MarginPurchaseTodayBalance" FROM "TaiwanStockMarginPurchaseShortSale" WHERE stock_id=%s ORDER BY date DESC LIMIT 1', (STK,))
            sh = q1(cur, 'SELECT "NumberOfSharesIssued" FROM "TaiwanStockShareholding" WHERE stock_id=%s ORDER BY date DESC LIMIT 1', (STK,))
            if mb and sh and sh[0]:
                marg, shares = float(mb[0]), float(sh[0])
                pct_as_lot = marg * 1000 / shares * 100            # 若融資=張(千股)
                pct_as_shr = marg / shares * 100                   # 若融資=股
                print(f"A3 融資餘額 {marg:,.0f} vs 發行 {shares:,.0f}：若張→{pct_as_lot:.2f}%、若股→{pct_as_shr:.4f}% 之發行股 "
                      f"→ {'融資單位=張(千股)' if 0.01 < pct_as_lot < 30 else '融資單位=股' if 0.01 < pct_as_shr < 30 else '?'}")

            # A4: HoldingSharesPer total unit vs 發行股數(定持股單位)
            hu = q1(cur, "SELECT unit FROM \"TaiwanStockHoldingSharesPer\" WHERE stock_id=%s AND \"HoldingSharesLevel\"='total' ORDER BY date DESC LIMIT 1", (STK,))
            if hu and sh and sh[0]:
                hunit = float(hu[0])
                print(f"A4 持股總 unit {hunit:,.0f} vs 發行 {shares:,.0f}：比(股)={hunit/shares:.3f}、比(張)={hunit*1000/shares:.1f} "
                      f"→ {'持股 unit=股' if 0.5 < hunit/shares < 2 else '持股 unit=張' if 0.5 < hunit*1000/shares < 2 else '?'}")

            # A5: 財報金額量級(元 確認)
            ta = q1(cur, "SELECT value FROM \"TaiwanStockBalanceSheet\" WHERE stock_id=%s AND type='TotalAssets' ORDER BY date DESC LIMIT 1", (STK,))
            if ta:
                print(f"A5 {STK} TotalAssets={float(ta[0]):,.0f} → {'✅ 元(台積電總資產~6兆元級)' if float(ta[0])>1e12 else '⚠️ 量級疑'}")
    print("\n判讀:跨源比≈1/合理% → 單位據實定;否則標待究。")


if __name__ == "__main__":
    main()
