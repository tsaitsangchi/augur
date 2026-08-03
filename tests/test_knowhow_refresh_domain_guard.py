"""🎯 knowhow-refresh 空轉 fail-loud 之回歸鎖(M-G8 S1)：**不存在的域不得靜默 rc=0**。

守 #15（rc=0 不代表有做事）、#29b（可用域 SSOT＝DB 非寫死清單）、#35（先驗紅）。

背景（2026-08-03 現查）：`augur-knowhow-refresh.service` 之 ExecStart 帶
`--from-stage promote --domain finance`，而全庫**無 finance 這個域**
（`knowledge_item WHERE domain='finance'` ＝ 0），同時刻全域 `knowledge_staging`
`status='pending'` ＝ 102,039。修復前該指令 rc=0、journal 自陳「待辦(前) 0」＝
每週準時 Finished 的空轉假綠（timer NEXT＝Sun 2026-08-09 04:30）。

本檔鎖的是**接線**（CLI 真的會擋、且擋在任何寫入之前），純判準之紅綠鎖在
`python scripts/refresh_knowledge_pipeline.py --selftest`。

先驗紅（2026-08-03 實跑）：把 `assert_domain_known(args.domain)` 一行拿掉（＝M-G8 之前的
行為），`test_bogus_domain_*` 立刻轉紅（rc 0≠2）；只改註解文字的對照臂則維持全綠——
故下列綠燈是這個閘擋下來的，不是恆真。

安全性：全部經 `--dry-run`。萬一閘被改壞而未擋下，落點是唯讀的待辦矩陣列印，
**不會**真的啟動 12 段管線（突變測試本身不得有副作用）。

執行：pytest tests/test_knowhow_refresh_domain_guard.py -v
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
CLI = SCRIPTS / "refresh_knowledge_pipeline.py"
PY = str(REPO / "venv" / "bin" / "python")

for _p in (str(SCRIPTS), str(REPO / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import refresh_knowledge_pipeline as rkp  # noqa: E402

BOGUS = "no_such_domain_zzz"


def run(*args, timeout=300):
    """跑 CLI 回 (rc, stdout+stderr)。一律帶 --dry-run＝零副作用。"""
    p = subprocess.run([PY, str(CLI), *args], cwd=str(REPO),
                       capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


# ── 域 fail-loud（本工單本體）────────────────────────────────────────────────

def test_bogus_domain_exits_nonzero():
    """驗收①：`--domain <不存在>` → rc≠0（修復前為 rc=0 且印 0 待辦）。"""
    rc, out = run("--domain", BOGUS, "--dry-run")
    assert rc == 2, f"不存在之域須 rc=2，得 rc={rc}\n{out}"
    assert "不存在" in out


def test_bogus_domain_prints_available_domains_from_db():
    """驗收①後半：須印**可用域清單**，且該清單來自 DB 而非寫死字面。

    斷言取兩個真實域：`chemistry`（registry 有登錄）與 `quant_finance`
    （registry **未**登錄、但有 15,552 個 item）——後者只有走「registry ∪ 實際落地」
    的聯集查詢才會出現，寫死 registry 清單的實作會漏掉它。
    """
    rc, out = run("--domain", BOGUS, "--dry-run")
    assert rc == 2
    assert "chemistry" in out and "quant_finance" in out, f"可用域清單未含真實域\n{out}"


def test_bogus_domain_suggests_near_match():
    """`finance` 須提示相近域（實際 unit 就是打成 finance）。"""
    rc, out = run("--domain", "finance", "--dry-run")
    assert rc == 2
    assert "finance_mgmt" in out, f"未提示相近域 finance_mgmt\n{out}"


def test_empty_domain_rejected():
    """`--domain ""` 原會因 truthy 判斷靜默退化為**全域**放量；須一併判紅。"""
    rc, out = run("--domain", "", "--dry-run")
    assert rc == 2, f"空字串域須 rc=2，得 rc={rc}\n{out}"


def test_valid_domain_still_passes():
    """對照臂：合法域不得被誤擋（閘不是恆紅）。"""
    rc, out = run("--domain", "chemistry", "--dry-run")
    assert rc == 0, f"合法域 chemistry 被誤擋 rc={rc}\n{out}"


def test_registry_gap_domain_not_false_red():
    """`quant_finance` 有 15,552 item 卻未登錄 registry——只認 registry 的實作會假紅擋掉正常週更。"""
    rc, out = run("--domain", "quant_finance", "--dry-run")
    assert rc == 0, f"registry 未登錄但有資料之域被假紅擋下 rc={rc}\n{out}"


# ── 候選數地板 ──────────────────────────────────────────────────────────────

def test_floor_blocks_when_below():
    rc, out = run("--stage", "promote", "--domain", "chemistry",
                  "--min-candidates", "999999999", "--dry-run")
    assert rc == 3, f"待辦不足須 rc=3，得 rc={rc}\n{out}"
    assert "候選數地板未達" in out


def test_floor_passes_when_above():
    """對照臂：真有待辦時地板放行（地板不是恆紅）。"""
    rc, out = run("--stage", "promote", "--domain", "chemistry",
                  "--min-candidates", "1", "--dry-run")
    assert rc == 0, f"chemistry promote 有待辦卻被擋 rc={rc}\n{out}"
    assert "候選數地板通過" in out


def test_floor_refuses_inventory_stages():
    """假綠自檢：`stats_items` 印的 188,069 是**全庫庫存**、不隨 domain 收斂。

    若地板把它當待辦（例如從顯示行正則刮數字），則 `--domain <任何值>` 都會過閘
    ＝地板恆過的假綠。故庫存語意之段須判紅（「無從評估」），不得靜默略過。
    """
    for stage in ("stats_items", "bridge"):
        rc, out = run("--stage", stage, "--domain", "chemistry",
                      "--min-candidates", "1", "--dry-run")
        assert rc != 0, f"{stage} 為庫存語意，地板須判紅而非略過，得 rc={rc}\n{out}"
        assert "無從評估" in out


def test_floor_rejects_zero_threshold():
    rc, _ = run("--stage", "promote", "--domain", "chemistry",
                "--min-candidates", "0", "--dry-run")
    assert rc != 0


# ── 純判準／上游真輸出（非手寫 fixture）──────────────────────────────────────

def test_known_domains_is_real_db_output():
    """`known_domains()` 餵真 DB：形狀＝非空 set[str]，且含 registry 缺漏之活躍域。"""
    from augur.core import db
    with db.connect() as conn, db.transaction(conn) as cur:
        known = rkp.known_domains(cur)
    assert isinstance(known, set) and known, "known_domains 須回非空 set"
    assert all(isinstance(x, str) for x in known)
    assert {"chemistry", "quant_finance", "erp_tiptop"} <= known
    assert "finance" not in known, "finance 不該存在——本工單前提"


def test_backlog_stages_exclude_inventory():
    """地板段集不變式：庫存/全量重建段不得入列（入列即地板恆過）。"""
    assert rkp.BACKLOG_STAGES <= set(rkp.NAMES)
    assert not (rkp.BACKLOG_STAGES
                & {"stats", "stats_items", "bridge", "concordance", "vector_export"})


def test_candidate_count_returns_none_for_inventory_stages():
    """非待辦語意之段須回 None（回 0/數字都會讓地板把庫存當待辦）；不觸 cursor 故傳 None 安全。"""
    for stage in ("stats", "stats_items", "bridge", "concordance", "vector_export"):
        assert rkp.candidate_count(None, stage, None) is None, stage


def test_selftest_green():
    p = subprocess.run([PY, str(CLI), "--selftest"], cwd=str(REPO),
                       capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, p.stdout + p.stderr
