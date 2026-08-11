"""知識文獻引文型別（STRUCT：自 philosophy.retrieval 抽出 ItemCitation）。

🎯 items 側逐字可溯源引用資料類；philosophy.retrieval 再匯出保 BC。

執行指令矩陣:
  python -m augur.knowledge.citations --selftest
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ItemCitation:
    """一筆逐字可溯源的知識文獻句引用(items 側)。"""

    sent_id: int
    itext_id: int
    item_id: int
    item_title: str
    domain: str
    entity_type: str
    char_start: int  # 相對 item_text.content 之定位(verify_verbatim_item 他證基準)
    char_end: int
    source_url: str
    license: str
    text: str  # 逐字原句(== item_text.content[char_start:char_end])
    score: float  # via='exact':查詢詞命中比; via='ann':cosine
    via: str  # 'exact' | 'ann' | 'readout' …


def _selftest() -> bool:
    c = ItemCitation(
        1, 1, 1, "t", "d", "e", 0, 1, "u", "l", "x", 0.5, "exact"
    )
    ok = c.text == "x" and c.via == "exact"
    print(("✓" if ok else "✗"), "ItemCitation construct")
    return ok


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(0 if _selftest() else 1)
    print(__doc__)
