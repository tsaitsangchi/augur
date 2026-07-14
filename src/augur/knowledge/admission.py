"""知識入庫統一治權界閘（admission_gate）+ 本機/SFTP 源註冊 — 件 A / 件 H 之單一住所（#12）。

🎯 這支在做什麼（白話）：本機匯入②/遠端 SFTP③ 通道之自有內容明文豁免 knowledge_staging 狀態機
   （R-H1 hugo 2026-07-14 拍板），改以本模組四件 fail-closed 界閘 + item_source_gate DB trigger 為治權。
   任何寫入 knowledge_item/knowledge_item_text 之通道（acquire_local_files / acquire_remote_files /
   apk / admin console 三入口）入庫前一律呼 admission_gate 做 fail-fast——**四件全在此單一住所、不得各通道
   open-code**（避免 SFTP 自寫一套之 #12/#19 漂移）。license 以 corpus.LICENSE_WHITELIST 為 SSOT（不複本）。

四件 fail-closed：(i) source approval_status='active'（不存在/≠active→deny，能抓≠該抓機械閘）
                 (ii) license ∈ corpus.LICENSE_WHITELIST
                 (iii) license='owned_local' ⇒ access_scope='local_private'（隔離命門 v1.36.0）
                 (iv) source_type ∈ SOURCE_TYPE_WHITELIST 且 ≠ 'ai_generated'（#1 禁 AI 生成入庫）

守 #12（界閘單一住所、比照 corpus.clean_item_sql）· #1（source_type 白名單擋 ai_generated）·
   #5（不碰憑證，僅判值）· #19（SOURCE_TYPE_WHITELIST↔DB/CLI choices 三側同步）· #29b（源定義住 DB）·
   隔離不變式（本模組住 augur.knowledge、不置 core、預測 7pkg 零 import）。

自測(本檔=library；CLI 消費見 scripts/acquire_local_files.py、acquire_remote_files.py)：
  python -m augur.knowledge.admission              # 印白名單（唯讀、免 DB）
  python -m augur.knowledge.admission --check      # 對 live DB 跑四件閘紅綠自測（唯讀、需 .env）
  PYTHONPATH=src python src/augur/knowledge/admission.py --check   # 未 pip install -e 時
"""
from augur.knowledge import corpus

# source_type 白名單全集（C1，#19 唯一 SSOT——acquire_local_files --source-type choices、
# migrate 之任何 CHECK、admission_gate(iv) 皆引此常數，杜三份字面副本漂移）。
# 全 writer 枚舉（實作前 grep 確認）：erp_extract(ERP loader)·local_upload(本機)·remote_sftp(SFTP)·
# apk_decompile(apk)·abstract(paper abstract)·*_desc(entity resolver)·pd_fetch(fetch_pd_fulltext)。
# 保守策略（R-A-C1 hugo 拍板）：DB chk_itext_source_type 維持黑名單（僅擋 ai_generated、容 legacy NULL），
# 本白名單由 admission_gate Python belt 對「新 source_key 通道」強制，不改 DB CHECK＝零斷通道風險。
SOURCE_TYPE_WHITELIST = (
    "erp_extract", "local_upload", "remote_sftp", "apk_decompile", "abstract",
    "cod_desc", "chembl_desc", "uniprot_desc", "gbif_desc", "pubchem_desc", "pd_fetch",
)


def admission_gate(cur, source_key, license, access_scope, source_type):
    """四件 fail-closed 界閘。回 (ok:bool, reason:str)；ok=False 時 reason 為中文拒因。
    呼叫慣例：ok, reason = admission_gate(cur, ...); if not ok: sys.exit(reason)。
    cur=已開之 DB cursor（source active 查 knowledge_source）。"""
    # (i) 源存在且 active（能抓≠該抓；proposed/suspended 一律拒，approve 唯人 TTY）
    if not source_key:
        return False, "admission 拒:未指定 source_key（本機/SFTP 通道須註冊 knowledge_source 列）"
    cur.execute("SELECT approval_status FROM knowledge_source WHERE source_key = %s", (source_key,))
    row = cur.fetchone()
    if row is None:
        return False, f"admission 拒:source_key='{source_key}' 未註冊於 knowledge_source"
    if row[0] != "active":
        return False, (f"admission 拒:source '{source_key}' approval_status='{row[0]}'≠active"
                       "（proposed→active 須人 TTY review_knowledge_source.py，AI 不自 approve）")
    # (ii) license 白名單（corpus SSOT）
    if license not in corpus.LICENSE_WHITELIST:
        return False, f"admission 拒:license='{license}' 不在白名單 {corpus.LICENSE_WHITELIST}"
    # (iii) owned_local ⇒ local_private（隔離命門，DB chk_itext_owned_local_private 亦硬擋、此為前置 belt）
    if license == "owned_local" and access_scope != "local_private":
        return False, f"admission 拒:owned_local 必配 access_scope='local_private'（得 '{access_scope}'）"
    # (iv) source_type 白名單 + 禁 AI 生成（#1）
    if source_type is not None and source_type not in SOURCE_TYPE_WHITELIST:
        return False, (f"admission 拒:source_type='{source_type}' 不在白名單 "
                       "（新通道須用策展值；擴充改 admission.SOURCE_TYPE_WHITELIST #19）")
    if source_type == "ai_generated":                      # 冗餘明擋（#1 命門，白名單本不含之）
        return False, "admission 拒:source_type='ai_generated' 違 #1 禁 AI 生成入庫"
    return True, "ok"


