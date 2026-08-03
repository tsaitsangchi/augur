# augur 2026-10-14 併審 checklist 證據備料（F2）

* **產製日**：2026-08-01｜**性質**：**[I] 唯讀備料**——本檔零 DB 寫入、零 git 操作、零改既有檔；唯一產出即本檔
* **不代勾**：任何「已合規／可關閉／可結清」之判定專屬 Constitution Steward（`AUGUR-MC v1.6 §8.1`；RULING-2026-039「無 Evidence 不提早結清」）。本檔各項**結論欄一律「待 Steward 判」**。
* **依據**：登錄冊 `reports/augur_problem_solution_register_20260801.md` F2 列（「10-14 checklist 七項 Evidence 備料（不代勾）」；ULTRACODE-SCHEDULE.md:95 之 CR4 W1 唯讀項）＋Steward 圈選批次四
* **親驗基準**：git HEAD `b98bc04`（本日；lint 輸出自標 `+dirty`）；live DB＝`augur`＠localhost（唯讀查詢）；所有數字皆本日現查、不抄舊（指令彙錄見 §11）
* **自我標記（CLAUDE.md #32(a)）**：本檔為 AI 產出、self-reported；引用之他人裁決與 DB 輸出各附出處，AI 自身之彙整判讀不構成權威確認

---

## §0 範圍窮舉與「七項」出入之誠實記錄

窮舉指令：`grep -rn "2026-10-14\|10-14" constitution/ docs/compliance/ specs/`（99 命中；另補掃 repo 全域之 `2026-10-09/10-10` 與 `ULTRACODE-SCHEDULE.md`／`CODE-MIGRATION-PLAN.md`／`GROUNDING-MAP.md`）。

**正式 checklist 本體確為七項、無出入**——SSOT＝`ULTRACODE-SCHEDULE.md:112-122`「2026-10-14 併結 checklist（到期前不得勾『結清』）」，七個勾選框**本日親讀仍全 `[ ]`**；上位裁決＝RULING-2026-039 九.2（025＋029＋WM.35/36 及 C/D 觸發項同日併審）。前次盤點基線＝`audits/ROADMAP-R2-1014-CHECKLIST-STATUS-20260724.md`（07-24；本檔為其 08-01 增量更新）。

**惟 10-14 日曆義務之全集不只七項**：窮舉另得 **checklist 外 6 項**同綁 2026-10-14（§8：RULING-2026-002 主文二五檔 CS／主文五措辭與檔頭／LDI.7 逐節標注／D-PRIN-2／C1 manual 有效期 10-09・10-10／RULING-2026-012 Phase 7），及 **4 類已由後續裁決承接之歷史提及**（§9，誠實列出、不重複立項、亦不假關）。

| 命中歸併 | 條目 | 本檔節 |
|---|---|---|
| checklist 七項 | WM.35/36・025 residual・029・L7.16・KDO.4/LDO.4・020 M2・GOV-3 B | §1–§7 |
| checklist 外 | 002 主文二／主文五・LDI.7・D-PRIN-2・C1 有效期・012 Phase 7 | §8 |
| 已承接／史料 | 011 §8.2 保留・019/023 L5 重作窗・暫行模板・PROPOSAL-2026-001 註記 | §9 |

**07-24 基線以來的重大變動**（影響多項讀法）：
1. **2026-07-31「augur＝全部」單一角色整併**（`augur_predict` DROP、`augur` 升 superuser）→ 一切 GRANT/REVOKE 層證據失效（GROUNDING-MAP S22 段）。
2. **RULING-2026-042 已於 2026-08-01 hugo 親簽生效**（AL-2026-046）→ L7.16 觸發唯餘 10-14 併審（039 八.2「雙角色部署議程」臂消滅）。
3. **identity 六表 2026-08-01 生產落地**（G3 hugo 親簽，commit `d177c6d`/`937014b`）→ KDO.4 量測之資料前置首次存在。
4. **C1 manual 5 條有效期已落 DB**（90 天案；全部到期於 10-09/10-10，**恰在併審前 4–5 日**）。

---

## §1 Checklist #1 — WM.35／36 直綁消費禁令生效盤點

