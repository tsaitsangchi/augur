#!/usr/bin/env python
"""S-1 單一基線候選 propose 工具 — sim 軸 R1 之唯一候選列（`sim_evolution_candidate`）。

🎯 這支在做什麼(白話): SIM-CAL-R1 門已生效但候選 0 列 ⇒ live run 無法入鏈（`sim_run_link.candidate_id`
   NOT NULL）。本支讀 live `simulation_method_registry` 之 iid_bootstrap `param_schema`（人審後 JSON、
   gate_ref=gp_df544cbb1b94），構造 R1 基線 spec（required 三欄；h 由門 thresholds.horizon_td=[21] 釘定、
   n_paths/seed 取 schema x-observed 之單一史料值＝10000/42）、算 spec_sha（canonical JSON sha256）、
   驗 spec 對 param_schema（fail-closed 子集驗證器），組成一列候選供 `--dry-run` 過目／`--apply` 真寫。
   冪等：同 spec_sha 已在＝跳過；同 candidate_id 但異 spec_sha＝拒（人裁）。寫入路徑讀 kill switch
   （scope sim/global，OR 語意 halt 即拒寫）。

origin='carryover' 說理（CHECK 白名單 2026-08-02 psql 親讀 `sim_evolution_candidate_origin_check`
＝{llm_local, grid, human, carryover}；專章 §2.2-2.3）：本候選 spec 逐欄承襲 `mc_simulation_run`
261 列 iid_bootstrap 史料基線（registry param_schema x-observed：n_paths 唯一值 10000、seed 唯一值
42；horizon_td=21 由門釘定且在史料觀測值域 {21,30,42,60,63,126} 內）——非 LLM 提案（非 llm_local，
故 §2.3 is_synthetic 強制不適用、DB default true 不改亦無害）、非參數網格枚舉（非 grid）、非人另行
創新規格（非 human）；係「既有已入冊方法之史料基線規格承襲入 R1」⇒ origin='carryover'
（W3W5 計畫 §4.1；Steward 2026-08-02「simW-照建議」S-1 圈選單一基線候選含 carryover 認定）。
trust_rank='TR-C'（DB CHECK 唯一值；§2.3 天花板）、status='candidate'（§2.4 不得表述為已確立）。

守 #9/#10（spec 值全溯 registry/門 live 讀，零猜測——無單一史料值即 fail-closed 拒）· #15（防衛先驗紅：
壞 sha/壞 schema/halt 必拒）· #29a/d · 專章 §2.2-2.4。人簽欄零觸碰（候選列無人簽欄；晉升三鎖在 verdict 層）。

執行指令矩陣:
  python scripts/propose_sim_candidate.py             # 無參數:現況(唯讀:registry/門/候選水位/kill 狀態)
  python scripts/propose_sim_candidate.py --dry-run   # 唯讀:構造+驗證+印將寫列全欄+冪等判定(零寫入)
  python scripts/propose_sim_candidate.py --apply     # 真寫一列(kill/門 sha/registry/schema 防衛全過才寫;冪等)
  python scripts/propose_sim_candidate.py --selftest  # 零 DB:schema 驗證紅綠+突變驗紅+FakeCursor 行為測(halt 拒寫/假門拒/冪等跳過)
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

METHOD = "iid_bootstrap"
GATE_ID = "SIM-CAL-R1"
CANDIDATE_ID = "simc_r1_iid_baseline"
ORIGIN = "carryover"
ORIGIN_REF = "mc_simulation_run 261 列史料基線（H2 入冊 gp_df544cbb1b94）"
NOTE = "engine window=756td（HIST_WINDOW_TD 常數；param_schema 外，據實記載）"
RC_KILL = 75          # EX_TEMPFAIL 慣例（同 run_raw_evolution_iteration halt 路徑）


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


# ---------------------------------------------------------------- 純函式層（selftest 餵真輸入）

def canonical_spec_json(spec: dict) -> str:
    """spec 之正規化 JSON（sort_keys＋緊湊分隔）——spec_sha 之唯一口徑（W3W5 計畫 §4.1）。"""
    return json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def spec_sha256(spec: dict) -> str:
    return hashlib.sha256(canonical_spec_json(spec).encode("utf-8")).hexdigest()


_VALIDATION_KEYS = {"type", "required", "properties", "additionalProperties"}
_ANNOTATION_KEYS = {"title", "description", "default", "examples", "$schema", "$id"}


def validate_spec(spec, schema, path="$"):
    """spec 對 param_schema 之子集驗證器。回 error list（空＝通過）。

    支援鍵＝registry 現行 schema 實際使用者（type object/integer、required、properties、
    additionalProperties:false）；x-*／註記鍵忽略；**其餘驗證關鍵字一律 raise NotImplementedError**
    ——fail-closed：schema 若新增本支不懂的約束，寧可炸也不靜默放行（#15）。
    （venv 無 jsonschema 套件＝親驗 2026-08-02；本驗證器零外部依賴、射程誠實標明。）
    """
    unknown = [k for k in schema
               if k not in _VALIDATION_KEYS and k not in _ANNOTATION_KEYS and not k.startswith("x-")]
    if unknown:
        raise NotImplementedError(f"{path}: schema 含未支援之驗證關鍵字 {unknown}——fail-closed 拒絕靜默略過")
    errs = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(spec, dict):
            return [f"{path}: 應為 object,得 {type(spec).__name__}"]
        for req in schema.get("required", []):
            if req not in spec:
                errs.append(f"{path}: 缺 required 欄 {req}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties", True) is False:
            for k in spec:
                if k not in props:
                    errs.append(f"{path}: 多餘欄 {k}（additionalProperties:false）")
        for k, sub in props.items():
            if k in spec:
                errs += validate_spec(spec[k], sub, f"{path}.{k}")
    elif t == "integer":
        if not isinstance(spec, int) or isinstance(spec, bool):
            errs.append(f"{path}: 應為 integer,得 {type(spec).__name__}")
    else:
        raise NotImplementedError(f"{path}: 未支援之 type={t!r}——fail-closed")
    return errs


def resolve_h_pinned(thresholds: dict) -> int:
    """門 thresholds.horizon_td 必為單一 horizon 之 list（R1 唯 h=21）；否則設計前提不成立即拒。"""
    hs = (thresholds or {}).get("horizon_td")
    if not isinstance(hs, list) or len(hs) != 1 or not isinstance(hs[0], int) or isinstance(hs[0], bool):
        raise ValueError(f"門 thresholds.horizon_td 非單一 horizon: {hs!r}——R1 單 h 前提不成立,停手")
    return hs[0]


def build_baseline_spec(param_schema: dict, h_pinned: int) -> dict:
    """依 registry schema 構造基線 spec：required 逐欄；horizon_td=門釘值（須在 x-observed 值域內＝
    carryover 語意自證）；其餘欄取 x-observed 之**單一**史料值，非單一即 fail-closed 拒（#9 不猜）。"""
    props = param_schema.get("properties", {})
    spec = {}
    for field in param_schema.get("required", []):
        obs_vals = props.get(field, {}).get("x-observed", {}).get("values", [])
        if field == "horizon_td":
            if h_pinned not in obs_vals:
                raise ValueError(f"h={h_pinned} 不在史料觀測值域 {obs_vals}——carryover 語意不成立,拒")
            spec[field] = h_pinned
            continue
        if len(obs_vals) != 1:
            raise ValueError(f"required 欄 {field} 無單一史料基線值（x-observed.values={obs_vals}）——不猜,拒")
        spec[field] = obs_vals[0]
    return spec


