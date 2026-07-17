"""共用資料模型：Finding / Severity / LintResult。"""
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

    def format(self) -> str:
        loc = f" @ {self.location}" if self.location else ""
        basis = f" [{self.mc_basis}]" if self.mc_basis else ""
        return f"  {self.severity.value.upper():7} {self.rule}: {self.message}{loc}{basis}"


@dataclass
class LintResult:
    target: str
    findings: list = field(default_factory=list)

    def add(self, rule, severity, message, mc_basis="", location=""):
        self.findings.append(Finding(rule, severity, message, mc_basis, location))

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
