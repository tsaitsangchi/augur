#!/usr/bin/env python
"""台股 TSFM benchmark — 鏡射 arXiv:2606.27100 方法論之在地化驗證(研究讀數、不進預測管線)。

🎯 這支在做什麼(白話):把「Pretrained Time-Series Foundation Models for Financial Return Forecasting」
   (arXiv:2606.27100)的實驗協定搬到台股:市值 top5 流動股(2330/2454/2308/2317/3711)、日 log return、
   **rolling-origin 10 窗×H=20 交易日、context L=512**,模型池=RW(零報酬)+SeasonalNaive(lag-5)基線
   + chronos-bolt-small + Chronos-2 + TimesFM-2.5 + Moirai-2.0-R-small(全本地零 API;TimeGPT=商用
   API 誠實跳過)。指標=MAE、skill=1−MAE/MAE_RW、rMAE vs SN、**Diebold-Mariano(HLN 校正、單尾、
   絕對損失)**+方向命中加測。機率輸出→中位數點預測(論文口徑)。資料 ≤2026-06-30(G1-PIN 對齊、
   已結算段、不追滾動)。**任一模型載入/推論失敗=誠實缺席留痕、不擋其他隊**。

守 #8(僅用 ≤origin 之 context,零前視)· #9/#10(全數字出自本 script 實跑、報告可溯源)· #15(DM 檢定
   非裸比較)· #28(全本地零 usage)· #29a/d。結果寫 reports/tsfm_taiwan_benchmark_<date>.md。

執行指令矩陣:
  python scripts/benchmark_tsfm_taiwan.py                    # 無參數:設計摘要+模型池可用性(唯讀)
  python scripts/benchmark_tsfm_taiwan.py --run              # 全跑(5 股×10 窗×全池;~10-30 分)
  python scripts/benchmark_tsfm_taiwan.py --run --stocks 2330 --windows 2 --models rw sn chronos_bolt  # 最小驗證(#25)
  python scripts/benchmark_tsfm_taiwan.py --selftest         # 指標/DM 純函式紅綠(零 DB 零模型)
"""
import argparse
import math
import sys
from datetime import date

import _bootstrap  # noqa: F401
import numpy as np

from augur.core import db

STOCKS = ["2330", "2454", "2308", "2317", "3711"]   # 市值 top5 @2026-07-16(DB 實查)
ASOF = "2026-06-30"      # G1-PIN 對齊:已結算段、固定標靶
CONTEXT = 512            # 論文 L
H = 20                   # 論文 H(交易日)
N_WIN = 10               # 論文 10 windows
QL = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


# ── 指標/檢定(純函式;selftest 鎖) ─────────────────────────────────────────────
def mae(pred, actual):
    return float(np.mean(np.abs(np.asarray(pred, float) - np.asarray(actual, float))))


def skill_vs(mae_f, mae_base):
    return 1.0 - mae_f / mae_base if mae_base > 0 else float("nan")


def dm_test_hln(e1, e2, h):
    """Diebold-Mariano(絕對損失)+Harvey-Leybourne-Newbold 校正;單尾(模型1 優於 2)。
    e1/e2=兩模型之逐點絕對誤差序列;回 (DM*, p_one_sided)。LRV=Newey-West lag h−1。"""
    d = np.asarray(e1, float) - np.asarray(e2, float)
    n = len(d)
    if n < 2 or np.allclose(d, d[0]):
        return float("nan"), float("nan")
    dbar = d.mean()
    dc = d - dbar
    lrv = float(np.mean(dc * dc))
    for k in range(1, min(h, n)):                      # NW lag=h−1(重疊 h 步預測)
        w = 1.0 - k / h
        lrv += 2.0 * w * float(np.mean(dc[:-k] * dc[k:]))
    lrv = max(lrv, 1e-18)
    dm = dbar / math.sqrt(lrv / n)
    hln = math.sqrt(max((n + 1 - 2 * h + h * (h - 1) / n) / n, 1e-12))   # 論文式
    dm_star = dm * hln
    try:
        from scipy.stats import t as tdist
        p = float(tdist.cdf(dm_star, df=n - 1))        # 單尾:d<0(模型1 誤差小)→p 小=顯著優
    except ImportError:
        p = float("nan")
    return float(dm_star), p


def sign_hit(pred, actual):
    """方向命中率(加測;非論文主指標):sign(pred median return) vs sign(actual)。"""
    p, a = np.asarray(pred, float), np.asarray(actual, float)
    return float(np.mean(np.sign(p) == np.sign(a)))


# ── 資料 ──────────────────────────────────────────────────────────────────────
def load_logret(conn, sid):
    with db.transaction(conn) as cur:
        cur.execute('SELECT close FROM "TaiwanStockPriceAdj" WHERE stock_id=%s AND date<=%s ORDER BY date',
                    (sid, ASOF))
        px = np.array([float(r[0]) for r in cur.fetchall()])
    return np.diff(np.log(px))


