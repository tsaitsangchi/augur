#!/usr/bin/env python
"""SIM-CAL-R1 五臂校準評估器 — sim 軸首輪預註冊門之證據計算（W3;模擬方法自進化專章 §3）。

🎯 這支在做什麼(白話):讀 `evolution_prereg_gate` 之 SIM-CAL-R1 列,**評估前先覆算兩級指紋**
   (D2S §6-2 兩式:criteria_sha=sha256(criteria_text)、criteria_text 末行 thresholds_sha=
   sha256((criteria->'thresholds')::text),任一不符即拒評 exit 1 零寫入——判準本文明文之評估紀律)。
   通過後收集 gate 之 live run(sim_run_link join mc_simulation_run join sim_realized_outcome),
   照 criteria_text 凍結定義構造五臂(live/ceiling/floor/shuffled/mismatched;robot 選配 R1 不跑;
   floor σ 截止 2026-07-31=S-2 裁定),逐格(asof 窗)計 coverage/pinball/CRPS/PIT-KS 與 k1-k3 判式
   素材(k2=date_cluster_block_bootstrap LCB、k3=日期簇 bootstrap KS 臨界值;B=1000/seed=42 照
   thresholds),寫 `sim_calibration_eval` 5 列(gate_id FK;uq_sce_cell 冪等)。n_valid<下限或簇<K
   或缺臂=誠實印 undecidable 素材(合法產出、不作 pass 用;**`--apply` 一律零寫入**——證據列只承載
   可判之尺;判定本身屬 W4 decide_sim_verdict)。kill switch(DB sim/global ∨ env)halt ⇒ 全模式拒評。
   **本評估=self-reported;promoted 須三鎖人簽**(chk_sev_promote_signed;本工具不設人名旗標)。

守 #8(樣本外斷言:史料 asof<=2026-05-31 任何數字不得入證據列;q_grid 物理擋)· #9/#10(數字全出自
   DB query 可溯)· #15(拒評條款+缺臂 raise+合成回歸自測先驗紅)· #28(本地零 usage)· #29a/d。
   判準 SSOT=SIM-CAL-R1 criteria_text(binding);設計=reports/sim_w3w5_implementation_plan_20260802.md §5。

執行指令矩陣:
  python scripts/evaluate_sim_calibration.py             # 無參數:現況(唯讀:門態+指紋覆算+證據水位+K 進度)
  python scripts/evaluate_sim_calibration.py --dry-run   # 全計算唯讀預演(不寫表;零 run=印「零格可評」誠實不炸)
                                                         #   kill halt(DB sim/global 或 env)亦拒評 exit 1
  python scripts/evaluate_sim_calibration.py --apply     # 防衛全過(兩 sha+targets_sha+樣本外+五臂+kill switch)
                                                         #   且 undecidable 素材全清(n_valid>=下限 且 K>=下限
                                                         #   且五臂全在)才寫 5 列;否則 exit 1 零寫入
  python scripts/evaluate_sim_calibration.py --selftest  # 零 DB:sha 拒評絆線(改一字必拒)/k1-k3 紅綠/五臂互斥
                                                         #   /derangement 無定點/合成常態回歸/LCB+KS bootstrap
                                                         #   /寫入閘 n_valid 不足零 INSERT/kill state 吃 env
  AUGUR_EVOLUTION_KILL_SWITCH=halt python scripts/evaluate_sim_calibration.py --dry-run   # 煞車實測(rc=1)
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import sys
from pathlib import Path
from datetime import date
from zoneinfo import ZoneInfo

import _bootstrap  # noqa: F401
import numpy as np
from augur.catalog import world_concept

ADJ_CONCEPT = "tw.daily_bar_adjusted"  # WM.36

GATE_ID = "SIM-CAL-R1"
HISTORY_FREEZE = date(2026, 5, 31)          # 史料上限:此前 asof 之任何數字不得入證據列(criteria_text 明文)
FLOOR_SIGMA_CUTOFF = date(2026, 7, 31)      # S-2 裁定:floor 全史 pooled σ 之截止日(approved 前最後交易日)
HORIZON_TD = 21
GRID_STEP_TD = 21
TAUS_99 = tuple((i + 1) / 100.0 for i in range(99))          # p1..p99
PINBALL_IDX = (4, 9, 24, 49, 74, 89, 94)                      # τ∈{.05,.10,.25,.50,.75,.90,.95} 之 grid index
REQUIRED_ARMS = ("live", "ceiling", "floor", "shuffled", "mismatched")   # 五臂地板;robot 選配 R1 不跑
PIT_CLAMP = (0.005, 0.995)
SELF_REPORTED_LINE = "本評估=self-reported,promoted 須三鎖人簽"

# D2S §6-2 兩式(逐字;server 端覆算,與 client 端 sha256 互證)
SQL_GATE_FINGERPRINT = """
SELECT status, criteria_sha, approved_at,
       encode(sha256(convert_to(criteria->>'criteria_text','UTF8')),'hex')      AS criteria_sha_srv,
       encode(sha256(convert_to((criteria->'thresholds')::text,'UTF8')),'hex')  AS thresholds_sha_srv,
       criteria->>'criteria_text', (criteria->'thresholds')::text
FROM evolution_prereg_gate WHERE gate_id=%s
"""
# 凍結清單推導=史料限定式(R-1:史料受 DELETE 閘保護=集合永穩;不用 binding 之無過濾式)
SQL_FROZEN_TARGETS = """
SELECT DISTINCT target_id FROM mc_simulation_run
WHERE target_id ~ '^[0-9]+$' AND asof_date = %s ORDER BY target_id
"""


def _sql_sigma_floor(adj_sql: str) -> str:
    """floor σ 查詢；表經 tw.daily_bar_adjusted（WM.36）。"""
    return f"""
