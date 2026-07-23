# AUGUR-INF v1.0 單層 ultracode 窮盡對抗檢驗報告 [I]（L7）

## 一、元資料

* **日期**：2026-07-23
* **攻擊標的**：`specs/INFRASTRUCTURE-SPECIFICATION.md`（AUGUR-L7 **v1.0**，1137 行，正文 L7.1–L7.92＋Annex LDI/LDO/OPEN/L7B/TR/CS/EO）
* **git HEAD**：`5af0d7789e2faf6b5c8cbe11500043794ccd7efd`
* **方法**：`ULTRACODE-SCHEDULE.md` L7 六維（PWR｜TST｜NUM｜LDI｜OPN｜RSD）× Find→Verify→Critic→Synthesize；三鏡反駁紀律同 L0–L6（預設 refuted=true、逐字＋行號、≥2 鏡出局）。
* **對照卷宗**：RULING-2026-025（§8.2 條件通過、provisional→v1.0；025 (iii)(iv)(vi) residual 分階段①）、RULING-2026-024（T-L7-13 §8.1 多軸解耦）、RULING-2026-020（M2 幽靈下放甲案——L6.21 產物表 trigger 俟 L7 §8.2）、RULING-2026-036（L6 v1.2；L7 cross-layer stale 留本層）、`audits/L6-AR-ULTRACODE-20260723.md`。
* **lint 基線（親跑）**：
  * 單檔：`python3 -m tools.constitution_lint compliance specs/INFRASTRUCTURE-SPECIFICATION.md` → **❌ FAIL（error 1 / warning 22 / info 3）**
  * corpus：`python3 -m tools.constitution_lint report` → **errors_L7=1、warnings_L7=22**（L0–L6 均 error 0）
  * **ERROR**：`upper-specs` 所列 `AUGUR-L6 v1.0` 無法解析至規格檔（`upper_spec_unresolved`）——L6 全列 TR 標籤權威來源缺位
  * **WARNING×22**：Annex TR.F `L6.1`–`L6.24`／`L6.90–L6.92` 標籤本次未受檢（同根因）
  * **info**：mc-version v1.4→v1.5 換發提醒；WM.44 骨架覆蓋；TR 已比對 120 筆（不含 L6 22 筆）
  * **僅作對照物，非合憲依據**；lint 紅燈不阻断 F-L7-1 之實質性（036 先例：L7 error 1 為既有、非 036 引入）。
* **鐵律聲明**：[I] 審查素材；零規格修改；不採信自陳（025 七項必審、33 列 LDI、OPEN 保守預設均親讀）；處置權專屬 Steward。
* **執行形態誠實揭露**：單代理 ultracode（同 L1–L6 輪）；獨立性弱於 2026-07-18 首審之多代理形態。
* **已知基線（不假裝乾淨）**：L6 核驗已預告 L7 `upper_spec_unresolved` 與 `AUGUR-L6 v1.0` stale——本輪納入攻擊並存活為 finding，非「新發現即 major」。

---

## 二、逐維 Find（全部候選，含事後出局者）

severity：major／**medium**／minor／info。

### PWR — 核心命題：權限主體集合交集（L7.16(e) 判準）

**L7.16(e) 親讀**：「強制機制與其可解除者同屬一權限主體時，該不變式在憲章意義上不成立——存疑即推定不成立（`§8.3`）。」

**逐項標明（現行部署語境）**：

