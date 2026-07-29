#!/usr/bin/env python
"""SRC-AUTO 謂詞引擎 — 六機械謂詞全過才 auto-approve;AI 零放行權(SRC-AUTO-go,hugo 2026-07-28)。

🎯 這支在做什麼(白話):3,528 個 proposed 來源不可能逐源 TTY 人批,但「依 AI 判斷審批」撞四條憲政
   (能抓≠該抓人閘/LLM 意見零證據力/能力無 A′ 證據/模型自選教材之利益衝突)。本支=PME-AUTO-B 同型:
   **人簽規則一次(SRC-AUTO-go),機器只在規則內自動**——六謂詞全部機械可驗,全過才放行:
     P1 license:兩條路皆機械——(路甲)source_key 匹配 source_license_whitelist(人 seed 帶 citation);
        (路乙,REGIME-MAP-v1 hugo 2026-07-28 核可)adapter_config->'re3data'->'licenses' 證據查
        license_regime_map(R1-R4 人簽 pattern;NC/ND code 側一票否決、多授權取最嚴、未映射=人閘)
        ——regime ∈ {public_domain, cc_whitelist} 才過(兩路皆空=不過,fail-closed)
     P2 domain ∈ 既核域集(=active 源之 domain 集,資料驅動;新域必人)
     P3 adapter ∈ 既核 adapter 集(=active 源之 adapter 集;新協定必人)
     P4 probe:近 30 日 review_log probe 之 http_status ∈ 2xx(#25 最小探測先行)
     P5 限速前置:pace_seconds/quota_limit/est_scale 皆已設 且 est_scale ≤ 50,000(#24)
     P6 tier ∉ {T3,T4}(AUTHORITY-TIER 落地後生效;欄未在=記「另案未接」不擋)
     P7 端點唯一(P7-go,hugo 2026-07-28):P1-P6 通過者中每 normalized OAI base 僅 min(source_key)
        代表可批;已 active 端點封鎖;其餘同端點列留 proposed(重複來源防呆,非拒絕)
   **護欄**:週上限 50 源;熔斷=任一 auto 批之源被事後 suspend → 拒絕再跑待人查;
   留痕=review_log(actor='auto_rules_v1', reason=逐謂詞 JSON)→ R6 digest 週掃視(P5.W5 監督不降)。
守 #26(規則內自動、碰線停)· #15(fail-closed;dry 分桶誠實)· #24/#25 · #29a/b/d。
SSOT=reports/augur_source_auto_review_plan_20260728.md。

執行指令矩陣:
  python scripts/auto_review_sources.py                 # 無參數:現況(週餘額/熔斷態/白名單數,唯讀)
  python scripts/auto_review_sources.py --dry-run       # 3,528 全量分桶統計(零寫入)
  python scripts/auto_review_sources.py --run --limit 10    # 實批(≤週餘額;全謂詞留痕)
  python scripts/auto_review_sources.py --selftest      # 零 DB 紅綠(謂詞邏輯/護欄)
"""
import argparse
import json
import re
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import curation

WEEKLY_CAP = 50            # 首月週上限(提額=規則修訂,人簽)
EST_SCALE_CAP = 50000      # P5 放量上限
PROBE_FRESH_DAYS = 30
AUTO_ACTOR = "auto_rules_v1"
P1_ALLOW = ("public_domain", "cc_whitelist")   # 納 metadata_only=規則 v2(人簽);dry 另印該假設統計
NC_ND_VETO = re.compile(r"[-/](nc|nd)\b", re.I)          # REGIME-MAP R-X:非商用/禁改作=必人
RESTRICT_ORDER = {"public_domain": 0, "cc_whitelist": 1}  # 多授權取最嚴(數字大=嚴)