WITH r AS (
  SELECT ln(close / lag(close) OVER (PARTITION BY stock_id ORDER BY date)) AS lr
  FROM {adj_sql}
  WHERE stock_id = ANY(%s) AND date <= %s AND close > 0
) SELECT stddev_samp(lr), count(lr) FROM r WHERE lr IS NOT NULL
"""


class GateRefusal(RuntimeError):
    """拒評(評估紀律):指紋不符/門態不對/樣本外違規/凍結清單漂移——一律 exit 1 零寫入。"""


class ArmIncomplete(RuntimeError):
    """五臂地板缺臂:不得靜默少跑(criteria_text「任一臂缺 ⇒ undecidable」之 fail-loud 載體)。"""


# ---------------------------------------------------------------- 純函式(selftest 全覆蓋)

def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_declared_thresholds_sha(criteria_text: str):
    """criteria_text 末行宣告之 thresholds_sha=<64hex>;缺=None(=拒評事由)。"""
    for line in reversed([ln.strip() for ln in criteria_text.strip().splitlines() if ln.strip()]):
        if line.startswith("thresholds_sha="):
            v = line.split("=", 1)[1].strip()
            return v if len(v) == 64 else None
    return None


def verify_gate_fingerprints(stored_criteria_sha, criteria_text, thresholds_canonical_text):
    """兩級覆算(D2S §6-2):任一不符 → (False, 事由)。拒評條款之核心純函式。"""
    reasons = []
    recomputed = sha256_hex(criteria_text)
    if recomputed != stored_criteria_sha:
        reasons.append(f"criteria_sha 不符:stored={stored_criteria_sha[:12]}… recomputed={recomputed[:12]}…")
    declared = parse_declared_thresholds_sha(criteria_text)
    if declared is None:
        reasons.append("criteria_text 末行無 thresholds_sha 宣告")
    else:
        recomputed_t = sha256_hex(thresholds_canonical_text)
        if recomputed_t != declared:
            reasons.append(f"thresholds_sha 不符:declared={declared[:12]}… recomputed={recomputed_t[:12]}…")
    return (len(reasons) == 0, reasons)


def frozen_targets_sha(target_ids) -> str:
    """口徑=排序後 \\n 串接 sha256(criteria_text 凍結清單式)。"""
    return sha256_hex("\n".join(sorted(target_ids)))


def grid_asofs(trading_days_from_anchor, step=GRID_STEP_TD):
    """格點=自 anchor 起已實現交易日之 index 0, step, 2*step, …(窗天然不重疊)。"""
    return [trading_days_from_anchor[i] for i in range(0, len(trading_days_from_anchor), step)]


def normalize_q_grid(summary: dict):
    """runner 追加之 terminal_q_grid(p1..p99 共 99 分位)→ list[99];缺/形壞=None(物理擋史料)。"""
    g = summary.get("terminal_q_grid")
    if isinstance(g, dict) and "p" in g:
        # runner 實形＝{"unit":…, "p": list[99]}（_q_grid 回 list）。
        # ⚠ 2026-08-02 我曾把 p 誤讀為 {p1..p99} dict 並手寫該形狀當 fixture ⇒ 測試綠、真路 None
        #   ——#35(1)「純函式餵真輸入」之實犯；2026-08-03 r4 對抗核驗抓出、改為兩形皆收。
        g = g["p"]
    if isinstance(g, dict):
        try:
            g = [g[f"p{i}"] for i in range(1, 100)]
        except KeyError:
            return None
    if not isinstance(g, (list, tuple)) or len(g) != 99:
        return None
    arr = [float(x) for x in g]
    if any(b < a - 1e-12 for a, b in zip(arr, arr[1:])):    # 分位必單調不減,否則資料毀損
        return None
    return arr


def coverage_flags(qgrid, realized):
    """(落 [q25,q75], 落 [q10,q90], 落 [q5,q95])——cov_p50/p80/p90 素材(q_grid 直讀)。"""
    return (qgrid[24] <= realized <= qgrid[74],
            qgrid[9] <= realized <= qgrid[89],
            qgrid[4] <= realized <= qgrid[94])


def pinball_terms(qgrid, realized):
    """逐 τ pinball loss 向量(p1..p99)。"""
    q = np.asarray(qgrid, dtype=float)
    t = np.asarray(TAUS_99)
    diff = realized - q
    return np.where(diff >= 0, t * diff, (t - 1.0) * diff)


def crps_from_qgrid(qgrid, realized) -> float:
    """CRPS 分位分解:2×mean pinball over τ=.01..0.99。"""
    return 2.0 * float(pinball_terms(qgrid, realized).mean())


def pinball_mean_from_qgrid(qgrid, realized) -> float:
    """mean pinball over τ∈{.05,.10,.25,.50,.75,.90,.95}。"""
    return float(pinball_terms(qgrid, realized)[list(PINBALL_IDX)].mean())


def pit_from_qgrid(qgrid, realized):
    """PIT=F̂(realized)(q_grid 線性插值);端點外夾 [0.005,0.995]。回 (pit, clamped)。"""
    if realized <= qgrid[0]:
        return PIT_CLAMP[0], True
    if realized >= qgrid[-1]:
        return PIT_CLAMP[1], True
    return float(np.interp(realized, np.asarray(qgrid, dtype=float), np.asarray(TAUS_99))), False


def ks_uniform_stat(pits) -> float:
    """單樣本 KS 統計量(對 U(0,1))。"""
    x = np.sort(np.asarray(pits, dtype=float))
    n = len(x)
    i = np.arange(1, n + 1)
    return float(max(np.max(i / n - x), np.max(x - (i - 1) / n)))


def cluster_bootstrap_lcb(per_cluster_stats, b=1000, seed=42, one_sided=0.95) -> float:
    """date_cluster_block_bootstrap(thresholds.skill_test):簇整塊重抽 B 次之均值分布,
    單尾 LCB(one_sided)=下 (1-one_sided) 分位。K 小時粒度極粗(R-3),照判準做、detail 揭露。"""
    arr = np.asarray(per_cluster_stats, dtype=float)
    k = len(arr)
    rng = np.random.default_rng(seed)
    means = arr[rng.integers(0, k, size=(b, k))].mean(axis=1)
    return float(np.percentile(means, (1.0 - one_sided) * 100.0))


def pit_ks_p_cluster_bootstrap(cluster_sizes, ks_obs, b=1000, seed=42) -> float:
    """KS p 值之日期簇 bootstrap 臨界值(thresholds.pit.critical_values):null=PIT~U(0,1),
    逐次以「簇(含 size)整塊重抽」保留簇結構,p=(1+#{KS_b>=KS_obs})/(B+1)。"""
    sizes = list(cluster_sizes)
    k = len(sizes)
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(b):
        drawn = rng.integers(0, k, size=k)
        n_b = int(sum(sizes[j] for j in drawn))
        if ks_uniform_stat(rng.random(n_b)) >= ks_obs:
            cnt += 1
    return (cnt + 1) / (b + 1)


def normal_q_grid(sigma_daily, h=HORIZON_TD):
    """floor 臂:無條件常數錐 N(0, σ√h)(log 域)之 p1..p99,換算簡單報酬對齊 q_grid 口徑。"""
    nd = statistics.NormalDist()
    s = float(sigma_daily) * math.sqrt(h)
    return [math.exp(s * nd.inv_cdf(t)) - 1.0 for t in TAUS_99]


def empirical_q_grid(values):
    """ceiling 臂:同窗實現值之事後經驗分位 p1..p99(每窗一錐、全 target 共用;僅上界參照不參賽)。"""
    v = np.asarray(values, dtype=float)
    return [float(np.percentile(v, p)) for p in range(1, 100)]


def derangement_map(n, rng, max_tries=10000):
    """固定 seed 之 derangement(無定點置換);n<2 不存在=None(該窗 mismatched 誠實除外)。"""
    if n < 2:
        return None
    base = np.arange(n)
    for _ in range(max_tries):
        p = rng.permutation(n)
        if not np.any(p == base):
            return p
    return None


def build_arms(obs, floor_grid):
    """五臂構造(criteria_text 定義凍結)。obs=list[dict(target,asof,qgrid,realized)]。
    回 (arms: {arm: [(qgrid, realized, cluster_key), …]}, notes)。shuffled/mismatched 逐窗
    default_rng(42)(判準逐字);<2 有效觀測之窗於此二臂誠實除外(notes 揭露)。"""
    arms = {a: [] for a in REQUIRED_ARMS}
    notes = {"shuffled_skipped_windows": [], "mismatched_skipped_windows": [],
             "derangement_map": {}, "shuffle_map": {}}
    by_win = {}
    for o in obs:
        by_win.setdefault(o["asof"], []).append(o)
    for asof in sorted(by_win):
        w = by_win[asof]
        ck = str(asof)
        realized = [o["realized"] for o in w]
        ceil_grid = empirical_q_grid(realized)
        for o in w:
            arms["live"].append((o["qgrid"], o["realized"], ck))
            arms["ceiling"].append((ceil_grid, o["realized"], ck))
            arms["floor"].append((floor_grid, o["realized"], ck))
        if len(w) >= 2:
            perm = np.random.default_rng(42).permutation(len(w))
            for i, o in enumerate(w):
                arms["shuffled"].append((o["qgrid"], w[int(perm[i])]["realized"], ck))
            notes["shuffle_map"][ck] = {w[i]["target"]: w[int(perm[i])]["target"] for i in range(len(w))}
            dmap = derangement_map(len(w), np.random.default_rng(42))
            if dmap is None:
                notes["mismatched_skipped_windows"].append(ck)
            else:
                for i, o in enumerate(w):
                    arms["mismatched"].append((o["qgrid"], w[int(dmap[i])]["realized"], ck))
                notes["derangement_map"][ck] = {w[i]["target"]: w[int(dmap[i])]["target"] for i in range(len(w))}
        else:
            notes["shuffled_skipped_windows"].append(ck)
            notes["mismatched_skipped_windows"].append(ck)
    return arms, notes


def assert_arms_complete(arms, required=REQUIRED_ARMS):
    """臂完備斷言:缺任一臂(含空臂)即 raise,不得靜默少跑。"""
    missing = [a for a in required if not arms.get(a)]
    if missing:
        raise ArmIncomplete(f"五臂地板缺臂: {missing}")


def arm_metrics(pairs):
    """單臂逐觀測計算 → 聚合。pairs=[(qgrid, realized, cluster_key), …]。"""
    covs, crps_list, pinb_list, pits = [], [], [], []
    clamped = 0
    per_cluster_crps = {}
    for qgrid, r, ck in pairs:
        covs.append(coverage_flags(qgrid, r))
        crps = crps_from_qgrid(qgrid, r)
        crps_list.append(crps)
        pinb_list.append(pinball_mean_from_qgrid(qgrid, r))
        pit, cl = pit_from_qgrid(qgrid, r)
        pits.append(pit)
        clamped += int(cl)
        per_cluster_crps.setdefault(ck, []).append(crps)
    n = len(pairs)
    c = np.asarray(covs, dtype=float)
    return {
        "n": n,
        "cov_p50": float(c[:, 0].mean()), "cov_p80": float(c[:, 1].mean()), "cov_p90": float(c[:, 2].mean()),
        "pinball_mean": float(np.mean(pinb_list)), "crps_mean": float(np.mean(crps_list)),
        "pit_ks_stat": ks_uniform_stat(pits), "pits": pits, "pit_clamped": clamped,
        "cluster_crps_mean": {ck: float(np.mean(v)) for ck, v in sorted(per_cluster_crps.items())},
        "cluster_sizes": {ck: len(v) for ck, v in sorted(per_cluster_crps.items())},
    }


def k1_breach(cov_p80, cov_p90, tol_p80, tol_p90) -> bool:
    """k1 判死式:|cov_p80−0.80|>tol 或 |cov_p90−0.90|>tol。"""
    return abs(cov_p80 - 0.80) > tol_p80 or abs(cov_p90 - 0.90) > tol_p90


def k2_live_beats_arm(delta_lcb) -> bool:
    """k2 素材:Δcrps(arm−live) 簇 bootstrap LCB>0 ⇔ live 勝過該臂(判死=任一臂未勝)。"""
    return delta_lcb > 0.0


def k3_breach(pit_ks_p, p_min) -> bool:
    """k3 判死式(唯 T-A):PIT KS 依日期簇 bootstrap 臨界值 p<p_min。"""
    return pit_ks_p < p_min


def undecidable_reasons(n_valid, n_valid_min, k_clusters, clusters_min, arms_present, required=REQUIRED_ARMS):
    """undecidable(criteria_text §5.4):n_valid<下限/日期簇<K/任一臂缺 ⇒ 誠實無能為合法產出。"""
    reasons = []
    if n_valid < n_valid_min:
        reasons.append(f"n_valid={n_valid} < n_valid_min={n_valid_min}")
    if k_clusters < clusters_min:
        reasons.append(f"date_clusters={k_clusters} < date_clusters_min={clusters_min}")
    missing = [a for a in required if a not in arms_present]
    if missing:
        reasons.append(f"缺臂: {missing}")
    return reasons


def apply_write_gate(n_valid, k_clusters, arms_present, thresholds):
    """`--apply` 之寫入閘(M-M1):undecidable 素材非空 ⇒ 不允寫。回 (allowed, reasons)。

    原缺口＝只擋 `k_clusters < date_clusters_min`、不擋 `n_valid < n_valid_min`,故 K 達標而
    樣本不足時仍寫出「看起來可判」的證據列(§5.4 明文 undecidable 不得作 pass 用)。判準素材單一
    住所＝`undecidable_reasons`(#12),此處只決定「允不允寫」不另立口徑。"""
    reasons = undecidable_reasons(n_valid, thresholds["n_valid_min"],
                                  k_clusters, thresholds["date_clusters_min"], arms_present)
    return (not reasons), reasons


def make_eval_set_id(asof_list) -> str:
    """eval_set_id='R1:h21:'+sha256(\\n.join(格點))[:12](設計 §5.5)。"""
    return "R1:h21:" + sha256_hex("\n".join(str(a) for a in sorted(asof_list)))[:12]


def eval_code_hash_of(source_bytes: bytes) -> str:
    """評估碼指紋:本檔原始碼 sha256——評估碼變更即新 cell(uq_sce_cell);實質變更=換尺(§5.3 專章)。"""
    return hashlib.sha256(source_bytes).hexdigest()


# ---------------------------------------------------------------- DB 邊(dry-run/apply 共用)

def _load_and_verify_gate(cur):
    """拒評防衛入口(dry-run 與 apply 之共同下游):讀門列+server/client 兩側覆算,任一不符 raise GateRefusal。"""
    cur.execute(SQL_GATE_FINGERPRINT, (GATE_ID,))
    row = cur.fetchone()
    if row is None:
        raise GateRefusal(f"{GATE_ID} 門列不存在")
    status, stored_sha, approved_at, sha_c_srv, sha_t_srv, criteria_text, thresholds_text = row
    if status != "approved":
        raise GateRefusal(f"門態非 approved(現={status})——本工具不評未生效/已終態之門")
    ok, reasons = verify_gate_fingerprints(stored_sha, criteria_text, thresholds_text)
    if not ok:
        raise GateRefusal("指紋覆算不符,拒評: " + "; ".join(reasons))
    if sha_c_srv != sha256_hex(criteria_text) or sha_t_srv != sha256_hex(thresholds_text):
        raise GateRefusal("server/client sha 覆算分歧(編碼異常)——拒評待鑑識")
    return {"criteria_text": criteria_text, "thresholds": json.loads(thresholds_text),
            "approved_at": approved_at, "criteria_sha": stored_sha,
            "thresholds_sha": parse_declared_thresholds_sha(criteria_text)}


def _verify_frozen_targets(cur, thresholds):
    cur.execute(SQL_FROZEN_TARGETS, (HISTORY_FREEZE,))
    targets = [r[0] for r in cur.fetchall()]
    sha = frozen_targets_sha(targets)
    if sha != thresholds.get("targets_sha"):
        raise GateRefusal(f"凍結清單 sha 漂移: recomputed={sha[:16]}… != targets_sha="
                          f"{str(thresholds.get('targets_sha'))[:16]}…(n={len(targets)})")
    return targets


def _env_halt() -> bool:
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == "halt"


def _kill_state(cur):
    """sim 軸有效煞車態(scope sim ∨ global ∨ env;OR fail-safe)。口徑單一住所＝
    `augur.philosophy.evolution.effective_kill_state`(#12;寫法同 propose_sim_candidate.py／
    settle_sim_outcomes.py)。原缺口＝本支未傳 `env_halt` ⇒ sim 軸四支中唯一 fail-open。"""
    from augur.philosophy.evolution import effective_kill_state
    cur.execute("SELECT state FROM evolution_kill_switch WHERE scope IN ('sim','global')")
    return effective_kill_state([r[0] for r in cur.fetchall()], env_halt=_env_halt())


def _anchor_and_grid(cur, approved_at):
    approved_date = approved_at.astimezone(ZoneInfo("Asia/Taipei")).date()
    adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=cur.connection)
    cur.execute(f"""SELECT date FROM {adj_sql}
                   WHERE stock_id='TAIEX' AND date > %s ORDER BY date""", (approved_date,))
    days = [r[0] for r in cur.fetchall()]
    if not days:
        return None, []
    return days[0], grid_asofs(days)