def rofe_slices(n_obs):
    """rolling-origin:最後 N_WIN×H 為 eval 段;回 [(ctx_slice, actual_slice)…](索引皆對 return 序列)。"""
    need = CONTEXT + N_WIN * H
    if n_obs < need:
        raise ValueError(f"序列 {n_obs} < 所需 {need}")
    out = []
    for w in range(N_WIN):
        origin = n_obs - (N_WIN - w) * H
        out.append((slice(origin - CONTEXT, origin), slice(origin, origin + H)))
    return out


# ── 模型 adapters(統一介面:forecast(ctx: np1d, h)->np1d 中位數 return 路徑) ────
class RW:
    key = "rw_zero"
    def forecast(self, ctx, h): return np.zeros(h)


class SeasonalNaive:
    key = "seasonal_naive5"
    def forecast(self, ctx, h):
        wk = ctx[-5:]
        return np.array([wk[i % 5] for i in range(h)])


class ChronosAny:
    def __init__(self, key, model_id):
        self.key, self.model_id, self._p = key, model_id, None
    def _load(self):
        if self._p is None:
            import torch
            from chronos import BaseChronosPipeline
            self._p = BaseChronosPipeline.from_pretrained(
                self.model_id, device_map="cuda" if torch.cuda.is_available() else "cpu",
                torch_dtype="auto")
        return self._p
    def forecast(self, ctx, h):
        import torch
        q, _ = self._load().predict_quantiles([torch.tensor(ctx, dtype=torch.float32)],
                                              prediction_length=h, quantile_levels=QL)
        arr = np.asarray(q[0], float)                              # v1=stacked(n,20,9)取[0]→(20,9);Chronos-2=list[(1,20,9)]取[0]→(1,20,9)
        while arr.ndim > 2:                                        # squeeze 前導 variate 維(實測 2026-07-17:兩代回形不同)
            arr = arr[0]
        return arr[:, QL.index(0.5)]                               # median 路徑(論文口徑)


class TimesFM25:
    key = "timesfm_2.5_200m"
    def __init__(self): self._m = None
    def _load(self):
        if self._m is None:
            import timesfm
            self._m = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
            self._m.compile(timesfm.ForecastConfig(max_context=CONTEXT, max_horizon=128,
                                                   normalize_inputs=True, use_continuous_quantile_head=True))
        return self._m
    def forecast(self, ctx, h):
        _, q = self._load().forecast(horizon=h, inputs=[np.asarray(ctx, float)])
        return np.asarray(q[0, :, 1 + QL.index(0.5)], float)      # q[...,0]=mean、1..9=分位;取 0.5


class Moirai2Small:
    key = "moirai_2.0_R_small"
    def __init__(self): self._pred = None
    def _load(self):
        if self._pred is None:
            from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module
            m = Moirai2Forecast(module=Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small"),
                                prediction_length=H, context_length=CONTEXT, target_dim=1,
                                feat_dynamic_real_dim=0, past_feat_dynamic_real_dim=0)
            self._pred = m.create_predictor(batch_size=8)
        return self._pred
    def forecast(self, ctx, h):
        import pandas as pd
        from gluonts.dataset.common import ListDataset
        ds = ListDataset([{"target": np.asarray(ctx, float),
                           "start": pd.Period("2000-01-03", freq="B")}], freq="B")
        fc = next(iter(self._load().predict(ds)))
        med = fc.quantile(0.5) if hasattr(fc, "quantile") else np.median(fc.samples, axis=0)
        return np.asarray(med, float)[:h]


MODEL_POOL = {
    "rw": RW, "sn": SeasonalNaive,
    "chronos_bolt": lambda: ChronosAny("chronos_bolt_small", "amazon/chronos-bolt-small"),
    "chronos2": lambda: ChronosAny("chronos_2", "amazon/chronos-2"),
    "timesfm": TimesFM25, "moirai2": Moirai2Small,
}


# ── 主流程 ────────────────────────────────────────────────────────────────────
def run(stocks, model_keys, n_win):
    global N_WIN
    N_WIN = n_win
    models, absent = {}, []
    for k in model_keys:
        try:
            models[k] = MODEL_POOL[k]()
        except Exception as e:   # noqa: BLE001
            absent.append((k, f"init:{str(e)[:80]}"))
    errs = {}                                          # (model,stock)→逐點絕對誤差 pooled
    preds = {}
    with db.connect() as conn:
        for sid in stocks:
            r = load_logret(conn, sid)
            slices = rofe_slices(len(r))
            print(f"▶ {sid}: {len(r)} returns、{len(slices)} 窗", flush=True)
            for k, m in list(models.items()):
                e_all, p_all, a_all = [], [], []
                try:
                    for cs, as_ in slices:
                        yhat = np.asarray(m.forecast(r[cs], H), float)[:H]
                        y = r[as_]
                        e_all.extend(np.abs(yhat - y))
                        p_all.extend(yhat)
                        a_all.extend(y)
                    errs[(k, sid)] = np.array(e_all)
                    preds[(k, sid)] = (np.array(p_all), np.array(a_all))
                    print(f"    {getattr(m,'key',k):22s} MAE={np.mean(e_all):.6f}", flush=True)
                except Exception as e:   # noqa: BLE001  誠實缺席:單模型敗不擋全局
                    absent.append((k, f"{sid}:{type(e).__name__}:{str(e)[:80]}"))
                    models.pop(k, None)
                    print(f"    ✗ {k} 誠實缺席:{str(e)[:80]}", flush=True)
    return report(stocks, list(models), errs, preds, absent)


