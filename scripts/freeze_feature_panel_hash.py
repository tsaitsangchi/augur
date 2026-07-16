#!/usr/bin/env python
"""feature 值逐 panel hash baseline — 凍結/驗證(arena 前置 G2 洩漏迴歸鎖;計畫 §5.2/§6.4)。

🎯 這支在做什麼(白話):把「凍結段 feature 值」逐 panel 算 hash 凍成 baseline(表 feature_panel_hash_baseline,
   本檔 DDL 單一住所)——之後任何時點重算比對,**任一 panel hash 變=舊時點值被改(洩漏/污染 #8)→ FAIL**。
   涵蓋兩軸(D-1/D-2):相對強度 `feature_values`(36 panel)+方向 `daily_direction_feature_values`(≤06-30
   2,830 panel、19.2M 列,server-side cursor 單趟流式、不炸記憶體)。
   口徑(D-6):值正規化**直接呼叫 reconcile._norm**(數字 round6/NULL→∅ sentinel;#12 同 byte-對帳口徑、
   零分歧)+確定性排序(panel,id,feature)+sha256;normalization_ref 版本化存列(口徑可溯源)。
   baseline 防偷改:UPDATE 禁改 hash/count/asof(trigger RAISE);重凍=--refreeze 明示(留痕印出)。
   零 API、純本地 DB(#28 零 usage)。

守 #8(舊時點不可變=洩漏鎖)· #12(_norm 單一口徑/DDL 單一住所)· #15(hash=機械證據)· #29a/d。
   SSOT=reports/arena_g1g5_admission_gate_plan_20260716.md §5.2/§6.4;asof 預設=G1-PIN 2026-06-30(SSOT=gate criteria)。

執行指令矩陣:
  python scripts/freeze_feature_panel_hash.py                                   # 無參數:現況(唯讀)
  python scripts/freeze_feature_panel_hash.py --init                            # 冪等建 baseline 表+防改 trigger
  python scripts/freeze_feature_panel_hash.py --freeze --axis relative_strength # 凍相對強度(36 panel,秒級)
  python scripts/freeze_feature_panel_hash.py --freeze --axis direction         # 凍方向(2,830 panel/19.2M 列,~數分)
  python scripts/freeze_feature_panel_hash.py --freeze --axis direction --refreeze  # 明示覆寫重凍(留痕)
  python scripts/freeze_feature_panel_hash.py --verify --axis relative_strength # 重算比對(0 mismatch=exit 0)
  python scripts/freeze_feature_panel_hash.py --verify --axis direction
  python scripts/freeze_feature_panel_hash.py --selftest                        # 純函式紅綠(零 DB 零 API)
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db
from augur.audit import reconcile

PIN_ASOF = "2026-06-30"     # G1-PIN 預設(hugo 2026-07-16);SSOT=arena_admission_gate criteria
NORM_REF = "npv1:reconcile._norm(round6)|∅=NULL|sort(id,feature)|sha256"
AXES = {"relative_strength": ("feature_values", "stock_id"),
        "direction": ("daily_direction_feature_values", "target_id")}
ITERSIZE = 50000            # server-side cursor 批量(19.2M 列流式)

DDL = """
CREATE TABLE IF NOT EXISTS feature_panel_hash_baseline (
  axis              text NOT NULL CHECK (axis IN ('relative_strength','direction')),
  source_table      text NOT NULL,
  panel_date        date NOT NULL,
  row_count         bigint NOT NULL,
  value_hash        text NOT NULL,
  normalization_ref text NOT NULL,
  frozen_as_of      date NOT NULL,
  frozen_at         timestamptz NOT NULL DEFAULT now(),
  git_sha           text,
  PRIMARY KEY (axis, source_table, panel_date)
);

CREATE OR REPLACE FUNCTION feature_hash_baseline_immutable() RETURNS trigger AS $$
BEGIN
  IF NEW.value_hash IS DISTINCT FROM OLD.value_hash
     OR NEW.row_count IS DISTINCT FROM OLD.row_count
     OR NEW.frozen_as_of IS DISTINCT FROM OLD.frozen_as_of THEN
    RAISE EXCEPTION 'feature_panel_hash_baseline %/%: baseline 凍結列不可改(洩漏鎖 #8);重凍=--refreeze(DELETE+INSERT 留痕)',
      OLD.axis, OLD.panel_date;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_feature_hash_immutable ON feature_panel_hash_baseline;