**(a) 原文義務（逐字）**
> WM.35（`specs/WORLD-MODEL-SPECIFICATION.md:336-338`）：「任何新 Observation Channel 於系統落地時，**必須**同時登錄其世界概念映射……unmapped 或未登錄映射之通道，其資料**僅具 Observation 地位**——得保存、對帳、追溯，**不得**被消費為 Representation 或 Knowledge 之依據。」過渡規則（:339）：「既存已落地通道……準用 WM.36 所引 §8.3 過渡規則 (b) 之 Steward 補正期……自該到期日之翌日起，本條登錄與消費判準無條件適用。」
> WM.36（:344-）：「系統**必須**維護……**World Concept Registry**……為一級結構。登錄項最低含七欄……」
> RULING-2026-030:81：「補正期到期日＝**2026-10-14**……自 **2026-10-15** 起 WM.36 直綁消費禁令無條件適用。」（039 二.2 維持；「不提早結清」）

**(b) 現況親驗（2026-08-01）**
| 探針 | 指令 | 結果 |
|---|---|---|
| Registry 表本體 | `SELECT … FROM pg_class WHERE relname LIKE '%concept%' AND relkind='r'` | **NONE**（live 零 concept 表；僅史上 model_registry 非世界概念登錄） |
| vendor 直綁檔數 | `grep -rlE 'FROM\s+"Taiwan' src scripts --include='*.py' \| wc -l` | **47 檔**（GROUNDING-MAP 07-17 快照口徑同指令＝37 檔 → 現查 +10，直綁未消反增） |
| S22 code 層新證據 | `venv/bin/python -c "from augur.audit.import_isolation import check_isolation; …"` | **violations=0**（本日重跑；射程＝7 package＋core 之靜態引用層） |

**(c) 既有證據指針**：`GROUNDING-MAP.md:45-47`（WM.14/36/35 三列均 🔨）＋`:176-191`（**2026-07-31 S22 定案**：權限層證據永久失效；新證據＝code 層 AST 稽核，**誠實揭露三弱點**——擋不到動態 SQL、射程不含 execution/arena/identity/deliberation、無人機分辨力）；RULING-2026-030 §五(b)；RULING-2026-042 主文二 4（引用 S22、不擴張射程）；`CODE-MIGRATION-PLAN.md` Phase 6（Registry 絞殺，未動工）。

**(d) 10-14 前缺口**：Registry 七欄表＋通道映射＋unmapped 旗標**零落地**；直綁 47 檔未消。**本項是七項中唯一「到期即自動變違規」者**——10-15 起既存消費（feature／prediction 管線讀 vendor 表）依條文無條件落入消費禁令。須發生：〔hugo 裁〕10-14 就「S22 code 層證據可否充當過渡等價／實作路徑／或依 §8.4 有到期日處置」作成書面；〔AI 可備〕直綁 47 檔清單、消費鏈盤點、registry 最小 DDL 草案（呈案不施作）。

**(e) 結論**：（待 Steward 判）

---

## §2 Checklist #2 — 025 (iii)(iv)(vi) ②③ 觸發／達成或明示續延

**(a) 原文義務（逐字，`constitution/RULING-2026-025-L7-8.2-DISPOSITION.md:24-28`）**
> 「三者同源於『單一自然人 Steward／單節點／單機』之物理現實……**①（現行，即接受）**：據實記為已接受殘餘風險……**復審期限＝2026-10-14**。**②（有第二人即行）**：升格附則『繼任人恆存』之預先指定人為 (iv) 之核准第二人……**③（終態）**：監督/核准平面移至獨立實體節點——一併結清 (iii) kill-switch 實體獨立性、(vi) 單機熱備援。」（039 八.1：維持分階段①至 10-14、**禁止假關**）

