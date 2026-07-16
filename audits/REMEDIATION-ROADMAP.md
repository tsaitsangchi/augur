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
| 7 | **AUD-02 補正**：raw_supersede_log 帳表＋heal 覆寫前快照舊列（同交易），upsert 主路徑不動 | **AUD-02 critical**（P4.E5 MUST NOT，§8.4 不可豁免） | augur-code 分支 | 🟡 計畫定案（決策 A/B 已拍板）；程式實作依 augur-code #20/#7/#19 受閘，待額度恢復由工作流程 build 續行 |
| 8 | **Layer 2 Ontology 規格**：台股世界類型體系、同一性判準框架 | AUD-04 類型面、承接 AUGUR-WM D2/D3 掛鉤 | augur-constitution | ✅ 定稿（v0.1-draft，commit fe45620；待 Steward 充任認定）|
| 9 | **Layer 3 Identity 規格**：entity registry、identifier 鑄造、lifecycle（merge/split/retire）、identity claim、跨來源解析 | **AUD-04/05/06 三項 major**、AUD-07、AUGUR-WM D1/D3/D4/D5/D6/D17 | augur-constitution | ✅ 定稿（v0.1-draft，commit 2a38255；待充任認定）|
| 10 | **Layer 4 Knowledge System 規格**：Confidence 單一形式化語義、五元組欄位、雙時間 as-of、supersede/tombstone、信任分級 | **AUD-03 critical**、AUD-08/16、形式化 AUD-02、AUGUR-WM D7–D11 | augur-constitution | ✅ 定稿（v0.1-draft，commit 49a6add；WM.44 矩陣完整、形式充分性成就；待充任認定）|
| 11 | **結構補正施工**：世界概念 registry、SQL 直綁消除（AUD-01）、entity registry＋lifecycle（AUD-04/05）、prediction_values append-only（AUD-08）、行動留痕六元組（AUD-10/11） | AUD-01 code 面、AUD-04/05/07/08/09/10/11 | augur-code 分支 | ⬜ 待辦 |
| 12 | **治理收尾**：五治權檔合規聲明（依 AUGUR-WM §11）＋檔頭從屬聲明＋「唯一系統記錄」措辭 patch；審計報告最終定案 | AUD-12/13/26、RULING-2026-002 主文二/五交辦（期限 2026-10-14） | augur-code＋augur-constitution | 🟡 部分完成 |

**步 12 進度**：✅ **檔頭從屬聲明**（5 檔）＋**SSOT 措辭正名**（大憲章「唯一真相來源」→「唯一系統記錄」＋WM.9 權威三分釐清，AUD-26）已於 augur-code main 完成，封存於 tag **`augur-mc-v1.3-compliance-seal`**（[tsaitsangchi/augur](https://github.com/tsaitsangchi/augur) @ 493fd73，2026-07-17）；AUD-02 卷宗一併併入 main。⬜ **待辦**：五治權檔完整合規聲明（AUGUR-WM §11＋WM.44 逐條矩陣，期限 2026-10-14）；原則精華 #7 條文改「新版本入庫、舊版標 superseded」（須 Steward 拍板）；審計報告最終定案。

**critical 解消里程碑**：✅ AUD-03 規格層已解（步 10，Layer 4 Confidence L_C 格）；🟡 AUD-02 計畫定案＋程式實作進行中（步 7）；🟡 AUD-01 規格層已解（Layer 1 生效），code 面待步 11 落地。**概念層規格 Layer 1–4 全數就緒**（WM v1.0 生效；ONT/ID/KS v0.1-draft 待充任認定）。

## ⚠️ 目前阻塞（更新 2026-07-17）

**已解**：步 7 兩項治權決策經 Steward 拍板（決策 A=加 trigger＋tombstone 例外、決策 B=nullable 事後回填）；步 7 計畫定案。

**仍待處置**：

1. ~~每月消費上限~~ ✅ **已解除**（2026-07-17 起工作流程正常執行；步 8、9 均以完整多代理流程完成）。
1b. **充任認定前置（Layer 2–4 共同）**：各層合規聲明依 `AUGUR-WM v1.0 §WM.44` 須有**逐條對應矩陣**（憲章全部 [N] 條款→本層落點之可機器盤點枚舉）。Layer 2/3 草案現以群組理由代替，Layer 3 已列為明文生效阻卻。**須於各層充任認定前補全**（步 12 或各層充任同案辦理）。
2. ~~augur-code 推送權限~~ ✅ **已授權並完成**（2026-07-17，Steward 明示「直接進 main＋tag」）：AUD-02 卷宗＋治權檔憲章從屬聲明＋SSOT patch 已進 augur main（493fd73），封存 tag `augur-mc-v1.3-compliance-seal`。分支 `remediation/aud-02-raw-supersede-log` 已 ff-merge 入 main。
3. **步 7 程式實作之閘**：依 augur-code CLAUDE.md #20（計畫先行＋拍板後實作）、#7（須實測，本機無 PostgreSQL）、#19（核心共用模組逐檔檢視），程式實作待額度恢復後由工作流程 build 階段續行（含被中斷之三重對抗審查）；不於未測、未審下硬寫核心寫入路徑。

## 更新紀錄

* 2026-07-16：行程建立（步 6）；步 7（AUD-02）設計＋評審完成（取向 B），施工階段因消費上限中斷。
* 2026-07-17：步 7 兩項治權決策拍板、計畫定案（decisions A/B）；消費上限解除；步 8（Layer 2 Ontology）定稿封存（fe45620，27 issue 全處置）；步 9（Layer 3 Identity）定稿封存（2a38255，18 issue 全處置）；步 10（Layer 4 Knowledge）啟動。
* 2026-07-17：步 12 部分完成——augur-code 治權檔憲章從屬聲明（5 檔）＋SSOT 措辭正名＋AUD-02 卷宗進 augur main（493fd73），封存 tag `augur-mc-v1.3-compliance-seal`。
