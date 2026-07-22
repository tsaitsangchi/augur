# Constitutional Compliance Statement 暫行模板

* **依據**：`AUGUR-MC v1.3 §8.3` 過渡規則 (a)（聲明格式定義於 Layer 1 生效前，由 Steward 發布暫行模板）
* **發布**：Constitution Steward（tsaitsangchi），2026-07-16；Steward 裁決第 2026-002 號主文三
* **登錄**：Amendment Log AL-2026-005
* **地位**：本模板與 `AUGUR-WM v1.0 §11`（WM.39–WM.45）實質等效；任何表述差異以 §11 為準。其功能以**追認 AUGUR-WM Annex C 依其作成**為限（`§8.3` 過渡規則 (a)(c)；RULING-2026-002 主文三）：AUGUR-WM 生效（2026-07-16）後，一切新作成之聲明（含五份治權檔之補正聲明）必須依 `AUGUR-WM v1.0 §11` 格式作成（`AUGUR-WM v1.0 §WM.45`）；本模板留存為歷史文件與 §11 之對照參考。

---

## 模板

依本模板作成之 Constitutional Compliance Statement 必須含下列**識別區塊**與**五部**（除五部外僅得另附待決事項節）：

### 識別區塊（機器可讀）

```
compliance-statement:
  spec: <規格名稱>
  spec-version: <版本>
  layer: <1–7>
  mc-version: <合規之憲章版本，如 AUGUR-MC v1.3>
  upper-specs: [<所依上層規格及版本；Layer 1 為空>]
  statement-format: <interim-template 或 AUGUR-WM v1.0 §11>
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: [<現行豁免逐項四欄組 {編號, 範圍, 到期日, 補正計畫引註}；無則空>]
  open-tensions: [<緊張關係編號>]
  defers-in: [<承接上層 DEFER 掛鉤之編號>]
  defers-out: [<下放下層 DEFER 掛鉤之編號>]
  date: <作成日>
  author: <作成者>
  archive-path: <依 Steward 裁決第 2026-002 號主文四所定處所之儲存庫相對路徑>
```

### 五部

1. **逐原則合規論證**：依固定七節順序——PA、P1、P2、P3、P4、P5、`§4 canonical chain`（獨立一節）——逐一載明所引 `AUGUR-MC` 條款、合規模式（滿足／細化 refines／承接 carries／DEFER hooks／不適用（附理由）；得複合；「不適用（附理由）」與 `AUGUR-WM v1.0 §WM.44` 之「不觸及」同義）、論證本文。canonical chain 之引用一律為節選標注且節點連續。
2. **判準揭示**：本規格引用之每一憲章評價性謂詞、及自創評價性謂詞，逐一給出可判定判準或引註其判準條款（`AUGUR-MC §8.3` 可判定性元規則）；判準未給出者明記採保守解釋。
3. **已知緊張關係揭露**：逐項載明所涉條款、描述、緩解／狀態。不得隱匿；「目前證據不足」為合法狀態。
4. **豁免登記**：現行豁免逐項四欄——編號、範圍、到期日、補正計畫引註——俱全；無則載 `none`。豁免期間 Knowledge 標記義務之落實方式。
5. **雙向 DEFER 承接表**：(a) 承接上層規格（或憲章）之掛鉤逐列；(b) 下放下層之掛鉤逐列（條款號 → 目標 Layer → 依據）。

### 效力規則

* 無聲明之規格不生效力（`AUGUR-MC §8.3`）；既存規格依過渡規則 (b) 於 Steward 裁定之補正期內推定有效（現行裁定：至 2026-10-14，Steward 裁決第 2026-002 號主文二）。
* `AUGUR-MC` 全部 [N] 條款均須對應至作成聲明之規格至少一條 [N] 條款、明記 DEFER 掛鉤、或明記「不觸及」及理由（形式充分性，對應 `AUGUR-WM v1.0 §WM.44`）。
* 聲明內容與規格正文不一致時，以正文 [N] 條款為準，不一致處視為文件缺陷依 `AUGUR-MC §8.2` 處理。
