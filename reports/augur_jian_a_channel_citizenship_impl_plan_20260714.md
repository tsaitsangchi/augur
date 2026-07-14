# 件 A 通道公民化 — 實作級計畫書（本機匯入②/遠端 SFTP③ 成 K 契約完整公民）

- **日期**：2026-07-14
- **性質**：#20 計畫先行／新子系統（觸安全授權邊界=高風險門檻）；已經 9-agent workflow（5 元件深化 + 4 鏡對抗審查）壓測。**待 hugo 拍板才 #19 一支一段實作**。
- **架構級 SSOT**：`reports/augur_knowhow_tri_channel_e2e_master_plan_20260714.md` 件 A1/A2/H；本檔為其**實作級深化 + 對抗審查修正定案**。
- **拍板前提（hugo 已裁）**：R-A1（類 A）、R-A2（B 案：SFTP 傳輸層 CLI + registry provenance）、R-H1（本機/SFTP 明文豁免 staging，以 license DB CHECK + cli_identity TTY 為治權）、通道②③皆自有資料合法必打通。

> **對抗審查結論**：骨架站得住、8 增補名目全覆蓋、DDL 用 NOT VALID→VALIDATE 降鎖、四支新 script 守 #29a/d。但 **6 blocker + 12 major** 皆為**跨元件契約不一致與安全洞**，須在計畫定案時鎖死、實作前對齊——**不動架構即可實作**。本計畫已折入全部修正。

---

## 第一部　鎖定跨元件契約（實作前必先定死，#19 執行前確認）

對抗審查最大宗問題＝五元件各自想像契約。以下**四項單一 SSOT 拍板**，實作三處一律引用、不得 open-code：

### C1　source_type 全集（單一 SSOT，杜三份漂移）
- **唯一住所**＝`admission.SOURCE_TYPE_WHITELIST`；DB CHECK 與 `acquire_local_files --source-type choices` 一律由此常數生成/引用（比照 `corpus.LICENSE_WHITELIST↔DB` 模式）。
- **全集（實作前 grep 全 writer 枚舉確認）**：
  ```
  erp_extract, local_upload, remote_sftp, apk_decompile, abstract,
  cod_desc, chembl_desc, uniprot_desc, gbif_desc, pubchem_desc, pd_fetch
  ```
  ⚠ **blocker 修正**：原設計漏 `remote_sftp`（SFTP writer）與 `pd_fetch`（fetch_pd_fulltext.py:131 writer）——白名單一落地即斷此二通道。**全writer清單必先 grep 確認**。
- **NULL 逃生口**：CHECK 寫 `source_type IS NULL OR source_type IN (...)`（容 1,126 列 legacy NULL、實證必要）；**誠實敘述**：白名單對 #1 的機械加固僅及非 NULL 值，NULL 由寫入端一律帶值收斂（#12 不 hand-patch）。
- **保守替代（若不願為邊際 #1 保護冒斷三通道風險）**：維持黑名單、僅對「新 source_key 通道」強制 source_type NOT NULL + belt 白名單，不動既有 OA/legacy 之 NULL。**此為拍板點 R-A-C1**。

### C2　admission_gate 唯一簽名（收斂單一住所）
- `admission.admission_gate(cur, source_key, license, access_scope, source_type) -> (ok, reason)`（**首參 cur**，內部 SELECT approval_status）。
- **三消費端**（acquire_local_files / acquire_remote_files / admin console 三入口）一律 `import admission; admission_gate(cur, ...)`，**不得各自 open-code 來源閘**（SFTP 原設計自寫一套＝違 #12）。admin console 於 subprocess 前 `with db.connect()` 取 cur 呼叫 fail-fast。
- 四件 fail-closed：(i) source approval_status='active' (ii) license∈LICENSE_WHITELIST (iii) owned_local⇒access_scope='local_private' (iv) source_type∈SOURCE_TYPE_WHITELIST。

### C3　下游抑制旗標名（統一，杜雙跑 embed）
- 全通道 acquirer 統一旗標 **`--acquire-only`**（貫穿 acquire_local_files / acquire_remote_files / 驅動器）；acquirer 收到即**真的**跳過自鏈 build_sentences→embed（非 no-op 靜默吞）。standalone（admin/手動）不帶此旗標才自鏈；驅動器 DAG 一律帶（下游由 DAG 承接，杜重複嵌入）。

