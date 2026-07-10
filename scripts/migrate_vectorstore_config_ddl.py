#!/usr/bin/env python
"""向量後端 config schema 遷移 — knowledge_vectorstore_config / vectorstore_shadow_eval 兩表冪等落地+種子(e2e 主計畫 P1)。

🎯 這支在做什麼(白話):把「向量索引後端用哪個」從 code 常數變成 **DB 資料列**——
   ① `knowledge_vectorstore_config`:每 scope 一列(backend=pgvector|qdrant_*;fallback 降級目標常備);
      **換後端/退回=UPDATE 一列**(#29b;憲章 v1.40.0「端到端管線暢通不變式」之接縫 DB 化);
      讀端須機械斷言 config.embed_model=embedspec 世代 SSOT,不一致 fail-loud 拒服務。
   ② `vectorstore_shadow_eval`:Qdrant cutover 前之影子評測落表(D6:50 題 top-10 重疊 ≥0.90 機械門檻,
      題集 seed/雜湊入 detail 可重現 #10/A-32)。
   種子:四 scope 列(sentence_items/sentence_works/lexicon/philosophy_chunk)全 backend='pgvector'
   (現況即權威;cutover 於 P4 影子綠後 UPDATE sentence_items 一列)。

守 #6(冪等)· #12(embedspec=世代唯一 SSOT,本表引用不複製判準)· #29b(換後端=資料列)· 憲章 v1.40.0 ·
   CLAUDE #29a。SSOT=reports/augur_omniscient_e2e_master_plan_20260710.md §5.1/§5.6/§6.8。

執行指令矩陣:
  python scripts/migrate_vectorstore_config_ddl.py            # 無參數:印本矩陣+表現況(唯讀)
  python scripts/migrate_vectorstore_config_ddl.py --run      # 冪等建表+種子四 scope 列
  python scripts/migrate_vectorstore_config_ddl.py --verify   # 斷言 config.embed_model/dims=embedspec 世代(不一致 exit 1=fail-loud)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge import embedspec

SCOPES = ("sentence_items", "sentence_works", "lexicon", "philosophy_chunk")

DDL = [
    ("table knowledge_vectorstore_config", """
        CREATE TABLE IF NOT EXISTS knowledge_vectorstore_config (
          scope        text PRIMARY KEY,
          backend      text NOT NULL DEFAULT 'pgvector'
                         CHECK (backend IN ('pgvector','qdrant_embedded','qdrant_server')),
          embed_model  text NOT NULL,
          dims         int  NOT NULL,
          endpoint     text,
          fallback     text NOT NULL DEFAULT 'pgvector'
                         CHECK (fallback IN ('pgvector','none')),
          updated_at   timestamptz NOT NULL DEFAULT now()
        )"""),
    ("comment knowledge_vectorstore_config", """
        COMMENT ON TABLE knowledge_vectorstore_config IS
        '向量索引後端接縫之 DB 化(憲章 v1.40.0 暢通不變式);換後端/退回=UPDATE 一列(#29b);embed_model/dims 須=embedspec 世代 SSOT、讀端機械斷言不一致 fail-loud 拒服務;唯一 sanctioned host 由 G3 allowlist 另管'"""),
    ("table vectorstore_shadow_eval", """
        CREATE TABLE IF NOT EXISTS vectorstore_shadow_eval (
          run_at        timestamptz NOT NULL DEFAULT now(),
          scope         text NOT NULL,
          backend_ref   text NOT NULL,
          backend_cand  text NOT NULL,
          n_queries     int  NOT NULL,
          top_k         int  NOT NULL,
          mean_overlap  double precision NOT NULL,
          min_overlap   double precision NOT NULL,
          threshold     double precision NOT NULL,
          passed        boolean NOT NULL,
          detail        jsonb NOT NULL,
          PRIMARY KEY (run_at, scope)
        )"""),
    ("comment vectorstore_shadow_eval", """
        COMMENT ON TABLE vectorstore_shadow_eval IS
        'Qdrant cutover 影子評測落表(D6:預設 50 題 top-10 重疊 ≥0.90=cutover 機械門檻);detail 含逐題 overlap+題集 seed/雜湊(可重現 #10/A-32)'"""),
]


def status():
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' AND table_name IN "
            "('knowledge_vectorstore_config','vectorstore_shadow_eval')")
        have = {r[0] for r in cur.fetchall()}
        for t in ("knowledge_vectorstore_config", "vectorstore_shadow_eval"):
            print(f"  {'✓' if t in have else '✗ 未建'} {t}")
        if "knowledge_vectorstore_config" in have:
            cur.execute("SELECT scope, backend, embed_model, dims, fallback FROM knowledge_vectorstore_config ORDER BY scope")
            for r in cur.fetchall():
                print(f"    {r[0]}: backend={r[1]} model={r[2]} dims={r[3]} fallback={r[4]}")


def run():
    model, dims = embedspec.MODEL_TAG, embedspec.dim_for()
    with db.connect() as conn:
        cur = conn.cursor()
        for name, sql in DDL:
            cur.execute(sql)
            print(f"  ✓ {name}")
        for s in SCOPES:  # 種子:已存在不覆蓋(現況即權威,cutover 只走 UPDATE)
            cur.execute("""
                INSERT INTO knowledge_vectorstore_config (scope, backend, embed_model, dims)
                VALUES (%s, 'pgvector', %s, %s) ON CONFLICT (scope) DO NOTHING""", (s, model, dims))
        conn.commit()
    print(f"✓ --run 完成(種子 {len(SCOPES)} scope,embed_model={model} dims={dims})")


def verify() -> int:
    ok = True
    model, dims = embedspec.MODEL_TAG, embedspec.dim_for()
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT scope, embed_model, dims FROM knowledge_vectorstore_config ORDER BY scope")
        rows = cur.fetchall()
        if not rows:
            print("✗ config 空表(先 --run)"); ok = False
        for scope, m, d in rows:
            if m != model or d != dims:
                print(f"✗ 世代不一致 fail-loud:{scope} config=({m},{d}) ≠ embedspec=({model},{dims})")
                ok = False
        missing = set(SCOPES) - {r[0] for r in rows}
        if missing:
            print(f"✗ 缺 scope 列:{missing}"); ok = False
    print("✓ --verify 全綠(config=embedspec 世代一致)" if ok else "✗ --verify 失敗")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.run:
        run(); return 0
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    print("表現況(唯讀):")
    status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
