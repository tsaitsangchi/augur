# Augur Steward 裁決第 2026-018 號

**AUGUR-WM v1.0（L1）首次三鏡對抗審查 findings 之處置——§8.6 patch＋§8.1 解釋**

* **依據**：`AUGUR-MC v1.4 §8.1`／`§8.6`；findings 冊 audits/WM-THREE-MIRROR-REVIEW-2026-07-18.md
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-18 書面核示「全艦明採 v1.4」
* **登錄**：Amendment Log AL-2026-021
* **性質**：Steward 作成；幕僚機械執行。WM 之修正為 §8.6 patch（引用格式／[I]／條頭），非原則級。
* **審查結論**：L1 首審**強過關**——三鏡零 major 存活（唯一 major 經雙反駁殺）、規範核心經證穩固、無一觸憲。殘餘全為 minor/patch。

## 一、擬處置（三項，Steward 裁酌）

### 處置一：版本斷鏈（195 處 v1.2＋§0.3 凍結 MUST＋WM.44 張力）——§8.6 patch
L1 為七份規格唯一仍錨 `AUGUR-MC v1.2` 者（195 處，餘六份皆 v1.3、MC 現已 v1.4）。RULING-2026-002 主文一已認 v1.2≡v1.3（合規聲明無須重作），故非牴觸；惟 §0.3 以 **MUST 永久凍結**「一律採 AUGUR-MC v1.2 §{條款}」、WM.44 又稱「現行版（以 v1.2 枚舉）」自相張力，且 MC 每次 minor 升版將令其愈發過時。
**擬**：§8.6 patch——(a) §0.3 凍結措辭改「採 **AUGUR-MC 現行版** §{條款}」相對表述；(b) 全文 195 處 `v1.2`→`現行版`或 `v1.4`（機械）；(c) WM.44 枚舉基準對齊「現行版」＝linter 實況。**〔待 Steward 擇 (a) 相對表述 or 明採 v1.4；擇定後幕僚機械執行〕**

### 處置二：C.10 §8.1 雙歸類矛盾——§8.6 patch
§8.1 於 WM.47/48 標 carries、又於 C.10 列「不觸及」——違 WM.44 三分互斥（弱 linter 未攔之治理裂縫、非覆蓋缺口）。
**擬**：C.10 將 §8.1 由「不觸及」改列「對應至 WM.47、WM.48（效力面承接）」，僅留 §8.5 於「不觸及」。機械 patch。

### 處置三：WM.38/WM.34 泛稱「下層」DEFER 條頭精度——§8.1 釐清＋[I] patch
WM.38（承 P1.E3）與 WM.34（稽核機制）以泛稱「下層」下放、條頭標 carries 而非 hooks、未入 Annex D 總表——與 WM.3「DEFER 必具名層」自訂紀律不符。**實質已於 Annex D D17（L3/L6）治癒、被下層承接，非鏈斷。** 與 MC 三鏡 P1.E3「未點名層」為同型（RULING-2026-017 已釋明 P1.E3 主責 L6）。
**擬**：(a) §8.1 釐明 WM.38 目標層＝L3/L6（承 017 之 P1.E3 主責 L6）、WM.34 稽核實作目標層；(b) [I] patch 條頭補「hooks｜目標 Layer」、Annex D 補 WM.34 列。

## 二、observation（登錄不併裁）
WM.9 權威三分位置名未入 WM.2 清單｜B.1 MC-34 hooks vs clause carries 字面差｜WM.15 衍生調整觀測之衍生地點語彙（AUD-14 家族、還原價系統自建後 Observation↔Representation 翻轉）——後者宜於 Phase 6 Annex F #1 啟動前 §8.1 釐清。

## 三、對 L1「完成」之意涵
一經 Steward 處置本草案，**AUGUR-WM v1.0 完成首次對抗審查閉環**——強過關（零 major）＋findings 經處置。在此前，L1「完成」之誠實現狀為「首審強過關、findings 待處置」。

---
*本草案不生效力；一切修訂與解釋俟 Steward 親為。*

---

## 四、執行記錄（2026-07-18，Steward「全艦明採 v1.4」）

* **處置一（全艦 v1.4）**：Steward 裁定明採 v1.4。L1 之 223 處 `AUGUR-MC v1.2`→v1.4（含 §0.3 凍結 MUST 改為「升版同步更新」根治、WM.44 枚舉基準、Annex C mc-version、地位句改寫）；L2–L7 之 `AUGUR-MC v1.3`→v1.4（ONT 90／ID 79／KS 113／L5 48／L6 71／L7 94；含各 front-matter mc-version）。**七份規格引用版號自此齊一 v1.4；L1 之版本落差警訊消失**。
* **處置二（C.10）**：§8.1 由「不觸及」改列「效力面對應 WM.47/48（carries）」，僅留 §8.5 於不觸及——解 WM.44 三分互斥矛盾。
* **處置三（WM.38/34）**：WM.38 條頭 carries→carries＋hooks 具名目標 L3/L6（承 D17）；WM.34 稽核實作 DEFER 具名 Layer 1＋Layer 7（承 RULING-2026-017 工具保真解釋）。
* **selftest 維護**：版本落差鎖原依 WM 真實 v1.2 落差當 fixture，全艦對齊後改以**合成落差**驗（暫存本降一 minor），判準不變、鎖更強。
* **驗證**：七份 gate 全 PASS、selftest 全綠、report 綁定同步。
* **待補**：本批全艦變更之獨立核驗（隨後發包——防批量替換誤傷）。

## 五、對 L1「完成」之結算
**AUGUR-WM v1.0 完成首次對抗審查閉環**：強過關（零 major）＋三項 findings 全數處置。L1「完成」自本裁決生效起成立；殘餘 observation（WM.9 命名／B.1 hooks／WM.15 衍生地點）登錄待 Phase 6 前 §8.1 釐清，不阻卻。

*本裁決生效。*
