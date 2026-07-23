"""審議引擎 config 讀取 — deliberation_engine_config 之唯讀門(B3;#29b 決定行為的資料住 DB)。

🎯 這支在做什麼(白話):fast_anchor 規則開關(哪些快路啟用,尤 L6_pytest 預設關)住 DB 表、不寫死
   Python——改開關=UPDATE 一列零改碼。本模組讀 config + 算 config_sha(正規化 JSON sha256,供
   GATE 快照對齊 §2.2 判準6);表缺列 → fail-safe 回「全關快路」(寧保守不擅開;#15)。

守 #29b(config 住 DB)· #12(config 讀取單一住所)· #15(缺列 fail-safe 全關)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.deliberation.engine_config              # 印用途+公開入口（唯讀）
  python -m augur.deliberation.engine_config --selftest   # 純紅綠自測（零 IO）
"""
import hashlib
import json

_CACHE = {}   # process cache:config_key → (dict, sha);常駐服務重啟即刷新(#7)


def config_sha(cfg):
    """正規化 JSON sha256(排序鍵、無空白)——GATE 快照對齊用。"""
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def load_rules(cur, key="fast_anchor_rules", fresh=False):
    """讀規則 dict + sha(cache)。表/列不存在 → ({}, None)=全關快路(fail-safe 保守)。
    fresh=True 跳 _CACHE(前台 tiers 翻旗標免重啟;預設 False=現行為)。"""
    if not fresh and key in _CACHE:
        return _CACHE[key]
    cur.execute("SELECT to_regclass('public.deliberation_engine_config')")
    if not cur.fetchone()[0]:
        return {}, None
    cur.execute("SELECT config, config_sha FROM deliberation_engine_config WHERE config_key=%s", (key,))
    row = cur.fetchone()
    out = (row[0], row[1]) if row else ({}, None)
    _CACHE[key] = out
    return out


def _selftest():
    """自測（零 DB/零 API）：合成 config 紅綠測 config_sha(純正規化 sha)+ load_rules 結構斷言。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("config_sha 決定性(同輸入同 sha)", config_sha({"a": 1}) == config_sha({"a": 1}))
    chk("config_sha 鍵序不變(排序鍵正規化)", config_sha({"a": 1, "b": 2}) == config_sha({"b": 2, "a": 1}))
    chk("config_sha 不同輸入不同 sha", config_sha({"a": 1}) != config_sha({"a": 2}))
    s = config_sha({"L6_pytest": False})
    chk("config_sha 回 16 位 hex", isinstance(s, str) and len(s) == 16 and all(c in "0123456789abcdef" for c in s))
    chk("load_rules 公開入口存在", callable(load_rules))
    chk("_CACHE 為 process cache dict", isinstance(_CACHE, dict))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("入口:load_rules / config_sha")
    print("(自測:python -m augur.deliberation.engine_config --selftest;免 DB 免 API)")
