# Augur Steward 裁決第 2026-012 號

**CODE-MIGRATION-PLAN 採認暨五決策點處置；併案登錄備份第二目的地決策之取消**

* **依據**：`AUGUR-MC v1.3 §8.1`、P5.W2（人類權威根節點）；CLAUDE.md #20（計畫先行——本裁決即「拍板」步）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-18 書面指示「CODE-MIGRATION-PLAN 採認＋五決策點」「備份第二目的地……取消」
* **日期**：2026-07-18｜**登錄**：Amendment Log AL-2026-015

## 一、主文

1. **（計畫書採認）** `CODE-MIGRATION-PLAN.md`（v0.1-draft，經對抗審查 8 issues 全採納之修訂版）**採認為移轉之權威計畫**；地位由 draft 轉**生效 [I] 計畫**（[I] 性質不變：各期之 apply／併 main／生產施作仍逐案依計畫節拍取得核准，本採認不構成概括授權）。
2. **（五決策點逐點處置）**
   (a) **排程節奏**：採幕僚建議——Phase 1 立即（**已完成 2026-07-18**）、Phase 2/3/4/5 兩週窗、Phase 6 一個月窗、Phase 7 期限驅動（2026-10-14）。
   (b) **Phase 1 之 PR 併 main＋owner 分離方案**：**已成就**（#19 三鏡審查准併 `f95557b`＋P5 核准施作完畢），本點結案登錄。
   (c) **Phase 3 升裁決 C**（authorization_ref 是否 NOT NULL）：採幕僚建議之**嚴格面——NOT NULL**（無授權引用之自動化行動列不得落地；fail-loud），於 Phase 3 施工卷宗執行；施工實測若證明既有維運流程無法即時歸因，得以「過渡期 DEFAULT 授權列」方式落地、不得以可空欄位方式落地。
   (d) **原則精華 #7 條文改**（新版本入庫、舊版標 superseded）：**方向採認**；執行屬 augur-code 側治權檔升版程序，排入 Phase 7 併整批辦理。
   (e) **CI merge-gate 時點**：L7 已充任（RULING-2026-011）——**CI 接線即日解鎖**，以現行 gate 版本接線（`tools/constitution_lint/github-workflow.yml` 為既備工作流）；gate 三輪硬化包另案、不阻接線。
3. **（備份第二目的地決策之取消，誠實登錄）** Steward 裁示**取消**「異機／雲端第二目的地＋RPO/RTO＋演練節奏」之核定程序。效果：L7.25 之故障域分離以**現況（本地 dump＋D:\ 異碟 restic 庫）為既定終態**；「機器全損則備份俱失」之殘餘風險**經 Steward 知悉並接受**，登錄於 ENVIRONMENT-SPEC §六。此為風險接受之決策、非缺口之消滅——後任接手者不得引本項為「缺口不存在」之依據。

## 二、程序聲明

計畫之採認與各決策點之處置為 Steward 裁決；幕僚建議之採認均於各點載明。Phase 2 起各期施工仍逐案走「沙盒實測→P5 拍板→生產→驗證→留痕」節拍，本裁決不預授任何生產變更。
