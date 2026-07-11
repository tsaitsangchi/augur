"""本地審議引擎純函式回歸 — 守三級殺權/停機/錨點/oracle 契約(A5 自審發現零覆蓋而補)。

🎯 這支在測什麼(白話):審議引擎承載 #15「多數不造真、oracle 反證單票即殺」的**確定性核心**
   (consensus 三級殺權、critic 停機、anchors L4-L6 錨點、verifiers oracle 契約+秘密 denylist)
   全是純函式、易測卻曾零 pytest 守護——本檔補上,任何人改聚合條件/放鬆機械鎖即紅燈。

守 #15(測 oracle 反證優先、consensus 不造 confirmed)· 對映引擎模式 2/4/5/6/8。
"""
from augur.deliberation import anchors, consensus, critic, verifiers


def _row(verifier, anchor, status, lens, claim_text="c"):
    return {"assigned_verifier": verifier, "anchor": anchor, "status": status,
            "lens": lens, "claim_text": claim_text}


# ── consensus 三級殺權(#15 核心安全邏輯)──────────────────────────────
def test_aggregate_refuted_single_vote_kill():
    """oracle 反證單票即殺:一票 refuted 壓過任何 confirmed(工具說假=假,不投票)。"""
    rows = [_row("db_query", "a", "confirmed", "skeptic"),
            _row("db_query", "a", "refuted", "complete")]
    agg = consensus.aggregate(rows)
    assert len(agg) == 1 and agg[0]["verdict"] == "refuted"


def test_aggregate_confirmed_via_oracle():
    """任一 oracle confirmed 即成立(無 refuted 時);escalated 不擋。"""
    rows = [_row("db_query", "a", "confirmed", "skeptic"),
            _row("db_query", "a", "escalated", "complete")]
    assert consensus.aggregate(rows)[0]["verdict"] == "confirmed"


def test_aggregate_all_escalated_never_confirmed():
    """全 escalated(無 oracle 定論)→ escalated,絕不因多數升 confirmed(#15 多數不造真)。"""
    rows = [_row("human_claude", "a", "escalated", "skeptic"),
            _row("human_claude", "a", "escalated", "complete"),
            _row("human_claude", "a", "escalated", "doctrine")]
    agg = consensus.aggregate(rows)
    assert agg[0]["verdict"] == "escalated" and agg[0]["n_lens"] == 3


def test_aggregate_dedup_by_verifier_anchor():
    """去重鍵=(verifier, 正規化 anchor):同檢查多 lens 算一組、異 anchor 分兩組。"""
    same = [_row("db_query", "T", "confirmed", "a"), _row("db_query", " t ", "confirmed", "b")]
    assert len(consensus.aggregate(same)) == 1                      # 大小寫/空白正規化後同鍵
    diff = [_row("db_query", "T1", "confirmed", "a"), _row("db_query", "T2", "confirmed", "b")]
    assert len(consensus.aggregate(diff)) == 2


def test_summarize_counts():
    rows = [_row("db_query", "a", "confirmed", "x"), _row("db_query", "b", "refuted", "x")]
    s = consensus.summarize(consensus.aggregate(rows))
    assert "confirmed 1" in s and "refuted 1" in s


# ── critic 停機/完整性 ───────────────────────────────────────────────
def test_is_dry_threshold():
    assert critic.is_dry(2, 2) is True and critic.is_dry(1, 2) is False
    assert critic.is_dry(3, 2) is True and critic.is_dry(0, 1) is False


def test_new_deterministic_keys_only_counts_oracle_verdicts():
    """只認 confirmed/refuted 為新發現;escalated 不湊數、已見過的排除。"""
    agg = [{"key": ("db_query", "a"), "verdict": "confirmed"},
           {"key": ("db_query", "b"), "verdict": "escalated"},
           {"key": ("db_query", "c"), "verdict": "refuted"}]
    fresh = critic.new_deterministic_keys(agg, seen_keys={("db_query", "a")})
    assert fresh == {("db_query", "c")}                             # b(escalated)不算、a 已見


# ── anchors L4-L6 快路(確定性、零 LLM)────────────────────────────────
def test_fast_anchor_l4_table_count():
    assert anchors.fast_anchor("表 feature_values 至少 100 列") == \
        ("db_query", "SELECT count(*) FROM feature_values => >= 100", "L4_db_query")
    assert anchors.fast_anchor("表 foo 至多 5 列") == ("db_query", "SELECT count(*) FROM foo => <= 5", "L4_db_query")