def _collect(cur):
    """gate 之 live 證據列(link join run join outcome;outcome 可缺=未結算)。"""
    cur.execute("""
        SELECT l.candidate_id, r.target_id, r.asof_date, r.horizon_td, r.summary,
               o.settle_mode, o.realized_logret
        FROM sim_run_link l
        JOIN mc_simulation_run r ON r.run_id = l.run_id
        LEFT JOIN sim_realized_outcome o ON o.run_id = l.run_id
        WHERE l.gate_id = %s AND l.arm = 'live'
        ORDER BY r.asof_date, r.target_id""", (GATE_ID,))
    return cur.fetchall()


def _sigma_floor(cur, targets):
    adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=cur.connection)
    sql = _sql_sigma_floor(adj_sql)
    cur.execute(sql, (targets, FLOOR_SIGMA_CUTOFF))
    sigma, n = cur.fetchone()
    if sigma is None:
        raise GateRefusal("floor σ 無法計算(pooled 日報酬空集)")
    return float(sigma), int(n), sql


def _evaluate(conn, apply_mode):
    cur = conn.cursor()
    gate = _load_and_verify_gate(cur)
    th = gate["thresholds"]
    print(f"✓ 拒評防衛通過: criteria_sha={gate['criteria_sha'][:16]}… thresholds_sha={gate['thresholds_sha'][:16]}…(兩級覆算合)")
    if th.get("horizon_td") != [HORIZON_TD]:
        raise GateRefusal(f"thresholds.horizon_td={th.get('horizon_td')} 非 [{HORIZON_TD}]——工具口徑不合,拒評")
    targets = _verify_frozen_targets(cur, th)
    print(f"✓ 凍結清單 sha 合({len(targets)} 檔)")
    kill = _kill_state(cur)
    print(f"  kill_switch(sim,global,env 有效態)={kill}")
    if kill != "clear":
        # 煞車＝停手,不分模式:dry-run 亦拒(同 settle/propose;煞車期間連 self-reported 讀數都不產)
        print("✗ kill switch=halt(scope sim/global 或 AUGUR_EVOLUTION_KILL_SWITCH)⇒ 拒評零寫入 exit 1")
        return 1

    anchor, grid = _anchor_and_grid(cur, gate["approved_at"])
    rows = _collect(cur)
    if anchor is None:
        print(f"  anchor 未實現(approved_at 次一交易日尚未入庫;TAIEX 待 sync)")
        if rows:
            raise GateRefusal("anchor 未實現卻已有 link 列——證據鏈異常,拒評")
        print("零格可評: link=0、格點未起算。誠實現況,非錯誤。")
        print(SELF_REPORTED_LINE)
        return 1 if apply_mode else 0
    grid_set = set(grid)
    print(f"  anchor={anchor} 已實現格點數={len(grid)}(step={GRID_STEP_TD}td)")

    if not rows:
        print("零格可評: sim_run_link(gate=SIM-CAL-R1, arm=live)=0 列——runner(W5)尚未產 run。")
        print(SELF_REPORTED_LINE)
        return 1 if apply_mode else 0

    # 樣本外斷言(#8;違者拒評非靜默剔除——史料/非格點 run 入 link=證據鏈污染,須人看)
    violations = [f"{r[1]}@{r[2]}" for r in rows
                  if r[2] <= HISTORY_FREEZE or r[2] < anchor or r[2] not in grid_set or r[3] != HORIZON_TD]
    if violations:
        raise GateRefusal(f"樣本外斷言違規 {len(violations)} 列(史料/非格點/h≠21): {violations[:8]}…")

    candidates = sorted({r[0] for r in rows})
    if len(candidates) != 1:
        raise GateRefusal(f"R1 預期單一候選,實得 {candidates}——候選集合=Steward 裁點(S-1),拒評")
    candidate_id = candidates[0]

    settle_ok = set(th["settle_modes"])
    obs, n_excluded, n_unsettled, n_no_qgrid = [], 0, 0, 0
    for _cand, target, asof, _h, summary, settle_mode, realized_logret in rows:
        if settle_mode is None:
            n_unsettled += 1
            continue
        if settle_mode not in settle_ok:
            n_excluded += 1
            continue
        qgrid = normalize_q_grid(summary if isinstance(summary, dict) else json.loads(summary))
        if qgrid is None:
            n_no_qgrid += 1                      # 物理擋:無 q_grid(史料 summary 形)不可能入證據
            continue
        obs.append({"target": target, "asof": asof, "qgrid": qgrid,
                    "realized": math.exp(float(realized_logret)) - 1.0})   # 簡單報酬口徑對齊 q_grid

    n_runs = len(rows)
    n_valid = len(obs)
    k_clusters = len({o["asof"] for o in obs})
    print(f"  n_runs={n_runs} n_valid={n_valid} n_excluded(unsettleable)={n_excluded} "
          f"未結算={n_unsettled} 無q_grid={n_no_qgrid} K(日期簇)={k_clusters}/{th['date_clusters_min']}")

    if n_valid == 0:
        print("零格可評: 有 run 但無已結算有效觀測(等 settle 波)。")
        print(SELF_REPORTED_LINE)
        return 1 if apply_mode else 0

    sigma, sigma_n, sigma_sql = _sigma_floor(cur, targets)
    print(f"  floor σ(pooled 日報酬, ≤{FLOOR_SIGMA_CUTOFF}, {len(targets)} 檔, n={sigma_n})={sigma:.6f}(S-2)")
    arms, arm_notes = build_arms(obs, normal_q_grid(sigma))
    assert_arms_complete(arms)

    st = th["skill_test"]
    metrics, deltas_detail = {}, {}
    for arm in REQUIRED_ARMS:
        metrics[arm] = arm_metrics(arms[arm])
    live_ck = metrics["live"]["cluster_crps_mean"]
    k2_result = {}
    for arm in th["skill_arms"]:
        common = [ck for ck in metrics[arm]["cluster_crps_mean"] if ck in live_ck]
        deltas = [metrics[arm]["cluster_crps_mean"][ck] - live_ck[ck] for ck in common]
        lcb = cluster_bootstrap_lcb(deltas, b=st["B"], seed=st["seed"], one_sided=st["one_sided_lcb"]) if deltas else float("nan")
        k2_result[arm] = {"delta_per_cluster": dict(zip(common, [round(d, 8) for d in deltas])),
                          "lcb": lcb, "live_beats": bool(deltas) and k2_live_beats_arm(lcb)}
        deltas_detail[arm] = deltas
    live = metrics["live"]
    pit_p = pit_ks_p_cluster_bootstrap(list(live["cluster_sizes"].values()), live["pit_ks_stat"],
                                       b=st["B"], seed=st["seed"])
    k1 = k1_breach(live["cov_p80"], live["cov_p90"], th["cov_tol"]["p80"], th["cov_tol"]["p90"])
    k2 = any(not v["live_beats"] for v in k2_result.values())
    k3 = k3_breach(pit_p, th["pit"]["p_min"])
    und = undecidable_reasons(n_valid, th["n_valid_min"], k_clusters, th["date_clusters_min"],
                              [a for a in arms if arms[a]])

    print("\n  臂別指標(逐格素材;判定屬 W4):")
    print("  arm         n    cov_p50 cov_p80 cov_p90 pinball    crps      ks_stat")
    for arm in REQUIRED_ARMS:
        m = metrics[arm]
        print(f"  {arm:<10} {m['n']:>4}  {m['cov_p50']:.4f}  {m['cov_p80']:.4f}  {m['cov_p90']:.4f}"
              f"  {m['pinball_mean']:.6f} {m['crps_mean']:.6f} {m['pit_ks_stat']:.4f}")
    print(f"  robot 臂:選配、R1 不跑(非地板要件)")
    print(f"\n  k1 判式(|cov80−.80|>{th['cov_tol']['p80']} 或 |cov90−.90|>{th['cov_tol']['p90']}): breach={k1}")
    for arm, v in k2_result.items():
        print(f"  k2 Δcrps({arm}−live) 簇均值 LCB({st['one_sided_lcb']})={v['lcb']:.6f} live_beats={v['live_beats']}")
    print(f"  k2 判式(任一臂未勝=判死素材): breach={k2}")
    print(f"  k3 判式(PIT KS p={pit_p:.4f} < {th['pit']['p_min']}): breach={k3}(p 依日期簇 bootstrap;K={k_clusters} 粒度限制見 detail)")
    if und:
        print(f"  ⚠ undecidable(§5.4 誠實無能為合法產出;不得作 pass 用): {'; '.join(und)}")
    print(f"\n  {SELF_REPORTED_LINE}")

    src = open(__file__, "rb").read()
    code_hash = eval_code_hash_of(src)
    eval_set_id = make_eval_set_id(sorted({o["asof"] for o in obs}))
    detail_common = {
        "gate_id": GATE_ID, "candidate_id": candidate_id,
        "criteria_sha": gate["criteria_sha"], "thresholds_sha": gate["thresholds_sha"],
        "anchor": str(anchor), "grid_evaluated": sorted(str(o) for o in {o["asof"] for o in obs}),
        "sigma_floor": sigma, "sigma_floor_cutoff": str(FLOOR_SIGMA_CUTOFF), "sigma_floor_n": sigma_n,
        "sigma_floor_sql": " ".join(sigma_sql.split()),
        "n_reconcile": {"n_runs": n_runs, "n_valid": n_valid, "n_excluded_unsettleable": n_excluded,
                        "n_unsettled": n_unsettled, "n_no_qgrid": n_no_qgrid},
        "k1": {"breach": k1, "cov_p80": live["cov_p80"], "cov_p90": live["cov_p90"], "tol": th["cov_tol"]},
        "k2": {arm: {"lcb": v["lcb"], "live_beats": v["live_beats"], "delta_per_cluster": v["delta_per_cluster"]}
               for arm, v in k2_result.items()},
        "k2_breach": k2,
        "k3": {"breach": k3, "pit_ks_p": pit_p, "pit_ks_stat": live["pit_ks_stat"],
               "p_algo": "cluster-size-preserving date_cluster bootstrap, p=(1+#{KS_b>=obs})/(B+1)",
               "B": st["B"], "seed": st["seed"], "granularity_note": f"K={k_clusters} 簇重抽粒度極粗(R-3),照判準"},
        "undecidable_reasons": und, "arm_notes": arm_notes,
        "robot_arm": "選配、R1 不跑", "self_reported": SELF_REPORTED_LINE,
    }

    if not apply_mode:
        print(f"\n  dry-run 完(零寫入)。eval_set_id={eval_set_id} eval_code_hash={code_hash[:16]}…")
        return 0

    inserted, blocked = _insert_eval_rows(
        cur, th=th, n_valid=n_valid, k_clusters=k_clusters,
        arms_present=[a for a in arms if arms[a]], metrics=metrics, detail_common=detail_common,
        candidate_id=candidate_id, eval_set_id=eval_set_id, code_hash=code_hash,
        n_runs=n_runs, n_excluded=n_excluded, pit_p=pit_p, git_sha=_git7())
    if blocked:
        print(f"✗ --apply 但 undecidable(§5.4): {'; '.join(blocked)} ⇒ 零寫入 exit 1"
              f"(undecidable 不得作 pass 用;證據列只承載可判之尺)")
        return 1
    conn.commit()
    print(f"✓ --apply 寫入 {inserted}/5 列(uq_sce_cell 冪等;0=同 cell 已在)。eval_set_id={eval_set_id}")
    print(f"  {SELF_REPORTED_LINE}")
    return 0