def load_context(cur):
    """一次載入謂詞所需資料側(全部資料驅動)。"""
    cur.execute("SELECT provider_pattern, license_regime FROM source_license_whitelist")
    wl = cur.fetchall()
    cur.execute("SELECT kind, pattern, regime FROM license_regime_map")
    regime_map = cur.fetchall()
    cur.execute("SELECT DISTINCT domain FROM knowledge_source WHERE approval_status='active'")
    domains = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT DISTINCT adapter FROM knowledge_source WHERE approval_status='active'")
    adapters = {r[0] for r in cur.fetchall()}
    cur.execute("""SELECT DISTINCT ON (source_key) source_key,
                          (probe_result->>'http_status')::int AS st
                   FROM knowledge_source_review_log
                   WHERE action='probe' AND created_at > now() - make_interval(days => %s)
                   ORDER BY source_key, review_id DESC""", (PROBE_FRESH_DAYS,))
    probe_ok = {k for k, st in cur.fetchall() if st is not None and 200 <= st < 300}
    cur.execute("""SELECT 1 FROM information_schema.columns
                   WHERE table_name='knowledge_source' AND column_name='authority_tier'""")
    tier_wired = cur.fetchone() is not None
    return {"wl": wl, "regime_map": regime_map, "domains": domains, "adapters": adapters,
            "probe_ok": probe_ok, "tier_wired": tier_wired}


def wl_match(source_key, wl):
    """白名單 LIKE 匹配(最長 pattern 優先=最特定);回 regime|None。純函式。"""
    best = None
    for pat, regime in wl:
        like = pat.replace("%", "")
        hit = (source_key == pat) if "%" not in pat else source_key.startswith(like) \
            if pat.endswith("%") and pat.count("%") == 1 else like in source_key
        if hit and (best is None or len(pat) > len(best[0])):
            best = (pat, regime)
    return best[1] if best else None


def classify_licenses(licenses, regime_map):
    """REGIME-MAP-v1(hugo 核可 2026-07-28):license 證據列 → regime|None。純函式、fail-closed。
    NC/ND 一票否決(code 側,先於映射);name=整詞匹配(防 'OGL' 誤中 'Google')、url=子字串;
    多授權取最嚴;任一未映射/被否決 → None(R-X 人閘)。"""
    if not licenses:
        return None
    regimes = []
    for lic in licenses:
        name, url = (lic.get("name") or ""), (lic.get("url") or "")
        if NC_ND_VETO.search(name) or NC_ND_VETO.search(url):
            return None
        hit = None
        for kind, pat, regime in regime_map:
            m = (kind == "name" and re.search(
                    r"(?<![A-Za-z0-9])" + re.escape(pat) + r"(?![A-Za-z0-9])", name, re.I)) \
                or (kind == "url" and pat.lower() in url.lower())
            if m and (hit is None or RESTRICT_ORDER[regime] > RESTRICT_ORDER[hit]):
                hit = regime
        if hit is None:
            return None
        regimes.append(hit)
    return max(regimes, key=RESTRICT_ORDER.get)


def _est_int(est):
    """est_scale(TEXT 欄)→ int|None。非數字/負數=None=P5 誠實不過(F4 拆彈:str-vs-int 崩防)。純函式。"""
    try:
        v = int(str(est).strip())
        return v if v >= 0 else None
    except (ValueError, TypeError):
        return None


def judge_source(row, ctx):
    """回 (all_pass, checks dict)。row=(source_key,domain,adapter,pace,quota,est_scale,tier,lic_evidence)。"""
    k, dom, ada, pace, quota, est, tier, lic = row
    regime = wl_match(k, ctx["wl"])
    via = "whitelist" if regime else None
    if regime is None and lic:
        regime = classify_licenses(lic, ctx["regime_map"])
        via = "regime_map" if regime else None
    checks = {
        "P1_license": regime in P1_ALLOW,
        "P2_domain": dom in ctx["domains"],
        "P3_adapter": ada in ctx["adapters"],
        "P4_probe": k in ctx["probe_ok"],
        "P5_pacing": pace is not None and quota is not None
                     and (est is not None and _est_int(est) is not None
                          and _est_int(est) <= EST_SCALE_CAP),
        "P6_tier": (tier not in ("T3", "T4")) if ctx["tier_wired"] else None,  # None=另案未接,不擋
        "_regime": regime,
        "_regime_via": via,
    }
    core = [v for c, v in checks.items() if c.startswith("P") and v is not None]
    return all(core), checks