def register_local_source(cur, source_key, *, domain, default_license,
                          access_scope="local_private", root_dir=None,
                          protocol="local_file", adapter="local_files", entity_type="document"):
    """冪等註冊本機/SFTP 通道之 knowledge_source 列（approval_status='proposed'，活化唯人 TTY）。
    行為資料（root_dir/license/scope/domain）住 adapter_config JSONB（#29b 不 hardcode）；
    憑證絕不寫此列（#5，SFTP 憑證住 .env）。ON CONFLICT DO NOTHING＝重跑冪等。"""
    import json
    cfg = {"default_license": default_license, "access_scope": access_scope, "domain": domain}
    if root_dir:
        cfg["root_dir"] = root_dir                          # 驅動情境 acquire_local_files 由此讀根目錄
    cur.execute(
        "INSERT INTO knowledge_source "
        "(source_key, adapter, protocol, domain, entity_type, license_regime, adapter_config, "
        " approval_status, fulltext_eligible) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,'proposed',false) ON CONFLICT (source_key) DO NOTHING",
        (source_key, adapter, protocol, domain, entity_type, default_license, json.dumps(cfg)))
    return cur.rowcount   # 1=新註冊、0=已存在（冪等）


def _selftest(check_db):
    """自測(唯讀、可個別驗證):印白名單;--check 時對 live DB 之 active/proposed 源跑四件閘紅綠測。"""
    print(f"SOURCE_TYPE_WHITELIST ({len(SOURCE_TYPE_WHITELIST)}): {', '.join(SOURCE_TYPE_WHITELIST)}")
    print(f"LICENSE_WHITELIST ({len(corpus.LICENSE_WHITELIST)}): {', '.join(corpus.LICENSE_WHITELIST)}")
    if not check_db:
        print("(--check 才對 live DB 跑四件閘自測;本次僅印白名單)")
        return 0
    from augur.core import db                               # 延遲 import:library 頂層依賴僅 corpus(#3)
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT source_key FROM knowledge_source WHERE approval_status='active' LIMIT 1")
        r = cur.fetchone()
        if not r:
            print("(無 active 源可測;僅印白名單)")
            return 0
        active = r[0]
        cur.execute("SELECT source_key FROM knowledge_source WHERE approval_status='proposed' LIMIT 1")
        pr = cur.fetchone()
        # (case, args, 期望 ok)——唯一應 True=active+owned_local+local_private+白名單 source_type
        cases = [("active+owned_local+local_private+local_upload", (active, "owned_local", "local_private", "local_upload"), True),
                 ("不存在源(拒 i)", ("__nope__", "owned_local", "local_private", "local_upload"), False),
                 ("owned_local+public(拒 iii)", (active, "owned_local", "public", "local_upload"), False),
                 ("壞 license(拒 ii)", (active, "nc-nd", "local_private", "local_upload"), False),
                 ("壞 source_type(拒 iv)", (active, "owned_local", "local_private", "weird"), False),
                 ("ai_generated(拒 iv)", (active, "cc-by", "public", "ai_generated"), False)]
        if pr:
            cases.insert(1, ("proposed源(拒 i)", (pr[0], "owned_local", "local_private", "local_upload"), False))
        allok = True
        for name, ga, expect in cases:
            ok, reason = admission_gate(cur, *ga)
            good = ok == expect
            allok = allok and good
            print(f"  {'✓' if good else '✗FAIL'} [{name}] ok={ok}" + ("" if ok else f" — {reason[:48]}"))
    print("四件閘自測:" + ("全通過 ✓" if allok else "有 FAIL ✗"))
    return 0 if allok else 1


if __name__ == "__main__":
    import sys
    sys.exit(_selftest("--check" in sys.argv))
