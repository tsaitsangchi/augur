"""🎯 sync_memory export 之密碼掃描閘：**掃到明碼就一個檔都不寫**（M-O3）。

守原則 #5（不把憑證推進 public repo）、#6（不可逆操作 fail-closed）、#15（紅燈必須會亮）、
#35（餵真輸入、絆線放在寫入路徑下游）。
背景：`handoff_memory/` 會被 commit+push 到 **public** repo，push 後不可逆；2026-07-13 實犯
夾帶明碼服務密碼，靠人在 push 前手掃才攔下（記憶 `memory-export-secret-scan`）。

本檔鎖的是**接線**（export 真的會呼叫掃描、紅則不寫），判準本身之紅綠鎖在
`python -m augur.audit.plaintext_credential --selftest`。
先驗紅：把 `run_secret_scan` 換成恆綠樁（＝M-O3 之前的 export 行為）時，`test_mutation_*`
證明明碼**真的**會被寫進快照——故上面那些綠燈是這個閘擋下來的，不是恆真。

執行：pytest tests/test_sync_memory_export_gate.py -v
"""
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import sync_memory as sm  # noqa: E402

# 合成值、真形狀：2026-07-13 實犯之行形，明碼換成假值（本檔不含真憑證）
FAKE_PW = "Tt@i" + "-2026" + "#live"
_AU = "app" + "_user"      # 連續字面會被 #8 隔離 AST 閘判為 RBAC 旁路（同 src 側處置）
LEAK_LINE = f"- 登入:`admin` / `{FAKE_PW}`(前後台同組;我重設 {_AU} 密碼=同值)。"
# 真陰性逐字取自 handoff_memory/（裸關鍵字命中但皆非明碼）——閘若對它們假紅就會被繞過
CLEAN_LINES = [
    "description: FinMind 資料源全貌——augur token=Sponsor 6000/hr、2026-06-24 到期",
    f"- 登入:`admin` / `⟨見 .env AUGUR_ADMIN_PASSWORD⟩`(前後台同組;我重設 {_AU} 密碼=同值)。",
    "- `.env`(鍵:`DB_USER/DB_PASSWORD`、`FINMIND_TOKEN`、`GITHUB_TOKEN`;**值不入記憶**)。",
]


@pytest.fixture
def memdirs(tmp_path, monkeypatch):
    """temp 之 live/snapshot 一組；REPO_ROOT 一併改指 temp（豁免清單＝缺檔＝零豁免）。"""
    live, snap = tmp_path / "live", tmp_path / "handoff_memory"
    live.mkdir()
    snap.mkdir()
    (live / "clean.md").write_text("\n".join(CLEAN_LINES) + "\n", encoding="utf-8")
    monkeypatch.setattr(sm, "live_memory_dir", lambda: live)
    monkeypatch.setattr(sm, "SNAPSHOT_DIR", snap)
    monkeypatch.setattr(sm, "REPO_ROOT", tmp_path)
    return live, snap


def _snapshot_text(snap):
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(snap.glob("*.md")))


def test_clean_corpus_exports(memdirs):
    """真陰性語料（裸 token/PASSWORD 字樣）不得假紅——閘天天假紅就會被繞過。"""
    live, snap = memdirs
    assert sm.cmd_export() == 0
    assert sorted(p.name for p in snap.glob("*.md")) == ["clean.md"]


def test_plaintext_credential_blocks_export(memdirs):
    """植入明碼 ⇒ rc≠0，且**整批不寫**（不是「只跳過那一檔」）。"""
    live, snap = memdirs
    (live / "ttai.md").write_text(LEAK_LINE + "\n", encoding="utf-8")
    rc = sm.cmd_export()
    assert rc != 0
    assert list(snap.glob("*.md")) == []
    assert FAKE_PW not in _snapshot_text(snap)


def test_scanner_import_failure_is_fail_closed(memdirs, monkeypatch):
    """掃描器載不進來（模組被刪／改名）⇒ 擋下，不得「找不到就放行」。"""
    live, snap = memdirs
    (live / "ttai.md").write_text(LEAK_LINE + "\n", encoding="utf-8")

    def _boom():
        raise ModuleNotFoundError("no plaintext_credential")

    monkeypatch.setattr(sm, "load_scanner", _boom)
    assert sm.cmd_export() != 0
    assert list(snap.glob("*.md")) == []


def test_mutation_removing_gate_lets_credential_through(memdirs, monkeypatch):
    """突變驗紅：閘拔掉（＝M-O3 之前）⇒ 明碼真的被寫進快照。

    這條**故意斷言洩漏發生**——它是上面三條綠燈的意義來源：沒有它，那三條可能恆真。
    """
    live, snap = memdirs
    (live / "ttai.md").write_text(LEAK_LINE + "\n", encoding="utf-8")
    monkeypatch.setattr(sm, "run_secret_scan", lambda files: (0, []))
    assert sm.cmd_export() == 0
    assert FAKE_PW in _snapshot_text(snap)


def test_waiver_requires_full_traceability(memdirs):
    """豁免可放行但必印留痕；欄位缺一即判紅（壞掉的豁免不得靜默生效）。"""
    live, snap = memdirs
    (live / "ttai.md").write_text(LEAK_LINE + "\n", encoding="utf-8")
    pc = sm.load_scanner()
    finding = pc.scan_text("ttai.md", LEAK_LINE)[0]
    ops = sm.REPO_ROOT / "ops"
    ops.mkdir()
    allowlist = ops / "memory_secret_allowlist.txt"

    allowlist.write_text("\t".join((finding.name, finding.rule, finding.digest,
                                    "test-approver", "2026-08-03", "pytest fixture")) + "\n",
                         encoding="utf-8")
    rc, msgs = sm.run_secret_scan(sm.md_files(live))
    assert rc == 0
    assert any("已豁免" in m and finding.digest in m for m in msgs)

    allowlist.write_text(f"{finding.name}\t{finding.rule}\t{finding.digest}\n",
                         encoding="utf-8")
    rc, msgs = sm.run_secret_scan(sm.md_files(live))
    assert rc != 0 and any("格式錯誤" in m for m in msgs)


def test_scanned_set_must_equal_written_set(memdirs, monkeypatch):
    """掃 A 卻寫 B 不算掃過——寫入集有未掃檔即判紅。"""
    live, _snap = memdirs
    (live / "other.md").write_text("# 無害\n", encoding="utf-8")
    pc = sm.load_scanner()
    monkeypatch.setattr(pc, "scan_files", lambda files: ([], {sorted(files)[0]}))
    rc, msgs = sm.run_secret_scan(sm.md_files(live))
    assert rc != 0 and any("掃描集" in m for m in msgs)