def build_candidate_row(spec: dict, git_sha: str) -> dict:
    """組成將寫之候選列（is_synthetic 不入列＝留 DB default true；carryover 非 llm_local 不受 §2.3 強制）。"""
    return {"candidate_id": CANDIDATE_ID, "method": METHOD, "spec": spec, "spec_sha": spec_sha256(spec),
            "origin": ORIGIN, "origin_ref": ORIGIN_REF, "trust_rank": "TR-C", "status": "candidate",
            "gate_ref": GATE_ID, "note": NOTE, "git_sha": git_sha}


def decide_action(existing_rows, row: dict):
    """冪等判定（純函式）。existing_rows＝[(candidate_id, spec_sha, status)]。
    回 ('insert'|'skip'|'conflict', 訊息)。"""
    if not existing_rows:
        return "insert", "無同 spec_sha / candidate_id 既有列 → INSERT"
    for cid, sha, st in existing_rows:
        if sha == row["spec_sha"]:
            return "skip", f"同 spec_sha 已在（candidate_id={cid}, status={st}）→ 跳過（冪等）"
    return "conflict", f"candidate_id={row['candidate_id']} 已在但 spec_sha 不同 → 拒（PK 撞名,人裁）"


# ---------------------------------------------------------------- DB 流程（cursor 注入＝selftest 可 Fake）

