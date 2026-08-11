"""KH8-DISCRIM · M3 答池闸（pool-gate）——權重 ≠ 可答。

🎯 白话：影子／薄项 weight 将来可能入主表让 disc 变绿，但 retrieve／readout／
   AUTO-LIFT **不得**只因有 weight 列就把无全文标题件当答案材料。本模组是契约 SSOT；
   热路径既有 JOIN item_text／has_text 守卫在此落成可测断言。

守 M3-adopt · merge plan §2.2 · E-keep · no-merge-in-this-module · FZ-keep。

執行指令矩陣:
  python -m augur.knowledge.pool_gate --selftest
  python -m augur.knowledge.pool_gate
"""
from __future__ import annotations

from typing import Any, Mapping

# 契约字面（探针／审计可贴）
CONTRACT = (
    "weight_hit≠answer_pool; answer_pool requires has_text "
    "(or CLEAN path that JOINs knowledge_item_text); "
    "AUTO-LIFT activate requires has_text; no-merge-by-this-gate"
)

RISK_TITLE_ONLY = "title_only_no_fulltext"


def answer_pool_eligible(
    *,
    has_text: bool,
    has_weight: bool = False,
    risk_flags: Any = None,
) -> bool:
    """答池资格：只要全文（或等價有文路徑）。weight／影标誌永不单独放行。

    has_weight 仅诊断；True 也不放宽。title_only risk_flags 一律 False。
    """
    if _has_title_only_flag(risk_flags):
        return False
    if not has_text:
        return False
    _ = has_weight  # 明示：有權亦不影響
    return True


def weight_alone_insufficient(*, has_weight: bool, has_text: bool) -> bool:
    """证伪向：有 weight、无 text → 不足进答池。"""
    return bool(has_weight) and not bool(has_text)


def activate_source_eligible(*, has_text: bool, source_key: str | None) -> bool:
    """AUTO-LIFT 机械 activate 同口径：source_key ∧ has_text。"""
    return bool(source_key) and bool(has_text)


def kh8_evaluate_requires_text(snap: Mapping[str, Any]) -> bool:
    """evaluate_item_evidence 入口须具备 has_text（无则 fail，不写当 pass）。"""
    return bool(snap.get("has_text"))


def _has_title_only_flag(risk_flags: Any) -> bool:
    if risk_flags is None:
        return False
    if isinstance(risk_flags, str):
        return RISK_TITLE_ONLY in risk_flags
    if isinstance(risk_flags, (list, tuple, set)):
        return RISK_TITLE_ONLY in {str(x) for x in risk_flags}
    if isinstance(risk_flags, dict):
        return RISK_TITLE_ONLY in {str(k) for k in risk_flags} or RISK_TITLE_ONLY in {
            str(v) for v in risk_flags.values()
        }
    return False


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("CONTRACT mentions weight≠pool", "weight_hit≠answer_pool" in CONTRACT)
    chk("text-only eligible", answer_pool_eligible(has_text=True) is True)
    chk("no text → False", answer_pool_eligible(has_text=False) is False)
    chk(
        "weight+no text → False",
        answer_pool_eligible(has_text=False, has_weight=True) is False,
    )
    chk(
        "weight+text → True",
        answer_pool_eligible(has_text=True, has_weight=True) is True,
    )
    chk(
        "title_only flag blocks even with text marker misuse",
        answer_pool_eligible(
            has_text=True,
            has_weight=True,
            risk_flags=[RISK_TITLE_ONLY],
        )
        is False,
    )
    chk(
        "weight_alone_insufficient",
        weight_alone_insufficient(has_weight=True, has_text=False) is True,
    )
    chk(
        "weight+text not alone-insufficient",
        weight_alone_insufficient(has_weight=True, has_text=True) is False,
    )
    chk(
        "activate needs text+key",
        activate_source_eligible(has_text=True, source_key="s1") is True,
    )
    chk(
        "activate no text",
        activate_source_eligible(has_text=False, source_key="s1") is False,
    )
    chk(
        "activate no key",
        activate_source_eligible(has_text=True, source_key=None) is False,
    )
    chk(
        "kh8 requires text",
        kh8_evaluate_requires_text({"has_text": True}) is True
        and kh8_evaluate_requires_text({"has_text": False}) is False,
    )
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("CONTRACT:", CONTRACT)
    print(
        "公開: answer_pool_eligible / weight_alone_insufficient / "
        "activate_source_eligible / kh8_evaluate_requires_text"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