def report(stocks, mkeys, errs, preds, absent):
    lines = [f"# 台股 TSFM benchmark(鏡射 arXiv:2606.27100;{date.today().isoformat()})",
             "", f"- 協定:log return、L={CONTEXT}、H={H}、{N_WIN} 窗 ROFE、資料 ≤{ASOF}(G1-PIN 段)",
             "- 機率輸出→中位數點預測;DM=絕對損失+HLN 校正、單尾 vs RW;p<0.05 顯著",
             f"- 誠實缺席:{absent if absent else '無'}", "",
             "| 股 | 模型 | MAE | skill vs RW | rMAE vs SN | DM* | p(單尾) | 方向命中 |",
             "|---|---|---|---|---|---|---|---|"]
    print("\n══ 結果 ══")
    wins = {}
    for sid in stocks:
        base_rw = errs.get(("rw", sid))
        base_sn = errs.get(("sn", sid))
        best, best_mae = None, 1e9
        for k in mkeys:
            if (k, sid) not in errs:
                continue
            e = errs[(k, sid)]
            m_ = float(np.mean(e))
            sk = skill_vs(m_, float(np.mean(base_rw))) if base_rw is not None else float("nan")
            rm = m_ / float(np.mean(base_sn)) if base_sn is not None else float("nan")
            if k not in ("rw",) and base_rw is not None:
                dm, p = dm_test_hln(e, base_rw, H)
            else:
                dm, p = float("nan"), float("nan")
            ph = sign_hit(*preds[(k, sid)])
            sig = "**" if (p == p and p < 0.05) else ""
            lines.append(f"| {sid} | {k} | {m_:.6f} | {sk:+.4f} | {rm:.4f} | {dm:.2f} | {sig}{p:.3f}{sig} | {ph:.3f} |"
                         if p == p else
                         f"| {sid} | {k} | {m_:.6f} | {sk:+.4f} | {rm:.4f} | — | — | {ph:.3f} |")
            if m_ < best_mae:
                best, best_mae = k, m_
        wins[sid] = best
        lines.append("")
    lines += ["## 每股最佳(MAE)", "", "| 股 | 勝者 |", "|---|---|"]
    for sid, b in wins.items():
        lines.append(f"| {sid} | {b} |")
    out = "reports/tsfm_taiwan_benchmark_" + date.today().strftime("%Y%m%d") + ".md"
    txt = "\n".join(lines) + "\n"
    with open(out, "w") as f:
        f.write(txt)
    print(txt)
    print(f"→ 已寫 {out}")
    return 0


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond; print(f"  {'✓' if cond else '✗FAIL'} {name}")
    chk("mae 基本", abs(mae([1, 2], [0, 0]) - 1.5) < 1e-12)
    chk("skill:同誤差=0、減半=0.5", abs(skill_vs(1, 1)) < 1e-12 and abs(skill_vs(0.5, 1) - 0.5) < 1e-12)
    rng = np.random.default_rng(7)
    a = rng.normal(0, 1, 400); good = np.abs(a * 0.2); bad = np.abs(a)
    dm, p = dm_test_hln(good, bad, 20)
    chk("DM:明顯較優→dm<0 且 p<0.05", dm < 0 and p < 0.05)
    dm2, p2 = dm_test_hln(bad, bad + rng.normal(0, 1e-9, 400), 20)
    chk("DM:同精度→不顯著", not (p2 == p2 and p2 < 0.05))
    chk("sign_hit 全對=1", sign_hit([1, -1], [2, -3]) == 1.0)
    chk("SN 週期重複", np.allclose(SeasonalNaive().forecast(np.arange(10.), 7)[:5], np.arange(5., 10.)))
    chk("RW 全零", np.allclose(RW().forecast(None, 5), 0))
    n = CONTEXT + 10 * H
    sl = rofe_slices(n)
    chk("ROFE:10 窗、無前視(ctx 尾=origin)", len(sl) == 10 and all(c.stop == a.start for c, a in sl)
        and sl[-1][1].stop == n)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--stocks", nargs="*", default=STOCKS)
    ap.add_argument("--windows", type=int, default=N_WIN)
    ap.add_argument("--models", nargs="*", default=list(MODEL_POOL))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.run:
        return run(args.stocks, args.models, args.windows)
    print(__doc__.split("執行指令矩陣:")[1])
    print(f"設計:stocks={STOCKS} L={CONTEXT} H={H} 窗={N_WIN} asof={ASOF}")
    print(f"模型池:{list(MODEL_POOL)}(TimeGPT=商用 API 不在池、誠實跳過)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