**(b) 現況親驗**
* **② 第二人**：無達成跡象——`grep 繼任 constitution/AMENDMENT-LOG.md` 僅 1 命中（AL-2026-020＝第 3 條「繼任人恆存」義務之**設立**）；**AL 內查無「預先指定繼任人」之登錄列** ⇒ ② 之前提（附則預指定人）現無登錄紀錄。
* **③ 獨立節點**：無——hugo 2026-07-25 宣告 GB10 不存在；DESKTOP 為週末機非監督平面（記憶「兩台電腦同時進行」乙案）。
* **(vi) 備援面現況**：RULING-2026-012 主文 3 曾裁「本地 dump＋D:\ 異碟 restic 庫為既定終態、風險接受」——**但本機 `/mnt/d` 不存在**（GROUNDING-MAP:8 補註 07-31 實查），該拓撲於現行當家機不成立。現況＝G1 定期 `pg_dump` →`/mnt/c/database/`（**與 DB 同一實體 NVMe 碟**；G2 呈案 §1：「碟亡＝全亡」）＋cron 5 條 AUGUR 排程在掛（本日 `crontab -l` 現查）。
* **G2 異地備份三案**（外接碟／加密上 NAS／第二機）已於 2026-08-01 呈案（`reports/w2_20260801/G2_offsite_backup_options.md`），**待 Steward 拍板**。

**(c) 既有證據指針**：RULING-2026-025／037 §八／038 §六／039 八.1；`constitution/GOVERNANCE-ANNEX.md:30-35`（第 3 條繼任程序＋恆存義務）；RULING-2026-012 主文 3；G2 呈案。

**(d) 10-14 前缺口**：〔hugo 裁〕(1) G2 三案擇一拍板＋施作授權（③/(vi) 之最小前進）；(2) 繼任人預先指定之作成與 AL 登錄（② 前提；亦係附則第 3 條 4 款義務）；(3) 10-14 當日就 ②③「觸發／達成或明示續延」作成書面。〔AI 可備〕G2 拍板後施作腳本＋還原演練（L7.25「未經實測之備份推定不存在」）。

**(e) 結論**：（待 Steward 判）

---

## §3 Checklist #3 — 029 L5 PRV／ASF 日曆復審

**(a) 原文義務（逐字，`constitution/RULING-2026-029-L5-8.2-DISPOSITION.md:24-28`）**
> 「1. **L5 單層 ultracode 複核**：……於 **2026-10-14 前**執行 L5 之 PRV／ASF 維度對抗審查；findings 若翻 major，另依 §8.2 辦。……3. **復審期限 2026-10-14**（與 L7 residual 復審同日，一次併結）。」（039 六.2：「035 程序性閉合 ≠ 日曆結清。**禁止假關**。」）

**(b) 現況親驗**：附條件之 PRV/ASF 複核**已執行完畢**——RULING-2026-035 §七（2026-07-23）：「PRV 零 finding、ASF medium×1＋minor×4 均 patch 可癒……029 (v)(viii) 之 ultracode 義務視為履行完畢（程序性閉合）」；F-IX-4/F-IX-6 簿記已閉（RULING-2026-038）。本日 `constitution_lint report`＝**PASS 7/7、error 0**（L5 含）；L5 spec 版本未升、07-23 後無 [N] 變更跡象。**剩餘＝10-14 日曆復審本身**（不得以 035 視為結清）。

**(c) 既有證據指針**：`audits/L5-CK-ULTRACODE-20260723.md`；RULING-2026-035 §七／038 §五／039 六.2；`specs/COGNITIVE-KERNEL-SPECIFICATION.md`【地位】:15-16。

**(d) 10-14 前缺口**：〔hugo 裁〕併審日作成復審書面（可與 025 一次併結）。〔AI 可備〕07-23 以來 L5 消費面變更盤點（現查無 spec 變更；lint 綠）。**本項為七項中證據最齊者**。

**(e) 結論**：（待 Steward 判）

---

## §4 Checklist #4 — L7.16 全棧 owner≠app 矩陣進度

**(a) 原文義務（逐字）**
> L7.16(a)（`specs/INFRASTRUCTURE-SPECIFICATION.md:193-`）：「**具結構變更權能之角色**……與**應用運行角色**……**必須**為**相異之權限主體**。」(e)：「**強制機制與其可解除者同屬一權限主體時，該不變式在憲章意義上不成立**——存疑即推定不成立（§8.3）。」
> RULING-2026-039 八.2：「全受保護儲存物件 owner≠app 矩陣——**觸發**＝雙角色部署議程或 2026-10-14 併審。」

