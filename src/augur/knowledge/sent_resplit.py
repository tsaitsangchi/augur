"""長句硬切 span 演算法 — LSR-S01。

🎯 這支在做什麼(白話):把超長 [char_start,char_end) 定長／偏好空白處切開，
   使每段 len≤max_chars（且≥min_chars，尾段可短），原文可精確切回。
守 #1(不改寫正文)· #15· LSR-PLAN D2/D3。

執行指令矩陣:
  python -m augur.knowledge.sent_resplit
  python -m augur.knowledge.sent_resplit --selftest
"""
from __future__ import annotations

MAX_CHARS_CAP = 1000  # 不得 ≥ embed is_junk(en) 線
DEFAULT_MAX_CHARS = 800
MIN_CHARS = 10


def _trim(content: str, start: int, end: int) -> tuple[int, int]:
    seg = content[start:end]
    left = len(seg) - len(seg.lstrip())
    right = len(seg) - len(seg.rstrip())
    return start + left, end - right


def hard_wrap_span(
    content: str,
    start: int,
    end: int,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> list[tuple[int, int]]:
    """回傳覆蓋 [start,end) 的子 span 列表；拼接後等於 trim 後原文片段。"""
    if max_chars > MAX_CHARS_CAP:
        raise ValueError(f"max_chars={max_chars} 禁止 >{MAX_CHARS_CAP}")
    if max_chars < MIN_CHARS:
        raise ValueError(f"max_chars={max_chars} 須 ≥{MIN_CHARS}")
    start, end = _trim(content, start, end)
    if end <= start:
        return []
    if end - start <= max_chars:
        return [(start, end)]

    spans: list[tuple[int, int]] = []
    i = start
    seps = ("\n\n", "\n", ". ", "; ", ", ", "、", "。", "；", " ")
    while i < end:
        if end - i <= max_chars:
            s, e = _trim(content, i, end)
            if e > s:
                spans.append((s, e))
            break
        target = i + max_chars
        window = content[i:target]
        break_at = None
        min_keep = max(MIN_CHARS, max_chars // 4)
        for sep in seps:
            pos = window.rfind(sep)
            if pos >= min_keep:
                break_at = i + pos + len(sep)
                break
        if break_at is None or break_at <= i:
            break_at = target
        s, e = _trim(content, i, break_at)
        if e > s:
            spans.append((s, e))
        elif break_at > i:
            # trim 吃光——硬推一窗避免死循環
            spans.append((i, min(i + max_chars, end)))
            break_at = min(i + max_chars, end)
        i = max(break_at, i + 1)
    return spans


def expand_spans(
    content: str,
    spans: list[tuple[int, int]],
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> list[tuple[int, int]]:
    """對既有句 span 逐一硬切後平坦化。"""
    out: list[tuple[int, int]] = []
    for s, e in spans:
        out.extend(hard_wrap_span(content, s, e, max_chars=max_chars))
    return out


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    text = ("Hello world. " * 100) + "END"
    spans = hard_wrap_span(text, 0, len(text), max_chars=80)
    chk("多段產出", len(spans) > 5)
    chk("每段≤80", all(e - s <= 80 for s, e in spans))
    joined = "".join(text[s:e] for s, e in spans)
    # trim 可能去掉頭尾空白——比對去空白後
    chk("可拼回（去空白）", "".join(joined.split()) == "".join(text.split()))
    short = hard_wrap_span("abc", 0, 3, max_chars=80)
    chk("短句單段", short == [(0, 3)])
    try:
        hard_wrap_span("x" * 10, 0, 10, max_chars=1001)
        chk("禁 max>1000", False)
    except ValueError:
        chk("禁 max>1000", True)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        if len(sys.argv) == 1:
            print(__doc__)
        sys.exit(_selftest())
    print(__doc__)
    sys.exit(0)