def _insert_eval_rows(cur, *, th, n_valid, k_clusters, arms_present, metrics, detail_common,
                      candidate_id, eval_set_id, code_hash, n_runs, n_excluded, pit_p, git_sha):
    """`--apply` 之**唯一**寫入路徑:先過 `apply_write_gate`,不允寫即 0 次 cur.execute。
    回 (inserted, blocked_reasons);blocked 非空 ⇒ inserted=0 且呼叫端不得 commit。"""
    allowed, reasons = apply_write_gate(n_valid, k_clusters, arms_present, th)
    if not allowed:
        return 0, reasons
    inserted = 0
    for arm in REQUIRED_ARMS:
        m = metrics[arm]
        detail = dict(detail_common)
        detail["cluster_crps_mean"] = m["cluster_crps_mean"]
        detail["pit_clamped"] = m["pit_clamped"]
        cur.execute("""
            INSERT INTO sim_calibration_eval
              (gate_id, candidate_id, arm, eval_set_id, eval_code_hash, n_runs, n_valid, n_excluded,
               cov_p50, cov_p80, cov_p90, pinball_mean, crps_mean, pit_ks_stat, pit_ks_p, detail, git_sha)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (gate_id, COALESCE(candidate_id, '-'), arm, eval_set_id, eval_code_hash) DO NOTHING""",
            (GATE_ID, candidate_id, arm, eval_set_id, code_hash, n_runs, m["n"], n_excluded,
             m["cov_p50"], m["cov_p80"], m["cov_p90"], m["pinball_mean"], m["crps_mean"],
             m["pit_ks_stat"], pit_p if arm == "live" else None,
             json.dumps(detail, ensure_ascii=False, default=str), git_sha))
        inserted += cur.rowcount
    return inserted, []