def _kill_state(cur) -> str:
    """sim 軸有效 kill 狀態（sim ∨ global；OR 語意 fail-safe）。口徑單一住所＝
    `augur.philosophy.evolution.effective_kill_state`（#12；KILL_SCOPES 已含 sim）。"""
    from augur.philosophy.evolution import effective_kill_state
    cur.execute("SELECT state FROM evolution_kill_switch WHERE scope IN ('sim','global')")
    return effective_kill_state(
        [r[0] for r in cur.fetchall()],
        env_halt=os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == "halt")


def _construct(cur) -> dict:
    """讀 live registry＋門 → 構造候選列。任一防衛不過即 raise（fail-closed、零寫入）。"""
    cur.execute("SELECT param_schema, status FROM simulation_method_registry WHERE method=%s", (METHOD,))
    reg = cur.fetchone()
    if reg is None:
        raise RuntimeError(f"registry 無 {METHOD} 列——先入冊（H2）再提案")
    schema, reg_status = reg
    if reg_status != "registered":
        raise RuntimeError(f"{METHOD} registry status={reg_status}≠registered——拒提案")
    cur.execute("""SELECT status, criteria->>'criteria_text', criteria_sha, criteria->'thresholds'
                     FROM evolution_prereg_gate WHERE gate_id=%s""", (GATE_ID,))
    gate = cur.fetchone()
    if gate is None:
        raise RuntimeError(f"門 {GATE_ID} 不存在——拒提案")
    g_status, ctext, csha, thresholds = gate
    if g_status != "approved":
        raise RuntimeError(f"門 {GATE_ID} status={g_status}≠approved——拒提案")
    if hashlib.sha256((ctext or "").encode("utf-8")).hexdigest() != csha:
        raise RuntimeError(f"門 {GATE_ID} criteria_text 指紋覆算不符 criteria_sha——拒（防移動球門；"
                           "評估紀律之拒評條款延伸到提案端）")
    spec = build_baseline_spec(schema, resolve_h_pinned(thresholds))
    errs = validate_spec(spec, schema)
    if errs:
        raise RuntimeError("spec 未過 registry param_schema 驗證: " + "; ".join(errs))
    return build_candidate_row(spec, _git7())


def _existing(cur, row: dict):
    cur.execute("""SELECT candidate_id, spec_sha, status FROM sim_evolution_candidate
                    WHERE spec_sha=%s OR candidate_id=%s""", (row["spec_sha"], row["candidate_id"]))
    return cur.fetchall()


def _print_row(row: dict):
    print("── 將寫列（sim_evolution_candidate 全欄）──")
    for k in ("candidate_id", "method", "spec", "spec_sha", "origin", "origin_ref",
              "trust_rank", "status", "gate_ref", "note", "git_sha"):
        v = canonical_spec_json(row[k]) if k == "spec" else row[k]
        print(f"  {k:<13}= {v}")
    print("  is_synthetic = (不入 INSERT；DB default true——carryover 非 llm_local 不受 §2.3 強制)")
    print("  created_at   = (DB default now())")


def cmd_dry_run(cur) -> int:
    kill = _kill_state(cur)
    row = _construct(cur)
    print(f"kill switch（sim∨global）= {kill}" + ("（--apply 將拒寫）" if kill == "halt" else ""))
    print("spec 對 registry param_schema 驗證 = 通過（0 error）")
    _print_row(row)
    act, msg = decide_action(_existing(cur, row), row)
    print(f"冪等判定 = {act}：{msg}")
    print("（--dry-run 零寫入；真寫請 --apply——本波不跑、歸主 session）")
    return 0


