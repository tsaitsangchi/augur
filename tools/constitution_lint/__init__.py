"""constitution_lint — Augur §8.3 機器稽核 CI 之雙 linter（骨架）。

依《Augur 憲章展開總綱》§5.4、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39–45`。

兩支 linter 為「規格生效」與「code 合憲」兩軌之橋：
- compliance_lint：管**規格生效**——查 Layer 1–7 規格之 Constitutional Compliance Statement
  是否依 WM.40（front-matter 閉集）/WM.41（七節）/WM.42（緊張四欄）/WM.43（DEFER 雙向）/
  WM.44（形式充分性）作成；接受 minor 版落差不誤紅。error 級＝規格不生效力。
- audit_lint：管 **code 合憲**——引用鏈雙合法終點（K→Evidence→Observation ∪ 明示宣告之假設，
  P4.E6）、Action→Identity 六元組、Knowledge 五元組、Confidence 存在性；以 AUD-01/03/10/11 為
  failing check 種子。語義嚴格度隨 L3（Identity）/L4（Confidence）充任而收緊（版本化 linter）。

**治權自動化止於「判定與阻擋」，不及於「執行變更」**——apply 與合併永遠保留給人類（P5.W2）。
本工具為骨架（skeleton）：框架與 compliance_lint 核心完備、對 AUGUR-WM v1.0 自檢綠；audit_lint 為
可示範之種子規則框架，完整規則集與 WM.44 嚴格枚舉隨後續階段強化（總綱階段 1→9）。
"""
from .model import Finding, Severity, LintResult

__all__ = ["Finding", "Severity", "LintResult"]
__version__ = "0.1.0-skeleton"