def test_fast_anchor_l5_conditional_where():
    got = anchors.fast_anchor("knowledge_item 表中 domain 欄等於 computer_science 的列數至少 5000")
    assert got == ("db_query", "SELECT count(*) FROM knowledge_item WHERE domain='computer_science' => >= 5000",
                   "L4_db_query")


def test_fast_anchor_table_exists():
    assert anchors.fast_anchor("資料表 feature_values 存在") == \
        ("information_schema", "feature_values", "L4_information_schema")


def test_fast_anchor_l6_pytest_and_isolation():
    v, a, rid = anchors.fast_anchor("pytest 節點 tests/test_x.py::test_y 通過")
    assert v == "pytest" and a == "tests/test_x.py::test_y" and rid == "L6_pytest"
    assert anchors.fast_anchor("隔離不變式成立") == ("import_isolation", "check_isolation", "L6_isolation")


def test_fast_anchor_none_when_not_mechanical():
    assert anchors.fast_anchor("這個設計理念很好但無法機械驗證") is None


# ── verifiers oracle 契約(fail-closed)+ 秘密 denylist(#5/#7)───────────
def test_run_verifier_rejects_non_oracle():
    v, _ = verifiers.run_verifier("bogus_verifier", "x")
    assert v == "undecidable"


def test_db_query_rejects_write_and_bad_anchor():
    assert verifiers.run_verifier("db_query", "no arrow here")[0] == "undecidable"
    assert verifiers.run_verifier("db_query", "DELETE FROM t => == 0")[0] == "undecidable"   # 非 SELECT
    assert verifiers.run_verifier("db_query", "SELECT 1; drop table t => == 1")[0] == "undecidable"  # 多語句


def test_file_grep_rejects_bad_anchor_and_escape():
    assert verifiers.run_verifier("file_grep", "no-sep-regex")[0] == "undecidable"
    assert verifiers.run_verifier("file_grep", "../../etc/passwd::root")[0] == "undecidable"  # 逃逸圍欄


def test_secret_denylist_pattern():
    """#7:秘密檔 denylist 命中 .env/金鑰/憑證,不命中正常源碼。"""
    assert verifiers._SECRET_DENY.search(".env")
    assert verifiers._SECRET_DENY.search("config/prod.key")
    assert verifiers._SECRET_DENY.search("my_credentials.txt")
    assert not verifiers._SECRET_DENY.search("src/augur/deliberation/verifiers.py")


# ── P0-B1/B3(補完計畫 §2.1/§2.3):規則化快路/注入反例/語意綁定 ────────────
def test_fast_anchor_returns_rule_id_3tuple():
    got = anchors.fast_anchor("資料表 feature_values 存在")
    assert got == ("information_schema", "feature_values", "L4_information_schema")


def test_fast_anchor_rules_gate_l6_pytest():
    """L6_pytest 關 → pytest 樣式不走快路;開 → 命中且 rule_id 正確(B3 config 閘)。"""
    txt = "pytest 節點 tests/test_x.py::test_y 通過"
    off = dict(anchors.RULES_ALL, L6_pytest=False)
    assert anchors.fast_anchor(txt, None, off) is None
    v, a, rid = anchors.fast_anchor(txt, None, anchors.RULES_ALL)
    assert (v, rid) == ("pytest", "L6_pytest")


def test_fast_anchor_injection_counterexample():
    """惡意/失控文字不得鑄錨:整段 SQL/UPDATE 樣式無法經樣板規則產生錨(B3 驗收③)。"""
    assert anchors.fast_anchor("執行 UPDATE feature_values SET value=0; 然後表 x 至少 1 列數") is None or \
        "UPDATE" not in (anchors.fast_anchor("執行 UPDATE feature_values SET value=0; 然後表 x 至少 1 列數") or ("", "", ""))[1]
    # 嵌套注入樣式:值 regex 限 [a-z0-9_.-],引號/分號進不了錨
    got = anchors.fast_anchor("knowledge_item 表中 domain 欄等於 x'; DROP TABLE y;-- 的列數至少 1")
    assert got is None or ("DROP" not in got[1] and ";" not in got[1])


def test_binding_check_negative_select1():
    """語意無關錨(SELECT 1)配洩漏宣稱 → 不綁定(B1 反例)。"""
    assert anchors.binding_check("X 資料集在 2020 年無洩漏", "db_query", "SELECT 1 => == 1") is False


def test_semantic_bound_of_fast_path_positive():
    """fast_path 樣式:錨可自文字重導出 → bound=True(B1 設計保證)。"""
    txt = "表 feature_values 至少 100 列"
    v, a, _ = anchors.fast_anchor(txt)
    assert anchors.semantic_bound_of(txt, v, a) is True


