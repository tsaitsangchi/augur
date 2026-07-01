"""P5 PredictionPayload — 量化本體 → 顧問前端的唯一唯讀資料通道。

🎯 as-of 快照凍結的真實預測(選股 + score + 驗證標籤)。frozen dataclass = 顧問**不可改一個數字**;
   所有數字帶 source_ref、trace 回真實模型輸出(#1);validation 帶誠實標籤(#15)。
守 #1(數字 trace 真實模型)· #15(validation 誠實標籤)· 憲章 v1.17.0(顧問對此唯讀、零寫回)。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class StockPick:
    symbol: str
    rank: int
    score: float
    source_ref: str          # trace 回真實模型輸出(如 eval/portfolio.py 之某 as-of run)


@dataclass(frozen=True)
class PredictionPayload:
    as_of: str               # as-of 日期(快照凍結、防洩漏 #8)
    horizon: int             # 預測期(如 60 日)
    model: str               # 產生預測的真實模型(如 "F3 as-of Ridge")
    picks: tuple             # (StockPick, ...) 橫斷面 top-N
    validation: dict         # {rank_ic, sharpe, note, ...} 誠實驗證標籤(#15)

    def numbers(self):
        """回 payload 內所有真實數字(供 guard:顧問輸出的預測數字必須 ∈ 此集合、不得編造)。"""
        ns = set()
        for p in self.picks:
            ns.add(round(p.score, 4))
            ns.add(float(p.rank))
        for v in self.validation.values():
            if isinstance(v, (int, float)):
                ns.add(round(float(v), 4))
        return ns


def example_payload():
    """示範 payload(供 P5 架構測試;真實資料由量化本體 as-of 預測填入,屬後續整合)。"""
    return PredictionPayload(
        as_of="2026-05-31", horizon=60, model="F3 as-of Ridge",
        picks=(
            StockPick("2330", 1, 0.87, "eval/portfolio.py:asof_run"),
            StockPick("2317", 2, 0.72, "eval/portfolio.py:asof_run"),
            StockPick("2454", 3, 0.65, "eval/portfolio.py:asof_run"),
        ),
        validation={"rank_ic": 0.1418, "sharpe": 1.26,
                    "note": "alpha 僅 long 側、long-short 無效;Sharpe 為扣成本後 purged walk-forward"},
    )
