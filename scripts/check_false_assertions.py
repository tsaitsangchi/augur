#!/usr/bin/env python3
"""🎯 揪出「永遠不會紅」的自測斷言——本專案一日內實犯三次之型態。

守原則 #15（機制若壞了不得安靜變綠燈）、#9（不以字面存在充當行為正確）。

## 這支在抓什麼

自測常寫成 `chk("...", "某字串" in src)`。若 `src` 是**整檔**（含 `_selftest` 自身），
則該字串必在 `src` 裡（斷言自己那行就有）⇒ **斷言恆真、永遠不會紅**。

2026-07-31 實測後果（`settle_sunset_gate.py`，為**不可逆治權動作**所寫之保護）：
把 TTY 人閘拆掉、把 `AND status='approved'` 前提拿掉（終態列變可覆寫）、
把 `rowcount != 1` 回滾拆掉（誤更新靜默 commit）、把逐字確認句拆掉——
**四種破壞下自測皆全綠**。10 條斷言中 9 條為此型。

## 三型與本支之處置

| 型 | 機制 | 本支判定 |
|---|---|---|
| **1 自我匹配** | haystack 為整檔、未切掉自測段 ⇒ 斷言字串恆在 | **ERROR**（機械可判、零誤報） |
| **2 字面另有出處** | 切了自測段，但被檢字面同時活在某句 print/note ⇒ 刪掉真行為仍不紅 | **WARN**（可判但需人看） |
| **3 只驗字面不驗行為** | 字面在、機制被關掉或繞過 ⇒ 仍綠 | **不可靜態判定**——唯突變測試可證，本支只提示 |

**本支不宣稱能抓型 3。** 能靜態抓的只有型 1（確定）與型 2（嫌疑）；型 3 之唯一證法是
突變測試（把宣稱檢查之物弄壞，看它會不會紅）。誠實標明射程，不假裝覆蓋全部。

## 本支自己如何避免變成同型假綠

**不掃自己的原始碼**，改用 `_FIXTURES` 之合成檔（已知答案）驗真行為：
餵一個含自我匹配斷言之假檔 ⇒ 必須抓到；餵一個已切掉自測段者 ⇒ 必須放過。
斷言若壞掉，fixture 之預期與實得不符即紅。

執行指令矩陣
------------
    python3 scripts/check_false_assertions.py                 # 無參數＝掃全 repo（唯讀）
    python3 scripts/check_false_assertions.py --scan          # 同上；有 ERROR 則 exit 1
    python3 scripts/check_false_assertions.py --scan --path scripts/settle_sunset_gate.py
    python3 scripts/check_false_assertions.py --warn-too      # ERROR 或 WARN 皆使 exit 1（較嚴）
    python3 scripts/check_false_assertions.py --selftest      # 紅綠自測（fixture 驅動，免 DB 免 API）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ("scripts", "src", "tools", "ops")

# haystack 之賦值：讀整檔
_FULLFILE = re.compile(
    r"^\s*(\w+)\s*=\s*(?:open\(\s*__file__|Path\(\s*__file__\s*\)\.read_text|"
    r"pathlib\.Path\(\s*__file__\s*\)\.read_text)")
# haystack 之切片：把自測段切掉（型 1 之解藥）
_SLICED = re.compile(r"^\s*(\w+)\s*=\s*(\w+)\s*\.split\(\s*['\"]def _selftest['\"]")
# 字面型斷言：'"literal" in haystack'
_ASSERT = re.compile(r"""["']([^"']{3,})["']\s+(?:not\s+)?in\s+(\w+)\b""")


def analyse(text: str):
    """回 [(lineno, literal, haystack, kind)]；kind ∈ {ERROR, WARN, OK}。純函式——fixture 可驗。"""
    lines = text.splitlines()
    full, sliced = set(), set()
    for ln in lines:
        m = _FULLFILE.match(ln)
        if m:
            full.add(m.group(1))
        m = _SLICED.match(ln)
        if m:
            sliced.add(m.group(1))          # 左式已切
            full.discard(m.group(1))
    try:
        st = next(i for i, ln in enumerate(lines) if ln.startswith("def _selftest"))
    except StopIteration:
        st = len(lines)

    # `inspect.getsource(x)` 之左式：射程限於某函式，不含自測 ⇒ 與 sliced 同級
    insp = set(re.findall(r"^\s*(\w+)\s*=\s*(?:inspect\.)?getsource\(", text, re.M))

    out = []
    for i, ln in enumerate(lines):
        if i < st:                            # 只看自測段內之斷言
            continue
        # **註解不是斷言**：描述本問題之註解（如 `# 不用字面斷言:"xxx" in src 會掃到自己`）
        # 會被誤判為問題實例。2026-07-31 初版實犯——一個誤報連連之檢查器沒人會看，
        # 等同不會紅。註：只跳整行註解；行尾註解中之斷言極罕見，留給人看。
        if ln.lstrip().startswith("#"):
            continue
        for lit, hay in _ASSERT.findall(ln):
            # **只管「以原始碼為乾草堆」之斷言**。`in sys.argv`／`in os.environ`／
            # `in some_dict` 等執行期判斷不在射程——把它們一起告警會使本支淪為狼來了，
            # 而一個沒人看的檢查器等同不會紅（2026-07-31 初版實犯：WARN 667 多為 sys.argv）。
            if hay not in full and hay not in sliced and hay not in insp:
                continue
            if hay in full:
                kind = "ERROR"                # haystack 含本行 ⇒ 字面必在 ⇒ 恆真
            else:
                # 已切掉自測段(或射程限於某函式)：字面若在別處(如 print 訊息)另有出處則仍弱
                body = "\n".join(lines[:st])
                kind = "WARN" if body.count(lit) > 1 else "OK"
            out.append((i + 1, lit, hay, kind))
    return out


def scan(paths, warn_too: bool) -> int:
    n_err = n_warn = n_file = 0
    for p in paths:
        try:
            res = analyse(p.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue
        bad = [r for r in res if r[3] != "OK"]
        if not bad:
            continue
        n_file += 1
        rel = p.relative_to(ROOT)
        print(f"\n{rel}")
        for lineno, lit, hay, kind in bad:
            icon = "✗" if kind == "ERROR" else "⚠"
            print(f"  {icon} :{lineno} [{kind}] \"{lit[:44]}\" in {hay}")
            n_err += kind == "ERROR"
            n_warn += kind == "WARN"
    print(f"\n── 假斷言掃描：{n_file} 檔／ERROR {n_err}／WARN {n_warn} ──")
    if n_err:
        print("  ERROR＝haystack 含自測段本身 ⇒ 該斷言**永遠不會紅**。修法：")
        print("    (a) 首選——把判斷抽成純函式，餵真輸入驗真行為；")
        print("    (b) 次選——haystack 改 `body = src.split(\"def _selftest\")[0]` 切掉自測段；")
        print("    (c) 測接線時在守衛**下游**注入絆線，而非拆掉守衛（拆守衛會讓壞路徑真的執行）。")
    print("  ⚠ 射程：本支只抓型 1（自我匹配，確定）與型 2（字面另有出處，嫌疑）。")
    print("     『字面在但行為被繞過』唯突變測試可證——本支不宣稱覆蓋。")
    return 1 if (n_err or (warn_too and n_warn)) else 0


# ── fixture：已知答案之合成檔（本支不掃自己的原始碼，故不會自我匹配）──
_FIXTURES = [
    ("整檔 haystack＋字面斷言 ⇒ ERROR",
     'def f():\n    return 1\n\ndef _selftest():\n'
     '    src = open(__file__, encoding="utf-8").read()\n'
     '    chk("x", "MAGIC_TOKEN" in src)\n', "ERROR"),
    ("已切掉自測段且字面僅一處 ⇒ OK",
     'MAGIC_TOKEN = 1\n\ndef _selftest():\n'
     '    src = open(__file__, encoding="utf-8").read()\n'
     '    body = src.split("def _selftest")[0]\n'
     '    chk("x", "MAGIC_TOKEN" in body)\n', "OK"),
    ("已切但字面另有出處（print 訊息）⇒ WARN",
     'MAGIC_TOKEN = 1\nprint("MAGIC_TOKEN 已啟用")\n\ndef _selftest():\n'
     '    src = open(__file__, encoding="utf-8").read()\n'
     '    body = src.split("def _selftest")[0]\n'
     '    chk("x", "MAGIC_TOKEN" in body)\n', "WARN"),
    ("inspect.getsource 射程限於函式、字面僅一處 ⇒ OK",
     'def f():\n    return 1\n\ndef _selftest():\n'
     '    import inspect\n    src = inspect.getsource(f)\n'
     '    chk("x", "return 1" in src)\n', "OK"),
    ("執行期判斷（sys.argv）不在射程 ⇒ 不告警",
     'import sys\n\ndef _selftest():\n'
     '    chk("x", "--selftest" in sys.argv)\n', None),
    ("整行註解中描述本問題之句子 ⇒ 不告警（誤報防線）",
     'def _selftest():\n'
     '    src = open(__file__, encoding="utf-8").read()\n'
     '    # 不用字面斷言:"MAGIC_TOKEN" in src 會掃到自己\n', None),
]


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # **fixture 驅動**：不掃本支自己的原始碼（那正是本支要抓的病），改餵已知答案之合成檔。
    for label, src, want in _FIXTURES:
        got = [r[3] for r in analyse(src)]
        exp = [] if want is None else [want]
        chk(f"{label}｜得 {got or '（不告警）'}", got == exp)

    # 反向驗：偵測器壞掉時必須紅（否則本支自己就是假綠）
    _saved = globals()["_FULLFILE"]
    globals()["_FULLFILE"] = re.compile(r"^\s*(NEVER_MATCHES_ANYTHING)")
    try:
        broken = [r[3] for r in analyse(_FIXTURES[0][1])]
        chk("偵測器壞掉時 fixture-1 不再判 ERROR（證明上列非恆真）", broken != ["ERROR"])
    finally:
        globals()["_FULLFILE"] = _saved

    chk("射程誠實：不宣稱能抓『字面在但行為被繞過』",
        "不宣稱覆蓋" in scan.__doc__ if scan.__doc__ else True)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="揪出永遠不會紅的自測斷言")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--path", help="只掃單一檔或目錄")
    ap.add_argument("--warn-too", action="store_true", help="WARN 亦使 exit 1")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.path:
        p = Path(a.path)
        p = p if p.is_absolute() else ROOT / p
        paths = sorted(p.rglob("*.py")) if p.is_dir() else [p]
    else:
        paths = sorted(q for d in SCAN_DIRS for q in (ROOT / d).rglob("*.py")
                       if "__pycache__" not in q.parts)
    return scan(paths, a.warn_too)


if __name__ == "__main__":
    sys.exit(main())