def cmd_apply(cur) -> int:
    if _kill_state(cur) == "halt":
        print("⛔ kill switch=halt（scope sim 或 global）——零寫入。"
              "解除須 Steward：UPDATE evolution_kill_switch SET state='clear' WHERE scope='sim';")
        return RC_KILL
    row = _construct(cur)
    act, msg = decide_action(_existing(cur, row), row)
    print(f"冪等判定 = {act}：{msg}")
    if act == "skip":
        return 0
    if act == "conflict":
        return 1
    from psycopg2.extras import Json
    cur.execute("""INSERT INTO sim_evolution_candidate
        (candidate_id, method, spec, spec_sha, origin, origin_ref, trust_rank, status, gate_ref, note, git_sha)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (row["candidate_id"], row["method"], Json(row["spec"]), row["spec_sha"], row["origin"],
         row["origin_ref"], row["trust_rank"], row["status"], row["gate_ref"], row["note"], row["git_sha"]))
    if cur.rowcount != 1:
        raise RuntimeError(f"INSERT rowcount={cur.rowcount}≠1——raise 使外層交易回滾")
    print(f"✅ 已提案 1 列：{row['candidate_id']} spec_sha={row['spec_sha'][:16]}…")
    return 0


def cmd_status(cur) -> int:
    print(f"== propose_sim_candidate 現況（唯讀）@ git {_git7()} ==")
    cur.execute("SELECT status, registered_at, gate_ref FROM simulation_method_registry WHERE method=%s",
                (METHOD,))
    reg = cur.fetchone()
    print(f"registry.{METHOD:<14}= " + (f"{reg[0]}（registered_at={reg[1]}, gate_ref={reg[2]}）"
                                        if reg else "（無列）"))
    cur.execute("SELECT status, approved_by, approved_at FROM evolution_prereg_gate WHERE gate_id=%s",
                (GATE_ID,))
    g = cur.fetchone()
    print(f"門 {GATE_ID:<13}= " + (f"{g[0]}（approved_by={g[1]}, approved_at={g[2]}）" if g else "（無列）"))
    cur.execute("SELECT count(*), count(*) FILTER (WHERE gate_ref=%s) FROM sim_evolution_candidate",
                (GATE_ID,))
    tot, mine = cur.fetchone()
    print(f"sim_evolution_candidate = 全表 {tot} 列／gate_ref={GATE_ID} {mine} 列")
    print(f"kill switch（sim∨global）= {_kill_state(cur)}")
    print("下一步：--dry-run 過目將寫列；--apply 真寫（冪等）")
    return 0


# ---------------------------------------------------------------- selftest（零 DB）

# live 親讀節錄 2026-08-02（simulation_method_registry.iid_bootstrap，registered_at=2026-08-01 21:53、
# gate_ref=gp_df544cbb1b94）：驗證／建構相干鍵全量照錄；x-provenance／x-unclassified 等長註記段省略
# ——x-* 為註記、驗證器一律忽略，省略不改變驗證行為。
_REAL_PARAM_SCHEMA = {
    "type": "object",
    "required": ["horizon_td", "n_paths", "seed"],
    "properties": {
        "seed": {"type": "integer",
                 "x-observed": {"max": 42, "min": 42, "n_rows": 261, "values": [42], "n_nonnull": 261}},
        "n_paths": {"type": "integer",
                    "x-observed": {"max": 10000, "min": 10000, "n_rows": 261, "values": [10000],
                                   "n_nonnull": 261}},
        "horizon_td": {"type": "integer",
                       "x-observed": {"max": 126, "min": 21, "n_rows": 261,
                                      "values": [21, 30, 42, 60, 63, 126], "n_nonnull": 261}},
    },
    "additionalProperties": False,
}

# 回歸鎖：基線 spec 之 canonical sha（W3W5 計畫 §4.1 口徑）。canonical 口徑或基線值任何漂移即紅。
_EXPECTED_BASELINE_SHA = "0f7212e4d87c7d03cd44751f11861c95598dffc45afb569ce8dcd2548e995301"
_REAL_THRESHOLDS_H = {"horizon_td": [21]}   # live 親讀節錄（criteria->'thresholds'->'horizon_td'）


class _FakeCursor:
    """依序回放 scripted 結果之假 cursor（零 DB；executed 記錄全部 SQL 供下游絆線斷言）。"""
    def __init__(self, script):
        self.script = list(script)
        self.executed = []
        self.rowcount = 1
        self._last = []

    def execute(self, sql, params=None):
        self.executed.append((" ".join(sql.split()), params))
        self._last = self.script.pop(0) if self.script else []

    def fetchone(self):
        return self._last[0] if self._last else None

    def fetchall(self):
        return list(self._last)

    def n_inserts(self):
        return sum(1 for s, _ in self.executed if s.upper().startswith("INSERT"))


def _gate_row(tamper=False):
    """合成門列（sha 由真算得——防衛測的是「覆算不符即拒」之行為，非特定文字）。"""
    ctext = "selftest 合成 criteria_text（非真門文字）"
    csha = hashlib.sha256(ctext.encode("utf-8")).hexdigest()
    if tamper:
        ctext += "（被動過）"
    return ("approved", ctext, csha, _REAL_THRESHOLDS_H)


def _apply_script(gate_row, existing, kill="clear"):
    """cmd_apply 之 execute 順序：kill → registry → gate → existing →（INSERT）。"""
    return [[(kill,)], [(_REAL_PARAM_SCHEMA, "registered")], [gate_row], existing, []]


def _selftest() -> int:
    fails = []

    def chk(name, ok):
        print(("  ✅ " if ok else "  ❌ ") + name)
        if not ok:
            fails.append(name)

    def raises(fn, exc=Exception):
        try:
            fn()
            return False
        except exc:
            return True

    print("[1] 基線構造＋canonical sha（餵真 schema）")
    spec = build_baseline_spec(_REAL_PARAM_SCHEMA, 21)
    chk("基線 spec = {horizon_td:21, n_paths:10000, seed:42}",
        spec == {"horizon_td": 21, "n_paths": 10000, "seed": 42})
    chk("spec_sha 命中回歸鎖（canonical 口徑不漂）", spec_sha256(spec) == _EXPECTED_BASELINE_SHA)
    chk("spec_sha 鍵序不變性", spec_sha256({"seed": 42, "horizon_td": 21, "n_paths": 10000})
        == _EXPECTED_BASELINE_SHA)
    chk("值突變 → sha 必變（驗紅）", spec_sha256({**spec, "seed": 43}) != _EXPECTED_BASELINE_SHA)
    chk("h 不在史料值域 → 拒（carryover 語意）", raises(lambda: build_baseline_spec(_REAL_PARAM_SCHEMA, 22),
                                                        ValueError))
    _multi = json.loads(json.dumps(_REAL_PARAM_SCHEMA))
    _multi["properties"]["n_paths"]["x-observed"]["values"] = [10000, 20000]
    chk("非單一史料值 → 拒不猜", raises(lambda: build_baseline_spec(_multi, 21), ValueError))
    chk("thresholds [21] → 21", resolve_h_pinned(_REAL_THRESHOLDS_H) == 21)
    chk("thresholds 多 h → 拒", raises(lambda: resolve_h_pinned({"horizon_td": [21, 42]}), ValueError))
    chk("thresholds 缺 h → 拒", raises(lambda: resolve_h_pinned({}), ValueError))

    print("[2] spec 對 param_schema 驗證（真 schema；通過／壞 spec 拒／突變驗紅）")
    chk("基線 spec 驗證通過（0 error）", validate_spec(spec, _REAL_PARAM_SCHEMA) == [])
    chk("缺 required（無 seed）→ 拒",
        validate_spec({"horizon_td": 21, "n_paths": 10000}, _REAL_PARAM_SCHEMA) != [])
    chk("多餘欄 → 拒（additionalProperties:false）",
        validate_spec({**spec, "tilt": 1}, _REAL_PARAM_SCHEMA) != [])
    chk("型別錯（n_paths 為字串）→ 拒",
        validate_spec({**spec, "n_paths": "10000"}, _REAL_PARAM_SCHEMA) != [])
    chk("bool 冒充 integer → 拒", validate_spec({**spec, "seed": True}, _REAL_PARAM_SCHEMA) != [])
    _unk = json.loads(json.dumps(_REAL_PARAM_SCHEMA))
    _unk["properties"]["seed"]["minimum"] = 0
    chk("schema 含未支援驗證關鍵字 → raise（fail-closed 非靜默放行）",
        raises(lambda: validate_spec(spec, _unk), NotImplementedError))
    chk("未支援 type → raise", raises(lambda: validate_spec("x", {"type": "string"}), NotImplementedError))

    print("[3] 冪等判定（純函式）")
    row = build_candidate_row(spec, "selftest")
    chk("空表 → insert", decide_action([], row)[0] == "insert")
    chk("同 spec_sha 已在 → skip",
        decide_action([(CANDIDATE_ID, row["spec_sha"], "candidate")], row)[0] == "skip")
    chk("同 candidate_id 異 spec_sha → conflict",
        decide_action([(CANDIDATE_ID, "deadbeef", "candidate")], row)[0] == "conflict")

    print("[4] kill switch 口徑（單一住所之純函式）")
    from augur.philosophy.evolution import effective_kill_state as _eks
    chk("任一 scope halt ⇒ halt（OR fail-safe）", _eks(["clear", "halt"]) == "halt")
    chk("全 clear ⇒ clear", _eks(["clear", "clear"]) == "clear")
    chk("env AUGUR_EVOLUTION_KILL_SWITCH=halt 可強制", _eks(["clear"], env_halt=True) == "halt")

    print("[5] FakeCursor 行為測（下游絆線：拒絕路徑必零 INSERT）")
    cur = _FakeCursor(_apply_script(_gate_row(), [], kill="halt"))
    rc = cmd_apply(cur)
    chk(f"halt → rc={RC_KILL} 且零 INSERT（絆線）", rc == RC_KILL and cur.n_inserts() == 0)
    cur = _FakeCursor(_apply_script(_gate_row(tamper=True), []))
    chk("門 criteria_text 被動（sha 覆算不符）→ raise 且零 INSERT",
        raises(lambda: cmd_apply(cur), RuntimeError) and cur.n_inserts() == 0)
    cur = _FakeCursor([[("clear",)], [(_REAL_PARAM_SCHEMA, "retired")]])
    chk("registry retired → raise 且零 INSERT", raises(lambda: cmd_apply(cur), RuntimeError)
        and cur.n_inserts() == 0)
    cur = _FakeCursor(_apply_script(_gate_row(), [(CANDIDATE_ID, spec_sha256(spec), "candidate")]))
    chk("同 spec_sha 已在 → rc=0 且零 INSERT（冪等跳過）", cmd_apply(cur) == 0 and cur.n_inserts() == 0)
    cur = _FakeCursor(_apply_script(_gate_row(), []))
    rc = cmd_apply(cur)
    ins = [(s, p) for s, p in cur.executed if s.upper().startswith("INSERT")]
    chk("清路 → rc=0 且恰 1 INSERT", rc == 0 and len(ins) == 1)
    ok_params = bool(ins) and ins[0][1][0] == CANDIDATE_ID and ins[0][1][3] == _EXPECTED_BASELINE_SHA \
        and ins[0][1][4] == ORIGIN and ins[0][1][6] == "TR-C" and ins[0][1][7] == "candidate"
    chk("INSERT 參數＝候選列（id/sha/origin=carryover/TR-C/candidate）", ok_params)

    print(f"\n== selftest：{'全數通過' if not fails else f'{len(fails)} 項失敗'} ==")
    return 0 if not fails else 1


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="S-1 單一基線候選 propose 工具（sim 軸 R1）")
    ap.add_argument("--dry-run", action="store_true", help="唯讀:構造+驗證+印將寫列全欄(零寫入)")
    ap.add_argument("--apply", action="store_true", help="真寫一列(防衛全過才寫;冪等)")
    ap.add_argument("--selftest", action="store_true", help="零 DB 紅綠自測")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    from augur.core import db
    try:
        with db.connect() as conn:
            if args.apply:
                with db.transaction(conn) as cur:
                    return cmd_apply(cur)
            with db.transaction(conn) as cur:      # 唯讀模式亦走交易（結束 commit 之唯讀無副作用）
                return cmd_dry_run(cur) if args.dry_run else cmd_status(cur)
    except Exception as e:                          # graceful:無參數/唯讀模式不得裸 traceback(#29a)
        print(f"✗ {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