**(b) 現況親驗（本項 07-24 基線後變動最大）**
* **RULING-2026-042 已生效**（hugo 親簽 2026-08-01，commit `5d08e16`；AL-2026-046 已登錄 `grep -c`＝1）：既成事實認定＋適用性註記——單一角色部署下 **DB 權限層強制「在憲章意義上不成立」**；触发**唯餘 2026-10-14 併審**（「雙角色部署議程」臂因 D13-3 乙消滅）；「**核心義務本身不得豁免**」「**本裁不預斷 10-14 結論**」。
* **live 角色**（本日）：`pg_roles` 僅 `augur`（**superuser**）＋`postgres`；`augur_predict` 已不存在。
* **紅燈在位**：`pytest tests/test_l716_conflict_registered.py` → **2 passed**（本日實跑）；先驗紅留痕 `audits/L716-RULING-042-REDRUN-20260801.md` 在。
* **補償控制現量（本日，口徑注意）**：全 trigger 函式 **34 種**；名含 guard 者 **8 種／73 綁定**；`honesty_delete_only_guard` 綁 **20 表**。RULING-2026-042 主文二 2 記「30 種 guard trigger 函式；honesty_delete_only_guard 23 表」（其 08-01 親驗口徑）——**兩把尺數字有出入**（042 之計數口徑未附指令；且 08-01 當日 G3 identity 六表落地新增 trigger）。本檔附指令、不判孰誤；併審引用時建議以附指令之現查為準。
* **殘餘風險不變**（042 明載）：superuser 可 `DISABLE TRIGGER`、繞過一切 GRANT；AST 稽核擋不到動態 SQL。

**(c) 既有證據指針**：RULING-2026-042（含 §四驗證四則）；`reports/augur_db_role_architecture_submission_20260731.md` §6（§6.2 OCV 四項對照）；`reports/augur_single_role_consolidation_plan_20260731.md`；`tests/test_l716_conflict_registered.py`；G3 呈案 §84（identity 六表建後同屬「半硬」層級之自陳）。

**(d) 10-14 前缺口**：〔hugo 裁〕依 L7.18(b) 處置順序作成書面——補強選型、或依 §8.2/§8.4 就履行時程為**有到期日**之處置（豁免核心義務不可）。〔AI 可備〕受保護儲存物件全清單 × 現行承載（trigger／AST／紀律）逐表矩陣＋補強選型比較呈案（如恢復最小雙角色、事件式偵測、外部 WORM 副本）。

**(e) 結論**：（待 Steward 判）

---

## §5 Checklist #5 — KDO.4／LDO.4 量測落地狀態

**(a) 原文義務（逐字）**
> KDO.4（`specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md:637`）：「KDO.4｜KS.83(i)｜未解析存量量測落地｜L5/L7｜`AUGUR-ID v1.0` IDO.4」；KS.83(i)（:513）：「未解析存量、解析時效、顯式待決同一性存量……量測落地 DEFER（KDO.4）」。
> LDO.4（`specs/COGNITIVE-KERNEL-SPECIFICATION.md:216`）：「未解析存量指標……之量測實作｜L7」。
> RULING-2026-039 五.3：「量測落地維持 DEFER L5／L7——**觸發**＝LDO.4／LDI.31 實作落地或 2026-10-14 併審；門檻數值不現寫。」

**(b) 現況親驗**
* **量測實作仍零**：`grep -rn "未解析存量" src/ scripts/` → **0 命中**。
* **但資料前置已首次存在**（07-24 基線時不存在）：identity 六表 2026-08-01 生產落地（hugo 親簽 `d177c6d`、落地 `937014b`）——本日現查 `entity_registry=3,503`／`entity_alias=3,503`／`entity_attribute_version=9,288`／`identity_lifecycle_event=344`／`identity_claim=0`／`entity_type_catalog` 在。
* **誠實界限**（G3 呈案 :80 引 `identifier.py:15-19` 自陳）：「機制就位、義務未結——攝取路徑現仍以外部碼直充身份」⇒ 未解析存量之「存量」本身尚未成為活資料流。

**(c) 既有證據指針**：`reports/w2_20260801/G3_identity_sandbox.md`；RULING-2026-039 五.3；`audits/ROADMAP-R2-…:33`。

**(d) 10-14 前缺口**：〔hugo 裁〕併審日二擇——開實作議程或明示續 DEFER。〔AI 可備〕基於六表之三指標（未解析存量／解析時效／顯式待決同一性存量）唯讀量測 SQL 原型＋門檻值選項呈案。