| 不變式／分離義務 | 可成立／組織性／物理不可能 | 證據 |
|---|---|---|
| append-only／owner≠應用角色（L7.16） | **存疑→推定不成立**（典型 PG 單一 `augur` 角色兼 DDL＋DML；AUD-02 trigger 僅覆 `raw_supersede_log` 等局部表） | `:199` L7.16(e)；`tests/test_raw_supersede_log.py` 局部覆蓋 |
| kill-switch 結構獨立（L7.40(a)） | **程序／容器層可成立；實體層 residual**（單節點 L7.51） | `:382` L7.40(e)；025 (iii) 接受 residual |
| owner 憑證 vs 人類權威憑證（L7.42(e)） | **組織性而非技術性**（單一 Steward 持雙憑證；025 (iv) 分階段①） | `:408` L7.42(e)；025 §二 |
| 角色五 vs 角色六 guard-the-guard（L7.15(b)） | **邏輯分離可成立；實體共置 residual** | `:188` L7.15(b)；T-L7-3 |
| Threshold Registry 棘輪 vs Agent 可寫（L7.70(c)(iv)） | **存疑**（登錄簿物理載體未獨立登錄；與 L7.16 互為條件） | `:559` L7.70(c)(iv)；T-L7-4 |

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L7-3 | minor | **L7.16 owner 分離之可執行證明未全棧**：規格要求以應用運行角色嘗試 DDL/TRUNCATE/停用 trigger 須被拒絕且**可執行回歸測試**證明（`:201`）；現有 `tests/test_raw_supersede_log.py` 僅 AUD-02 局部表 append-only trigger，**非**全受保護儲存物件、**非** owner≠app 拒絕矩陣 | `:201`；`tests/test_raw_supersede_log.py:7-8` |
| （本維零 major） | — | 025 (iii)(iv) residual 已明示接受；T-L7-3 與 L7.18 保守處置在卷——非 ultracode 新開 defect | 025 §一(iii)(iv)；`:1001` CS.2 T-L7-3 |

**出局候選**：「025 residual 等於規格自我豁免 P5」——3/3 出局（`:20`【地位】區分義務本身 vs 履行時程；L7.28(c) 非豁免宣示；025 §二① 仍 RT-4／棘輪標受限）。

### TST — 可執行測試證明覆蓋（L7.21(f)(iv) 推定）

**應有 vs 實有清點**：

| 義務落點 | 規格要求之測試 |  repo 實有 |
|---|---|---|
| L7.21(f)(i) Source NOT NULL 引擎拒絕 | 每欄一則回歸測試 | **未見** |
| L7.21(f)(i) Identity NOT NULL 引擎拒絕 | 同上 | **未見** |
| L7.21(f)(i) Evidence NOT NULL 引擎拒絕 | 同上 | **未見** |
| L7.21(f)(ii) instance/type NOT NULL 引擎拒絕 | 同上 | **未見** |
| L7.16 owner 拒絕 | 可執行回歸 | **局部**（raw_supersede_log append-only only） |
| L7.40(b) kill-switch 五層逐層觸發 | 留痕＋實測 | **未見** |
| L7.15／L7.17 分離 | 可執行測試 | **未見** |

**L7.21(f)(iv) 推定計算（保守解釋）**：
* 測試未存在或未通過期間，承載 Knowledge 之儲存**推定不滿足本款**（`:253`）→ 其內容**不得**為任何 **RT ≥ 1 Action 之 Knowledge Basis**。
* 另：OPEN-L7-00（角色一未登錄）、OPEN-L7-02（語意記憶／as-of 向量未解）、OPEN-L7-07（無故障域副本）之保守預設疊加後，**實務上幾乎全部既有 Knowledge 表資料在憲章意義上不得作為 RT≥1 之 Knowledge Basis**——除非逐表補齊 schema NOT NULL＋四欄拒絕測試＋Bearer 七欄登錄＋Tier 宣告（L7.20(f)）。
* **不估算具體列數**（需 DB 連線與 schema 盤點；本環境 psycopg2 未裝、未跑量化 query——#9 零幻像）。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| **F-L7-2** | **medium** | **L7.21(f) 四欄引擎層拒絕之可執行回歸測試套件缺失**：正文 `:253` 明定「每一欄各具一則…測試…文件宣稱不構成證明」；repo 無對應 pytest／migration 自測；僅 AUD-02 局部 append-only 測試，**不滿足** L7.21(f) 全四欄 | `:249-254` L7.21(f)；`tests/test_raw_supersede_log.py`（無 Source/Identity/Evidence/instance-type 拒絕用例） |
| F-L7-3 | minor | （併 PWR 維）owner 分離測試不全 | 同上 |

**出局候選**：「L7.5(d) 已要求故視為已測」——3/3 出局（`:128` L7.5(d) 為義務句，非自陳完成；無測試即推定不滿足 `:253`）。

### NUM — 數值 vs 結構界線

**基線逐項標明**：

