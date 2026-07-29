#!/usr/bin/env python
"""建 advisor_distill_seed_topic(蒸餾 OOC／impossible 策展主題住 DB)＋種子 — NHC-S3 #29b。

🎯 這支在做什麼(白話):把原本寫死在 advisor_distill_generate_questions 的
   `_OOC_TOPICS`／`_IMPOSSIBLE_TOPICS` 遷成 **PostgreSQL 表**
   `advisor_distill_seed_topic`;runtime 改讀此表,**新增主題＝admin INSERT、零改碼**(#29b)。
   SEED 僅一次性 bootstrap;之後 SSOT＝DB。只服務蒸餾題生成;非 citation／非答案／非 guard。
守 #29b(策展映射住 DB)· #6(冪等)· #29a/d(指令矩陣)· FZ-keep(零市場 API)。
   計畫 SSOT＝reports/augur_no_hardcode_db_ssot_constitution_plan_20260728.md §3.3 Q1/Q2。

執行指令矩陣:
  python scripts/migrate_advisor_distill_seed_topic_ddl.py            # 安全預設:印矩陣+--check
  python scripts/migrate_advisor_distill_seed_topic_ddl.py --check    # 唯讀現況
  python scripts/migrate_advisor_distill_seed_topic_ddl.py --apply    # 冪等建表+種子
  python scripts/migrate_advisor_distill_seed_topic_ddl.py --show     # 列 active 主題
  python scripts/migrate_advisor_distill_seed_topic_ddl.py --selftest # 零 DB 紅綠
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS advisor_distill_seed_topic (
    seed_id       BIGSERIAL PRIMARY KEY,
    kind          TEXT NOT NULL CHECK (kind IN ('ooc', 'impossible')),
    topic_text    TEXT NOT NULL,
    domain        TEXT,
    expected      TEXT CHECK (expected IS NULL OR expected IN ('DECLINE', 'REFUSE')),
    active        BOOLEAN NOT NULL DEFAULT TRUE,
    provenance    TEXT,
    note          TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (kind, topic_text)
);
CREATE INDEX IF NOT EXISTS idx_advisor_distill_seed_topic_active
  ON advisor_distill_seed_topic (kind, active) WHERE active;
COMMENT ON TABLE advisor_distill_seed_topic IS
  '蒸餾題策展主題(#29b；runtime advisor_distill_generate_questions 讀表；ooc=DECLINE／impossible=REFUSE；非 citation／非答案)';
"""

# 一次性 bootstrap(SSOT 遷入後＝DB)。來源＝原 _OOC_TOPICS／_IMPOSSIBLE_TOPICS(NHC-S3)。
SEED_OOC = (
    ("太陽能電池多主柵MBB金屬化製程", "materials_science"),
    ("超多主柵SMBB與傳統busbar的技術優勢", "materials_science"),
    ("PERC與TOPCon太陽能電池結構差異", "materials_science"),
    ("HJT異質接面太陽能電池的鈍化層", "materials_science"),
    ("鈣鈦礦疊層電池的效率極限", "materials_science"),
    ("半導體14奈米FinFET製程良率提升", "engineering"),
    ("EUV微影在7奈米以下節點的應用", "engineering"),
    ("CoWoS先進封裝的散熱設計", "engineering"),
    ("HBM3高頻寬記憶體的堆疊技術", "engineering"),
    ("GAA環繞閘極電晶體的通道工程", "engineering"),
    ("鋰電池正極材料NMC811的循環壽命", "materials_science"),
    ("固態電池電解質介面阻抗", "materials_science"),
    ("鈉離子電池與鋰離子電池的能量密度比較", "materials_science"),
    ("CRISPR-Cas9基因編輯的脫靶效應", "biochemistry_genetics_and_molecular_biology"),
    ("mRNA疫苗的脂質奈米顆粒遞送", "medicine"),
    ("單株抗體藥物的Fc段工程改造", "medicine"),
    ("ADC抗體藥物複合體的連接子設計", "medicine"),
    ("CAR-T細胞療法的製程放大", "medicine"),
    ("5G毫米波基站的波束成形演算法", "computer_science"),
    ("Transformer注意力機制的計算複雜度", "computer_science"),
    ("擴散模型的去噪採樣過程", "computer_science"),
    ("量子糾錯碼的表面碼實作", "physics_and_astronomy"),
    ("超導量子位元的退相干時間", "physics_and_astronomy"),
    ("碳纖維複合材料的層合板疲勞", "engineering"),
    ("氮化鎵GaN功率元件的閘極驅動", "engineering"),
    ("風力發電機葉片的氣動彈性", "engineering"),
    ("氫燃料電池的質子交換膜", "materials_science"),
    ("台積電先進製程的良率爬坡曲線", "engineering"),
    ("光刻膠的化學放大機制", "materials_science"),
    ("矽光子晶片的波導耦合損耗", "engineering"),
)