**(e) 結論**：（待 Steward 判）

---

## §6 Checklist #6 — 020 M2 仍 deferred 或另案承接

**(a) 原文義務（逐字，`constitution/RULING-2026-020-L6-DISPOSITION.md`「M2 執行（甲案）」段）**
> 「**產物閉集／展示分級／零寫入之 DB 物理強制**下放收窄——L7 現未承接，俟 L7 §8.2 正式設計；此前 L6 側 fail-closed 介面義務仍為單一執法點、不因 L7 未承接而免除。」
> RULING-2026-039 九.1：「維持 **honest deferred**……**禁止假關**、不虛假下放。**觸發**＝L7 正式設計產物表 trigger **或** Steward 另裁收窄／承接。」

**(b) 現況親驗**：07-24 基線後**無變動**——未見 L7 產物表 trigger 之正式設計議程檔；L7 spec 版本未升（lint 綠、`AGENT-RUNTIME` L6.21 與 `INFRASTRUCTURE` cross-layer 誠實句原文未改）；F-L7-8 追蹤義務（RULING-2026-037）在卷。

**(c) 既有證據指針**：RULING-2026-020／037（F-L7-8）／038 §一／039 九.1；`specs/AGENT-RUNTIME-SPECIFICATION.md` L6.21；`audits/ROADMAP-R2-…:34`。

**(d) 10-14 前缺口**：〔hugo 裁〕併審日確認「仍 deferred」或另裁收窄／承接（純書面即可）。〔AI 可備〕誠實輸出契約產物面現況盤點（產物表有無 trigger 級零寫入強制之逐表清單）。

**(e) 結論**：（待 Steward 判）

---

## §7 Checklist #7 — GOV-3 B 有無新越權 Evidence

**(a) 原文義務（逐字）**
> RULING-2026-028 第 2 點：「凡 AI 系統於治理文書鏈（憲章／裁決／附則／生效規格）之任何施作，一律適用第 3 點義務」；第 3 點＝施作留痕＋獨立核驗常態化；:59：「GOV-3 B……判準先以解釋運行，若再現越權事件……以實務案例為 Evidence 升格 [N]」。
> META-CONSTITUTION Appendix I（:727）：「GOV-3 B……＝**維持觀察觸發**……本輪不升格。」039 一.2：本裁再確認＝已拍板維持。

**(b) 現況親驗——候選事證清單（是否構成「新越權 Evidence」專屬 Steward 認定；本節僅列、不定性）**
| # | 候選事證 | 載體與現查 | 備註 |
|---|---|---|---|
| 1 | 2026-07-25 AI 代填 `promoted_by='hugo'`（人簽欄代打） | live `local_model_version` 現 3 列 `promoted_by='hugo'`（07-25×2、07-26×1）、1 列 NULL；**DB 本身無法自證由誰鍵入**；事件記錄現存於 session 記憶（「不代打人簽」則，self-reported）——**repo 內查無該事件之正式留痕檔** | 時點在 028（07-23）之後；周邊佐證＝`reports/augur_treaty_core_alignment_plan_20260730.md:208/:356` 已把「人類簽核代打」列為 P5.W2 偽造向量並提案 CLAUDE.md 新條，**現行 CLAUDE.md v1.35 尚無「不代打人簽」明文**（`grep 代打 CLAUDE.md`→0）；r2 深化 N4 另指 `local_model_version` INSERT 路徑零人簽硬檢 |
| 2 | 2026-07-31 單一角色整併之 OCV 弱化（人類介入點 −1、揭露比例下降） | RULING-2026-042 主文二 1 已認定為 **Steward 拍板之既成事實**並補登 AL-2026-046 | 已循程序留痕；是否仍列 GOV-3 盤點材料＝Steward 定 |
| 3 | 07-23 後治理文書鏈施作之程序面 | 042 附先驗紅（`audits/L716-RULING-042-REDRUN-20260801.md`）＋同 commit 紅燈；TTY 親簽包 `d96937a`（9 格一次 session 簽完） | 形式上循 028 第 3 點體例 |

**(c) 既有證據指針**：RULING-2026-028／039 一.2／040 獨立核驗 #4；MC Appendix I。

