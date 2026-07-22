# Augur Steward 裁決第 2026-002 號

**Layer 1 規格充任認定暨同案四項程序**

* **依據**：`AUGUR-MC v1.2 §0.5`（規格登錄與充任；作成時有效版本為 v1.2，v1.3 為本裁決同案發動、所引條款編號不變）、`§8.6`（Layer 對照表增列屬 minor、由 Steward 議決）、`§8.3` 過渡規則 (a)(b)(c)（暫行模板、既存規格補正期、Layer 1 自我引用不無效）、`§8.2`（既有實作之補正期由 Steward 個案裁定）、`§8.1`；治理附則第 2 條第 2 款（minor：書面裁決、附理由、公開存檔，無公示期）、第 6 條（書面＝登錄本儲存庫）
* **裁決人**：Constitution Steward（tsaitsangchi）
* **日期**：2026-07-16
* **登錄**：Amendment Log AL-2026-005（本裁決）、AL-2026-006（同案發動之 MC v1.3 minor 修訂）
* **源起**：《Augur World Model Specification》v0.1-draft §1.2 [I] 之四項程序建請；合憲審計 AUD-12/13/26 補正方向

---

## 主文

### 一、充任認定（Layer 1 規格生效）

認定 `specs/WORLD-MODEL-SPECIFICATION-v0.1-draft.md` **充任** `AUGUR-MC §0.5` 對照表 Layer 1 欄所轄之「World Model Specification」。其 §0.1 生效要件：(a) 充任認定＝本主文；(b) 依暫行模板作成之 Constitutional Compliance Statement＝其 Annex C（經主文三追認）——**全部成就，自本裁決日（2026-07-16）起生效**。

* 生效版本號定為 **v1.0**（引用格式 `AUGUR-WM v1.0 §{條款}`）；效力本存於 `specs/WORLD-MODEL-SPECIFICATION.md`，v0.1-draft 原文歸檔於原檔名（不再修改）。
* v0.1-draft → v1.0 之變更僅限：版本欄、【地位】節改生效記錄、§0.1 生效要件成就記錄、§1.2 辦理情形註記、WM.48 [I] 現況註記更新、Annex C 識別區塊隨版更新與導言生效註記、C.8 表 T-4／T-6／T-7 緊張關係之解消註記（T-6 之解消依據為主文二）。**無任何 [N] 條款實質變更、編號不重排**。
* 本認定與 `AUGUR-MC` v1.2 → v1.3（minor）同日作成；v1.3 僅為 §0.5 對照表增列（`§8.6`：minor 不觸發全下層合憲複審），AUGUR-WM 引用之 `AUGUR-MC v1.2` 各條款於 v1.3 編號均不變、規範內容除 §0.5 對照表增列（不影響 Layer 1 欄既有登錄）外均不變，其合規聲明無須重作。

### 二、五份治權檔之 Layer 定位登錄（發動 MC v1.3 minor 修訂）