CREATE TRIGGER trg_feature_hash_immutable
  BEFORE UPDATE ON feature_panel_hash_baseline
  FOR EACH ROW EXECUTE FUNCTION feature_hash_baseline_immutable();

COMMENT ON TABLE feature_panel_hash_baseline IS
  'G2 洩漏迴歸鎖:凍結段 feature 值逐 panel hash(口徑=normalization_ref);verify hash 變=舊時點值被改 FAIL;UPDATE 禁改 trigger、重凍須 --refreeze 明示';
"""


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _norm_value(v):
    """值正規化(D-6 口徑):None→'∅';餘走 reconcile._norm(數字→round(float,6));repr=決定性最短表示。"""
    nv = reconcile._norm(v)
    return "∅" if nv is None else repr(nv)


def _panel_hash(rows):
    """單 panel hash:rows=[(id,feature,value)…] → 排序(id,feature)→'id|feature|norm' 行流 sha256。
    純函式(selftest 可測):輸入順序無關(排序)、值口徑=_norm_value。"""
    h = hashlib.sha256()
    for i, f, v in sorted(rows, key=lambda r: (str(r[0]), str(r[1]))):
        h.update(f"{i}|{f}|{_norm_value(v)}\n".encode())
    return h.hexdigest()


def _stream_panels(conn, table, id_col, asof):
    """server-side cursor 單趟流式:ORDER BY panel_date 分組 yield (panel_date, rows)。19.2M 列不炸記憶體。"""
    cur = conn.cursor(name=f"fph_{table[:40]}", withhold=True)   # server-side;WITH HOLD=跨 commit 存活(freeze 分批 commit 實證 2026-07-16:無 withhold 首次 commit 即殺 cursor)
    cur.itersize = ITERSIZE
    cur.execute(f'SELECT panel_date, "{id_col}", feature, value FROM "{table}" '
                "WHERE panel_date <= %s ORDER BY panel_date", (asof,))
    cur_panel, buf = None, []
    for pd, i, f, v in cur:
        if pd != cur_panel:
            if buf:
                yield cur_panel, buf
            cur_panel, buf = pd, []
        buf.append((i, f, v))
    if buf:
        yield cur_panel, buf
    cur.close()


def init():
    with db.connect() as conn:
        c = conn.cursor()
        c.execute(DDL)
        conn.commit()
    print("✓ --init 完成(冪等):feature_panel_hash_baseline + trg_feature_hash_immutable 就位")
    return 0


def freeze(axis, asof, refreeze=False):
    table, id_col = AXES[axis]
    git = _git7()
    ins = skip = 0
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT panel_date FROM feature_panel_hash_baseline WHERE axis=%s AND source_table=%s",
                        (axis, table))
            existing = {r[0] for r in cur.fetchall()}
        if existing and refreeze:
            with db.transaction(conn) as cur:   # 重凍=明示 DELETE+INSERT(trigger 禁 UPDATE 改 hash;留痕印出)
                cur.execute("DELETE FROM feature_panel_hash_baseline WHERE axis=%s AND source_table=%s",
                            (axis, table))
            print(f"⚠ --refreeze:刪除既有 {len(existing)} baseline 列重凍(留痕)")
            existing = set()
        wcur = conn.cursor()
        for n, (pd, rows) in enumerate(_stream_panels(conn, table, id_col, asof), 1):
            if pd in existing:
                skip += 1
                continue
            wcur.execute("INSERT INTO feature_panel_hash_baseline "
                         "(axis,source_table,panel_date,row_count,value_hash,normalization_ref,frozen_as_of,git_sha) "
                         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                         (axis, table, pd, len(rows), _panel_hash(rows), NORM_REF, asof, git))
            ins += 1
            if ins % 200 == 0:
                conn.commit()
                print(f"  {axis} 凍結 {ins} panel…", flush=True)
        conn.commit()
    print(f"✓ freeze {axis}({table} ≤{asof}):新凍 {ins} panel、既有跳過 {skip}(重凍須 --refreeze)")
    return 0


def verify(axis, asof=None):
    table, id_col = AXES[axis]
    mism, extra, seen = [], [], set()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT panel_date, row_count, value_hash, frozen_as_of FROM feature_panel_hash_baseline "
                        "WHERE axis=%s AND source_table=%s", (axis, table))
            rows_b = cur.fetchall()
            base = {r[0]: (r[1], r[2]) for r in rows_b}
        if not base:
            print(f"✗ verify {axis}:無 baseline(先 --freeze)")
            return 1
        asof = asof or max(r[3] for r in rows_b).isoformat()
        for pd, rows in _stream_panels(conn, table, id_col, asof):
            seen.add(pd)
            if pd not in base:
                extra.append(pd)                 # ≤asof 段長出新 panel=異常(凍結段不該增生)
                continue
            rc, vh = base[pd]
            if len(rows) != rc or _panel_hash(rows) != vh:
                mism.append((pd, rc, len(rows)))
    missing = sorted(set(base) - seen)           # 表內少了 baseline 有的 panel=被刪=FAIL
    ok = not mism and not extra and not missing
    tag = "✓ PASS(凍結段值不變,無洩漏改寫)" if ok else "✗ FAIL"
    print(f"{tag} verify {axis}({table} ≤{asof}):baseline {len(base)} panel、比對 {len(seen & set(base))}")
    if mism:
        print(f"  ✗ hash/count 不符 {len(mism)} panel(舊時點值被改 #8!):{[str(p) for p, _, _ in mism[:8]]}")
    if extra:
        print(f"  ✗ 凍結段新增 panel {len(extra)}(≤as-of 不該增生):{[str(p) for p in extra[:8]]}")
    if missing:
        print(f"  ✗ baseline panel 消失 {len(missing)}:{[str(p) for p in missing[:8]]}")
    return 0 if ok else 1


def _selftest():
    """純函式紅綠(零 DB 零 API #29a):口徑決定性/順序無關/值等價/竄改偵測。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("_norm_value NULL→∅", _norm_value(None) == "∅")
    chk("_norm_value 數字等價('1.0'==1==1.0000001→round6)", _norm_value("1.0") == _norm_value(1) == _norm_value(1.0000001))
    chk("_norm_value NaN→∅(placeholder)", _norm_value("NaN") == "∅")
    rows = [("A", "f1", 1.5), ("B", "f2", None), ("A", "f2", "2.0")]
    chk("_panel_hash 決定性", _panel_hash(rows) == _panel_hash(list(rows)))
    chk("_panel_hash 順序無關(排序鎖)", _panel_hash(rows) == _panel_hash(rows[::-1]))
    chk("_panel_hash 值等價('2.0' vs 2)", _panel_hash(rows) == _panel_hash([("A", "f1", 1.5), ("B", "f2", None), ("A", "f2", 2)]))
    chk("_panel_hash 竄改值→hash 變", _panel_hash(rows) != _panel_hash([("A", "f1", 1.6), ("B", "f2", None), ("A", "f2", 2.0)]))
    chk("_panel_hash 增列→hash 變", _panel_hash(rows) != _panel_hash(rows + [("C", "f1", 9)]))
    chk("DDL 冪等+PK+trigger", "CREATE TABLE IF NOT EXISTS" in DDL and "PRIMARY KEY" in DDL
        and "trg_feature_hash_immutable" in DDL)
    chk("AXES 兩軸就位", set(AXES) == {"relative_strength", "direction"})
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--axis", choices=list(AXES))
    ap.add_argument("--asof", default=PIN_ASOF)
    ap.add_argument("--refreeze", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.init:
        return init()
    if args.freeze:
        if not args.axis:
            sys.exit("--freeze 需 --axis")
        return freeze(args.axis, args.asof, refreeze=args.refreeze)
    if args.verify:
        if not args.axis:
            sys.exit("--verify 需 --axis")
        return verify(args.axis)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.feature_panel_hash_baseline')")
        if cur.fetchone()[0]:
            cur.execute("SELECT axis, source_table, count(*), min(panel_date), max(panel_date), max(frozen_at)::date "
                        "FROM feature_panel_hash_baseline GROUP BY axis, source_table")
            rows = cur.fetchall()
            print("現況:", rows if rows else "(表在、零 baseline;先 --freeze)")
        else:
            print("現況:(表未建,先 --init)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