| 數值 | 登錄位置 | 結構推導／自由裁量 | 依據 |
|---|---|---|---|
| H_max RT-4=**1 秒** | L7.41 `:391` | **結構推導＋025 核定**（L6.8 有限上限；T-L7-12 pre-commit hold 輔助） | 025 (i)；`:391-392` |
| H_max RT-3/2/1=5/15/60 秒 | L7.41 `:392-394` | **025 核定照收**（領域基線＋單調） | 025 (i) |
| C_max RT-2/3/4=**0** | L7.45(b) `:439` | **結構推導**（L6.13 RT-2+ 須事中在環） | `:439` 推導欄 |
| C_max RT-1=**50** | L7.45(b) `:439` | **自由裁量登錄基線** | `:439`「登錄基線」 |
| I3≥**50** Identity／≥**NT$1,000,000** | L7.45(d) `:441` | **領域基線**（得 Domain Profile 收緊） | `:441`；025 (ii) 核定 |
| OOS 最低 **250** 交易日 | L7.45(f-4) `:456` | **領域基線** | `:456` |
| banding 帶界 | L7.45(a) `:438` | **結構推導**（KS.33 序＋§P4.E4 上界開 1.00） | `:438` |

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L7-4 | minor | **I3 量值門檻與 RT-1 C_max=50 之推導欄仍偏「領域基線／登錄基線」**：NUM 維無結構矛盾（025 已核定）；惟 L7.45(d) I3 雙閾值無 L6.9 原文逐字錨（50／100 萬為 [I] 領域值），與 T-L7-5「架空可判定性」殘餘同型——**documentation residual，非數值架空結構** | `:441` L7.45(d)；`:439` L7.45(b)；025 (ii) |

**零 medium**（025 已審 numerics；T-L7-13 已 §8.1 裁）。

### LDI — 33 列三向對表與目標層正確性