### C4　admission.py 歸屬 = 件 A1（非件 H）
- `src/augur/knowledge/admission.py` 於**件 A1 建**；件 H 的界閘落地即此模組。元件④/⑤ 一律「件 A1 已建·本件消費」。相依序：**件 A1（admission.py + acquire_local_files --source-key/--source-type）→ 元件④/⑤**。

---

## 第二部　治權硬約束修正（對抗審查 blocker/major，須人拍板）

### T1　item_source_gate DB trigger 升為**必要**（R-H1 B案≈A案之關鍵）
- **問題**：原列「(選、建議)」。豁免 staging 後，直插 knowledge_item 的源-active 強制若只靠 Python belt，**機械強度嚴格弱於現況 staging 路徑（DB trigger）**——逾越「明文豁免」授權（豁免一道 DB 閘卻不補等效 DB 閘＝淨弱化）。
- **修正（MANDATORY）**：
  1. trigger 掛 **`knowledge_item_text` BEFORE INSERT**（非只 knowledge_item）：查父 item→source_key→protocol/approval_status，涵蓋「對既有 item 追加 text 列」與「來源後撤 suspend」場景。
  2. 堵 **NULL 逃生口**：對 `owned_local ∧ access_scope='local_private' ∧ source_key IS NULL` 亦 RAISE（否則 source_key=NULL 一行繞過整個 trigger）。
  3. manual_file 處置與 staging_source_gate 一致（避免「走 staging 可繞、走直插被擋」雙標）——**建議兩閘皆不豁免 manual_file**（收緊補洞）。
- **【拍板點 R-A-T1】**：item_source_gate 必要 vs 維持選配（若不採，則屬治權弱化須升決策層，#26）。

### T2　CLAUDE #29b doctrine 文字須人拍板（治權檔變更）
- #29b（v1.20, line 69）明文「任何知識抓取一律走完整管線 acquire→staging→promote→…」。本機/SFTP 直插繞 staging **直接違此治權檔判準**。修憲（憲章）不需（共同不變式①②③④+隔離全保留），但 **CLAUDE.md 治權檔文字須 hugo 核定**：補一句「owned_local 本機/SFTP 軌得豁免 knowledge_staging 直入 knowledge_item，治權繫於 license DB CHECK + 源-active TTY + admission_gate + item_source_gate DB trigger」。**AI 不逕改治權檔**（§26）。佐證：erp_extract 15 萬列（manual_file、staging 首行豁免）已繞 staging，#29b 早與現況不符、更須補正。
- **【拍板點 R-A-T2】**：核定 #29b 文字增補。

### T3　concordance RBAC 旁路——私有內容進 concordance 前必先收窄
- **問題**：`retrieval.py:190-222 concordance_lookup` 回逐字原句且自述**不過 clean_item_sql 收窄**。件 A 下游（build_sentences→build_concordance）會把 local_private/owned_local 私有內容餵進 knowledge_concordance；一旦 L2 逐字查詢接入顧問（件 G 閉環自然延伸）＝**繞 owner 收窄吐私有原文**。
- **修正（件 A 私有通道開通之前置硬依賴）**：二擇一——(a) concordance_lookup 加 clean_item_sql(access_scope/owner/domain) 收窄 fail-closed；或 (b) build_concordance 端排除 access_scope='local_private'（私有件不建 concordance）。**不得晚於首筆私有內容落地**。

### T4　其餘治權落點（無新增判準、既有硬牆沿用）
- license 三軌：knowledge_item_text_license_check（5 值）+ chk_itext_owned_local_private（owned_local⇒local_private）已 live，沿用。
- #5 密鑰：SFTP 私鑰路徑住 .env（`SFTP_<NAME>_KEYPATH`），絕不入 DB/log/git；host/port/glob 住 adapter_config JSONB。
- 隔離不變式：三通道皆素養層零量化、不進預測管線；admission.py 置 augur.knowledge（非 core）。
- 能抓≠該抓：source proposed→active 唯人 TTY（review_knowledge_source.py），AI 永不自 approve/放量（#26）。

---

## 第三部　五元件實作規格（折入修正）

