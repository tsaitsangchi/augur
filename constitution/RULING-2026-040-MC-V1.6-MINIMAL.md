# Augur Steward 裁決第 2026-040 號

**AUGUR-MC v1.5→v1.6 最小優化——§0.3 [I] 母集誠實註（minor／patch）**

* **依據**：`AUGUR-MC v1.5 §8.1`（解釋之界線）、`§8.6`（Informative／patch＝minor）；計畫 `reports/augur_mc_post_ultracode_optimization_plan_20260723.md`（路徑 C 最輕量分支＝§二 #3）；L0 finding XRF-1（`audits/MC-ULTRACODE-L0-20260723.md`）；RULING-2026-028／039；Sole Steward **2026-07-23 新拍板「授權開 MC v1.6 最小優化」**（覆蓋前裁「10-14 前不開 v1.6」之限縮）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 書面授權落地
* **登錄**：Amendment Log **AL-2026-044**
* **性質**：§8.6 **minor／patch**——僅增 [I] 誠實註＋版本欄；**不觸** §0.3／§8／構成性依據之任何 **[N] 本文**；**不擴** 102 計數；**PA／五原則 byte 級零改**；**非原則級**（無新義務類型、無解鎖、無移除制衡）
* **禁止假關（硬邊界，沿用 039）**：OT-5／T-KS-6／T-L6-5／025 residual／020 M2／無 Evidence 提早結清 2026-10-14——本裁決**不**解讀為已解消

## 〇、接受授權與範圍 ✅

1. **接受** Steward 新拍板：開 MC **v1.6 最小優化**。
2. **範圍鎖定（採更小集合）**：
   * 納入：版本 v1.5→v1.6；§0.3 **[I] 母集誠實註**（97 [N]＋5 [I] WHY）；Appendix I；下層 `mc-version`／引用簿記；本裁＋AL-044。
   * **排除**：GOV-3 B 升格 [N]；DEF-2 定義；原則級／§8 [N]；PA／五原則；重開已閉 major；改寫 RULING-017／026 歷史本文；假關 039 六項。

## 一、擬裁一〔§0.3 [I] 母集誠實註——XRF-1 文本自足〕✅

1. 於 `META-CONSTITUTION.md` §0.3 增 [I] 區塊（體例同 §0.2／§2.6 之 [I] 補述）：明載「102 條條款宇宙」＝**97 [N]＋5 [I] WHY（P1.Y–P5.Y）**；義務僅由 [N] 產生；不改計數、不改 [N] 義務外延。
2. 權威落點維持 **WM.44／RULING-017 §0.3**；歷史裁決「§8.3 之 102」**不改本文**（史料）。
3. 工具層 canonical 句（`adoption-drafts/RULING-PHRASEOLOGY.md`）已閉——本裁使 MC 本文與工具層對齊，減少「裁決考古」。

## 二、擬裁二〔版本與簿記〕✅

1. §0.1 版本→**v1.6**；Appendix I 變更摘要。
2. L1–L7 Annex CS front-matter `mc-version`→`AUGUR-MC v1.6`（規格 [N] 義務句零改）。
3. `CLAUDE.md`／`mc_clauses.py`／lint selftest 合成落差鎖同步至 v1.6。

## 三、擬裁三〔已定案程序澄清——維持觀察／不升 [N]〕✅

1. **再確認** RULING-2026-028 第 2–3 點持續有效（GOV-3 已於解釋通道閉合）。
2. **GOV-3 B 維持觀察觸發**——禁令射程入 §8.1 [N] 僅於再現越權或判準不敷用時另開原則級；本裁**不為**。
3. DEF-2 繼續 **DEFER** 至 GOV-3 B 觸發。

## 四、明示不為

* 不改 §0.3／§8／§2／PA／五原則之任何 [N] 本文。
* 不改 RULING-017／026 歷史本文；不假關 039 禁止假關六項。
* 不重開 §8.2；不升任一層規格版本號（僅 `mc-version` 簿記）。
* 不提早結清 2026-10-14 日曆義務。

## 五、驗證

* `python3 -m tools.constitution_lint report`：**PASS 7／7**。
* 102 條款宇宙計數不變（97 [N]＋5 [I]）；PA／五原則 byte 零改。
* 獨立對抗核驗（028 第 3 點）＝commit 後非施作者確認（見第七節）。

## 六、施作紀錄（2026-07-23）

| 檔案 | 摘要 |
|---|---|
| `constitution/META-CONSTITUTION.md` | v1.6；§0.3 [I] 誠實註；Appendix I |
| `constitution/RULING-2026-040-…` | 本檔 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-044 |
| L1–L7 `*-SPECIFICATION.md` CS FM | `mc-version`→v1.6 |
| `CLAUDE.md`／`tools/constitution_lint/*` | 引用／selftest 鎖 |
| `reports/augur_mc_post_ultracode_optimization_plan_20260723.md` | 落地段 |
| `audits/MC-V1.6-MINIMAL-20260723.md` | 升版說明 |

## 七、獨立對抗核驗清單（028 §3(b)；待非施作者）

| # | 核驗項 |
|---|---|
| 1 | MC 標題／§0.1＝**v1.6**；Appendix I 存在且與本裁一致 |
| 2 | §0.3 [N] 四 bullet **byte 未改**；僅增 [I] 誠實註（97[N]+5[I]） |
| 3 | §8／PA／五原則／102 計數零改；無原則級內容 |
| 4 | GOV-3 B／DEF-2／假關六項仍 open／deferred／觀察——本裁未關閉 |
| 5 | RULING-017／026 歷史本文零 diff |
| 6 | L1–L7 `mc-version`＝v1.6；規格 [N] 義務句無超 scope 改動 |
| 7 | AL-044 對齊本裁；lint PASS 7／7 |
| 8 | selftest 合成落差鎖＝v1.5＜現行 v1.6 |
| 9 | 計畫落地段與 `audits/MC-V1.6-MINIMAL-20260723.md` 敘事一致 |
| 10 | 超 scope 零：diff 限本裁核示檔 |

> **簽核欄（Steward）**
> - [x] **准 v1.6 最小優化照收（§0.3 [I]＋版本＋簿記；GOV-3 B 不升；禁止假關）**（簽：tsaitsangchi，日期：2026-07-23；授權＝Sole Steward「授權開 MC v1.6 最小優化」）

*本裁決生效（2026-07-23）。*