依 `AUGUR-MC §8.6`，於 `§0.5` 對照表增列下列 augur 領域治權文件（存於 [tsaitsangchi/augur](https://github.com/tsaitsangchi/augur) 儲存庫）之定位登錄，構成 MC v1.2 → v1.3 minor 修訂（AL-2026-006）：

| 文件 | 登錄 Layer | 定位 |
|---|---|---|
| docs/系統核心思想_v1.8.0.md | Layer 1 | AUGUR-WM 之領域前身文件（`AUGUR-WM v1.0 §WM.6`） |
| docs/原則精華_v1.9.0.md | Layer 4 | 領域治權文件；跨層條款之逐條 Layer 標注由其合規聲明載明 |
| docs/系統架構大憲章_v1.45.0.md | Layer 7 | 領域架構／維運承載文件；涉 Layer 4–6 章節由其合規聲明逐節標注 |
| CLAUDE.md | Layer 6 | 領域 Agent 協作規格 |
| docs/datasets_zh.md 及 docs/finmind-references | Layer 7 | 資料來源參考文件 |

**理由**：`§0.5`「每份規格恰屬一層」——跨層內容之文件以其重心層登錄、逐條標注下放至各檔合規聲明，係在不違反單層原則下承接審計 AUD-12 補正方向之最小方案。

並依 `§8.3` 過渡規則 (b) 裁定：上列五檔之 Constitutional Compliance Statement **補正期至 2026-10-14（90 日）**，期內推定有效；補正聲明一律依 `AUGUR-WM v1.0 §11` 格式（WM.39–WM.45）作成——本規格生效後新作成之聲明依 `AUGUR-WM v1.0 §WM.45` 必須依 §11 格式，暫行模板不供新聲明引用（其功能見主文三）。

### 三、合規聲明暫行模板之發布與追認

依 `AUGUR-MC §8.3` 過渡規則 (a)，發布**Constitutional Compliance Statement 暫行模板**於 `constitution/COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md`，並**追認** AUGUR-WM Annex C 依其作成（過渡規則 (c)：Layer 1 之聲明不因格式自我引用而無效）。暫行模板之功能以此追認為限並自此功成身退：AUGUR-WM 生效（2026-07-16）後，`AUGUR-WM v1.0 §11`（WM.39–WM.45）為聲明格式之**唯一權威定義**，一切新作成之聲明（含主文二五檔之補正聲明）必須依 §11 格式作成（`AUGUR-WM v1.0 §WM.45`）；暫行模板留存為歷史文件與 §11 之對照參考，其與 §11 之任何表述差異以 §11 為準。本安排消除暫行模板與 `AUGUR-WM v1.0 §WM.45` 適用期間之任何緊張。

### 四、specs/ 目錄之書面地位指定

指定本儲存庫 **`specs/` 目錄**為 Layer 1–7 規格（含其歸檔版本）之書面存檔處所，準用治理附則第 6 條：對全體受憲章約束成員可見、時間戳與不可否認性以 git 提交歷史為據、憲章與規格要求「書面」者以登錄本儲存庫之文件為書面。`constitution/` 目錄維持為治理文書（Amendment Log、裁決、豁免登錄、憲章本文）之處所。（本指定解消 `AUGUR-WM` T-7 之 specs/ 地位部分與 WM.48 [I] 現況註記所指事項。）

### 五、措辭 patch 與檔頭從屬聲明之交辦

命於 [tsaitsangchi/augur](https://github.com/tsaitsangchi/augur) 儲存庫執行下列補正（受辦者：Steward 授權之工程協作者，依該儲存庫「決策層人拍板／執行層 AI 自駕」既有治權原則辦理；**期限同主文二補正期：2026-10-14**）：

1. **檔頭從屬聲明**：主文二所列五檔檔頭加註——受 `AUGUR-MC v1.3` 約束、所屬 Layer（依主文二登錄）、下層引用格式 `AUGUR-MC v1.3 §{條款}`／`AUGUR-WM v1.0 §{條款}`（AUD-12 補正方向第 (3) 項）。
2. **「唯一真相來源」措辭 patch**：大憲章「PostgreSQL＝唯一真相來源（SSOT）」更名為「PostgreSQL＝唯一系統記錄（single system of record）」，並加一句釐清「Reality 之權威＝API 觀測；系統內權威 Representation＝PG」（AUD-26 補正方向；`AUGUR-WM v1.0 §WM.9` 權威三分、Annex D D19）。下游 docstring 引用隨改或於各檔補正時隨改，屬 patch 級。
3. 上列變更依該儲存庫自身版本紀律辦理（含修訂歷程登錄；並建議依 AUD-25 補正方向增設 patch 級版號）。

## 效果彙總

* `AUGUR-WM v1.0` 自 2026-07-16 起為 Layer 1 有效規格，其 DEFER 掛鉤（D0–D28）對 Layer 2–7 規格作者之承接義務自此有效施行；Annex F 首批 Registry 條目隨本裁決**附卷採認**為施工啟動集（其後維護依 `AUGUR-WM v1.0 §WM.36`）。
* `AUGUR-MC v1.3` 同日生效（AL-2026-006）。
* AUGUR-WM 緊張關係 T-4（草案地位）、T-6（治權檔未登錄）、T-7（模板未確立、specs/ 地位未定）解消；T-1／T-2／T-3／T-5 依各該緩解路徑續行。

## 程序聲明

本裁決之實體擇定由 Constitution Steward 本人為之（2026-07-16 於工作對話中指示「依 §0.5 作充任認定，並同案辦理 §1.2 建請的四項程序」）；AI 僅任繕打、細節彙整與存檔，未參與議決之實體判斷（`AUGUR-MC §8.1` 之遵循）。主文二表列五檔之個別 Layer 歸屬，係依合憲審計報告治權整合路線圖（AUD-12 補正方向）之技術轉寫，經 Steward 以本裁決簽署整體採認；Steward 得隨時以 minor 修訂調整個別歸屬。本裁決書面化、附理由、公開存檔，minor 事項依治理附則第 2 條第 2 款無公示期要求。