def _git7():
    from simulate_mc_paths import _git7 as g          # sibling import 既有引擎檔(有先例)
    return g()


def status():
    """無參數:唯讀現況(graceful;連不上 DB 印矩陣不裸 traceback)。"""
    try:
        from augur.core import db
        with db.connect() as conn:
            cur = conn.cursor()
            try:
                gate = _load_and_verify_gate(cur)
                print(f"✓ {GATE_ID}: approved({gate['approved_at']});兩級指紋覆算合")
                th = gate["thresholds"]
                anchor, grid = _anchor_and_grid(cur, gate["approved_at"])
                print(f"  anchor={anchor or '未實現(待 sync)'} 已實現格點={len(grid)}"
                      f" K 需求={th['date_clusters_min']} n_valid_min={th['n_valid_min']}")
            except GateRefusal as e:
                print(f"✗ 拒評: {e}")
            cur.execute("SELECT count(*) FROM sim_run_link WHERE gate_id=%s AND arm='live'", (GATE_ID,))
            n_link = cur.fetchone()[0]
            cur.execute("""SELECT count(*) FROM sim_realized_outcome o
                           JOIN sim_run_link l ON l.run_id=o.run_id WHERE l.gate_id=%s""", (GATE_ID,))
            n_settled = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM sim_calibration_eval WHERE gate_id=%s", (GATE_ID,))
            n_eval = cur.fetchone()[0]
            print(f"  證據水位: live link={n_link} 已結算={n_settled} eval 列={n_eval}")
            print(f"  {SELF_REPORTED_LINE}")
    except GateRefusal as e:
        print(f"✗ 拒評: {e}")
        return 1
    except Exception as e:
        print(f"(DB 不可用: {type(e).__name__}: {e})")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


