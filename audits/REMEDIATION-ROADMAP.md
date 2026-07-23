# Augur 合憲補正行程（Remediation Roadmap）

* **建立日**：2026-07-16
* **授權**：Constitution Steward（tsaitsangchi）指示自主逐步展開執行、每步完成即上傳
* **基準**：合憲審計報告（audits/CODE-COMPLIANCE-AUDIT-2026-07-16.md，已驗證＋裁決定調）；補正三波優先序（報告第六節）＋解釋裁決 2026-001（P4.E3 家族尺度）
* **性質**：§8.2 補正追蹤之治理文件；隨各步完成更新狀態

---

## 排程原則

1. **憲章由上而下**：先立上層規格，再依規格補正下層程式（`AUGUR-MC §0.6` lex superior、constrains）。
2. **critical 前置**：三項 critical 優先解消——AUD-01（Layer 1 規格已生效）、AUD-02（活違憲、獨立、可立即補）、AUD-03（Layer 4 DEFER，需先建 Layer 4）。
3. **每步一循環**：ultracode 工作流程（設計→對抗審查→修訂）→ 我親自複核 → commit → push GitHub。
4. **生產系統紀律**：凡動 [tsaitsangchi/augur](https://github.com/tsaitsangchi/augur)（活台股系統）之程式補正，一律走**分支**、附 migration＋測試＋對抗驗證，**不對生產 DB apply、不併 main**——套用與合併保留給人類（P5.W2、該系統既有「決策層人拍板」紀律）。

---

## 行程表

| 步 | 事項 | 解消 | 產出位置 | 狀態 |
|---|---|---|---|---|
| 6 | **本補正行程**（排程與追蹤） | — | augur-constitution | 🔄 進行中 |
| 7 | **AUD-02 補正**：raw_supersede_log 帳表＋heal 覆寫前快照舊列（同交易），upsert 主路徑不動 | **AUD-02 critical**（P4.E5 MUST NOT，§8.4 不可豁免） | augur-code 分支 | ✅ 程式實作完成、統一於 [PR #2](https://github.com/tsaitsangchi/augur/pull/2)（分支 `remediation/aud-02-consolidated`）＝ `impl-2026-07-17` 實作 ＋ 補可執行 DB 行為回歸測試；另一 session 之獨立實作（PR #1）交叉驗證同樣三發現後關閉、統一取代。**✅ 真 PG 16.14 實測全綠**（userspace micromamba/conda-forge；15 tests：8 純函式/gate＋7 DB 六不變式；migration 冪等＋VERIFY；51 回歸）——六不變式門檻已達；待人類 #19 檢視＋P5 拍板後 apply 生產 DB、併 main |
| 8 | **Layer 2 Ontology 規格**：台股世界類型體系、同一性判準框架 | AUD-04 類型面、承接 AUGUR-WM D2/D3 掛鉤 | augur-constitution | ✅ **v1.0 生效**（2026-07-17 充任認定：裁決 2026-003／AL-2026-007 @`15d61b6`）；v0.1-draft 定稿於 `fe45620`、原文歸檔於 `specs/ONTOLOGY-SPECIFICATION-v0.1-draft.md` |
| 9 | **Layer 3 Identity 規格**：entity registry、identifier 鑄造、lifecycle（merge/split/retire）、identity claim、跨來源解析 | **AUD-04/05/06 三項 major**、AUD-07、AUGUR-WM D1/D3/D4/D5/D6/D17 | augur-constitution | ✅ **v1.0 生效**（2026-07-17 充任認定：裁決 2026-004／AL-2026-008 @`3b50197`）；v0.1-draft 定稿於 `2a38255`、原文歸檔於 `specs/IDENTITY-SPECIFICATION-v0.1-draft.md` |
| 10 | **Layer 4 Knowledge System 規格**：Confidence 單一形式化語義、五元組欄位、雙時間 as-of、supersede/tombstone、信任分級 | **AUD-03 critical**、AUD-08/16、形式化 AUD-02、AUGUR-WM D7–D11 | augur-constitution | ✅ **v1.0 生效**（2026-07-17 充任認定：裁決 2026-005／AL-2026-009 @`3b50197`）；v0.1-draft 定稿於 `49a6add`、原文歸檔於 `specs/KNOWLEDGE-SYSTEM-SPECIFICATION-v0.1-draft.md` |
| 11 | **結構補正施工**：entity registry/claim/lifecycle/屬性 as-of（AUD-04/05/06/07）、行動六元組 log（AUD-10/11）、prediction append-only 伴生表（AUD-08）——9 table＋python，全新增式 | AUD-04/05/06/07/08/10/11 | augur-code 分支 | ✅ **九表已 apply 生產（2026-07-18）**：沙盒實測→P5 拍板→生產 apply 驗證綠。runtime 接線（resolve-or-mint、action_log 掛載、serving 消費切換）＋AUD-01 直綁消除為 follow-up Phase 1-5 |
| 12 | **治理收尾**：五治權檔合規聲明（依 AUGUR-WM §11）＋檔頭從屬聲明＋「唯一系統記錄」措辭 patch；審計報告最終定案 | AUD-12/13/26、RULING-2026-002 主文二/五交辦（期限 2026-10-14） | augur-code＋augur-constitution | 🟡 部分完成 |

**步 12 進度**：✅ **檔頭從屬聲明**（5 檔）＋**SSOT 措辭正名**（大憲章「唯一真相來源」→「唯一系統記錄」＋WM.9 權威三分釐清，AUD-26）已於 augur-code main 完成，封存於 tag **`augur-mc-v1.3-compliance-seal`**（[tsaitsangchi/augur](https://github.com/tsaitsangchi/augur) @ 493fd73，2026-07-17）；AUD-02 卷宗一併併入 main。⬜ **待辦**：五治權檔完整合規聲明（AUGUR-WM §11＋WM.44 逐條矩陣，期限 2026-10-14）；原則精華 #7 條文改「新版本入庫、舊版標 superseded」（須 Steward 拍板）；審計報告最終定案。

**critical 解消里程碑**（更新 2026-07-17）：✅ AUD-03 規格層已解（步 10，Layer 4 Confidence L_C 格）；🟡 **AUD-02 程式實作完成、統一於 PR #2**（DRAFT，**未併 main、未 apply 生產 DB**）；**待人類 #19 檢視＋P5 拍板**（步 7）——與本表步 7 列一致；🟡 AUD-01 規格層已解（Layer 1 生效），code 面待步 11 落地。

**概念層規格 Layer 1–4 全數生效**（**M1 達成**）：WM v1.0；**ONT v1.0 @`15d61b6`**（裁決 2026-003／AL-2026-007）；**ID v1.0＋KS v1.0 @`3b50197`**（裁決 2026-004／AL-2026-008、2026-005／AL-2026-009）。**執行層 L5／L6 亦已生效**：**L5 v1.0（provisional，§8.2 延後）@`b48f699`**（裁決 2026-006／AL-2026-010）、**L6 v1.0（含 §8.2 實質人類審查）@`b372d71`**（裁決 2026-007／AL-2026-011）。**L7 v0.1-draft 未生效、充任受阻。**

> **基線漂移聲明**：本檔前次 commit `e439f89` 為 **2026-07-17 09:19**，早於當日全部充任認定（ONT 11:43／ID＋KS 11:49／L5 12:36／L6 13:45）**2～4.5 小時**。前版此處記「ONT/ID/KS v0.1-draft 待充任認定」與步 8/9/10 之「定稿…待充任認定」即為該 09:19 快照之殘留，**已據實更新**。**⚠️ 生效 ≠ 無瑕疵**：§8.3 gate 硬化後測得四份生效規格仍有未結之 WM.44-LABEL 誤標，且 L2 之 Annex TR 從未受檢——見 HANDOFF 待裁 #22。

## ⚠️ 目前阻塞（更新 2026-07-17）

**已解**：步 7 兩項治權決策經 Steward 拍板（決策 A=加 trigger＋tombstone 例外、決策 B=nullable 事後回填）；步 7 計畫定案。

**仍待處置**：

1. ~~每月消費上限~~ ✅ **已解除**（2026-07-17 起工作流程正常執行；步 8、9 均以完整多代理流程完成）。
1b. ~~**充任認定前置（Layer 2–4 共同）**：各層合規聲明依 `AUGUR-WM v1.0 §WM.44` 須有**逐條對應矩陣**~~ ✅ **已解（2026-07-17）**：ONT／ID／KS 三層 Annex TR **逐條完整枚舉、缺 0 條**，`§WM.44` 形式充分性成就，已隨充任認定生效（裁決 2026-003／004／005）——依據見 `IDENTITY-SPECIFICATION.md:17`、`KNOWLEDGE-SYSTEM-SPECIFICATION.md:17` 之【地位】節逐字記載。
    > **惟形式充分性 ≠ 實質正確**（交叉參照，非本檔之認定）：`§8.3` gate 硬化後測得 —— (i) **L2（ONT）之 Annex TR 標題為 h1，其 <!--lint:tr_rows_L2-->66<!--/lint--> 列矩陣從未被 gate 讀取**（比對筆數 <!--lint:compared_L2-->4<!--/lint--> 筆——矩陣在場、一列未讀；二數均由 `python3 -m tools.constitution_lint report` 導出並綁定），故其「缺 0 條／PASS」未經機器複核；(ii) ONT 之 Annex TR 標 **[I]** 而 ID／KS 標 **[N]**，同一義務之標注不一致。二者均屬 **Steward 事項**（生效規格之編輯屬 `§8.5`／`§8.6`），本檔不作認定，見 **HANDOFF 待裁 #22**。
2. ~~augur-code 推送權限~~ ✅ **已授權並完成**（2026-07-17，Steward 明示「直接進 main＋tag」）：AUD-02 卷宗＋治權檔憲章從屬聲明＋SSOT patch 已進 augur main（`493fd73`），封存 tag `augur-mc-v1.3-compliance-seal`。
   > ⚠️ **分支名碰撞，讀此句務必分辨**：`remediation/aud-02-raw-supersede-log` **有二個不同物**——
   > * **本機分支 @`759f3e5`**（AUD-02 **卷宗** commit）：確為 `main` 之祖先，**已 ff-merge 入 main**（`git merge-base --is-ancestor` → YES）。**本句所指者為此。**
   > * **GitHub 同名遠端分支 @`5432389`**（PR #1 之**實作** head）：**非** `main`、**亦非** `origin/main` 之祖先（二者皆 → NO）。**PR #1 已 CLOSED（非 merged）**，由 **PR #2**（`remediation/aud-02-consolidated`）取代——與本檔步 7 列及更新紀錄末條一致。
   >
   > 即：**進 main 的是卷宗，不是 PR #1 的實作**。前版僅書分支名，讀者易誤認 PR #1 之實作已達 main。**建議將本機分支改名以消除碰撞。**
3. **步 7 程式實作之閘**：依 augur-code CLAUDE.md #20（計畫先行＋拍板後實作）、#7（須實測，本機無 PostgreSQL）、#19（核心共用模組逐檔檢視），程式實作待額度恢復後由工作流程 build 階段續行（含被中斷之三重對抗審查）；不於未測、未審下硬寫核心寫入路徑。

## 更新紀錄

* 2026-07-16：行程建立（步 6）；步 7（AUD-02）設計＋評審完成（取向 B），施工階段因消費上限中斷。
* 2026-07-17：步 7 兩項治權決策拍板、計畫定案（decisions A/B）；消費上限解除；步 8（Layer 2 Ontology）定稿封存（fe45620，27 issue 全處置）；步 9（Layer 3 Identity）定稿封存（2a38255，18 issue 全處置）；步 10（Layer 4 Knowledge）啟動。
* 2026-07-17：步 12 部分完成——augur-code 治權檔憲章從屬聲明（5 檔）＋SSOT 措辭正名＋AUD-02 卷宗進 augur main（493fd73），封存 tag `augur-mc-v1.3-compliance-seal`。
* 2026-07-17：步 7（AUD-02 程式實作，5cee263）＋步 11（結構補正 9 table＋python，7932ba9）完成，推 augur 分支 `remediation/impl-2026-07-17`，交接 `docs/remediation/HANDOFF-2026-07-17.md`。全走分支、未 apply DB、未併 main（待人類 #7 實測＋#19 檢視＋P5 拍板）。5 項升 Steward/P5 裁決（見 HANDOFF §三）。
* 2026-07-17：**兩份 AUD-02 實作合流**。另一 session 獨立以工作流程實作 AUD-02（PR #1，`remediation/aud-02-raw-supersede-log`），經三重對抗審查抓到 psycopg2 `Json(default=)` blocker＋TRUNCATE 繞過＋第三 heal 路徑——與 `impl-2026-07-17` **獨立同抓**同三發現（強交叉驗證）。依 Steward「合併取長、統一一份」：以 `impl-2026-07-17`（超集：REVOKE 縱深/SECURITY DEFINER/actor 欄/INFRA_DDL 單一源/`_supersessions` 純函式）為 canonical 基底，補其所缺之可執行 DB 行為回歸測試 `tests/test_raw_supersede_log.py`，統一於 [PR #2](https://github.com/tsaitsangchi/augur/pull/2)（`remediation/aud-02-consolidated`）；PR #1 關閉。零 DB 全綠；DB 六不變式待真 PG 實測＋P5。