### 元件① 本機匯入 + admission_gate（件 A1；**先行、餘件依賴**）
- **新** `src/augur/knowledge/admission.py`：`admission_gate(cur,...)`（C2）+ `SOURCE_TYPE_WHITELIST`（C1，11 值）+ `register_local_source(cur, source_key, *, domain, default_license, access_scope, root_dir, protocol, adapter)`（冪等 proposed INSERT + adapter_config JSONB）。引 corpus.LICENSE_WHITELIST 為 license SSOT。
- **改** `acquire_local_files.py`：加 `--source-key`（寫入必填）/`--source-type`（choices=SOURCE_TYPE_WHITELIST）/`--acquire-only`；INSERT knowledge_item 回填 source_key（修 :97 NULL、:100-102 缺欄）；item_text source_type 綁 args（取代 :109 硬寫）；walk 前呼 admission_gate fail-fast；**#29b 修正**：有 `--source-key` 無 `--dir` 時 SELECT `adapter_config->>'root_dir'` 為根（缺則 graceful 誠實報，非靜默 no-op）——否則驅動情境 no-op、root_dir 成死資料。
- **改** `curation.py`：transition approve/activate 對 protocol∈(local_file,sftp) **直接略過** `_recent_probe_ok` http-probe（http 概念不適用）——**不在 curation 內建檔案/ssh probe**（避免污染純 DB 模組、破 #18/#3）；其餘 TTY+superuser 閘不變。
- **新** `scripts/migrate_local_admission_ddl.py`（#29a/d，--dry-run/--apply，冪等）：seed 'local' domain → source_type 白名單 CHECK 換版（NOT VALID→VALIDATE→DROP 舊）→ knowledge_item.domain FK（零 orphan 可即加）→ **item_source_gate trigger（T1 必要、掛 item_text、堵 NULL）** → register 本機源列 proposed。
- **DDL**：見附錄 A。

### 元件② SFTP 子系統（件 A2；全新，依賴①）
- **改** `pyproject.toml`：加 `paramiko>=3.0`（admin extra；#23 import smoke）。
- **改** `sftpbrowse.py`：`_client`(:63) 升公開 `open_client`（保留別名不破既有呼叫）。
- **新** `src/augur/knowledge/sftpsync.py`（#18）：`iter_changed_files(client, host, base_path, glob, dest, prior_state, *, download, max_files, max_bytes)` → yield `SyncedFile`；增量以 remote_mtime+size 比對。**安全修正（major）**：每 basename 過 `webupload.sanitize_relpath` 語意（拒 os.sep/'..'/絕對）+ 每次 get 前 `assert realpath(lp).startswith(realpath(dest)+os.sep)`（堵 tar-slip path traversal）；**headless 連線改 RejectPolicy + known_hosts pinning + look_for_keys=False/allow_agent=False**（堵 MITM/金鑰枚舉）。
- **新** `scripts/acquire_remote_files.py`（#29a/d）：讀 sftp source 列 + .env 憑證 → **呼 admission_gate（C2，不自寫閘）** → sftpsync 增量 → 複用 `acquire_local_files.ingest_file` 入庫（source_type='remote_sftp'）→ UPSERT sftp_sync_state → `--acquire-only`（C3）時不自鏈。
- **正確性修正（major）**：
  - **changed 檔撤回**：新 text_sha1≠舊 → 對舊 item_text 撤回（刪或標 superseded + 清 embedding）再寫新，sftp_sync_state 留 superseded_item_id 稽核（否則私有檔每次編輯舊版永久殘留可答）。
  - **skip 落帳**：凡被檢視的檔一律 UPSERT sftp_sync_state（item_id 允 NULL、change_kind 增 'skip'），使 unknown_ext/短檔/oversize 也落帳、下輪 mtime/size 未變不重抓（否則永不收斂、疊 max_files 截斷成零進度死循環）。
- **新** `scripts/migrate_sftp_sync_ddl.py`：冪等建 sftp_sync_state（DDL 見附錄 A，item_id **int**（對齊實證 knowledge_item.item_id=integer、非 master plan 誤寫 bigint）；連線設定住 **adapter_config JSONB**（非 master plan 誤寫 query_template TEXT））。

### 元件③ apk 反組譯（件 A1 後）
- **新** `scripts/decompile_apk_to_owned.py`：jadx -d 反組譯 → **allowlist 分段邊界比對**（`relpath==prefix+'.java'` 或 `startswith(prefix.replace('.',os.sep)+os.sep)`——**安全修正**：原 startswith 會撈 com/example2、com/examplelib 第三方碼洗版權）→ 複製真檔（fileparse 跳 symlink）→ 交 acquire_local_files（source_type='apk_decompile' + `--acquire-only`）。default-deny（無 --include-package 即拒）；混淆碼（ProGuard/R8）owned_local 判定強制 admin 逐案確認。
- **前置**（#23，人工、入 HANDOFF #31）：JRE + jadx（GitHub release，apt 無）；現機皆未裝。