**親讀清點**：
* front-matter `defers-in` 陣列 **33 項**（機器 count 確認）＝ CS.3(a) 表 33 列＝ LDI.0 宣告承接列 33（LDI.20 零列宣告不計、LDI.23 保留不計）——**三向 PASS**。
* LDI.23 目標 Layer 誤植更正（IDO.6→L4、IDO.7→L6）親讀 ID Annex DO 邏輯——**非幽靈**。
* LDI.43 KS.41–46 正文直接課 L7——**實質落點** L7.20(f) 親讀有表級＋通道級 Tier（`:233-238`）。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| **F-L7-1** | **medium** | **`upper-specs`／全文仍锚 `AUGUR-L6 v1.0`，L6 已 v1.2（036）**：`:60`、`:958` CS front-matter、`【地位】`:7-15` 等 **111 處**；linter 無法解析 L6 檔→ **ERROR 1＋WARNING 22**（L6.1–L6.24 TR 標籤未受檢）；L7.91 要求 upper-specs 同步升版 | `:60`；`:958`；lint 親跑；036 §八 L7 範圍外留本層 |
| F-L7-5 | minor | **CS front-matter `mc-version: AUGUR-MC v1.4`**（lint info v1.5 換發提醒）——末層應跟 MC v1.5 同步（L7.91） | `:957` CS front-matter；lint info |

**出局候選**：「33 列缺漏」——3/3 出局（defers-in count=33 親算；CS.3(a) `:1021-1058` 逐列可解析）。

### OPN — 六角色全 OPEN 下之實際可運作性

**OPEN 合取保守預設（親讀 Annex OPEN `:692-698`）**：

| OPEN | 保守後果（憲章意義上） |
|---|---|
| OPEN-L7-00 | 角色一未登錄→RT-4；§P4.E3 部署層推定不成立 |
| OPEN-L7-01–02 | 角色二／三未登錄→RT-4；語意輸出候選／synthetic |
| OPEN-L7-03 | **無 Action 能力**（L6.22 F3） |
| OPEN-L7-04 | **執法點不成立→全系統 fail-closed 不得 Action** |
| OPEN-L7-05 | 未登錄 model 不得進 Action 鏈 |
| OPEN-L7-06 | **RT-4 不得自動 commit** |
| OPEN-L7-07 | 無分離副本→不得 RT≥1 Action |

**合取後系統在憲章意義上能做什麼**：僅 **RT-0 純表徵**（且須 L7.44(f) 物理限制成立）＋**人類逐案 RT-4 路徑**（仍須 L7.44 介面存在——OPEN-L7-04 使之外部 Action 全禁）→ **實質：對外 Action 全禁；內部唯讀／離線開發可繼續**。與 `audits/L0-L7-INTERACTION-ULTRACODE-2026-07-23.md` O-IX-1（operability 1/7）一致。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L7-6 | minor | **OPEN-L7-00 之 [I] 現況句「環境盤點載資料庫全數缺位」與專案現況脫節**：L7.11 `:152`／OPEN `:692` 仍引 2026-07-16 前 ENVIRONMENT-SPEC 快照；專案已長期以 PostgreSQL 為 SSOT（CLAUDE #29、import_database.sh），**物理 DB 存在 vs Bearer Registry 七欄未登錄**應分拆敘事——現文案將「未登錄」與「全數缺位」混寫，易誤導稽核 | `:152`；`:692` OPEN-L7-00；L7.52(d) 30 日更新義務 |
| F-L7-7 | minor | **CS.4 `:1073` 末段仍載「本子代理不宣稱任何規格已生效…（DRAFT）」**——與 v1.0 生效／025 條件通過矛盾（009 附錄乙同型） | `:1073` CS.4 |

**出局候選**：「OPEN 即豁免 P5」——3/3 出局（L7.3(d) OPEN 非豁免；`:692` 保守預設 RT-4）。

### RSD — residual (iii)(iv)(vi) 分階段補正可達性

**025 分階段親讀**：
* **①（現行）**：(iii) kill-switch 單節點 residual、(iv) 單人雙憑證、(vi) 單機無熱備——**已接受**；復審 **2026-10-14**。
* **②（有第二人即行）**：繼任人為核准第二人——**現況：無第二人**（Steward 單自然人專案）；**可達、未觸發**。
* **③（終態）**：監督平面獨立節點——**成本高、需硬體／拓撲**；L7.24(e) 未來登錄；**可達、未排程**。
* **020 M2**：L6.21 產物表 DB trigger 級機械強制**L7 現未承接**（L6 `:211`）——L7 規格**未宣稱已承接**，與 020 甲案一致；**非 L7 幽靈下放**。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L7-8 | minor | **020 M2 產物 trigger 物理強制仍為 cross-layer 待辦**：L6 ultracode F-L6-5（TR.D D28 stale）指向 L7 §8.2；L7 正文無 L6.21 產物表 trigger 承接條款——**誠實 deferred**，惟 Phase 3b／執行層仍須追蹤 | L6 `:211`；020 M2；L6 F-L6-5 |
| （本維零 major） | — | 025 residual 路徑在卷、期限明確；②③ 未達成不構成規格 defect | 025 §二；`:570` L7.90(c) |

**出局候選**：「2026-10-14 已過期」——3/3 出局（今日 2026-07-23，期限未至）。

---

## 三、Verify — 三鏡獨立反駁結果

### 存活（8）

**F-L7-1【medium·存活 3/3】upper-spec L6 v1.0 stale＋lint ERROR**
* 文本體系鏡：**未能反駁**（`:60` v1.0 vs L6 檔 v1.2；036 已施作 L6）。
* 形式邏輯鏡：**未能反駁**（linter 無法載入 L6→22 標籤未檢＝WM.44 形式缺口）。
* 實務規避鏡：**未能反駁**（引用 v1.0 在保守解釋下仍可能有效，但 **lint ERROR 為實質 defect**）。

**F-L7-2【medium·存活 3/3】L7.21(f) 可執行測試缺失**
* 三鏡：**未能反駁**（`:253` 推定規則＋repo 無四欄拒絕測試為可驗證事實）。

**F-L7-3【minor·存活 2/3】L7.16 測試不全**
* 三鏡：實務鏡降 minor（AUD-02 測試存在但範圍窄；全棧 owner 分離待補）。

**F-L7-4【minor·存活 2/3】I3／C_max 領域基線**
* 三鏡：025 (ii) 已核定；僅 documentation 精度 residual。

**F-L7-5【minor·存活 2/3】mc-version v1.4**
* 三鏡：同 L5 F-L5-4 模式；換發議程非 defect。

**F-L7-6【minor·存活 2/3】OPEN-L7-00 [I] 快照 stale**
* 文本體系鏡：**未能反駁**（「全數缺位」與 PG-SSOT 專案事實矛盾）。
* 實務鏡：OPEN 保守預設仍有效（**未登錄**≠**無 DB**）→ minor。

**F-L7-7【minor·存活 2/3】CS.4 DRAFT 殘句**
* 三鏡：同 L6 F-L6-3 DRAFT 章標模式。

**F-L7-8【minor·存活 2/3】020 M2 trigger cross-layer**
* 三鏡：L7 誠實未承接；追蹤項非 open defect。

### 出局（4）

| id | 出局鏡數 | 反駁 counter_evidence |
|---|---|---|
| 「025 residual＝豁免核心」 | 3/3 | `:20`【地位】；L7.28(c)；025 §二。 |
| 「33 LDI 缺列」 | 3/3 | defers-in count=33；`:1059` CS.3。 |
| 「T-L7-13 未裁」 | 3/3 | 024；`:578` L7.90(d)(vii)。 |
| 「六 OPEN＝規格矛盾」 | 3/3 | L7.3(b) OPEN 設計；`:692-698` 保守預設閉集。 |

---

## 四、Critic — 完整性批評與抽查

**「什麼還沒被檢查」（誠實清點）**：

1. **L7→runtime 全量 operability**——`ops/phase2/operability_probe.py` 已於交互 ultracode 跑過；本單層未重跑 probe（#28 本地優先；交互報告 O-IX-1 可引用）。
2. **Bearer Registry 七欄實體檔**——`infrastructure/BEARER-REGISTRY-v0.1-draft.md` 仍 draft；未逐欄 machine-parse 驗證。
3. **Annex TR 全 120+22 列**——22 L6 列因 F-L7-1 未 lint；其餘 120 列 lint info 已比對。
4. **DB schema NOT NULL 盤點**——需 live PG；本輪未連線（#9）。
5. **Phase 3b L5–7 交互**——排程收束後待跑；與本單層互補。
6. **MC v1.5 換發對 L7**——F-L7-5 minor；非 L7 本体 P5 缺陷。

**抽查推翻理由**：F-L7-4/5/6/7/8 之 minor 降級理由经查 025／036／020 史实成立。**F-L7-1／2 不可降级**——分触 WM.44 形式／§8.4 可執行證明。

**方法界限**：单代理；lint FAIL 不阻断 medium 存活（铁律 #3）。

---

## 五、Steward 呈核摘要

### 存活清单（medium×2＋minor×6）

| id | severity | 一句主张 | 建议处置与门槛 |
|---|---|---|---|
| **F-L7-1** | **medium** | `upper-specs` 与全文仍引 `AUGUR-L6 v1.0`（L6 已 v1.2）→ lint ERROR 1＋22 L6 TR 标签未检 | 同案 patch／minor：`§0.1`、CS front-matter、`【地位】`、Annex TR.F 引用→`AUGUR-L6 v1.2`；重跑 lint 至 error 0 |
| **F-L7-2** | **medium** | L7.21(f) 四栏引擎拒绝对应可执行回归测试缺失 | 执行层同案：schema NOT NULL 迁移＋`tests/` 四栏拒绝对应用例（L7.5(d)）；未测前维持 `:253` 保守推定 |
| F-L7-3 | minor | L7.16 owner 分离仅 AUD-02 局部 append-only 测试 | 并入 F-L7-2 测试矩阵或单列 owner≠app 拒绝对测 |
| F-L7-4 | minor | I3／RT-1 C_max 领域基线文档精度 | 可选 [I] 脚注或 Steward 确认 025 (ii) 即可 |
| F-L7-5 | minor | CS mc-version v1.4 stale | 并入 F-L7-1 或 MC v1.5 换发议程 |
| F-L7-6 | minor | OPEN-L7-00「资料库全数缺位」[I] 与 PG-SSOT 现状脱节 | [I] patch：分拆「物理 PG 存在 vs Bearer 七栏未登录」；L7.52(d) 更新 |
| F-L7-7 | minor | CS.4 末段 DRAFT 残句 | 同案删 `:1073` DRAFT 尾段 |
| F-L7-8 | minor | 020 M2 产物 trigger 仍 deferred | 留 Phase 3b／执行层；L7 不虚假承接 |

### 建议同案 RULING 要点（本轮仅呈核，不开正式档）

1. **一揽子标题**：`RULING-2026-037-L7-INF-ULTRACODE-DISPOSITION`（次号 **037**；Amendment Log 建议 **AL-2026-041**——查实况：AL-040＝036、次序递增）
2. **major**：**零**——025 §8.2 已作成；33 LDI 三向 PASS；OPEN 合取诚实；T-L7-13 已 §8.1 裁；P5 物理条款在卷
3. **025 residual**：(iii)(iv)(vi) **维持分阶段①**至 2026-10-14 复审——不翻 major
4. **medium 同案顺修**：F-L7-1（L6 v1.2 引用＋lint 绿）＋F-L7-2（L7.21(f) 测试套件）必含；minor×6 并入或分期
5. **独立核验**：依 028 第 3 点，处置后独立 agent＋lint 亲跑
6. **Amendment Log**：`AL-2026-041`（建议序号，由 Steward 确认）

### 正面确认（强化盖章之证据）

* **PWR**：L7.16(e) 判准 explicit；025 (iii)(iv) residual 揭露完整；T-L7-3 不自我认定可接受。
* **TST**：L7.5(d)／L7.21(f)(iv) 要求可执行证明——规格诚实，执行层缺口=F-L7-2 非规格自欺。
* **NUM**：H_max／C_max RT-2+／banding 结构推导清晰；025 (i)(ii) 核定入正式。
* **LDI**：33 列三向 machine-verified；LDI.23 误植更正非幽灵。
* **OPN**：八 OPEN 保守合取可判定；fail-closed 设计一致（T-L7-10）。
* **RSD**：025 分阶段②③ 可达成性在卷；020 M2 不虚假下放至 L7。
* **cross-layer**：024 T-L7-13 交集解释已锚 L7.45(f)(f-4)；036 L6 stale 留本层 F-L7-1。

### 是否动摇 L7 盖章

**否——不動搖**。零 major；2 medium 均为 **引用同步／可执行证明执行层**（非 P5 骨架、非 025 撤销、非 LDI 漏收）；6 minor 为 [I] 快照／DRAFT 残句／cross-layer 追踪。**動搖程度定級：僅需 patch／minor 同案＋执行层测试落地**（非重採認、非 §8.2 补审——025 已作成）。

### 盖章 verdict

**L7（AUGUR-INF v1.0）ultracode 呈核：零 major；medium×2＋minor×6 存活；025 residual 维持；lint FAIL（error 1／warning 22）亲跑对照、不假装干净基线。建议 Steward 接受呈核并同案 RULING-2026-037 顺修 F-L7-1–8。**

### Steward 定案（2026-07-23）

> **接受 L7 ultracode 呈核（零 major、medium×2＋minor×6）；同案 **RULING-2026-037** 顺修 F-L7-1（upper-specs→AUGUR-L6 v1.2＋lint 归零）＋F-L7-2（L7.21(f) 四栏可执行回归测试）及 minor×6；025 (iii)(iv)(vi) residual 维持分阶段①、复审 2026-10-14；盖章不動搖。**

**处置闭环**：AL-2026-041；lint 施作后 **PASS 7/7**（L7 error 0／warning 0，2026-07-23 亲跑）。**RULING-2026-028 第十二节独立对抗核验待另轮**（非施作者 agent）。

### 建议拍板句（供 Steward）〔已采纳〕

> **接受 L7 ultracode 呈核（零 major、medium×2＋minor×6）；同案 RULING-2026-037 顺修 F-L7-1（upper-specs→AUGUR-L6 v1.2＋lint 归零）＋F-L7-2（L7.21(f) 四栏可执行回归测试）及 minor×6；025 (iii)(iv)(vi) residual 维持分阶段①、复审 2026-10-14；盖章不動搖。**

---

*本報告為 [I] 審查素材；ultracode 呈核段待 Steward 定案。攻擊官／反駁官／批評官：ultracode-L7 代理（單代理分節），2026-07-23；L7 lint error 1／warning 22 親跑對照（corpus errors_L7=1）。*
