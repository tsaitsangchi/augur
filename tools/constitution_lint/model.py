"""共用資料模型：Finding / Severity / LintResult。

執行指令矩陣：
  python -m tools.constitution_lint.model              # 印用途（唯讀、免外部依賴）
  python -m tools.constitution_lint.model --selftest    # Finding/LintResult 建構+report 紅綠自測（零外部依賴）
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional


class Severity(enum.Enum):
    """三級。error＝阻斷（規格不生效力 / code 違憲）；warning＝應處理；info＝提示（如 minor 版落差）。"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Finding:
    rule: str            # 規則代號（如 WM.40、AUD-03）
    severity: Severity
    message: str
    mc_basis: str = ""   # 憲章/規格依據（如 AUGUR-MC v1.3 §8.3）
    location: str = ""   # 檔案:行 或 章節
    source: str = ""     # 標籤權威來源（`clause["source"]`：`MC` 或 `AUGUR-XX vY`）；
                         # **空字串＝未歸類**，非「MC」。僅於 finding 確由某一已解析條款之
                         # 原文比對而生時填入；代號無法解析、區段缺位等**發生於 clause 解析
                         # 之前**者本無 source 可歸，一律留空並於統計中獨立列出。
                         # 「未歸類併入 MC 側」即為捏造（HANDOFF：MC 110／上層 89／未歸類 1）。
    kind: str = ""       # error 型態之**穩定機器標籤**（於 finding 生成處指定，非事後以訊息字串
                         # 反推）。分型計數之權威即此欄；以 grep 訊息計數者一律非權威。
    code: str = ""       # 受判之條款代號（如 `P4.E1`）；僅標籤判定類 finding 填之。
    label: str = ""      # 規格所載之標籤原字串（**未經正規化**，即 Annex TR 表列所書者）。
                         # code／label 二欄之用途：跨規格之「逐字複製誤標」統計須以**結構化
                         # 欄位**為據——README 該節自陳「以程式導出，非手數」，惟前版實為手數
                         # 且錯（記 30，實為 31，且其自身表格三列相加即得 31）。以 grep 訊息
                         # 反推者一律非權威：訊息措辭一改，統計即靜默失準。

    def format(self) -> str:
        loc = f" @ {self.location}" if self.location else ""
        basis = f" [{self.mc_basis}]" if self.mc_basis else ""
        return f"  {self.severity.value.upper():7} {self.rule}: {self.message}{loc}{basis}"


@dataclass
class LintResult:
    target: str
    findings: list = field(default_factory=list)
    meta: dict = field(default_factory=dict)   # 非判定性附帶統計（如 label_compared 逐來源比對筆數）

    def add(self, rule, severity, message, mc_basis="", location="", source="", kind="",
            code="", label=""):
        self.findings.append(Finding(rule, severity, message, mc_basis, location, source, kind,
                                     code, label))

    @property
    def errors(self):
        return [f for f in self.findings if f.severity is Severity.ERROR]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity is Severity.WARNING]

    @property
    def passed(self) -> bool:
        """通過＝零 error（warning/info 不阻斷）。"""
        return not self.errors

    def report(self) -> str:
        lines = [f"── {self.target}"]
        if not self.findings:
            lines.append("  ✓ 無發現")
        for f in sorted(self.findings, key=lambda x: [Severity.ERROR, Severity.WARNING, Severity.INFO].index(x.severity)):
            lines.append(f.format())
        n_e, n_w = len(self.errors), len(self.warnings)
        verdict = "✅ PASS" if self.passed else "❌ FAIL"
        lines.append(f"  → {verdict}（error {n_e} / warning {n_w} / info {len(self.findings) - n_e - n_w}）")
        return "\n".join(lines)


def _selftest() -> int:
    r = LintResult(target="selftest")
    ok = r.passed and "無發現" in r.report()
    r.add("T.01", Severity.ERROR, "測試錯誤")
    ok = ok and not r.passed and len(r.errors) == 1 and len(r.warnings) == 0
    r.add("T.02", Severity.WARNING, "測試警告")
    ok = ok and len(r.warnings) == 1 and "FAIL" in r.report()
    print("constitution_lint.model selftest:" + (" OK" if ok else " FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