### 元件④ webupload 三入口 + RBAC owner（件 A1+H 後）
- **改** `serve_admin_console.py`：三入口 :873/:903/:934 subprocess 補 `--source-key`（`_local_source_key()` 白名單校驗、防任意 FK/注入）+ `--owner-user-id`（`_owner_uid()=identity.verify_session(token)`）；subprocess 前呼 admission_gate fail-fast（回 400 明確訊息，非靜默 stderr）。
- **改** `webupload.py`：LICENSES/SCOPES 改 import 單一住所（消與 corpus 重複，#12）。
- **RBAC 邊界（誠實）**：env 後門記憶體 session→uid=None→owner 落 NULL→非 super 永遠 deny（現 app_user 僅 uid=1 super，owner 收窄對 super 無實質差異）；完整 uid 化＝env 後門映射 app_user，屬件 H RBAC 續作。UI 明示 owner=NULL 導引改 DB 帳號登入。
- **既有限制**：save_upload 同名檔靜默覆寫 → 去重命名或計數誠實回報（landing 數=上傳數斷言）。

### 元件⑤ 驅動器 + timer 通道統一（件 A1/A2 後；R-G/R3）
- **改** `refresh_knowledge_pipeline.py`：harvest 段升「API 子抓 + 檔案通道迭代」；`CHANNEL_ACQUIRERS={'local_files':...,'sftp':...}`（協定映射屬邏輯、#29b 豁免）；`harvest_file_channels()` 逐 active 檔案通道源 subprocess（帶 `--source-key --acquire-only`，C3）+ per-source try/except 續跑 + `_upsert_file_channel_log`（query_id=0 sentinel）；pending_lines 加檔案通道行（三通道可見）。
- **改** `fetch_oa_fulltext.py`：PENDING_WHERE 加 `protocol IN('local_file','sftp')` 顯式排除（**誠實修正**：首要天然障壁實為 external_id 非 DOI 形，protocol 為額外防線、三者並存防私有件送外部 OA resolver）。
- **改** `install_services.sh`：加 augur-knowhow-refresh.{service,timer}（oneshot + EnvironmentFile=.env + Sun 02:00 + 預設**不啟**，`--with-refresh` 才 start）。
- **API 放量護欄（#26）**：週日 timer harvest 段打外部 API＝無人看顧放量、有 re-ban 風險；**預設不啟** + 提供 `--from-stage promote` 純下游保守模式；外部 harvest 放量留 attended R-A3（IP 健康看顧）。**【拍板點 R-A-R3】**。

---

## 第四部　分階段 + 相依序 + 拍板點