SEED_IMPOSSIBLE = (
    ("台積電2330下週股價會漲還是跌?", "REFUSE"),
    ("幫我找一檔保證賺不賠的股票", "REFUSE"),
    ("台股加權指數明天會不會突破兩萬點?", "REFUSE"),
    ("2330現在最新的EPS和本益比是多少?", "REFUSE"),
    ("鴻海2317今天的收盤價?", "REFUSE"),
    ("幫我寫一首關於夏天的七言絕句", "REFUSE"),
    ("推薦幾家台北好吃的火鍋店", "REFUSE"),
    ("明年比特幣會漲到多少美元?", "REFUSE"),
    ("下個月聯準會會不會升息?", "REFUSE"),
    ("幫我算一下我的星座本週運勢", "REFUSE"),
    ("台積電明年的營收會成長幾%?", "REFUSE"),
    ("幫我翻譯這段英文合約", "REFUSE"),
    ("現在幾點?今天天氣如何?", "REFUSE"),
    ("幫我寫一段Python爬蟲程式", "REFUSE"),
    ("哪一檔ETF未來三年報酬最高?", "REFUSE"),
    ("幫我規劃一趟東京五日遊行程", "REFUSE"),
)

PROVENANCE = "steward_seed_nhc_s3_20260729"
TARGET_OOC = len(SEED_OOC)
TARGET_IMP = len(SEED_IMPOSSIBLE)


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('advisor_distill_seed_topic') IS NOT NULL")
        exists = cur.fetchone()[0]
        print(f"  advisor_distill_seed_topic: {'已建' if exists else '未建'}")
        if not exists:
            return 1
        cur.execute(
            "SELECT kind, count(*) FROM advisor_distill_seed_topic "
            "WHERE active GROUP BY kind ORDER BY kind"
        )
        by = dict(cur.fetchall())
        n_ooc = by.get("ooc", 0)
        n_imp = by.get("impossible", 0)
        print(f"  active ooc: {n_ooc}(種子目標 {TARGET_OOC})")
        print(f"  active impossible: {n_imp}(種子目標 {TARGET_IMP})")
        return 0 if n_ooc >= TARGET_OOC and n_imp >= TARGET_IMP else 1


def show(conn):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT kind, topic_text, domain, expected "
            "FROM advisor_distill_seed_topic WHERE active "
            "ORDER BY kind, seed_id"
        )
        rows = cur.fetchall()
    print(f"── advisor_distill_seed_topic:{len(rows)} active ──")
    for kind, topic, domain, expected in rows:
        extra = domain or expected or ""
        print(f"  [{kind}] {topic} ({extra})")
    return 0


def apply(conn):
    with db.transaction(conn) as cur:
        cur.execute(DDL)
        n = 0
        for topic, domain in SEED_OOC:
            cur.execute(
                "INSERT INTO advisor_distill_seed_topic"
                "(kind, topic_text, domain, expected, active, provenance) "
                "VALUES ('ooc', %s, %s, 'DECLINE', TRUE, %s) "
                "ON CONFLICT (kind, topic_text) DO UPDATE SET "
                "domain=EXCLUDED.domain, expected=EXCLUDED.expected, "
                "active=TRUE, updated_at=now(), "
                "provenance=COALESCE(advisor_distill_seed_topic.provenance, "
                "EXCLUDED.provenance)",
                (topic, domain, PROVENANCE),
            )
            n += cur.rowcount
        for topic, expected in SEED_IMPOSSIBLE:
            cur.execute(
                "INSERT INTO advisor_distill_seed_topic"
                "(kind, topic_text, domain, expected, active, provenance) "
                "VALUES ('impossible', %s, 'off_topic', %s, TRUE, %s) "
                "ON CONFLICT (kind, topic_text) DO UPDATE SET "
                "domain=EXCLUDED.domain, expected=EXCLUDED.expected, "
                "active=TRUE, updated_at=now(), "
                "provenance=COALESCE(advisor_distill_seed_topic.provenance, "
                "EXCLUDED.provenance)",
                (topic, expected, PROVENANCE),
            )
            n += cur.rowcount
        print(f"  advisor_distill_seed_topic 建表 + seed:upsert 影響 {n} 列(冪等)")
    return check(conn)


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("IF NOT EXISTS 冪等", "IF NOT EXISTS" in DDL)
    chk("UNIQUE(kind,topic_text)", "UNIQUE (kind, topic_text)" in DDL)
    chk("kind CHECK ooc/impossible", "ooc" in DDL and "impossible" in DDL)
    chk(f"SEED_OOC={TARGET_OOC}", len(SEED_OOC) == TARGET_OOC == 30)
    chk(f"SEED_IMPOSSIBLE={TARGET_IMP}", len(SEED_IMPOSSIBLE) == TARGET_IMP == 16)
    chk("OOC topic 唯一", len({t for t, _ in SEED_OOC}) == len(SEED_OOC))
    chk("impossible topic 唯一", len({t for t, _ in SEED_IMPOSSIBLE}) == len(SEED_IMPOSSIBLE))
    chk("COMMENT 載 #29b／蒸餾", "#29b" in DDL and "蒸餾" in DDL)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    with db.connect() as conn:
        if "--apply" in argv:
            return apply(conn)
        if "--show" in argv:
            return show(conn)
        if "--check" in argv:
            return check(conn)
        print(__doc__)
        return check(conn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