def test_run_verifier_db_and_file_integration():
    """整合(打本機 augur DB/repo):真表存在=confirmed、count>=0=confirmed、repo 檔含字串=confirmed。"""
    assert verifiers.run_verifier("information_schema", "feature_values")[0] == "confirmed"
    assert verifiers.run_verifier("db_query", "SELECT count(*) FROM feature_values => >= 0")[0] == "confirmed"
    assert verifiers.run_verifier("file_grep", "src/augur/deliberation/verifiers.py::run_verifier")[0] == "confirmed"


# ── P0-B2 GATE-lite(§2.2)+ 模式 10 run/task(§3.1)────────────────────────
def test_mcnemar_exact_known_values():
    """對照已知值:b=0,c=13 → p≈2.44e-4;b=c → p=1;b+c=0 → 1(B2 判準3 之數學件)。"""
    import importlib.util, pathlib
    spec = importlib.util.spec_from_file_location(
        "bench", pathlib.Path(__file__).resolve().parent.parent / "scripts" / "benchmark_deliberation.py")
    import sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
    bench = importlib.util.module_from_spec(spec); spec.loader.exec_module(bench)
    assert abs(bench.mcnemar_exact(0, 13) - 2 * 0.5 ** 13) < 1e-12
    assert bench.mcnemar_exact(3, 3) == 1.0
    assert bench.mcnemar_exact(0, 0) == 1.0
    assert bench.mcnemar_exact(0, 5) == 2 * 0.5 ** 5          # 30 題/輪 +15pp 淨勝5 → 0.0625(逐輪假嚴格例證)


def test_build_tasks_seeded_reproducible():
    """題集 seed:同 seed 同題序、異 seed 異抽樣(P-1 重複軸=題目抽樣)。"""
    import importlib.util, pathlib, sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "bench2", pathlib.Path(__file__).resolve().parent.parent / "scripts" / "benchmark_deliberation.py")
    bench = importlib.util.module_from_spec(spec); spec.loader.exec_module(bench)
    a1 = bench.build_tasks(4, seed=41)
    a2 = bench.build_tasks(4, seed=41)
    b1 = bench.build_tasks(4, seed=42)
    assert [t[1] for t in a1] == [t[1] for t in a2]
    assert [t[1] for t in a1] != [t[1] for t in b1]


# ── P2 D6:redline consult(治權觸線→強制人裁,快路豁免不了)────────────────
def test_redline_forces_human_and_red_line_reason():
    """含 anti-leakage 觸線欄之 claim → assigned_verifier 強制 human_claude、
    verify 走 escalation reason='red_line_category'(status='escalated',oracle 不逕裁)。"""
    from augur.core import db as _db
    from augur.deliberation import ledger as lg
    from augur.deliberation.verifiers import verify_claim as vc
    with _db.connect() as conn:
        cur = conn.cursor()
        sid = lg.new_session_id()
        lg.open_session(cur, sid, "redline 測試", None, "fake")
        claim = {"category": "antileakage", "assigned_verifier": "db_query",
                 "claim_text": "TaiwanStockDividend.AnnouncementDate 欄可直接當 as-of 用",
                 "anchor": "SELECT 1 => == 1"}
        cid = lg.insert_claim(cur, sid, claim, "skeptic", "fake", None)
        cur.execute("SELECT assigned_verifier, provenance FROM deliberation_claim WHERE claim_id=%s", (cid,))
        ver, prov = cur.fetchone()
        assert ver == "human_claude" and prov.get("redline", {}).get("kind") == "antileakage_column"
        r = vc(cid, cur=cur)
        assert r["status"] == "escalated" and r["reason"] == "red_line_category"
        conn.rollback()


def test_session_heartbeat_columns_exist():
    """D3:session 三欄(heartbeat_at/finished_at/duration_s)已就位。"""
    from augur.core import db as _db
    with _db.connect() as conn, _db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema='public' "
                    "AND table_name='deliberation_session' "
                    "AND column_name IN ('heartbeat_at','finished_at','duration_s')")
        assert cur.fetchone()[0] == 3


# ── P1 模式 9 自我迭代(§3.2)+ 模式 4 judge panel(§3.3)——假 LLM 零 GPU ──────
def _fake_llm(script):
    """假 LLM:依序回放 script(prompt, schema 無關;測狀態機非模型)。"""
    it = iter(script)

    def fn(prompt, schema):
        return next(it)
    return fn