| 階段 | 內容 | 依賴 | 拍板點 |
|---|---|---|---|
| **P-A1** 本機成公民 | 元件①（admission.py + acquire_local_files 修 + curation 豁免 + migrate DDL）+ **T1 item_source_gate 必要** | C1-C4 契約定死 | R-A-C1（白名單策略）/ R-A-T1（trigger 必要）/ R-A-T2（#29b 文字）|
| **P-T3** concordance 收窄 | T3（私有進 concordance 前收窄）——**私有通道開通前置硬依賴** | — | — |
| **P-A2** SFTP 子系統 | 元件②（paramiko + sftp_sync_state + sftpsync 含 path-guard/host-key + acquire_remote_files + changed 撤回 + skip 落帳）| P-A1（ingest_file/admission） | R-A2（已裁）+ 逐源 TTY activate |
| **P-apk** | 元件③（分段 allowlist）| P-A1 + jadx 前置(#23) | — |
| **P-web** | 元件④（三入口 + RBAC owner）| P-A1 + admission.py | 件 H RBAC（env 後門遷 app_user）|
| **P-drv** 驅動器+timer | 元件⑤（通道迭代 + fetch_oa skip + timer）| P-A1/P-A2 | R-A-R3（timer 掛載/保守模式）|

**每階段**：#29d import 級 + #25 最小單位實測（造 nonce 檔/源 → migrate --apply(dev) → TTY activate → acquire → 驗 source_key≠NULL/admission 四件/FK/CHECK/trigger 物理擋 + 反向斷言未 active 源被拒）；DDL 於 prod 走 #30 dump 後、audit 綠再跑。**#19 一支一段做完呈過目再進下一**。

---

## 第五部　驗收準則

1. **三通道各一 sentinel 端到端**：API nonce 源 / 本機 nonce 檔 / SFTP nonce 檔 → 單命令驅動器 → advisor 逐字引用命中 + fail-closed（owned_local 不被無授權檢索）+ 隔離斷言（素養層零列進 term_affinity）→ exit 0。
2. **對抗修正驗證**（deliberate.py 零 token 機械斷言）：`owned_local∧scope≠local_private ⇒ ==0`、`source_type∉白名單 ⇒ ==0`、`protocol∈(local_file,sftp) 源非 active 卻有 item ⇒ ==0`、SFTP path-guard 反向測（惡意 filename 被拒）、apk allowlist 分段邊界測（com/example2 被排除）、concordance 無 local_private 洩漏。
3. **通道治理對等**：本機/SFTP 皆有 knowledge_source 列（source_key≠NULL）、經 admission_gate 四件、item_source_gate 物理擋。
4. **resume**：SFTP 重跑零重下載、changed 撤回舊版、skip 落帳收斂。

---

## 附錄 A　DDL（實作前對照；#30 dump 後、audit 綠再跑）

```sql
-- 元件②：SFTP 增量帳本（item_id int 對齊實證、非 bigint；連線設定住 adapter_config 非此表）
CREATE TABLE IF NOT EXISTS sftp_sync_state (
    sync_id      bigserial PRIMARY KEY,
    source_key   varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
    remote_host  text NOT NULL, remote_path text NOT NULL,
    remote_mtime bigint, size_bytes bigint, content_sha1 char(40),
    item_id      int REFERENCES knowledge_item(item_id),
    superseded_item_id int,                      -- changed 撤回稽核(major 修正)
    change_kind  varchar(8),                      -- new|changed|skip(major 修正)
    first_seen timestamptz NOT NULL DEFAULT now(), last_synced timestamptz NOT NULL DEFAULT now(),
    UNIQUE(source_key, remote_path)              -- #6 冪等增量鍵
);

-- 元件①：source_type 白名單升版（C1 全集含 remote_sftp/pd_fetch；容 legacy NULL）
ALTER TABLE knowledge_item_text ADD CONSTRAINT chk_itext_source_type_v2
  CHECK (source_type IS NULL OR source_type IN
    ('erp_extract','local_upload','remote_sftp','apk_decompile','abstract',
     'cod_desc','chembl_desc','uniprot_desc','gbif_desc','pubchem_desc','pd_fetch')) NOT VALID;
-- VALIDATE CONSTRAINT chk_itext_source_type_v2;  DROP CONSTRAINT chk_itext_source_type;

-- 元件①：domain seed + FK（knowledge_item 零 orphan 可即加）
INSERT INTO knowledge_domain (domain,label_zh,is_authz_boundary,is_investment,enabled)
  VALUES ('local','本機匯入',false,false,true) ON CONFLICT (domain) DO NOTHING;
ALTER TABLE knowledge_item ADD CONSTRAINT fk_item_domain
  FOREIGN KEY (domain) REFERENCES knowledge_domain(domain) NOT VALID;  -- 再 VALIDATE

-- 元件①：item_source_gate 物理牆(T1 必要;掛 item_text、堵 NULL 逃生口)
-- CREATE FUNCTION trg_item_source_gate(): 查父 item.source_key→protocol/approval_status;
--   protocol∈(local_file,sftp)∧approval_status≠'active' → RAISE;
--   owned_local∧access_scope='local_private'∧source_key IS NULL → RAISE(堵 NULL);
-- CREATE TRIGGER item_source_gate BEFORE INSERT ON knowledge_item_text ...
```

---

*承 #20 計畫先行 + 對抗審查（6 blocker+12 major 已折入修正）+ #19 逐段檢視 + #26 碰治權/放量護欄停下問。拍板點：R-A-C1（白名單策略）/ R-A-T1（item_source_gate 必要）/ R-A-T2（#29b 文字增補）/ R-A-R3（timer 保守模式）+ R-A2 逐源 activate。實作前確認①完整②內部一致③與 code 一致④可實作。*