**(d) 10-14 前缺口**：〔hugo 裁〕併審日盤點上表並二擇——升格 [N] 或維持觀察（040／優化計畫 §二 #7 之二擇）；候選事證 1 若採為 Evidence，宜先由 hugo 確認事實並補正式留痕（現僅記憶級）。〔AI 可備〕07-23 以來治理文書鏈施作之留痕／核驗對照清單。

**(e) 結論**：（待 Steward 判）

---

## §8 Checklist 外之 2026-10-14 日曆項（窮舉補遺；同樣不代勾）

### 8-A RULING-2026-002 主文二——五檔合規聲明補正（期限 10-14）
* **原文**（`constitution/RULING-2026-002-LAYER1-ADOPTION.md:37`）：「五檔之 Constitutional Compliance Statement **補正期至 2026-10-14（90 日）**，期內推定有效……一律依 `AUGUR-WM v1.0 §11` 格式」。
* **現況**：五檔 CS **全數存在**——`docs/compliance/`：CS-CLAUDE.md、CS-系統核心思想_v1.10.0.md、CS-原則精華_v1.12.0.md、CS-系統架構大憲章_v1.54.0.md、CS-datasets_zh.md（另存 v1.47.0/v1.48.0 舊版）；各檔頭自稱「主文二本檔補正已履行」；lint PASS 7/7。
* **出入（誠實列）**：`CS-系統架構大憲章_v1.54.0.md` **檔內版本漂移**——標題與 `spec-version`＝v1.53.0、CS.2 稱覆蓋 v1.50.0、檔名與「正文 SSOT」＝v1.54.0，四處三值。是否須補正一致＝待 Steward 判。
* **缺口**：〔AI 可備〕版本欄一致化 patch 草案；〔hugo 裁〕10-14 認定補正完成與否。**結論：（待 Steward 判）**

### 8-B RULING-2026-002 主文五——檔頭從屬聲明＋「唯一真相來源」措辭 patch（期限 10-14）
* **現況親驗**：五檔檔頭**均已有**「憲章從屬（AUGUR-MC v1.6）」聲明（本日 head 親讀：CLAUDE.md／系統核心思想／原則精華／大憲章／datasets_zh 各 :2-3）。措辭 patch：大憲章正文採「唯一系統記錄」（3 處）；殘 2 處「唯一真相來源」皆非違規語境（:34＝AUD-26 正名說明自引舊語、:423＝SUPERSEDED 修訂史）。下游 docstring 漸改屬 patch 級持續項。
* **缺口**：〔hugo 裁〕10-14 認定主文五結案與否。**結論：（待 Steward 判）**

### 8-C LDI.7／L7.60(b)(c)——大憲章＋datasets 逐節 Layer 標注（補正期 10-14）
* **原文**（`specs/INFRASTRUCTURE-SPECIFICATION.md:543`）：「系統架構大憲章涉 Layer 4–6 之章節、datasets 參考文件涉 Layer 1–4 之內容，其**逐節／逐條 Layer 標注**必須由各該檔之 Compliance Statement 載明……至 2026-10-14」；:1015 自載「**尚未完成**」。
* **現況親驗**：`CS-系統架構大憲章_v1.54.0.md` 檔頭稱「涉 L4–6 由本聲明逐節標注」，**但全檔（54 行）無任何逐節標注表**（僅 CS.1 七節逐原則論證）——宣稱與內容不符。`CS-datasets_zh.md` CS.4 有一句總括「整體 Layer 7……不含 L4–6 義務句」（是否滿足「逐節」要求＝待 Steward 判）。
* **缺口**：〔AI 可備〕大憲章逐章 Layer 歸屬草表（呈案）；〔hugo 裁〕標注粒度之認定與收尾。**本項為 checklist 外最實質之未完成義務。結論：（待 Steward 判）**

### 8-D D-PRIN-2——AUD-02 `raw_supersede_log` code／migration 操作閉合（至遲併 10-14）
* **原文**（`docs/compliance/CS-原則精華_v1.12.0.md:69`）：「AUD-02 raw_supersede_log **code**／migration 操作閉合……至遲併 **2026-10-14** 補正／Phase 7 節奏……不假關 039 其他項」。
* **現況親驗**：live 表**已存在**且活躍——`raw_supersede_log` 本日 **4,665 列**（GROUNDING-MAP 07-31 記 3,914 → 增量中）；`tests/test_raw_supersede_log.py` 在。
* **缺口**：〔hugo 裁〕D-PRIN-2 可否關閉之認定（含 migration 面是否已閉）。**結論：（待 Steward 判）**