def test_iterate_chain_and_oracle_only_confirmed():
    """模式 9 驗收①②:proposal 鏈 parent 可溯至 draft;迭代期新 confirmed 全數有 verdict 列(不繞 oracle)。"""
    from augur.core import db as _db
    from augur.deliberation import iterate
    claim = {"category": "schema", "claim_text": "資料表 feature_values 存在",
             "anchor": "feature_values", "assigned_verifier": "information_schema"}
    script = [
        {"draft": "d1", "claims": [claim]},                       # DRAFT
        {"critiques": [{"point": "驗證太少", "severity": "minor"}]},   # ATTACK r1
        {"draft": "d2", "claims": [claim]},                       # REFINE r1(同宣稱→r2 無新發現→dry)
        {"critiques": [{"point": "ok", "severity": "minor"}]},       # ATTACK r2
        {"draft": "d3", "claims": [claim]},                       # REFINE r2
    ]
    with _db.connect() as conn:
        cur = conn.cursor()
        fid = iterate.run_iteration(cur, _fake_llm(script), "測試題", None, max_rounds=3)
        # 鏈可溯:final → refine → attack → … → draft
        pid, hops = fid, 0
        while pid is not None and hops < 10:
            cur.execute("SELECT parent_id, stage FROM deliberation_proposal WHERE proposal_id=%s", (pid,))
            parent, stage = cur.fetchone()
            pid, hops = parent, hops + 1
        assert stage == "draft" and hops >= 3                     # 至少 final→refine→attack→draft
        # 驗收②:本次迭代 confirmed 全數有 is_deterministic verdict(不繞 oracle)
        cur.execute("""SELECT count(*) FROM deliberation_claim c
                       JOIN deliberation_proposal p ON c.claim_id = ANY(p.claim_ids)
                       WHERE p.proposal_id=%s AND c.status='confirmed'
                       AND NOT EXISTS (SELECT 1 FROM deliberation_verdict v
                                       WHERE v.claim_id=c.claim_id AND v.is_deterministic)""", (fid,))
        assert cur.fetchone()[0] == 0
        conn.rollback()                                           # 零副作用


def test_panel_scores_soft_only_no_claim_write():
    """模式 4 驗收③:panel 落分+排序,期間 deliberation_claim 零新列(零 confirmed 權)。"""
    from augur.core import db as _db
    from augur.deliberation import iterate, ledger as lg, panel_judge
    with _db.connect() as conn:
        cur = conn.cursor()
        sid = lg.new_session_id()
        lg.open_session(cur, sid, "panel 測試", None, "fake")
        p1 = iterate._insert_proposal(cur, sid, "draft", 1, {"draft": "A"})
        p2 = iterate._insert_proposal(cur, sid, "draft", 1, {"draft": "B"})
        cur.execute("SELECT count(*) FROM deliberation_claim")
        before = cur.fetchone()[0]
        fake = _fake_llm([{"score": 8, "rationale": "solid"}, {"score": 5, "rationale": "weak"},
                          {"score": 7, "rationale": "ok"}, {"score": 4, "rationale": "thin"}])
        ids = panel_judge.synthesize_panel(cur, fake, [p1, p2], ["skeptic", "complete"], "fake")
        assert len(ids) == 4
        rk = panel_judge.ranking(cur, [p1, p2])
        assert rk[0][0] == p1 and rk[0][1] > rk[1][1]             # A(8,5) > B(7,4)... mean 6.5 vs 5.5
        cur.execute("SELECT count(*) FROM deliberation_claim")
        assert cur.fetchone()[0] == before                        # 零 claim 寫入
        conn.rollback()


def test_run_task_ledger_roundtrip():
    """模式 10:create_run 冪等(同 key 回同 run)/next_task 取工/mark/finish;rollback 不留痕。"""
    from augur.core import db as _db
    from augur.deliberation import ledger as lg
    with _db.connect() as conn:
        cur = conn.cursor()
        plan = [{"seed": 41, "arm": "engine"}, {"seed": 42, "arm": "engine"}]
        rid1 = lg.create_run(cur, "test:roundtrip", plan)
        rid2 = lg.create_run(cur, "test:roundtrip", plan)
        assert rid1 == rid2                                    # 冪等
        t = lg.next_task(cur, rid1)
        assert t is not None and t[1] == 0
        lg.mark_task(cur, t[0], "done")
        t2 = lg.next_task(cur, rid1)
        assert t2 is not None and t2[1] == 1
        lg.mark_task(cur, t2[0], "failed")
        assert lg.resume_reset(cur, rid1) == 1                 # failed(attempt<3)→pending
        t3 = lg.next_task(cur, rid1)
        lg.mark_task(cur, t3[0], "done")
        assert lg.finish_run(cur, rid1) == "completed"
        conn.rollback()                                        # 測試零副作用
