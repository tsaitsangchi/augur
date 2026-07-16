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
| 7 | **AUD-02 補正**：raw_supersede_log 帳表＋heal 覆寫前快照舊列（同交易），upsert 主路徑不動 | **AUD-02 critical**（P4.E5 MUST NOT，§8.4 不可豁免） | augur-code 分支 | ⬜ 待辦 |
| 8 | **Layer 2 Ontology 規格**：台股世界類型體系、同一性判準框架 | AUD-04 類型面、承接 AUGUR-WM D2/D3 掛鉤 | augur-constitution | ⬜ 待辦 |
| 9 | **Layer 3 Identity 規格**：entity registry、identifier 鑄造、lifecycle（merge/split/retire）、identity claim、跨來源解析 | **AUD-04/05/06 三項 major**、AUGUR-WM D1/D4/D5/D6 | augur-constitution | ⬜ 待辦 |
| 10 | **Layer 4 Knowledge System 規格**：Confidence 單一形式化語義、五元組欄位、雙時間 as-of、supersede/tombstone、信任分級 | **AUD-03 critical**、AUD-08/16、形式化 AUD-02、AUGUR-WM D7–D11 | augur-constitution | ⬜ 待辦 |
| 11 | **結構補正施工**：世界概念 registry、SQL 直綁消除（AUD-01）、entity registry＋lifecycle（AUD-04/05）、prediction_values append-only（AUD-08）、行動留痕六元組（AUD-10/11） | AUD-01 code 面、AUD-04/05/07/08/09/10/11 | augur-code 分支 | ⬜ 待辦 |
| 12 | **治理收尾**：五治權檔合規聲明（依 AUGUR-WM §11）＋檔頭從屬聲明＋「唯一系統記錄」措辭 patch；審計報告最終定案 | AUD-12/13/26、RULING-2026-002 主文二/五交辦（期限 2026-10-14） | augur-code＋augur-constitution | ⬜ 待辦 |

**critical 解消里程碑**：步 7 解 AUD-02；步 10 解 AUD-03；步 8–11 完成後 AUD-01 code 面落地——三項 critical 全清。

## 更新紀錄

* 2026-07-16：行程建立（步 6）；步 7（AUD-02）啟動。