# ---------------------------------------------------------------- selftest(零 DB 零 API)

class _FakeCursor:
    """餵真下游(_load_and_verify_gate)之假 cursor:回傳固定門列(server sha=誠實覆算)。"""

    def __init__(self, row):
        self._row = row

    def execute(self, sql, params=None):
        pass

    def fetchone(self):
        return self._row


def _make_gate_row(criteria_text, thresholds_text, stored_sha=None, status="approved"):
    import datetime
    return (status, stored_sha or sha256_hex(criteria_text),
            datetime.datetime(2026, 8, 2, 19, 49, 40, tzinfo=datetime.timezone(datetime.timedelta(hours=8))),
            sha256_hex(criteria_text), sha256_hex(thresholds_text), criteria_text, thresholds_text)


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # -- 1) sha 拒評絆線:合成門(已知答案),改一字必拒;經真下游 _load_and_verify_gate 走完整路
    th_text = '{"cov_tol": {"p80": 0.05, "p90": 0.05}, "n_valid_min": 100}'
    good_text = "門:SELFTEST 合成判準\n評估紀律:覆算兩 sha\nthresholds_sha=" + sha256_hex(th_text)
    good = _load_and_verify_gate(_FakeCursor(_make_gate_row(good_text, th_text)))
    chk("好門通過且 thresholds 可解析", good["thresholds"]["n_valid_min"] == 100)
    tampered_text = good_text.replace("覆算兩", "覆算三", 1)      # 改一字;stored sha 仍=原文
    try:
        _load_and_verify_gate(_FakeCursor(_make_gate_row(tampered_text, th_text,
                                                         stored_sha=sha256_hex(good_text))))
        chk("criteria_text 改一字必拒評", False)
    except GateRefusal:
        chk("criteria_text 改一字必拒評", True)
    try:
        _load_and_verify_gate(_FakeCursor(_make_gate_row(good_text, th_text.replace("0.05", "0.50", 1))))
        chk("thresholds payload 被動必拒評(末行宣告不符)", False)
    except GateRefusal:
        chk("thresholds payload 被動必拒評(末行宣告不符)", True)
    try:
        _load_and_verify_gate(_FakeCursor(_make_gate_row(good_text, th_text, status="proposed")))
        chk("非 approved 門必拒評", False)
    except GateRefusal:
        chk("非 approved 門必拒評", True)
    chk("末行無 thresholds_sha 宣告=不通過", not verify_gate_fingerprints(
        sha256_hex("x"), "x", th_text)[0])

    # -- 2) k1-k3 判式紅綠(純函式)
    chk("k1 紅:cov80 偏 0.06>tol", k1_breach(0.86, 0.90, 0.05, 0.05))
    chk("k1 紅:cov90 偏 0.06>tol", k1_breach(0.80, 0.96, 0.05, 0.05))
    chk("k1 綠:兩帶皆容忍內", not k1_breach(0.83, 0.87, 0.05, 0.05))
    chk("k2 紅:LCB<=0=未勝", not k2_live_beats_arm(0.0) and not k2_live_beats_arm(-0.01))
    chk("k2 綠:LCB>0=勝", k2_live_beats_arm(1e-6))
    chk("k3 紅:p<p_min", k3_breach(0.049, 0.05))
    chk("k3 綠:p>=p_min", not k3_breach(0.05, 0.05))
    r = undecidable_reasons(50, 100, 2, 3, ["live", "ceiling"])
    chk("undecidable 三事由全列", len(r) == 3 and "n_valid=50" in r[0])
    chk("undecidable 空=可判", undecidable_reasons(150, 100, 3, 3, list(REQUIRED_ARMS)) == [])

    # -- 3) 五臂構造:互斥/完備/derangement 無定點/shuffled 多重集保持
    rng = np.random.default_rng(7)
    sigma = 0.02
    grid_true = normal_q_grid(sigma)
    obs = []
    for asof in (date(2026, 8, 3), date(2026, 9, 1), date(2026, 10, 1)):
        for t in ("1101", "2330", "2317", "2454", "2603"):
            obs.append({"target": t, "asof": asof, "qgrid": grid_true,
                        "realized": math.exp(sigma * math.sqrt(21) * rng.standard_normal()) - 1.0})
    arms, notes = build_arms(obs, normal_q_grid(sigma * 3))
    chk("五臂全在", sorted(arms) == sorted(REQUIRED_ARMS))
    chk("live/ceiling/floor 觀測數=全量", all(len(arms[a]) == len(obs) for a in ("live", "ceiling", "floor")))
    for ck, m in notes["derangement_map"].items():
        chk(f"mismatched@{ck} 無定點(derangement)", all(a != b for a, b in m.items()))
    sh_real = sorted(r for _, r, _ in arms["shuffled"])
    lv_real = sorted(r for _, r, _ in arms["live"])
    chk("shuffled 實現值多重集=live(僅重排)", np.allclose(sh_real, lv_real))
    floor_cones = {id(q) for q, _, _ in arms["floor"]}
    chk("floor 全 target 全 asof 同一錐(常數錐)", len(floor_cones) == 1)
    try:
        assert_arms_complete({a: arms[a] for a in REQUIRED_ARMS if a != "floor"})
        chk("缺臂必 raise", False)
    except ArmIncomplete:
        chk("缺臂必 raise", True)
    chk("derangement n=1 誠實 None", derangement_map(1, np.random.default_rng(42)) is None)
    d5 = derangement_map(5, np.random.default_rng(42))
    chk("derangement n=5 為無定點置換", d5 is not None and sorted(d5) == list(range(5))
        and not np.any(d5 == np.arange(5)))
    # seed=3 之首抽置換含定點(親驗)→ 唯 retry 迴圈真在才回無定點解(突變絆線:容許定點必紅)
    d5_retry = derangement_map(5, np.random.default_rng(3))
    chk("derangement 首抽含定點時 retry 至無定點", d5_retry is not None
        and not np.any(d5_retry == np.arange(5)))

    # -- 4) 合成常態回歸:真分佈之錐 → 覆蓋收斂名目值/PIT 近均勻/CRPS live<floor(3σ)
    rng2 = np.random.default_rng(11)
    n_big = 4000
    realized = np.exp(sigma * math.sqrt(21) * rng2.standard_normal(n_big)) - 1.0
    pairs = [(grid_true, float(r), f"c{i % 5}") for i, r in enumerate(realized)]
    m_live = arm_metrics(pairs)
    chk(f"cov_p50 收斂名目(得 {m_live['cov_p50']:.3f})", abs(m_live["cov_p50"] - 0.50) < 0.03)
    chk(f"cov_p80 收斂名目(得 {m_live['cov_p80']:.3f})", abs(m_live["cov_p80"] - 0.80) < 0.03)
    chk(f"cov_p90 收斂名目(得 {m_live['cov_p90']:.3f})", abs(m_live["cov_p90"] - 0.90) < 0.03)
    chk(f"PIT 近均勻(KS={m_live['pit_ks_stat']:.4f})", m_live["pit_ks_stat"] < 0.03)
    grid_floor3 = normal_q_grid(sigma * 3)
    m_floor = arm_metrics([(grid_floor3, float(r), f"c{i % 5}") for i, r in enumerate(realized)])
    chk("正確錐 CRPS < 3σ 樣板錐 CRPS", m_live["crps_mean"] < m_floor["crps_mean"])
    deltas = [m_floor["cluster_crps_mean"][c] - m_live["cluster_crps_mean"][c]
              for c in m_live["cluster_crps_mean"]]
    chk("k2 LCB:真差距為正之簇 bootstrap LCB>0", cluster_bootstrap_lcb(deltas) > 0)
    noise = [1e-6, -1e-6, 2e-7, -3e-7, 1e-7]
    chk("k2 LCB:零差距噪音 LCB<=0", cluster_bootstrap_lcb(noise) <= 0)
    pits_u = list(np.random.default_rng(3).random(300))
    p_u = pit_ks_p_cluster_bootstrap([100, 100, 100], ks_uniform_stat(pits_u))
    chk(f"KS-p 均勻 PIT 不判死(p={p_u:.3f})", p_u >= 0.05)
    p_bad = pit_ks_p_cluster_bootstrap([100, 100, 100], ks_uniform_stat([0.9] * 300))
    chk(f"KS-p 集中 PIT 判死(p={p_bad:.4f})", p_bad < 0.05)

    # -- 5) 口徑小件:凍結清單 sha/格點/PIT 夾取/q_grid 正規化
    chk("凍結清單 sha 口徑=排序\\n串接", frozen_targets_sha(["2317", "1101"]) == sha256_hex("1101\n2317"))
    days = list(range(100))
    chk("格點=index 0,21,42,63,84", grid_asofs(days) == [0, 21, 42, 63, 84])
    chk("PIT 端點外夾取", pit_from_qgrid(grid_true, grid_true[0] - 1)[0] == PIT_CLAMP[0]
        and pit_from_qgrid(grid_true, grid_true[-1] + 1)[0] == PIT_CLAMP[1])
    chk("q_grid dict 形可正規化", normalize_q_grid(
        {"terminal_q_grid": {f"p{i}": grid_true[i - 1] for i in range(1, 100)}}) is not None)
    chk("q_grid 巢狀形（dict 子鍵形）可解",
        normalize_q_grid({"terminal_q_grid": {"unit": "x",
            "p": {f"p{i}": grid_true[i - 1] for i in range(1, 100)}}}) is not None)
    # **契約絆線**：fixture 取自 runner 之真 _q_grid 輸出（非手寫形狀）——runner 改形狀即紅。
    try:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location(
            "_runner_for_contract", str(Path(__file__).resolve().parent / "run_sim_calibration_cell.py"))
        _rn = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_rn)
        _real = {"terminal_q_grid": {"unit": "terminal_simple_return_vs_asof_close",
                                     "p": _rn._q_grid(np.asarray(grid_true))}}
        chk("**W5→W3 契約**：evaluator 收得下 runner 真輸出（形狀變即紅）",
            normalize_q_grid(_real) is not None)
    except Exception as _e:                       # noqa: BLE001
        chk(f"**W5→W3 契約**：runner 不可 import（{type(_e).__name__}）——誠實紅，不當跳過", False)
    chk("q_grid 缺=None(物理擋史料)", normalize_q_grid({"terminal": {}}) is None)
    chk("q_grid 非單調=None", normalize_q_grid({"terminal_q_grid": [1.0] + [0.0] * 98}) is None)

    # -- 6) M-M1 寫入閘:n_valid 不足即零 INSERT。fixture 全取自本檔上游真輸出
    #      (obs → build_arms → arm_metrics;thresholds 經 _load_and_verify_gate 真解析),非手寫形狀。
    class _CountingCursor:
        """只數 execute 次數之假 cursor:證明「不允寫時 0 次 INSERT」是行為、不是文字。"""

        def __init__(self):
            self.executed = []
            self.rowcount = 1

        def execute(self, sql, params=None):
            self.executed.append(sql)

    def _th_of(payload_text):
        body = "門:SELFTEST 寫入閘\nthresholds_sha=" + sha256_hex(payload_text)
        return _load_and_verify_gate(_FakeCursor(_make_gate_row(body, payload_text)))["thresholds"]

    th_strict = _th_of('{"n_valid_min": 100, "date_clusters_min": 3}')
    th_loose = _th_of('{"n_valid_min": 10, "date_clusters_min": 3}')
    m_real = {a: arm_metrics(arms[a]) for a in REQUIRED_ARMS}
    present = [a for a in arms if arms[a]]
    nv, kk = len(obs), len({o["asof"] for o in obs})
    chk(f"M-M1 fixture 取自真上游(n_valid={nv} K={kk})", nv == m_real["live"]["n"] and kk == 3)

    def _try_write(th, n_valid, k_clusters, arms_present=None):
        c = _CountingCursor()
        n, why = _insert_eval_rows(
            c, th=th, n_valid=n_valid, k_clusters=k_clusters,
            arms_present=present if arms_present is None else arms_present,
            metrics=m_real, detail_common={"gate_id": GATE_ID}, candidate_id="SELFTEST",
            eval_set_id="R1:h21:selftest", code_hash="0" * 64, n_runs=n_valid, n_excluded=0,
            pit_p=0.5, git_sha="0000000")
        return n, why, len(c.executed)

    n_b, why_b, ex_b = _try_write(th_strict, nv, kk)
    chk(f"M-M1 紅:K={kk} 達標但 n_valid={nv}<100 ⇒ 零 INSERT", n_b == 0 and ex_b == 0)
    chk("M-M1 紅:拒寫事由指名 n_valid(K 已達標故不在事由內)",
        any("n_valid" in r for r in why_b) and not any("date_clusters" in r for r in why_b))
    n_g, why_g, ex_g = _try_write(th_loose, nv, kk)
    chk("M-M1 綠:n_valid 與 K 皆達標 ⇒ 五臂全寫", n_g == 5 and ex_g == 5 and why_g == [])
    n_k, _, ex_k = _try_write(th_loose, nv, 2)
    chk("M-M1:原有 K 閘不得回退(K=2<3 仍零 INSERT)", n_k == 0 and ex_k == 0)
    n_a, why_a, ex_a = _try_write(th_loose, nv, kk, arms_present=["live", "ceiling", "floor"])
    chk("M-M1:缺臂亦零 INSERT", n_a == 0 and ex_a == 0 and any("缺臂" in r for r in why_a))

    # -- 7) M-M2 煞車:_kill_state 須吃 env(evaluator 曾是 sim 軸四支中唯一 fail-open 的一支)
    class _KillCursor:
        def __init__(self, states):
            self._states = states

        def execute(self, sql, params=None):
            pass

        def fetchall(self):
            return [(s,) for s in self._states]

    _prev_env = os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH")
    try:
        os.environ["AUGUR_EVOLUTION_KILL_SWITCH"] = "halt"
        chk("M-M2 紅:DB 全 clear 但 env=halt ⇒ 有效態 halt(不傳 env_halt 即回 clear=fail-open)",
            _kill_state(_KillCursor(["clear", "clear"])) == "halt")
        chk("M-M2:env=halt 於零列(表無列)亦 halt", _kill_state(_KillCursor([])) == "halt")
        os.environ["AUGUR_EVOLUTION_KILL_SWITCH"] = "  HALT "
        chk("M-M2:env 大小寫/空白正規化後仍 halt", _kill_state(_KillCursor(["clear"])) == "halt")
        os.environ.pop("AUGUR_EVOLUTION_KILL_SWITCH", None)
        chk("M-M2 綠:env 未設且 DB 全 clear ⇒ clear",
            _kill_state(_KillCursor(["clear", "clear"])) == "clear")
        chk("M-M2:DB scope halt 仍 halt(OR 語意未因加 env 而失)",
            _kill_state(_KillCursor(["clear", "halt"])) == "halt")
    finally:
        os.environ.pop("AUGUR_EVOLUTION_KILL_SWITCH", None)
        if _prev_env is not None:
            os.environ["AUGUR_EVOLUTION_KILL_SWITCH"] = _prev_env

    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args, _ = ap.parse_known_args()
    if args.selftest:
        return _selftest()
    if args.dry_run or args.apply:
        from augur.core import db
        try:
            with db.connect() as conn:
                return _evaluate(conn, apply_mode=args.apply)
        except (GateRefusal, ArmIncomplete) as e:
            print(f"✗ 拒評(零寫入): {e}")
            return 1
    return status()


if __name__ == "__main__":
    sys.exit(main())