### 8-E C1——validation_evidence manual 5 條有效期（到期 10-09／10-10，**恰在併審前**）
* **現況親驗**（live 本日）：19 列證據帳、5 列 manual 全 green 且 `valid_until` 已落——**E3、E4_gm＝2026-10-09；E2、E5、E7＝2026-10-10**（90 天案；DDL 三步已落地 commit `4b43ac6`/`b8821bb`；到期自動轉 unverified 紅之降轉機制與 cron 排程 live）。
* **時序含義**：**五綠燈將於 10-14 併審前 4–5 日全數到期**——屆時若未重簽，併審桌上此 5 項顯示為紅（unverified）。重簽＝hugo TTY 親跑（AI 不代打人簽）；C1 呈案 :92 建議「重簽可併該次復審一次做完」。
* **缺口**：〔hugo 裁〕提前重簽或併 10-14 一次辦之擇定。**結論：（待 Steward 判）**

### 8-F RULING-2026-012 Phase 7——治權收尾（期限驅動 10-14）
* **原文**（`CODE-MIGRATION-PLAN.md:77-78`）：「Phase 7——治權收尾（期限 2026-10-14）：五份治權檔完整合規聲明……；原則精華 #7 條文改……；審計報告終局定案（§8.2）。」
* **現況**：三子項——(1) 五檔 CS：見 §8-A（存在、lint 綠）；(2) #7 條文改：**已由 RULING-2026-041 執行**（原則精華 v1.10.0 改條；現行 v1.12.0）——`CODE-MIGRATION-PLAN.md:129`「條文實改仍待執行」為**過期敘述**（早於 041）；(3) 審計報告終局定案（§8.2）：**查無單獨結案留痕**。另誠實記：Phase 2/3/4/5 兩週窗（自 07-18 起算）已過，runtime 接線 GROUNDING-MAP 稱多未動（identity 六表 08-01 落地屬 Phase 2 面之進展）——排程滑動之處置屬 Steward。
* **缺口**：〔hugo 裁〕Phase 7 收尾認定＋(3) 之定案；〔AI 可備〕計畫檔 :129 過期敘述之機械軌更正呈案。**結論：（待 Steward 判）**

---

## §9 已由後續裁決承接之 10-14 提及（列出以示窮舉完整；不另立項、不假關）

| 提及處 | 內容 | 承接情形 |
|---|---|---|
| RULING-2026-011:25 | L7 §8.2 七項必審列管至 10-14 | 已於 2026-07-19 作成（RULING-2026-025）→ 化為 §2 之 residual 日曆 |
| RULING-2026-019/023（CK spec :15） | L5 矩陣重作窗硬期限 10-14＋§8.1 橋接 | 023 重採認（07-19）→「橋接功成身退」；後 029/035 蓋章 |
| COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md:44 | 過渡規則 (b) 補正期引用 | 模板已功成身退（002 主文三）；實體義務即 §8-A |
| PROPOSAL-2026-001:57 | §8.2 未結案件（10-14）與修訂正交之註記 | 純註記；無獨立義務 |
| RULING-2026-039 八.2 之「雙角色部署議程」觸發臂 | L7.16 雙觸發之一 | **已由 RULING-2026-042 主文三認定消滅**（2026-08-01）→ 唯餘 10-14 併審 |

---

## §10 最大缺口 Top 3（AI 彙整判讀，self-reported）

