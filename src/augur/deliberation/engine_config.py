"""審議引擎 config 讀取 — deliberation_engine_config 之唯讀門(B3;#29b 決定行為的資料住 DB)。

🎯 這支在做什麼(白話):fast_anchor 規則開關(哪些快路啟用,尤 L6_pytest 預設關)住 DB 表、不寫死
   Python——改開關=UPDATE 一列零改碼。本模組讀 config + 算 config_sha(正規化 JSON sha256,供
   GATE 快照對齊 §2.2 判準6);表缺列 → fail-safe 回「全關快路」(寧保守不擅開;#15)。

守 #29b(config 住 DB)· #12(config 讀取單一住所)· #15(缺列 fail-safe 全關)。
"""
import hashlib
import json

_CACHE = {}   # process cache:config_key → (dict, sha);常駐服務重啟即刷新(#7)


def config_sha(cfg):
    """正規化 JSON sha256(排序鍵、無空白)——GATE 快照對齊用。"""
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def load_rules(cur, key="fast_anchor_rules"):
    """讀規則 dict + sha(cache)。表/列不存在 → ({}, None)=全關快路(fail-safe 保守)。"""
    if key in _CACHE:
        return _CACHE[key]
    cur.execute("SELECT to_regclass('public.deliberation_engine_config')")
    if not cur.fetchone()[0]:
        return {}, None
    cur.execute("SELECT config, config_sha FROM deliberation_engine_config WHERE config_key=%s", (key,))
    row = cur.fetchone()
    out = (row[0], row[1]) if row else ({}, None)
    _CACHE[key] = out
    return out