def _rows(cur):
    tier_sel = "authority_tier" if _tier_wired(cur) else "NULL"
    cur.execute(f"""SELECT source_key, domain, adapter, pace_seconds, quota_limit, est_scale,
                           {tier_sel}, adapter_config->'re3data'->'licenses'
                    FROM knowledge_source WHERE approval_status='proposed' ORDER BY source_key""")  # noqa: S608
    return cur.fetchall()


def _tier_wired(cur):
    cur.execute("""SELECT 1 FROM information_schema.columns
                   WHERE table_name='knowledge_source' AND column_name='authority_tier'""")
    return cur.fetchone() is not None


def endpoint_bases(cur, status):
    """{source_key: normalized base}——某審批狀態源之最新新鮮 2xx probe 端點(P7 資料側)。"""
    cur.execute("""SELECT DISTINCT ON (l.source_key) l.source_key,
                          split_part(l.probe_result->>'url','?',1)
                   FROM knowledge_source_review_log l
                   JOIN knowledge_source s ON s.source_key = l.source_key
                   WHERE s.approval_status = %s AND l.action='probe'
                     AND l.probe_result->>'http_status' IS NOT NULL
                     AND (l.probe_result->>'http_status')::int BETWEEN 200 AND 299
                     AND l.created_at > now() - make_interval(days => %s)
                   ORDER BY l.source_key, l.review_id DESC""", (status, PROBE_FRESH_DAYS))
    return dict(cur.fetchall())


def pick_endpoint_winners(passing, ep_of, active_bases):
    """P7(P7-go,hugo 2026-07-28):端點唯一——P1-P6 通過者中,每端點唯一代表(min source_key)可批;
    已 active 端點封鎖全部;無端點證據者不適用(pass-through)。純函式,回 (winners, dups)。"""
    by_base = {}
    for k in sorted(passing):
        b = ep_of.get(k)
        if b is None or b in active_bases:
            continue
        by_base.setdefault(b, k)
    winners = {k for k in passing
               if ep_of.get(k) is None or by_base.get(ep_of.get(k)) == k}
    return winners, set(passing) - winners


def breaker_tripped(cur):
    """熔斷:任一 auto 批之源現為 suspended → True(拒跑待人查)。"""
    cur.execute("""SELECT count(*) FROM knowledge_source s
                   WHERE s.approval_status='suspended'
                     AND EXISTS (SELECT 1 FROM knowledge_source_review_log l
                                 WHERE l.source_key=s.source_key AND l.actor=%s
                                   AND l.action='approve')""", (AUTO_ACTOR,))
    return cur.fetchone()[0] > 0


def weekly_remaining(cur):
    cur.execute("""SELECT count(*) FROM knowledge_source_review_log
                   WHERE actor=%s AND action='approve'
                     AND created_at > now() - interval '7 days'""", (AUTO_ACTOR,))
    return max(0, WEEKLY_CAP - cur.fetchone()[0])