1. **WM.35/36（§1）——唯一「到期即自動生效之禁令」**：Registry 本體零落地、vendor 直綁 47 檔（不減反增）、S22 code 層證據自載三弱點；2026-10-15 起消費禁令**無條件適用**，現行管線消費將整面落入違規語境。其餘各項到期日是「復審日」，本項到期日是「法律效果切換日」。
2. **L7.16（§4）——單一角色下權限錨定在憲章意義上不成立（042 已誠實登錄）**：涉及**全部**受保護儲存物件；10-14 須依 L7.18(b) 作成有到期日之處置，且核心義務不得豁免——與 025 ②③（單人單機單碟；繼任人 AL 零登錄、G2 異地備份呈案待拍板）同源，實質為同一個「單一自然人／單一機器」物理現實的兩面。
3. **時序依賴（§8-E＋§2）——併審前 4–5 日五綠燈全到期**：C1 manual 5 條 10-09/10-10 到期自動轉紅、重簽唯 hugo TTY；加上 G2 拍板、繼任人指定等純 hugo 動作若壓到 10-14 當日，併審負載集中——可分流的 hugo 動作宜先於 10-14 排定。

---

## §11 親驗指令彙錄（全唯讀；2026-08-01 實跑）

```text
git HEAD                          → b98bc04（lint 自標 +dirty）
grep -rn "2026-10-14|10-14" constitution/ docs/compliance/ specs/   → 99 命中（窮舉母集）
ULTRACODE-SCHEDULE.md:116-122     → 七勾選框全 [ ]
python3 -m tools.constitution_lint report → PASS 7/7、七層 error 0
psql pg_roles                     → augur(superuser)、postgres 二者；augur_predict 不存在
psql pg_class '%concept%'         → NONE（WM.36 registry 表零）
grep -rlE 'FROM\s+"Taiwan' src scripts --include='*.py' | wc -l     → 47
venv/bin/python -c "…check_isolation…"                              → violations=0
venv/bin/python -m pytest tests/test_l716_conflict_registered.py -q → 2 passed
psql trigger 計數                 → 全函式 34；guard 名 8 種/73 綁定；honesty_delete_only_guard 20 表
psql validation_evidence          → 19 列；manual 5 列 green，valid_until=10-09×2、10-10×3
psql identity 六表                → entity_registry 3503/entity_alias 3503/entity_attribute_version 9288/
                                    identity_lifecycle_event 344/identity_claim 0/entity_type_catalog 在
psql raw_supersede_log            → 4,665 列
psql local_model_version          → 4 列全 retired；promoted_by：hugo×3（07-25×2、07-26×1）、NULL×1
crontab -l | grep -cE "validation_evidence|backup_database|AUGUR"   → 5
grep 繼任 constitution/AMENDMENT-LOG.md → 1 命中（義務設立；查無預先指定登錄）
grep 代打 CLAUDE.md               → 0（v1.35 無「不代打人簽」明文條）
```

*建立：2026-08-01｜F2 唯讀備料｜下一日曆錨：2026-10-14 併審（Steward 裁決域）*

---

## 追記（2026-08-03，M-N1 第 19 步／M-N13——加時戳與現值對照；正文不改）

本節為追加式現值對照（r4 §3.2 慣行：引用時加限定詞、不改正文）。下列數字由 M-N1 探針之
`check_cmd` 當場導出、不手抄；`read_treaty_probes.py --check` 對本節 `<!--probe:ID-->` 標記
與 live 值驗 diff，漂移即 rc≠0。

- **§1（line 43）「Registry 表本體 → NONE」＝08-01 當日值，已過期**。live 現值：public 內
  `relname LIKE '%concept%'` 之 base table＝<!--probe:doc_f2_registry_tables-->3<!--/probe--> 張
  （probe `doc_f2_registry_tables`；2026-08-03 現查＝`world_concept`／`world_concept_registry_legacy`／
  `world_concept_version`）。「零落地」敘述不再成立；惟七欄結構與 `authoritative_binding_id`
  落值是否達 WM.36 要件仍屬 Steward 裁決域（M-W5），本節不代判。
- **§1（line 49）／§5（line 215）「直綁 47 檔」＝08-01 當日值（其尺未載）**。live 現值
  （尺＝`grep -rlE 'FROM\s+"Taiwan' src scripts --include='*.py' | wc -l`，已登錄為
  `vendor_direct_bind/grep_from_taiwan_src_scripts`、authoritative=false）＝
  <!--probe:doc_f2_vendor_bind_grep-->51<!--/probe--> 檔（probe `doc_f2_vendor_bind_grep`）。
  **權威尺選定＝M-N7（Steward 裁決域），本節不代裁**；四把尺並存現況見
  `reports/augur_optimization_master_plan_20260803.md` 第 20 步。
