"""🎯 明碼憑證偵測——擋住「記憶檔被 export 進 public repo」這條不可逆洩漏路徑。

白話:`sync_memory.py export` 把**全部活 memory 檔**鏡射進 repo `handoff_memory/`,而 repo 是
**public**;push 出去即不可逆(主分支不得 force,#6)。2026-07-13 實犯:export 夾帶 ttai 檔內的明碼
服務密碼,**push 前逐檔人工掃到才攔下**——即「靠人記得手跑」的防線。本模組把該判準寫成**純函式**,
供 export 路徑在寫檔前 fail-closed 攔阻。

## 判準(五條規則;誤報一律走留痕豁免,不得弱化規則)

| 規則 | 抓什麼 | 為何這樣切 |
|---|---|---|
| `kv_strong` | `密碼/password/passwd/pwd = <字面>` | 強關鍵字:凡非佔位符之字面即紅 |
| `kv_weak` | `token/secret/api_key/金鑰… = <亂數樣字面>` | 弱關鍵字在本語料是**日常詞**(「token 額度」「待 token 重建」),故值必須先像亂數才算 |
| `login_pair` | `登入:`admin` / `<字面>`` | **2026-07-13 實犯之形狀**——該行沒有 `password=`,只靠 kv 規則會漏 |
| `known_prefix` | `ghp_…`／`sk-…`／`AKIA…`／`AIza…`／`xox?-…`／JWT／PRIVATE KEY 區塊 | 前綴自證,零上下文即可判 |
| `url_credential` | `scheme://user:pass@host` | 連線字串內嵌密碼 |

**佔位符不算洩漏**:`⟨見 .env AUGUR_ADMIN_PASSWORD⟩`／`<your-pass>`／`${VAR}`／全大寫變數名／
含中日韓字之敘述／純數字／`xxx` 類——本語料 81 檔實測 42 處裸關鍵字命中,終判 0 誤報。

## 誠實射程(本模組**不**宣稱之事)

- 不做熵值/字典攻擊,亦不判「這串亂碼到底是不是真密碼」;判的是**形狀**。
- 全大寫變數名一律視為佔位符 ⇒ `PASSWORD=ABCDEFGHIJKL` 這種全大寫真密碼會漏(取捨:本語料
  滿是 `DB_PASSWORD`／`FINMIND_TOKEN` 之變數名清單,不豁免則閘天天假紅、必被繞過)。
- 只掃 `*.md`(記憶檔之實體形式);不掃自己與任何 `.py`。
- 掃描集必須等於寫入集——**掃到 0 檔不得判綠**(地板住 `augur.audit.scan_floor`)。

守原則 #5(不 commit 憑證)· #15(紅燈必須會亮:fixture 真陽/真陰＋突變驗紅)· #6(不可逆操作 fail-closed)·
#28(零 DB 零 API 零 usage、純本地字串判定)· #35(判準抽純函式、餵真輸入、下游絆線)。
SSOT=`reports/augur_optimization_master_plan_20260803.md` M-O3;事故留痕=記憶 `memory-export-secret-scan`。
消費者:`sync_memory.py` 之 `export` 路徑(唯一強制點)。豁免清單:`ops/memory_secret_allowlist.txt`。

執行指令矩陣:
  python -m augur.audit.plaintext_credential                      # 印用途＋公開入口(唯讀)
  python -m augur.audit.plaintext_credential --scan-dir handoff_memory  # 掃某目錄之 *.md(唯讀;有殘留即 exit 1)
  python -m augur.audit.plaintext_credential --selftest           # 純紅綠自測(免 DB 免 API、零 usage)
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from augur.audit import scan_floor

ALLOWLIST_REL = "ops/memory_secret_allowlist.txt"
ALLOWLIST_COLS = ("檔名", "規則", "值指紋", "核准者", "核准日", "理由")
SCAN_GLOB = "*.md"

# ── 關鍵字(詞表繫於機械閘=邏輯側,#29(b) 豁免款,同 vendor 閘 caliber) ──
_STRONG_KW = ("password", "passwd", "pwd", "密碼", "口令", "通行碼")
_WEAK_KW = ("secret", "token", "api_key", "apikey", "api-key", "access_key", "accesskey",
            "secret_key", "client_secret", "private_key", "privatekey", "credential",
            "金鑰", "密鑰", "憑證")

# 值:引號/反引號/角括號包覆優先,否則吃到空白或中文標點為止
_QUOTED_VAL = (r"`[^`\n]+`|\"[^\"\n]+\"|'[^'\n]+'|「[^」\n]+」|⟨[^⟩\n]+⟩|<[^>\n]+>|\{[^}\n]+\}")
# 裸值之終止字元:空白、引號、各式括號、逗號分號,**以及任何 CJK 字元**。
# CJK 必須終止裸值——否則 `密碼: <明碼>(前後台同組)` 會把後面的中文一起吃進「值」,
# 而「值含中文 ⇒ 判為敘述、放行」⇒ **真陽性靜默漏掉**(2026-08-03 首次紅檢即抓到此形)。
_STOP_RANGES = "".join(f"{chr(lo)}-{chr(hi)}" for lo, hi in (
    (0x2010, 0x2027),    # 破折號/彎引號(本語料以「——」當分隔符)
    (0x27E8, 0x27EF),    # 數學角括號(記憶檔引用寫法之外框)
    (0x2E80, 0x9FFF),    # CJK 部首→統一表意文字(含全形標點 U+3000 區段)
    (0xF900, 0xFAFF),    # CJK 相容表意文字
    (0xFF00, 0xFFEF),    # 全形英數與標點
))
_BARE_VAL = r"[^\s\"'`,;()\[\]{}<>" + _STOP_RANGES + "]+"
_VAL = f"(?P<val>{_QUOTED_VAL}|{_BARE_VAL})"
# 關鍵字邊界不用 \b:`DB_PASSWORD` 之 `_` 使 \b 失效,而那正是最該抓的形狀
_BOUND_L, _BOUND_R = r"(?<![A-Za-z])", r"s?(?![A-Za-z])"
_ASSIGN = r"[ \t]*(?:[=:：＝]|=>|->)[ \t]*"


def _kw_re(words):
    return re.compile(_BOUND_L + "(?P<kw>" + "|".join(words) + ")" + _BOUND_R + _ASSIGN + _VAL,
                      re.IGNORECASE)


_STRONG_RE = _kw_re(_STRONG_KW)
_WEAK_RE = _kw_re(_WEAK_KW)
# 2026-07-13 實犯之形狀:`- 登入:`admin` / `<明碼>`(前後台同組…)` 與 `前台 8090 登入(admin/`<明碼>`、…`
_LOGIN_RE = re.compile(r"(?:登入|登錄|帳密|帳號密碼|login|credentials?)[ \t]*[:：(（][ \t]*"
                       r"(?P<user>[`\"']?[\w.@+-]{1,40}[`\"']?)[ \t]*/[ \t]*" + _VAL,
                       re.IGNORECASE)
_KNOWN_RE = (
    ("github_token", re.compile(r"(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9]{20,}")),
    ("github_pat", re.compile(r"(?<![A-Za-z0-9])github_pat_[A-Za-z0-9_]{20,}")),
    ("openai_anthropic_key", re.compile(r"(?<![A-Za-z0-9])sk-(?:ant-)?[A-Za-z0-9_-]{20,}")),
    ("aws_access_key_id", re.compile(r"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}(?![A-Za-z0-9])")),
    ("google_api_key", re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_-]{35}(?![A-Za-z0-9])")),
    ("slack_token", re.compile(r"(?<![A-Za-z0-9])xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("jwt", re.compile(r"(?<![A-Za-z0-9])eyJ[A-Za-z0-9_-]{10,}"
                       r"\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]{0,24}PRIVATE KEY-----")),
)
_URL_RE = re.compile(r"(?<![A-Za-z0-9])(?P<scheme>[a-z][a-z0-9+.-]{1,15})://"
                     r"(?P<user>[^\s:/@]{1,64}):(?P<val>[^\s:/@]{1,128})@")

# 佔位符字面(小寫比對)——「寫了但不是值」之常見形
_PLACEHOLDER_WORDS = {
    "x", "xx", "xxx", "xxxx", "xxxxx", "yyy", "zzz", "none", "null", "nil", "n/a", "na",
    "todo", "tbd", "changeme", "your_password", "your-password", "yourpassword", "password",
    "passwd", "secret", "token", "empty", "unset", "unknown", "required", "optional",
    "redacted", "masked", "hidden", "same", "above", "below", "see", "true", "false", "yes",
    "no", "-", "--", "...", "…", "***", "*****", "略",
}
_PLACEHOLDER_PREFIX = ("⟨", "<", "{", "$", "%", "＄", "見", ".env", "os.environ", "env.",
                       "process.env", "getenv")
_WRAPPERS = (("`", "`"), ('"', '"'), ("'", "'"), ("「", "」"), ("⟨", "⟩"), ("<", ">"),
             ("{", "}"))
_CJK = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]")
_ENVVAR_NAME = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")
_NUMERIC = re.compile(r"^[0-9]+(?:[.,:/_-][0-9A-Za-z]{1,8})*$")
_MIN_STRONG_LEN = 4          # 3 碼以下之字面判為敘述殘塊,非密碼
_MIN_WEAK_LEN = 8


@dataclass(frozen=True)
class Finding:
    """一筆疑似明碼憑證。**不帶明碼**——只帶指紋與遮罩後樣貌(本結構會被列印)。"""

    name: str        # 檔名(不含目錄;豁免指紋以此為鍵)
    line: int
    rule: str
    keyword: str
    digest: str      # sha256(值)[:12]
    masked: str      # 遮罩後之值
    excerpt: str     # 該行(值已置換為遮罩)

    @property
    def key(self) -> tuple[str, str, str]:
        """豁免鍵——**不含行號**(行號隨編輯漂移會使既有豁免失效、製造假紅)。"""
        return (self.name, self.rule, self.digest)


def digest_of(value: str) -> str:
    """值之指紋(純函式)。豁免清單只存指紋——清單自身不得成為洩漏管道。"""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _mask(value: str) -> str:
    if len(value) <= 3:
        return "*" * len(value)
    return value[0] + "*" * min(len(value) - 1, 15) + f"(len={len(value)})"


def _unwrap(raw: str) -> str:
    """去掉包覆符與尾隨標點 → 內層字面(純函式)。"""
    v = raw.strip()
    changed = True
    while changed and len(v) >= 2:
        changed = False
        for lo, hi in _WRAPPERS:
            if v.startswith(lo) and v.endswith(hi):
                v, changed = v[1:-1].strip(), True
                break
    return v.rstrip(".,;:!?、。，；")


def is_placeholder(raw: str) -> bool:
    """「寫了但不是明碼」→ True(純函式)。raw 為**未去包覆**之原始字面。"""
    inner = _unwrap(raw)
    for cand in (raw.strip(), inner):
        if not cand:
            return True
        if cand.lower() in _PLACEHOLDER_WORDS:
            return True
        if cand.startswith(_PLACEHOLDER_PREFIX):
            return True
        if _CJK.search(cand):            # 含中日韓字 ⇒ 敘述,非明碼
            return True
        if _ENVVAR_NAME.match(cand):     # 全大寫=變數**名**,非值
            return True
        if _NUMERIC.match(cand):         # 純數字/版號/時間
            return True
    return False


def looks_random(value: str) -> bool:
    """弱關鍵字之值是否「像亂數」(純函式)。擋掉 `token=Sponsor` 這類日常敘述。"""
    if len(value) < _MIN_WEAK_LEN:
        return False
    classes = sum((any(c.islower() for c in value), any(c.isupper() for c in value),
                   any(c.isdigit() for c in value), any(not c.isalnum() for c in value)))
    if len(value) >= 16 and classes >= 2:
        return True
    return classes >= 2 and any(c.isdigit() for c in value)


def _mk(name, lineno, rule, keyword, value, line) -> Finding:
    masked = _mask(value)
    excerpt = line.strip().replace(value, masked)
    if len(excerpt) > 160:
        excerpt = excerpt[:157] + "…"
    return Finding(name, lineno, rule, keyword, digest_of(value), masked, excerpt)


def scan_text(name: str, text: str) -> list[Finding]:
    """一份文字 → 疑似明碼憑證清單(**純函式**;無 IO、可餵真輸入)。"""
    out: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for label, rx in _KNOWN_RE:
            for m in rx.finditer(line):
                out.append(_mk(name, lineno, "known_prefix", label, m.group(0), line))
        for m in _URL_RE.finditer(line):
            if not is_placeholder(m.group("val")):
                out.append(_mk(name, lineno, "url_credential", m.group("scheme"),
                               m.group("val"), line))
        for m in _STRONG_RE.finditer(line):
            raw = m.group("val")
            inner = _unwrap(raw)
            if len(inner) >= _MIN_STRONG_LEN and not is_placeholder(raw):
                out.append(_mk(name, lineno, "kv_strong", m.group("kw").lower(), inner, line))
        for m in _WEAK_RE.finditer(line):
            raw = m.group("val")
            inner = _unwrap(raw)
            if not is_placeholder(raw) and looks_random(inner):
                out.append(_mk(name, lineno, "kv_weak", m.group("kw").lower(), inner, line))
        for m in _LOGIN_RE.finditer(line):
            raw = m.group("val")
            inner = _unwrap(raw)
            if len(inner) >= _MIN_STRONG_LEN and not is_placeholder(raw):
                out.append(_mk(name, lineno, "login_pair", _unwrap(m.group("user")), inner,
                               line))
    return out


def scan_files(files) -> tuple[list[Finding], set[str]]:
    """`{檔名: Path}` → (findings, **實掃檔名集**)。實掃集是地板與「掃描集=寫入集」之唯一素材。"""
    findings, seen = [], set()
    for name, path in sorted(dict(files).items()):
        findings.extend(scan_text(name, Path(path).read_text(encoding="utf-8",
                                                             errors="replace")))
        seen.add(name)
    return findings, seen


# ── 豁免清單(誤報之唯一出路;每列即一次人為判定之留痕) ────────────────────────────
def default_allowlist_path(repo_root) -> Path:
    """豁免清單之單一住所(#12)。呼叫端傳 repo 根,避免各處各自推導。"""
    return Path(repo_root) / ALLOWLIST_REL


def parse_allowlist(text: str) -> tuple[dict, list[str]]:
    """豁免清單文字 → ({(檔名,規則,指紋): 理由}, 格式錯誤列)(純函式)。

    六欄缺一即列入錯誤——**壞掉的豁免不得靜默生效**(fail-closed)。
    """
    rows, errors = {}, []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cols = [c.strip() for c in raw.split("\t")]
        if len(cols) != len(ALLOWLIST_COLS) or not all(cols):
            errors.append(f"第 {lineno} 行:須為 {len(ALLOWLIST_COLS)} 個 TAB 分隔非空欄位"
                          f"({'／'.join(ALLOWLIST_COLS)}),實得 {len(cols)} 欄")
            continue
        rows[(cols[0], cols[1], cols[2])] = f"{cols[3]}@{cols[4]}:{cols[5]}"
    return rows, errors


def load_allowlist(path) -> tuple[dict, list[str]]:
    """讀豁免清單。**檔案不存在=空清單**(缺檔只會更嚴,不是放行),讀不到才算錯誤。"""
    p = Path(path)
    if not p.exists():
        return {}, []
    try:
        return parse_allowlist(p.read_text(encoding="utf-8"))
    except OSError as exc:
        return {}, [f"豁免清單讀取失敗({p}):{exc}"]


def apply_allowlist(findings, allow) -> tuple[list[Finding], list[tuple[Finding, str]]]:
    """→ (未豁免之殘留, [(已豁免 finding, 留痕)])(純函式)。"""
    remaining, waived = [], []
    for f in findings:
        if f.key in allow:
            waived.append((f, allow[f.key]))
        else:
            remaining.append(f)
    return remaining, waived


def verdict(findings, waived, scanned, allow_errors=(), floor=1) -> tuple[int, list[str]]:
    """(殘留, 已豁免, 實掃檔名集, 豁免格式錯誤) → (rc, 訊息列)(純函式;呼叫端負責列印)。

    rc≠0 之三個獨立理由:① 有殘留疑似明碼 ② 豁免清單格式壞掉 ③ 實掃檔數未達地板。
    """
    msgs, rc = [], 0
    frc, fmsgs = scan_floor.verdict("記憶密碼掃描",
                                    [scan_floor.FloorCheck("掃描 md 檔", len(set(scanned)),
                                                           floor)])
    msgs.extend(fmsgs)
    rc |= frc
    for e in allow_errors:
        msgs.append(f"✗ 豁免清單格式錯誤(fail-closed,視同無豁免):{e}")
        rc = 1
    for f, note in waived:
        msgs.append(f"⚠ 已豁免:{f.name}:{f.line} [{f.rule}/{f.keyword}] "
                    f"{f.masked} sha={f.digest} ← {note}")
    if findings:
        rc = 1
        msgs.append(f"✗ **偵測到 {len(findings)} 處疑似明碼憑證——export 中止**"
                    f"(記憶檔會被 commit+push 到 public repo,push 後不可逆):")
        for f in findings:
            msgs.append(f"  · {f.name}:{f.line} [{f.rule}/{f.keyword}] {f.masked} "
                        f"sha={f.digest}")
            msgs.append(f"      {f.excerpt}")
        msgs.append("  處置(擇一):")
        msgs.append("    (a) 改記憶檔:明碼換成引用寫法,如 ⟨見 .env AUGUR_ADMIN_PASSWORD⟩;")
        msgs.append(f"    (b) 確係誤報 → 於 {ALLOWLIST_REL} 加一列留痕(人簽,AI 不代填):")
        msgs.append(f"        {'<TAB>'.join(ALLOWLIST_COLS)}")
        for f in findings:
            # 核准者/日期/理由留空白佔位——**人簽欄不代填**,由核准的人自己寫上
            msgs.append(f"        {f.name}\t{f.rule}\t{f.digest}\t<核准者>\t<YYYY-MM-DD>\t<理由>")
    elif rc == 0:
        msgs.append(f"✓ 密碼掃描:{len(set(scanned))} 檔、0 處疑似明碼憑證"
                    f"({len(waived)} 處經留痕豁免)。")
    return rc, msgs


def scan_dir(directory, allowlist_path=None, floor=1) -> tuple[int, list[str]]:
    """掃一個目錄之 `*.md`(薄 IO 包裝)→ (rc, 訊息列)。"""
    d = Path(directory)
    files = {p.name: p for p in sorted(d.glob(SCAN_GLOB))} if d.is_dir() else {}
    findings, seen = scan_files(files)
    allow, errors = load_allowlist(allowlist_path) if allowlist_path else ({}, [])
    remaining, waived = apply_allowlist(findings, allow)
    return verdict(remaining, waived, seen, errors, floor)


# ── 自測(fixture 驅動:真陰性逐字取自 handoff_memory/ 真檔;真陽性為**合成值**之真形狀) ──
# 真陽性之敏感字面一律運行期串接組出——本檔原始碼不含連續之 token 字面,repo 級 grep 不受污染。
_FAKE_PW = "Tt@i" + "-2026" + "#live"
_FAKE_GHP = "ghp_" + "A1b2C3d4E5f6G7h8I9j0" + "K1l2M3n4O5p6"
_FAKE_JWT = "eyJ" + "hbGciOiJIUzI1NiJ9." + "eyJ1c2VyX2lkIjoiZGVtbyJ9." + "S1gnatur3xxxxxxxxxx"
_FAKE_HEX32 = "1a2b3c4d5e6f7a8b" + "9c0d1e2f3a4b5c6d"
# 真語料原文含 RBAC 字面,連續寫出會被 #8 隔離 AST 閘判為「字串拼 SQL 旁路」(2026-08-03 首跑實遇)
_AU = "app" + "_user"

# 真陰性:逐字取自 handoff_memory/ 之真檔(2026-08-03 親抄;裸關鍵字命中但皆非明碼)
_REAL_NEG = [
    ("finmind-data-source.md",
     "description: FinMind 資料源全貌——augur token=Sponsor 6000/hr、2026-06-24 到期、"
     "/datalist 維度 id 來源;完整研究見 report"),
    ("ttai-integration-and-platform.md",
     f"- 登入:`admin` / `⟨見 .env AUGUR_ADMIN_PASSWORD⟩`(前後台同組;我重設 {_AU} 密碼=同值;"
     "admin 後台亦可帳號留空走 env 後門)。`.env` 加 AUGUR_INTERNAL_SECRET/"
     "AUGUR_ADMIN_PASSWORD/OLLAMA_TIMEOUT=1800(不進 git)。"),
    ("ttai-integration-and-platform.md",
     "端到端實測:前台 8090 登入(admin/`⟨見 .env AUGUR_ADMIN_PASSWORD⟩`、**表單密碼欄名=`pw` "
     "非 password**)→ MBB → 「知識庫中無此內容」。"),
    ("cross-machine-handoff.md",
     "- `.env`(**須手動重建**,鍵:`DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`、"
     "`FINMIND_TOKEN`、`FRED_API_KEY`、`GITHUB_TOKEN`、`AUGUR_ADMIN_PASSWORD`;**值不入記憶**)。"),
    ("augur-data-layer.md",
     "① `TaiwanStockDividend` **PK=stock_id 單欄塌列**(碼已修 require_keys=date、待 token 重建;"
     "現未入生產特徵不影響 alpha)"),
    ("MEMORY.md",
     "- [記憶 export 密碼掃描](memory-export-secret-scan.md) — sync_memory export 全量推 public "
     "repo;記憶不存明碼憑證、commit/push 前必掃密碼(2026-07-13 差點洩漏 ttai admin 密碼)"),
    ("git_identity_in_env.md",
     "但 .env 同檔含真正機密(FINMIND_TOKEN / FRED_API_KEY / DB_PASSWORD / GITHUB_TOKEN / "
     "GEMINI_API_KEY...)——**只取身分、絕不外洩或 commit 其餘 keys**。"),
    ("memory-export-secret-scan.md",
     "2. **export→commit→push 前必掃密碼**:`git diff --cached` 的 handoff_memory 逐檔掃 "
     "`password|token|secret|登入:.*/ \\`...\\``;抓到明碼即從 commit 移除或改引用,再 push。"),
    ("slow-but-precise.md", "- 與 #28 省 usage 二分不衝突:省的是 Claude token(執行層)。"),
]

# 真陽性:真形狀 + 合成值(第一列即 2026-07-13 實犯之行形,只把明碼換成假值)
_REAL_POS = [
    ("ttai.md", f"- 登入:`admin` / `{_FAKE_PW}`(前後台同組;我重設 {_AU} 密碼=同值)。",
     "login_pair"),
    ("ttai.md", f"前台 8090 登入(admin/`{_FAKE_PW}`、表單密碼欄名=`pw`)", "login_pair"),
    ("env.md", f"AUGUR_ADMIN_PASSWORD={_FAKE_PW}", "kv_strong"),
    ("env.md", f"- 後台密碼: {_FAKE_PW}(前後台同組)", "kv_strong"),
    ("env.md", f"db_password = '{_FAKE_PW}'", "kv_strong"),
    ("tok.md", f"FINMIND_TOKEN={_FAKE_JWT}", "known_prefix"),
    ("tok.md", f"export GITHUB_TOKEN={_FAKE_GHP}", "known_prefix"),
    ("tok.md", f"FRED api_key={_FAKE_HEX32}", "kv_weak"),
    ("db.md", f"psql postgresql://augur:{_FAKE_PW}@localhost:5432/augur", "url_credential"),
]


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # ── 真陰性:逐字真語料,一處都不許紅(閘若天天假紅,必被繞過 ⇒ 等同不存在) ──
    for fname, line in _REAL_NEG:
        got = scan_text(fname, line)
        chk(f"真陰性[{fname}]:{line[:26]}… ⇒ 0 命中",
            got == [], )
        if got:
            print(f"      誤報:{[(g.rule, g.keyword, g.masked) for g in got]}")

    # ── 真陽性:每列至少一筆,且**規則對得上**(只數數量會讓規則錯配矇混) ──
    for fname, line, want_rule in _REAL_POS:
        got = scan_text(fname, line)
        chk(f"真陽性[{want_rule}]:{line[:34]}… ⇒ 被抓",
            bool(got) and any(g.rule == want_rule for g in got))

    # ── 值不外洩:Finding 之任一欄位皆不得含明碼(本結構會被列印進 log) ──
    f_one = scan_text("x.md", f"password={_FAKE_PW}")[0]
    chk("Finding 不帶明碼(name/rule/masked/excerpt/digest 全無原值)",
        all(_FAKE_PW not in str(v) for v in (f_one.name, f_one.rule, f_one.keyword,
                                             f_one.masked, f_one.excerpt, f_one.digest)))
    chk("excerpt 仍保留行內其他文字(供人定位)", "password" in f_one.excerpt)
    chk("指紋可重現且不可逆(同值同指紋、長度 12)",
        f_one.digest == digest_of(_FAKE_PW) and len(f_one.digest) == 12)

    # ── 純函式邊界(餵真值域,非字面斷言) ──
    chk("佔位符:⟨見 .env X⟩", is_placeholder("`⟨見 .env AUGUR_ADMIN_PASSWORD⟩`"))
    chk("佔位符:全大寫變數名", is_placeholder("AUGUR_ADMIN_PASSWORD"))
    chk("佔位符:${VAR}", is_placeholder("${AUGUR_ADMIN_PASSWORD}"))
    chk("佔位符:含中文之敘述(同值)", is_placeholder("同值"))
    chk("佔位符:純數字(1800)", is_placeholder("1800"))
    chk("非佔位符:合成明碼", not is_placeholder(f"`{_FAKE_PW}`"))
    chk("looks_random:Sponsor 不像亂數(擋 token=Sponsor 誤報)", not looks_random("Sponsor"))
    chk("looks_random:32 碼 hex 像亂數", looks_random(_FAKE_HEX32))
    chk("looks_random:短字串不算(<8)", not looks_random("a1b2c3"))
    chk("_unwrap:多層包覆(反引號外、角括號內)", _unwrap("`⟨abc⟩`") == "abc")

    # ── 突變驗紅 A:偵測 regex 弱化為恆不匹配 ⇒ 全部真陽性必須消失 ──
    _saved = {k: globals()[k] for k in ("_STRONG_RE", "_WEAK_RE", "_LOGIN_RE", "_URL_RE",
                                        "_KNOWN_RE")}
    _dead = re.compile(r"(?!x)x")
    globals().update(_STRONG_RE=_dead, _WEAK_RE=_dead, _LOGIN_RE=_dead, _URL_RE=_dead,
                     _KNOWN_RE=(("dead", _dead),))
    try:
        gone = all(scan_text(n, ln) == [] for n, ln, _ in _REAL_POS)
    finally:
        globals().update(_saved)
    chk("突變:五條 regex 弱化後真陽性全數不再被抓(證明上列真陽性斷言非恆真)", gone)

    # ── 突變驗紅 B:把佔位符判定改成恆真(=「一律當誤報放行」) ⇒ 真陽性必須失守 ──
    _sp = globals()["is_placeholder"]
    globals()["is_placeholder"] = lambda raw: True
    try:
        leaked = [ln for n, ln, r in _REAL_POS
                  if r != "known_prefix" and scan_text(n, ln) == []]
    finally:
        globals()["is_placeholder"] = _sp
    chk("突變:佔位符判定恆真時 kv/login/url 全部失守(證明該判定是承重牆)",
        len(leaked) == len([1 for _n, _l, r in _REAL_POS if r != "known_prefix"]))

    # ── 豁免清單:格式紅綠雙向＋鍵不含行號 ──
    good = "\t".join(("x.md", "kv_strong", f_one.digest, "hugo", "2026-08-03", "測試留痕"))
    rows, errs = parse_allowlist(f"# 註解\n\n{good}\n")
    chk("豁免:合法列被解析、註解與空行略過", rows == {("x.md", "kv_strong", f_one.digest):
                                                 "hugo@2026-08-03:測試留痕"} and not errs)
    chk("豁免:欄位不足 ⇒ 格式錯誤(不靜默生效)",
        parse_allowlist("x.md\tkv_strong\tdeadbeef\n")[1] and
        not parse_allowlist("x.md\tkv_strong\tdeadbeef\n")[0])
    chk("豁免:欄位空白 ⇒ 格式錯誤(核准者/理由不得留空)",
        bool(parse_allowlist("\t".join(("x.md", "kv_strong", "d", "", "2026-08-03", "r"))
                             + "\n")[1]))
    _rem, _wv = apply_allowlist([f_one], rows)
    chk("豁免:命中鍵 ⇒ 移出殘留、進留痕", _rem == [] and len(_wv) == 1)
    other_line = scan_text("x.md", f"# 說明\npassword={_FAKE_PW}")[0]
    chk("豁免鍵不含行號(同檔同值換行號仍豁免)",
        other_line.line != f_one.line and apply_allowlist([other_line], rows)[0] == [])
    _rem2, _ = apply_allowlist([Finding("y.md", 1, "kv_strong", "password", f_one.digest,
                                        "m", "e")], rows)
    chk("豁免不跨檔(換檔名即不再豁免)", len(_rem2) == 1)

    # ── verdict:紅綠雙向＋地板(掃 0 檔不得判綠——本模組要消滅之假綠) ──
    chk("verdict:有殘留 ⇒ 紅", verdict([f_one], [], {"x.md"})[0] == 1)
    chk("verdict:零殘留＋有實掃 ⇒ 綠", verdict([], [], {"x.md"})[0] == 0)
    chk("verdict:掃 0 檔 ⇒ 紅(「沒掃到」不得與「掃過都乾淨」同判)",
        verdict([], [], set())[0] == 1)
    chk("verdict:豁免清單格式壞掉 ⇒ 紅", verdict([], [], {"x.md"}, ["壞列"])[0] == 1)
    _rc_w, _msgs_w = verdict([], [(f_one, "hugo@2026-08-03:測試留痕")], {"x.md"})
    chk("verdict:豁免亦列印留痕(不得靜默通過)",
        _rc_w == 0 and any("已豁免" in m and f_one.digest in m for m in _msgs_w))
    _rc_r, _msgs_r = verdict([f_one], [], {"x.md"})
    chk("verdict:紅訊息帶處置指引與可貼上之豁免列骨架",
        any(ALLOWLIST_REL in m for m in _msgs_r) and
        any(m.strip().startswith(f_one.name) and f_one.digest in m for m in _msgs_r))
    chk("verdict:紅訊息不得含明碼", all(_FAKE_PW not in m for m in _msgs_r))

    # ── 真語料端到端:repo 之 handoff_memory/ 現況必須 0 殘留(有則此閘上不了線) ──
    root = Path(__file__).resolve().parents[3]
    snap = root / "handoff_memory"
    if snap.is_dir():
        _rc_live, _msgs_live = scan_dir(snap, default_allowlist_path(root), floor=10)
        n_md = len(list(snap.glob(SCAN_GLOB)))
        chk(f"真語料:handoff_memory/ {n_md} 檔實掃 ⇒ 0 殘留(rc={_rc_live})", _rc_live == 0)
        if _rc_live:
            for m in _msgs_live:
                print(f"      {m}")
        chk("真語料:地板高於實檔數 ⇒ 紅(掃描範圍消失之絆線)",
            scan_dir(snap, None, floor=n_md + 1)[0] == 1)
    else:
        print(f"  ⚠ SKIP 真語料端到端:{snap} 不存在(非 FAIL——本模組不依賴該目錄)")

    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="明碼憑證偵測(記憶 export 之 fail-closed 閘)")
    ap.add_argument("--scan-dir", metavar="DIR", help="掃該目錄之 *.md(唯讀)")
    ap.add_argument("--selftest", action="store_true", help="純紅綠自測(免 DB 免 API)")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.scan_dir:
        root = Path(__file__).resolve().parents[3]
        rc, msgs = scan_dir(a.scan_dir, default_allowlist_path(root))
        for m in msgs:
            print(m, file=sys.stderr if rc else sys.stdout)
        return rc
    print(__doc__.split("執行指令矩陣")[0].strip()[:600])
    print("\n公開入口(唯讀):scan_text(name, text) / scan_files({name: path}) / scan_dir(dir) /")
    print("              is_placeholder(raw) / looks_random(v) / digest_of(v) /")
    print("              parse_allowlist(text) / load_allowlist(path) /")
    print("              apply_allowlist(findings, allow) / verdict(...)")
    print(f"豁免清單:{ALLOWLIST_REL}(六欄留痕;缺檔=無豁免、格式壞=判紅)")
    print("自測:python -m augur.audit.plaintext_credential --selftest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