def dry_run():
    from collections import Counter
    with db.connect() as conn, db.transaction(conn) as cur:
        ctx = load_context(cur)
        rows = _rows(cur)
        ep_of = endpoint_bases(cur, "proposed")
        active_eps = set(endpoint_bases(cur, "active").values())
        first_fail, meta_only_gain = Counter(), 0
        p1_via_map, passing = 0, []
        for row in rows:
            ok, checks = judge_source(row, ctx)
            p1_via_map += (checks["_regime_via"] == "regime_map")
            if ok:
                passing.append(row[0])
                continue
            for c in ("P1_license", "P2_domain", "P3_adapter", "P4_probe", "P5_pacing", "P6_tier"):
                if checks.get(c) is False:
                    first_fail[c] += 1
                    break
            if checks["_regime"] == "metadata_only":
                c2 = dict(checks)
                c2["P1_license"] = True
                if all(v for c, v in c2.items() if c.startswith("P") and v is not None):
                    meta_only_gain += 1
    winners, dups = pick_endpoint_winners(passing, ep_of, active_eps)
    print(f"── SRC-AUTO dry 分桶(proposed {len(rows)} 源;白名單 {len(ctx['wl'])} 列/"
          f"REGIME-MAP {len(ctx['regime_map'])} 列) ──")
    print(f"  ✅ 七謂詞全過(可自動):{len(winners)}")
    if dups:
        print(f"  ✗ P7_endpoint 重複端點(留 proposed,每端點唯一代表已在可自動桶):{len(dups)}")
    print(f"  ⓘ P1 由 REGIME-MAP(路乙)判入:{p1_via_map}(仍受 P4 probe/P5 pacing 閘)")
    for c, n in first_fail.most_common():
        print(f"  ✗ 首個未過={c}:{n}")
    print(f"  ⓘ 規則 v2 假設(P1 納 metadata_only 時另可自動):{meta_only_gain}(僅供人議,現規則不採)")
    if not ctx["wl"]:
        print("  ⚠ 白名單 0 列=P1 全數不過(fail-closed);首批 pattern 待 hugo 核(草案見計畫報告)")
    return 0


