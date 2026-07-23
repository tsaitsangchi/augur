"""身份屬性 as-of 雙時間繫結 — SCD-2 版本化(ID.60-61)。

🎯 這支在做什麼(白話):把身份之時變屬性(產業分類、名稱、市場類別、股權分級…)以 **valid time + transaction
   time 版本化**保存,**禁原地覆蓋**(last-write-wins/無版本=禁止型態)。使「任一過去時刻系統當時認為此
   Identity 之屬性為何」可重建——供 core_gate 產業判定改讀 as-of 屬性(follow-up)。
   **本層義務=屬性繫結存在**;完整 as-of 重建引擎(雙時間查詢引擎)DEFER Layer 4 KS.40-46(ID.61 分界)——
   本檔 get_asof 提供最小 as-of 讀取(單點近似),非能力等級操作化引擎。

DDL 單一權威=scripts/migrate_identity_ddl.py(entity_attribute_version append-only 硬化;
   transaction_time 預設 clock_timestamp() 使同交易多次 put 不撞複合 PK)。
守 ID.60(as-of 繫結義務)· ID.61(繫結存在 vs 重建引擎分界)· #18。

執行指令矩陣(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.identity.attribute_version              # 印用途+公開入口(唯讀)
  python -m augur.identity.attribute_version --selftest   # 純紅綠自測(零 IO)
"""
from __future__ import annotations


def put_version(cur, augur_id, attribute_name, value, valid_from,
                source_ref=None, evidence_ref=None, valid_to=None):
    """append 一個新屬性版本(不覆蓋既有版本;SCD-2)。transaction_time 由 DB clock_timestamp() 給。

    valid_from 為硬義務(as-of 繫結之起點;ID.60);valid_to 可 None(開放至今)。
    """
    if not attribute_name:
        raise ValueError("put_version 須具 attribute_name")
    if valid_from is None:
        raise ValueError("put_version 須具 valid_from(as-of 繫結起點;ID.60)")
    cur.execute(
        "INSERT INTO entity_attribute_version (augur_id, attribute_name, valid_from, "
        "attribute_value, valid_to, source_ref, evidence_ref) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (augur_id, attribute_name, valid_from, value, valid_to, source_ref, evidence_ref))


def get_asof(cur, augur_id, attribute_name, as_of):
    """取 as_of 當時系統認知之屬性版本(單點近似):valid_from ≤ as_of 且 (valid_to 空或 > as_of)
    且 transaction_time ≤ as_of,取最新 transaction_time、再最新 valid_from;無則 None。

    ⚠ 能力等級(A0-A3)操作化與完整雙時間查詢引擎 DEFER Layer 4 KS.40-46(ID.61):此為最小讀取入口、
       非重建引擎;as_of 同時用於 valid 與 transaction 軸(呼叫端傳單一時點)。
    ⚠ 雙時間軸未分離之邊界語義(誠實揭露):傳 date(如 '2020-01-01')者,transaction 軸被 coerce 為當日
       00:00,故「當日稍晚(如 09:30)才登錄之事後修正版本」在該 as_of 下**不可見**;需精確 transaction 軸
       (見當日事後修正)請傳 timestamptz。完整雙軸分離簽名(valid_asof: date / tx_asof: timestamptz)之查詢
       引擎 DEFER Layer 4——下游(如 core_gate 產業判定)引用前須明辨此單點近似之邊界,勿誤讀為精確雙時間。
    """
    cur.execute(
        "SELECT attribute_value, valid_from, valid_to, transaction_time, source_ref, evidence_ref "
        "FROM entity_attribute_version WHERE augur_id=%s AND attribute_name=%s "
        "AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s) AND transaction_time <= %s "
        "ORDER BY transaction_time DESC, valid_from DESC LIMIT 1",
        (augur_id, attribute_name, as_of, as_of, as_of))
    r = cur.fetchone()
    if r is None:
        return None
    return {"attribute_value": r[0], "valid_from": r[1], "valid_to": r[2],
            "transaction_time": r[3], "source_ref": r[4], "evidence_ref": r[5]}


def _selftest():
    """自測(零 DB/零 API;put/get 皆 IO-bound → import-smoke + 參數守衛結構斷言,零 IO)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("put_version 缺 valid_from → ValueError", _raises(put_version, None, "a", "n", "v", None))
    chk("put_version 缺 attribute_name → ValueError", _raises(put_version, None, "a", "", "v", "2020-01-01"))
    chk("公開入口皆存在", all(callable(f) for f in (put_version, get_asof)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _raises(fn, *args):
    """守衛路徑須在觸 DB(cur=None)前先擲 ValueError → 證明參數校驗早於任何 IO。"""
    try:
        fn(*args)
        return False
    except ValueError:
        return True
    except Exception:
        return False


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.identity.attribute_version --selftest;免 DB 免 API)")
