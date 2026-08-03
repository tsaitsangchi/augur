"""M-K2 回歸鎖：`prior_depth` 承接層不得蓋 pass 章，且 raw_verdict 行為不變。

🎯 這支在做什麼(白話):`progressive_item` 對 `d < before` 的層只是承接既有水印、**本輪根本沒評**，
   舊碼卻記 `{"verdict":"pass","note":"prior_depth"}`——自我背書的綠燈。本測鎖住兩件事：
   (a) 承接層一律記 `not_reevaluated`（沒評過就不准寫 pass）；
   (b) 同一筆 run 的 `raw_verdict` 仍為 `pass`（正名是**零行為變更**，不得順手把 raw 判死）。
   兩把鎖分別打靶 `auto_admit.py` 之 `d < before` 分支與 `raw_v` 判斷式。
   fixture＝真 DB 真 item 跑真 `progressive_item`（apply=True 後 ROLLBACK），不手寫形狀。
   DB 不可用→skip（非假 pass）。

守 CLAUDE #7(須實測)· #9(零幻像:斷言對象為真程式輸出)· #15(誠實 skip)· #35(回歸鎖須可驗紅)
"""
from __future__ import annotations

import pytest


@pytest.fixture()
def conn():
    """真 DB 連線；teardown 一律 ROLLBACK（本測 apply=True 但不留任何列）。"""
    try:
        import psycopg2

        from augur.core import config
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 依賴不可用、跳過 M-K2 回歸鎖:{e}")
        return
    try:
        c = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 不可用、跳過 M-K2 回歸鎖:{e}")
        return
    c.autocommit = False
    try:
        yield c
    finally:
        c.rollback()
        c.close()


def _one_carried_item(cur) -> int:
    """取一個 admit_depth≥1 之真 item（其層 0 必走 d<before 承接分支）。"""
    cur.execute(
        """
        SELECT st.target_id
          FROM knowhow_auto_admit_state st
          JOIN knowledge_item i ON i.item_id = st.target_id::bigint
         WHERE st.target_kind = 'item' AND st.admit_depth >= 1
         ORDER BY st.target_id
         LIMIT 1
        """
    )
    row = cur.fetchone()
    if not row:
        pytest.skip("庫內無 admit_depth≥1 之 item、無承接層可測")
    return int(row[0])


def _run(cur, item_id: int) -> dict:
    """up_to=0 ⇒ 只跑層 0；before≥1 故該層必走承接分支。activate_source=False 免外部副作用。"""
    from augur.knowledge import auto_admit as aa

    res = aa.progressive_item(cur, item_id, up_to=0, apply=True, activate_source=False)
    assert res.get("ok") is True, res
    return res


def test_carried_layer_is_not_marked_pass(conn):
    """承接層（本輪未重評）記 not_reevaluated——退回 verdict='pass' 即紅。"""
    cur = conn.cursor()
    item_id = _one_carried_item(cur)
    res = _run(cur, item_id)
    layer0 = res["layer_scores"]["0"]
    assert layer0["note"] == "prior_depth", layer0
    assert layer0["verdict"] == "not_reevaluated", layer0
    assert all(
        v.get("verdict") != "pass"
        for v in res["layer_scores"].values()
        if isinstance(v, dict) and v.get("note") == "prior_depth"
    ), res["layer_scores"]


def test_persisted_layer_scores_have_no_prior_depth_pass(conn):
    """落庫的 run／state 兩張帳也不得出現 prior_depth×pass（驗收①之單列版）。"""
    cur = conn.cursor()
    item_id = _one_carried_item(cur)
    res = _run(cur, item_id)
    cur.execute(
        "SELECT layer_scores FROM knowhow_auto_admit_run WHERE run_id=%s", (res["run_id"],)
    )
    run_scores = cur.fetchone()[0]
    cur.execute(
        "SELECT layer_scores FROM knowhow_auto_admit_state "
        "WHERE target_kind='item' AND target_id=%s",
        (str(item_id),),
    )
    state_scores = cur.fetchone()[0]
    for name, scores in (("run", run_scores), ("state", state_scores)):
        assert not [
            k
            for k, v in scores.items()
            if isinstance(v, dict) and v.get("note") == "prior_depth"
            and v.get("verdict") == "pass"
        ], (name, scores)


def test_raw_verdict_unchanged_by_rename(conn):
    """行為不變之錨：層 0 為承接時 raw_verdict 仍是 pass（只認 'pass' 的舊判斷式即紅）。"""
    cur = conn.cursor()
    item_id = _one_carried_item(cur)
    res = _run(cur, item_id)
    cur.execute(
        "SELECT raw_verdict, admit_depth_before, admit_depth_after "
        "FROM knowhow_auto_admit_run WHERE run_id=%s",
        (res["run_id"],),
    )
    raw_v, before, after = cur.fetchone()
    assert raw_v == "pass", (raw_v, res["layer_scores"])
    assert before == after, (before, after)
