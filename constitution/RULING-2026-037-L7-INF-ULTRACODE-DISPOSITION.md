# Augur Steward 裁決第 2026-037 號

**L7（AUGUR-INF v1.0）單層 ultracode findings 處置——upper-specs→L6 v1.2、L7.21(f) 四欄可執行回歸、OPEN／DRAFT／cross-layer minor×6（合併版 findings：2 medium＋6 minor，同案）**

* **依據**：`AUGUR-MC v1.4 §8.6`（minor／patch）、`§8.2`（較嚴格解讀之解消）、`§8.1`（解釋之界線）；findings 冊 `audits/L7-INF-ULTRACODE-20260723.md`；RULING-2026-025（§8.2 已作成、provisional→v1.0；(iii)(iv)(vi) residual 分階段① 復審 2026-10-14）；RULING-2026-036（L6 v1.2；L7 cross-layer stale 留本層）；RULING-2026-020（M2 幽靈下放甲案）；RULING-2026-028（施作留痕＋獨立核驗）；先例＝RULING-2026-036（L6 同體例一攬子）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **登錄**：Amendment Log **AL-2026-041**
* **性質**：minor／patch 執行層施作（第一至九點）；**不動 parent 歸類、不觸 MC [N] 本文、PA／五原則 byte 級零改、INF 版本維持 v1.0**——所涉變更為 [N] 引用同步／可執行證明掛點、[I] OPEN 快照／DRAFT 殘句／cross-layer 追蹤
* **分級登錄（Steward 2026-07-23）**：**F-L7-1／2**＝ **medium**（處置採 patch／minor）；**F-L7-3–8**＝ **minor**。零 major；**不動搖 L7 蓋章**（findings 冊結論）

## 一、擬裁一〔upper-specs／全文 L6 v1.2 同步——F-L7-1，medium〕✅

1. **§0.1 upper-specs**、**【地位】**、**Annex CS front-matter `upper-specs`**、全文 **`AUGUR-L6 v1.0`→`AUGUR-L6 v1.2`**（111 處級引用同步，對齊 036）。
2. **Annex CS front-matter `mc-version`**：`AUGUR-MC v1.4`→**`AUGUR-MC v1.5`**（併 F-L7-5）。
3. **定級**：Steward 定級 **medium**（lint `upper_spec_unresolved` ERROR 1＋22 L6 TR 標籤未檢→WM.44 形式缺口）。

## 二、擬裁二〔L7.21(f) 四欄可執行回歸測試——F-L7-2＋F-L7-3，medium〕✅

1. **規格掛點**：L7.21(f)(iv) 與可判定判準明示回歸測試路徑＝`tests/test_l7_knowledge_not_null.py`（Source／Identity／Evidence／instance-type 逐欄引擎 NOT NULL 拒絕；每欄一則）。
2. **執行層**：新增上述 pytest 模組（DB 不可用→skip、非假 pass）；L7.16 owner 分離局部覆蓋仍指 `tests/test_raw_supersede_log.py`（AUD-02 append-only；全受保護儲存物件矩陣俟擴充）。
3. **保守推定**：測試未通過期間維持 `:253` 推定——承載 Knowledge 之儲存**推定不滿足** L7.21(f)。
4. **定級**：Steward 定級 **medium**（§8.4 可執行證明執行層缺口；規格已誠實、本裁決補掛點＋最小套件）。

## 三、擬裁三〔I3／C_max 領域基線文檔精度——F-L7-4，minor〕✅

1. **L7.45(d)**：增 [I] 領域基線註記——I3 之 50／NT$1,000,000 與 RT-1 C_max＝50 為領域基線登錄值；**RULING-2026-025 (ii) 已核定照收**。

## 四、擬裁四〔CS mc-version v1.4 stale——F-L7-5，minor〕✅

1. **併入擬裁一**——Annex CS front-matter `mc-version`→v1.5。

