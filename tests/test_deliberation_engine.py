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
    assert anchors.fast_anchor("表 feature_values 至少 100 列") == ("db_query", "SELECT count(*) FROM feature_values => >= 100")
    assert anchors.fast_anchor("表 foo 至多 5 列") == ("db_query", "SELECT count(*) FROM foo => <= 5")


def test_fast_anchor_l5_conditional_where():
    got = anchors.fast_anchor("knowledge_item 表中 domain 欄等於 computer_science 的列數至少 5000")
    assert got == ("db_query", "SELECT count(*) FROM knowledge_item WHERE domain='computer_science' => >= 5000")


def test_fast_anchor_table_exists():
    assert anchors.fast_anchor("資料表 feature_values 存在") == ("information_schema", "feature_values")


def test_fast_anchor_l6_pytest_and_isolation():
    v, a = anchors.fast_anchor("pytest 節點 tests/test_x.py::test_y 通過")
    assert v == "pytest" and a == "tests/test_x.py::test_y"
    assert anchors.fast_anchor("隔離不變式成立") == ("import_isolation", "check_isolation")


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


def test_run_verifier_db_and_file_integration():
    """整合(打本機 augur DB/repo):真表存在=confirmed、count>=0=confirmed、repo 檔含字串=confirmed。"""
    assert verifiers.run_verifier("information_schema", "feature_values")[0] == "confirmed"
    assert verifiers.run_verifier("db_query", "SELECT count(*) FROM feature_values => >= 0")[0] == "confirmed"
    assert verifiers.run_verifier("file_grep", "src/augur/deliberation/verifiers.py::run_verifier")[0] == "confirmed"