def run(limit):
    with db.connect() as conn:
        cur = conn.cursor()
        if breaker_tripped(cur):
            print("⛔ 熔斷:曾有 auto 批之源被 suspend——拒跑,待人查明復位(#26 碰護欄即停)")
            return 75
        rem = weekly_remaining(cur)
        if rem <= 0:
            print(f"⏸ 週上限 {WEEKLY_CAP} 已滿——本週不再自動批(提額=規則修訂人簽)")
            return 0
        ctx = load_context(cur)
        rows = _rows(cur)
        ep_of = endpoint_bases(cur, "proposed")
        active_eps = set(endpoint_bases(cur, "active").values())
        pre = {r[0] for r in rows if judge_source(r, ctx)[0]}
        winners, _ = pick_endpoint_winners(pre, ep_of, active_eps)
        n = 0
        for row in rows:
            if n >= min(limit, rem):
                break
            ok, checks = judge_source(row, ctx)
            if not ok or row[0] not in winners:
                continue
            k = row[0]
            checks["P7_endpoint"] = True
            checks["_endpoint"] = ep_of.get(k)
            regime = checks.pop("_regime")
            # 正規路=curation.transition 兩步(approve→activate),非裸 UPDATE——
            # 尊重 chk_ks_active_needs_approval 閘與狀態機;HUMAN_ONLY 之授權鏈=
            # SRC-AUTO-go+P2-16-核可(hugo 2026-07-28 簽),actor 誠實掛機器名不冒人簽。
            cur.execute("""UPDATE knowledge_source SET license_regime=coalesce(license_regime, %s)
                WHERE source_key=%s AND approval_status='proposed'""", (regime, k))
            conn.commit()
            try:
                curation.transition(k, "approve", AUTO_ACTOR, reason=json.dumps(
                    {"rule": "SRC-AUTO v1", "checks": checks}, ensure_ascii=False))
                curation.transition(k, "activate", AUTO_ACTOR,
                                    reason="SRC-AUTO v1 auto-activate(P2-16-核可;enabled=False 休眠池)")
            except (ValueError, PermissionError) as e:
                print(f"  ⚠ {k}: 狀態機拒絕——{e}(誠實跳過,不硬改)")
                continue
            n += 1
            print(f"  ✓ auto-approve {k}(regime={regime})")
    print(f"合計自動批 {n}(週餘額 {rem};留痕 review_log actor={AUTO_ACTOR} → R6 digest 掃視)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM source_license_whitelist")
        print(f"  白名單:{cur.fetchone()[0]} 列")
        print(f"  週餘額:{weekly_remaining(cur)}/{WEEKLY_CAP}")
        print(f"  熔斷:{'⛔ 已觸發' if breaker_tripped(cur) else 'clear'}")
        cur.execute("SELECT count(*) FROM knowledge_source WHERE approval_status='proposed'")
        print(f"  proposed 積壓:{cur.fetchone()[0]}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    wl = [("arxiv%", "cc_whitelist"), ("re3data_r3d100000001", "public_domain")]
    chk("wl:前綴 pattern 匹配", wl_match("arxiv_search", wl) == "cc_whitelist")
    chk("wl:精確鍵優先於前綴", wl_match("re3data_r3d100000001", wl + [("re3data%", "metadata_only")])
        == "public_domain")
    chk("wl:未列=None(fail-closed)", wl_match("unknown_src", wl) is None)
    RM = [("name", "CC0", "public_domain"), ("name", "OGL", "cc_whitelist"),
          ("url", "/licenses/by/", "cc_whitelist"), ("url", "publicdomain/zero", "public_domain")]
    ctx = {"wl": wl, "regime_map": RM, "domains": {"general"}, "adapters": {"generic_json"},
           "probe_ok": {"arxiv_search"}, "tier_wired": False}
    row_ok = ("arxiv_search", "general", "generic_json", 2, 100, 1000, None, None)
    chk("六謂詞全過=放行", judge_source(row_ok, ctx)[0])
    chk("P1 兩路皆空=不放", not judge_source(("x", "general", "generic_json", 2, 100, 1000, None, None), ctx)[0])
    chk("P2 新域=不放", not judge_source(("arxiv_search", "newdom", "generic_json", 2, 100, 1000, None, None), ctx)[0])
    chk("P4 無 probe=不放", not judge_source(("arxiv2", "general", "generic_json", 2, 100, 1000, None, None),
                                         {**ctx, "wl": [("arxiv%", "cc_whitelist")]})[0])
    chk("P5 pace 未設=不放", not judge_source(("arxiv_search", "general", "generic_json", None, 100, 1000, None, None), ctx)[0])
    chk("P5 est_scale 超限=不放",
        not judge_source(("arxiv_search", "general", "generic_json", 2, 100, EST_SCALE_CAP + 1, None, None), ctx)[0])
    # ── F4 拆彈(est_scale 為 TEXT 欄;SRC-QUALIFY Q1) ──
    chk("P5 文字數字='8214' 過(TEXT 欄慣例)",
        judge_source(("arxiv_search", "general", "generic_json", 2, 100, "8214", None, None), ctx)[0])
    chk("P5 非數字文字=誠實不過不炸", not judge_source(
        ("arxiv_search", "general", "generic_json", 2, 100, "n/a", None, None), ctx)[0])
    chk("P5 文字超限=不過", not judge_source(
        ("arxiv_search", "general", "generic_json", 2, 100, str(EST_SCALE_CAP + 1), None, None), ctx)[0])
    chk("P5 負數=不過", _est_int("-5") is None)
    chk("P6 tier 未接=None 不擋", judge_source(row_ok, ctx)[1]["P6_tier"] is None)
    chk("P6 接線後 T3 必人", not judge_source(("arxiv_search", "general", "generic_json", 2, 100, 10, "T3", None),
                                          {**ctx, "tier_wired": True})[0])
    chk("P6:未評(NULL)放行=簽核原文(hugo 2026-07-29「依 P6 簽核原文」;收緊須另簽)",
        judge_source(("arxiv_search", "general", "generic_json", 2, 100, 10, None, None),
                     {**ctx, "tier_wired": True})[1]["P6_tier"] is True)
    chk("metadata_only 不在 P1 放行集(納入=規則 v2 人簽)", "metadata_only" not in P1_ALLOW)
    # ── REGIME-MAP-v1 路乙(classify_licenses;hugo 核可 2026-07-28) ──
    chk("map:CC0 名(R1)→public_domain", classify_licenses([{"name": "CC0"}], RM) == "public_domain")
    chk("map:/licenses/by/ URL(R2)→cc_whitelist", classify_licenses(
        [{"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"}], RM) == "cc_whitelist")
    chk("map:-nc 一票否決(R-X)", classify_licenses(
        [{"name": "CC BY-NC 4.0", "url": "https://creativecommons.org/licenses/by-nc/4.0/"}], RM) is None)
    chk("map:-nd URL 否決(R-X)", classify_licenses(
        [{"name": "custom", "url": "https://x.org/licenses/by-nd/4.0/"}], RM) is None)
    chk("map:多授權取最嚴(CC0+CC BY→cc_whitelist)", classify_licenses(
        [{"name": "CC0"}, {"name": "y", "url": "https://c.org/licenses/by/4.0/"}], RM) == "cc_whitelist")
    chk("map:任一未映射=fail-closed 人閘", classify_licenses(
        [{"name": "CC0"}, {"name": "Custom EULA"}], RM) is None)
    chk("map:空證據=None", classify_licenses([], RM) is None)
    chk("map:整詞匹配防誤中('Google'≠OGL)", classify_licenses([{"name": "Google Terms"}], RM) is None)
    chk("map:OGL-Canada 詞界仍中(R3)", classify_licenses([{"name": "OGL-Canada 2.0"}], RM) == "cc_whitelist")
    j = judge_source(("re3data_r3d1", "general", "generic_json", 2, 100, 10, None,
                      [{"name": "CC0"}]), ctx)[1]
    chk("judge:路乙判入時 P1=True 且留痕 via=regime_map",
        j["P1_license"] and j["_regime_via"] == "regime_map" and j["_regime"] == "public_domain")
    chk("judge:路甲優先於路乙(白名單先問)", judge_source(
        ("arxiv_search", "general", "generic_json", 2, 100, 10, None, [{"name": "CC0"}]),
        ctx)[1]["_regime_via"] == "whitelist")
    # ── P7 端點唯一(P7-go 2026-07-28) ──
    ep = {"a1": "https://x/oai", "a2": "https://x/oai", "b1": "https://y/oai", "c1": None}
    w, d = pick_endpoint_winners({"a1", "a2", "b1"}, ep, set())
    chk("P7:同端點 min(source_key) 代表勝", w == {"a1", "b1"} and d == {"a2"})
    w2, d2 = pick_endpoint_winners({"a1", "a2"}, ep, {"https://x/oai"})
    chk("P7:已 active 端點封鎖全部", w2 == set() and d2 == {"a1", "a2"})
    w3, _ = pick_endpoint_winners({"c1"}, ep, set())
    chk("P7:無端點證據=pass-through 不擋", w3 == {"c1"})
    chk("P7:winners∪dups=全集不漏列", (w | d) == {"a1", "a2", "b1"})
    import inspect
    src = inspect.getsource(run)
    chk("熔斷先於一切(breaker 在 run 首查)", src.index("breaker_tripped") < src.index("weekly_remaining"))
    chk("週上限硬蓋(min(limit, rem))", "min(limit, rem)" in src)
    chk("留痕含逐謂詞 JSON(R6 可稽)", '"checks": checks' in src)
    chk("actor=auto_rules_v1(與人批可辨)", AUTO_ACTOR == "auto_rules_v1")
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="SRC-AUTO 謂詞引擎(六機械謂詞;AI 零放行權)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.dry_run:
        return dry_run()
    if a.run:
        return run(a.limit)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