## 五、擬裁五〔OPEN-L7-00 [I] 快照 stale——F-L7-6，minor〕✅

1. **OPEN-L7-00**、**L7.11 角色一現行值欄**：分拆「物理 PostgreSQL 已存在（專案 SSOT）」vs「Bearer Registry 七欄未登錄」——**未登錄 ≠ 無 DB**。

## 六、擬裁六〔CS.4 DRAFT 殘句——F-L7-7，minor〕✅

1. **CS.4 末段**：刪「本子代理不宣稱…（DRAFT）」——與 v1.0 生效／025 條件通過一致；改為 020 M2 cross-layer 誠實追蹤句（F-L7-8）。

## 七、擬裁七〔020 M2 產物 trigger cross-layer——F-L7-8，minor〕✅

1. **CS.4 [I] 追蹤**：L6.21 產物表 trigger 級 DB 機械強制**L7 誠實未承接**——俟 Phase 3b／執行層；不虛假下放。

## 八、RULING-2026-025 residual (iii)(iv)(vi)

1. **維持分階段①**至 **2026-10-14** 復審——**不關閉**、不翻 major、不重開 §8.2。
2. ②（有第二人即行）／③（終態監督平面獨立節點）仍在卷、未觸發。

## 九、明示不為

* 不動 `AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0`／`AUGUR-KS v1.1`／`AUGUR-L5 v1.0`／`AUGUR-L6 v1.2` 任何 [N] 條文；不動 MC [N] 本文；PA／五原則 byte 級零改。
* L6.21 產物表 trigger 級物理強制**不併本案虛假承接**（F-L7-8 留 Phase 3b）。
* MC v1.5 原則級換發**不併本案**（僅 CS front-matter mc-version 簿記同步）。

## 十、驗證

* `python3 -m tools.constitution_lint report`：**PASS 7／7**（L7 error 0／warning 0）。
* `ULTRACODE-SCHEDULE.md` L7 列更新＋Amendment Log 登錄 AL-2026-041 於簽核生效時一併辦理。

## 十一、施作紀錄（2026-07-23）

| 檔案 | 施作摘要 |
|---|---|
| `specs/INFRASTRUCTURE-SPECIFICATION.md` | F-L7-1～8 全覆蓋：L6 v1.2 引用＋CS mc-version v1.5；L7.21(f) 測試掛點；L7.16 局部測試引用；L7.45(d) 領域基線註記；OPEN-L7-00／L7.11；CS.4 DRAFT 刪＋020 M2 追蹤 |
| `tests/test_l7_knowledge_not_null.py` | L7.21(f) 四欄 NOT NULL 引擎拒絕回歸（新增） |
| `constitution/RULING-2026-037-…` | 本檔生效＋簽核 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-041 |
| `ULTRACODE-SCHEDULE.md` | L7 列閉環 |
| `audits/L7-INF-ULTRACODE-20260723.md` | 呈核段更新 |

## 十二、獨立對抗核驗（RULING-2026-028 第 3 點 (b)）

> **誠實揭露**：下列項次為 commit 後**須經非施作者**確認之核驗清單。**獨立對抗核驗已完成**（2026-07-23；核驗者＝Cursor 獨立核驗 agent；方法＝逐項檔案原文／`git show 4411e2f`／親跑 lint；非施作者 4411e2f）。

