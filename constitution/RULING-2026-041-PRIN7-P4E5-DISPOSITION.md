# Augur Steward 裁決第 2026-041 號

**P3：原則精華 #7 ↔ `§P4.E5` 緊張處置——#7 改條對齊 supersede（非豁免；code 不先行）**

* **依據**：`AUGUR-MC v1.6 §0.6`（lex superior）；`§P4.E3`／`§P4.E5`；計畫 `reports/augur_docs_into_mc_initial_constitution_plan_20260723.md` P3；RULING-2026-012 主文 2(d)（#7 方向採認）；AUD-02 設計卷宗 `docs/remediation/AUD-02-raw-supersede-log.md`（決策 A/B 已拍板、code 受閘）
* **裁決人**：Constitution Steward（tsaitsangchi）——Sole Steward **開 P3**（2026-07-23）授權落地
* **登錄**：Amendment Log **AL-2026-045**
* **性質**：領域治權（原則精華）**minor** 升版——**不觸** MC／PA／五原則 [N] 本文；**不**假關 039 其他 10-14 項；**不上收** docs 進 META；**不**改 prediction／ingestion code

## 〇、衝突摘要與位階 ✅

| 側 | 義務 | 位階 |
|---|---|---|
| `#7`（舊） | correction＝重跑 sync → upsert **覆蓋** live 為當前 API | 領域 L4 |
| `§P4.E5` | 衝突 Evidence **共存＋顯式標記**；禁靜默 last-write-wins | **L0 lex superior** |
| `§P4.E3` | 只失效不刪除（supersede／retract） | L0 |

**衝突點**：舊 #7 允許 live 覆寫消滅舊觀測於主表，且僅靠短暫 audit examples——與 P4.E5「原始證據永不覆寫消滅」緊張。

**優先**：下層／領域牴觸 MC 之部分無效（§0.6）→ **必須改領域條或明示過渡**；**不得**為消緊張改弱 MC [N]、**不得**豁免 P4.E5。

## 一、採案 ✅

**採 (a) 最佳案**：原則精華 **最小改條**——#7 ENFORCE 改為「**新版本入庫（live＝當前 API）＋舊版 append-only superseded／衝突共存**」。

* **不採**裸豁免（waivers: [] 維持）。
* **過渡**：規範緊張**關閉**；AUD-02 **code** 實作仍受閘（設計已定案、施工另開）——過渡錨＝操作閉合待 `raw_supersede_log` 落地，**非**對 P4.E5 之豁免。
* **承** RULING-2026-012 2(d) 方向採認；本裁＝文字升版執行（原排 Phase 7 之文案，Sole Steward 開 P3 提前落地）。

## 二、主文 ✅

1. **原則精華** `v1.9.1` → **`v1.10.0`**：#7 ENFORCE 依上案改寫；檔頭撤「開放緊張」；演進記錄登錄。
2. **合規聲明** `CS-原則精華_v1.10.0.md`：`open-tensions` **移除** `T-PRIN-7-P4E5`（狀態＝**已閉／規範對齊**）；`D-PRIN-2` 改為 AUD-02 **操作／code 補正** defer（目標至遲併 **2026-10-14** 補正窗，與 RULING-002／012 Phase 7 日曆一致——**不**假關其他 039 項）。
3. **MC／specs／prediction code**：本裁 **零改**。
4. **禁止假關**：OT-5／T-KS-6／T-L6-5／025 residual／020 M2／無 Evidence 提早結清 10-14——本裁**不**解讀為已解消。

## 三、明示不為

* 不改 META／PA／P1–P5 [N]；不為消緊張大幅改 MC。
* 不上收 docs 進 MC；不開案 A／C／P4 領域包。
* 不先行實作 AUD-02／改 heal／upsert 行為。

## 四、驗證

* 原則精華 #7 本文含 supersede／禁靜默 LWW／對齊 P4.E3／E5。
* CS：`open-tensions` 不含 T-PRIN-7-P4E5；waivers 仍 `[]`。
* `python3 -m tools.constitution_lint report`：PASS（本裁不改 specs [N]）。
* diff 範圍限本裁核示檔；無 prediction／ingestion 行為碼。

## 五、施作紀錄（2026-07-23）

| 檔案 | 摘要 |
|---|---|
| `docs/原則精華_v1.10.0.md` | #7 改條；v1.10.0；緊張閉 |
| `docs/compliance/CS-原則精華_v1.10.0.md` | T 閉；D-PRIN-2→AUD-02 code |
| `constitution/RULING-2026-041-…` | 本檔 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-045 |
| `constitution/GOVERNANCE-MAP.md`／計畫 P3／交叉引用 | 狀態＋路徑 |
| `audits/P3-PRIN7-P4E5-20260723.md` | 執行留痕 |
| `docs/remediation/AUD-02-…` | 條文義務已入憲註記 |

> **簽核欄（Steward）**
> - [x] **准 P3：#7 改條對齊 P4.E5 supersede；非豁免；code 不先行**（簽：tsaitsangchi，日期：2026-07-23；授權＝Sole Steward「開 P3」）

*本裁決生效（2026-07-23）。*
