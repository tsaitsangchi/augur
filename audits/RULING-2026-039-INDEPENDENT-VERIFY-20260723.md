# RULING-2026-039 獨立對抗核驗報告

* **性質**：[I] 審查素材；非施作者逐項覆核 RULING-2026-039 第十四節十項
* **施作者 commit**：`31491ad`（tag `archive-20260723-039-residual-omnibus`）
* **核驗者**：Cursor 獨立核驗 agent（非施作者）
* **核驗 HEAD**：`31491ad4a42dc3719aa7c92a15a8c1fd5682f4cf`（親跑 lint 同 HEAD）
* **方法**：逐項檔案原文／`git show 31491ad`／`rg` 殘留掃描／`python3 -m tools.constitution_lint report` 親跑
* **依據**：`constitution/RULING-2026-039-L0-L7-RESIDUAL-OMNIBUS.md` 第十四節；先例＝RULING-2026-038 §九

---

## 十項結果

| # | 核驗項 | 範圍 | 判定 | 證據 |
|---|---|---|---|---|
| 1 | **禁止假關六項**仍 open／deferred／日曆 | OT-5、T-KS-6、T-L6-5、025、020 M2、10-14 | ✅ PASS | **OT-5**：ONT CS `open-tensions: […OT-5]` `:513`；CS.8 表 `:581` 仍揭露 T.28 parent 分歧；039 diff 未改為「已解消」。**T-KS-6**：KS CS `open-tensions` 含 T-KS-6 `:999`；CS.2 `:1033` 仍列定性分歧待 ID／KS 升版對齊；034 狀態未動。**T-L6-5**：AR CS `:495`「**OCV 維度充分性 residual open-tension 保留**」；039 排程明示「007 residual 維持」。**025**：INF【地位】`:570` 分階段①、復審 **2026-10-14**；039 diff 未結清 (iii)(iv)(vi)。**020 M2**：AR L6.21 `:211`「**L7 現未承接**…020 M2 甲案收窄」；INF `:1073` cross-layer「**L7 誠實未承接**」；039 僅再確認 deferred。**10-14**：CK【地位】`:16`、INF【地位】`:570`、WM WM.35/36 過渡規則仍 **2026-10-14**；`ULTRACODE-SCHEDULE.md` checklist 七項全 `[ ]` 未勾結清 |
| 2 | **XRF-1** 工具層措辭仍「97[N]+5[I]」；017／026 歷史本文未改 | L0 | ✅ PASS | `tools/constitution_lint/mc_clauses.py:1`「102 條條款宇宙（97 [N]＋5 [I] WHY）」；`README.md:266` 同型；`git diff 31491ad^..31491ad -- constitution/RULING-2026-017* constitution/RULING-2026-026*` 零行 |
| 3 | **Issuer T.20** 仍待採認；改名／借殼仍保守 | L1／L3 | ✅ PASS | ID `:357`「**Issuer（T.20）判準仍待採認**」；T-ID-3 `:748` 同型；039 裁決 §三「**不另採認**」。改名／借殼：ID `:357`「改名／借殼殘留面續依保守預設（030／033）」；039 §二／§三「**維持保守預設**」；039 diff 無 OPEN-1 採認新 [N] |
| 4 | **F-L1-2／3** 無新 [N]；T.6／L7.21(f)／KDO.1 概念閉敘事一致 | L1–L7 (A) | ✅ PASS | F-L1-2／3：`ULTRACODE-SCHEDULE.md:51-52` DEFER 下次 WM 升版；039 diff 對 WM 僅 `mc-version` 一行、無 Annex C 新 [N]。**T.6**：ONT T.6 `:293` 判準含「外部識別碼體系×代碼值×有效期間」（032 三要素）。**L7.21(f)**：INF `:249-254` 四欄 NOT NULL＋引擎拒絕＋回歸掛點 `tests/test_l7_knowledge_not_null.py`（037 已立；039 追認）。**KDO.1**：CK L5.3 `:119-120` 承接 KDO.1 Confidence 傳播；LDI.1 `:196` 掛鉤一致 |
| 5 | **L1–L6 `mc-version`＝v1.5**；L7 維持 v1.5 | CS FM | ✅ PASS | 六份生效本 Annex CS front-matter 均 `mc-version: AUGUR-MC v1.5`（WM `:784`、ONT `:508`、ID `:708`、KS `:994`、CK `:462`、AR `:450`）；L7 INF `:957` 已 v1.5（037）；`selftest.py` 合成落差鎖同步改 v1.5↔v1.4 |
| 6 | **AL-041** 補登對齊 RULING-037；**AL-043** 對齊本裁 | 簿記 | ✅ PASS | AL-041 `:432-439` 事項／文件／037 定案／「漏寫入本簿…機械補登」與 RULING-037 一致；AL-043 `:451-458` 事項 bullet 對齊 039 §〇–§十一分類 (A)–(E) |
| 7 | **lint PASS 7／7** | corpus | ✅ PASS | 親跑 `python3 -m tools.constitution_lint report`：PASS 7/7、total_errors=0、total_warnings=0、git_head=31491ad |
| 8 | **PA／五原則／MC [N] byte 零改** | `constitution/` `docs/` | ✅ PASS | `git diff 31491ad^..31491ad -- constitution/META-CONSTITUTION.md docs/` 零行；constitution/ 僅 AMENDMENT-LOG＋新 RULING-039 |
| 9 | **蓋章不動搖**；各層版本號未升 | 全案 | ✅ PASS | AL-043 登錄**零 major**；spec-version 未變（WM/ONT/ID v1.0、KS v1.1、CK v1.0、AR v1.2、INF v1.0）；31491ad diff 無版本欄變更 |
| 10 | **超 scope 零**：diff 限本裁核示 | git diff | ✅ PASS | 31491ad 限 12 檔（6 specs mc-version＋RULING＋AL＋2 排程＋plan＋selftest）；+257/-16；無 MC [N] 本文、無規格 [N] 實質改、無 major 升版 |

---

## 總評

**接受**——RULING-2026-039 第十四節十項全 ✅；施作者 commit `31491ad` 與裁決核示一致；禁止假關六項均維持 open／deferred／2026-10-14 日曆；(A) 類 mc-version v1.5＋selftest 鎖已同步；lint PASS 7/7 親跑確認。

## 建議 Steward 下一句

> L0–L7 殘留 omnibus 定案＋獨立核驗 PASS（2026-07-23）。全棧 ultracode／3b／039 殘留拍板已齊——**2026-10-14 併結 checklist** 為下一日曆錨（025／029／WM.35／36＋C／D 觸發項）；020 M2 trigger 仍 honest deferred，俟 L7 正式設計或另裁。

---

*本報告為 [I] 審查素材；核驗者≠施作者 31491ad。*