| # | 核驗項 | 範圍 | 狀態 |
|---|---|---|---|
| 1 | **L6 v1.2 引用**：§0.1／CS upper-specs／【地位】／全文零 `AUGUR-L6 v1.0` | INF 全檔 | ✅ 獨立核驗 PASS（2026-07-23；全檔零 `AUGUR-L6 v1.0`；112 處 `AUGUR-L6 v1.2`；§0.1 `:60`、CS `:957-958` upper-specs／mc-version v1.5） |
| 2 | **lint L7 歸零**：`compliance specs/INFRASTRUCTURE-SPECIFICATION.md` error 0 | L7 | ✅ 獨立核驗 PASS（2026-07-23；error 0／warning 0／info 2 親跑；L6 v1.2 22 筆 TR 已比對） |
| 3 | **corpus PASS 7/7**：`python3 -m tools.constitution_lint report` | 全 corpus | ✅ 獨立核驗 PASS（2026-07-23；PASS 7/7、errors_L7=0、warnings_L7=0、git HEAD 4411e2f 親跑） |
| 4 | **L7.21(f) 測試掛點**：規格 `:253` 與 `tests/test_l7_knowledge_not_null.py` 四欄逐項 | L7.21(f) | ✅ 獨立核驗 PASS（2026-07-23；`:253` `:255` 明示掛點；測試 4 欄 parametrize＋schema 盤點＋skip 路徑；**pytest／PG 未裝→結構對齊、未實跑**） |
| 5 | **OPEN-L7-00 分拆**：物理 PG vs Bearer 未登錄 | OPEN | ✅ 獨立核驗 PASS（2026-07-23；`:152` L7.11「物理 PG 已存在」；`:692` OPEN-L7-00「未登錄 ≠ 無 DB」） |
| 6 | **CS.4 無 DRAFT 殘句** | CS.4 | ✅ 獨立核驗 PASS（2026-07-23；`:1073` 末段零「本子代理不宣稱…（DRAFT）」；全檔 grep 零匹配） |
| 7 | **025 residual 維持**：(iii)(iv)(vi) 分階段①、復審 2026-10-14、未關閉 | 025 §二 | ✅ 獨立核驗 PASS（2026-07-23；037 §八維持分階段①；025 §二① 復審 2026-10-14 未改；②③ 在卷未觸發） |
| 8 | **020 M2 誠實 deferred**：L7 不虛假承接 trigger | CS.4 | ✅ 獨立核驗 PASS（2026-07-23；`:1073` cross-layer 追蹤「L7 誠實未承接…俟 Phase 3b」） |
| 9 | **[N] 零逾越**：diff 限本裁決核示之 patch | INF 全 diff | ✅ 獨立核驗 PASS（2026-07-23；4411e2f 限 6 檔、INF +214/-109，F-L7-1～8 授權範圍；無 [N] 義務句逾越） |
| 10 | **PA／五原則 byte 零改** | `constitution/` 五原則檔 | ✅ 獨立核驗 PASS（2026-07-23；4411e2f MC／PA／五原則檔零 diff） |
| 11 | **蓋章不動搖**：零 major、INF v1.0 維持 | 全案 | ✅ 獨立核驗 PASS（2026-07-23；零 major；【地位】v1.0 生效維持；025 residual 分階段①保留） |

**誠實揭露**：上列十一項均經獨立 agent 逐項原文／diff／lint 覆核；L7.21(f) 測試本環境 pytest／psycopg2 未裝，結構對齊 PASS、執行層實跑 SKIP。

**Steward 2026-07-23：**接受 L7 ultracode 呈核、同案 037**（定案）**

## 簽核

> - [x] **准各項擬裁照收（一攬子採納；F-L7-1 upper-specs→L6 v1.2＋lint 歸零；F-L7-2 L7.21(f) 四欄可執行回歸；F-L7-3–8 同案 minor；025 residual 維持分階段①至 2026-10-14）**（簽：tsaitsangchi，日期：2026-07-23）
> - [x] **分級登錄**：F-L7-1／2＝medium；F-L7-3–8＝minor；零 major
> - [x] **逐項改核**：全照收（無逐項改核）
> - [ ] 修改意見：（無）

*本裁決定案（2026-07-23；Steward **接受 L7 ultracode 呈核、同案 037**）。L7 ultracode 處置閉環；蓋章不動搖。第十二節獨立對抗核驗已完成（2026-07-23；十一項全 ✅）。*
