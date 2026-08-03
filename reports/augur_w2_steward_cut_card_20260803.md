# W2 Steward 呈裁決策卡｜必裁三條＋U1 圈選 — 2026-08-03

> **位階**：[I] 呈案／決策卡（非 META-CONSTITUTION [N]；**非**正式 RULING 號；計畫級拍板登錄即可）。  
> **性質**：勾選拍板 → 授權**下一輪**依形制草 SQL／propose（仍 dry）；**本次不含任何 DB 寫入**。  
> **上游**：`reports/augur_w2_undefined_concept_unblock_plan_20260803.md` §6 · `reports/augur_w2_phase1_concept_unblock_prep_20260803.md` §1–§2 · `reports/wm_channel_registration_draft_20260803.md`（Q-R1…／§7.1）。  
> **硬紀律**：AI **不代勾「准」**／不代簽 `decided_by`；**FZ-keep**（不解凍 FinMind／FRED）；**M-T5** 不搶 `heavy_slot`；不 commit／不 push。  
> **Live 錨**（Phase1 附錄 A＝2026-08-03 PC002；歷史凍結）：概念覆蓋 **(mapped, 草案23, 無概念, 總)=(10, 23, 65, 98)**；機械配對 **9/98（9.2%）**；嚴格值欄展開面 **472**；多值欄通道 **67**；DRAFT23＝`[78,60,56,49,62,43,68,35,85,93,44,38,69,23,86,51,53,77,31,83,70,17,30]`；U1 樣本＝**31／62／93**。  
> **執行後 live（2026-08-03 21:18:59+08；U1 31＋62＋93 皆已親簽）**：`mapped=13/98` · `source_column 已填=3/98`（93＝`audits/W2-U1-BINDING93-EXECUTED-20260803.md`；62／31 見各執行 audit）。

---

## 0. 本件效力邊界（先讀再勾）

| 項 | 本卡 |
|---|---|
| 裁完＝ | Steward 明示答案記入本卡（或口頭＋本檔補勾） |
| **授權寫庫？** | **否**——裁完僅＝授權 AI 下一輪依選定形制**草** SQL／propose（dry／文件）；**hugo 親跑／親簽另授** |
| 解凍 API？ | **否**（FZ-keep） |
| 宣稱 WM.36 完成？ | **否**（Q-R1／W2-1／M-W3 未裁前禁大規模填 `source_column`） |

---

## 必裁①｜Q-R1 形制（unmapped → mapped）

> **未裁＝任何登錄 SQL 不得執行**（草案 §7 原文）。  
> **本輪已裁**：形制 **(a) 原地 UPDATE**（2026-08-03 Steward）；仍 **不得執行 DB 寫入**——僅授權 dry SQL 草擬。

| 選項 | 內容 | 後果（一行） |
|---|---|---|
| ☑ **(a) 原地 UPDATE（建議）** | `binding_id` 不變；`SET LOCAL augur.honesty_write='on'` 後同列改 `mapping_status`＋`concept_key` | 草案所列 binding_id 可沿用；WM.35「unmapped＝合法過渡」字面傾向；須親授 honesty 通行證 |
| ☐ **(b) supersede＋INSERT** | 舊列標 `superseded_at`；INSERT 新 mapped 列 | **append-only**；本批 23 個 binding_id **全部作廢重編**；引用草稿／報告之 ID 須全鏈改寫 |
| ☐ **其他**：____________ | （請寫一句） | — |

**附帶（若選 (a) 或 (b) 皆可能需要）**  
☑ **同意本輪（及後續親簽批次）得用 `SET LOCAL augur.honesty_write='on'`**　← **已發放：限 U1 試點 binding 31／62／93 之 dry→親簽執行窗（建議項）**（**2026-08-03 19:05+08** Steward 補裁）　☐ 改由腳本封裝後再授　☐ 其他：____  

> **意義邊界（寫死）**  
> - 通行證＝允許下一步「親簽後依 dry 稿執行 UPDATE」之**資格**  
> - **本輪仍不自動執行**、不連庫 COMMIT；須另有一句「親簽執行／do it」才動  
> - 射程嚴格限 **31／62／93**；其他 binding、假 concept 灌庫、FZ 取數皆**不**因本裁解凍  
>
> **本輪備註**：Steward 已裁 ①＝(a)；**附帶 honesty 通行證＝已發放（上列有界）**——dry SQL 之 `SET LOCAL` 對齊已發證條件；**仍待**親簽 `decided_by`＋明示執行句才可 `COMMIT`。

---

## 必裁②｜納入範圍＋A.11 指標粒度（W2-4／binding 93）

### 2-A 納入範圍（65 無概念）

> 備料標記：範圍軸＝**已拍預設**（計畫 §1.1／§6）；寫入仍閘在本卡明示。

| 選項 | 內容 | 後果（一行） |
|---|---|---|
| ☑ **P1→P4＋B0／infra 緩登（建議＝維持已拍預設）** | P1 消費錨 → P2 草案23 → P3 高用量 → P4 其餘；B0×11＋infra×2（88／89）**緩登**、不造假 concept | 對齊 Phase1 §4；K1 分母不含強求 98/98 |
| ☐ **改範圍**：____________ | （請寫） | — |
| ☐ **暫不裁範圍，只裁 A.11** | 佇列形狀維持備料預設 | 可進 U1 圈選；65 分流不得宣稱已定案 |

### 2-B A.11／W2-4（指標類；含 binding **93**）

> Live／抽樣：`TaiwanBusinessIndicator`＝**8** 值欄（含 `monitoring_color`）；草案擬**單**概念 `tw.business_cycle_indicator`。  
> A.11 字面：「每一指標為世界量」⇒ 領先／同時／落後／對策等可讀為 **7–8 個概念**而非 1 個。  
> 備料：93 暫用單概念、**明示 W2-4 衝突仍待裁**。

| 選項 | 內容 | 後果（一行） |
|---|---|---|
| ☑ **(單) 單表單概念（建議＝暫登、後再拆）** | 先登 `tw.business_cycle_indicator`；provenance 揭露與 A.11 張力 | 概念數對齊「23 表→23 概念」草圖；日後可 supersede 拆分 |
| ☐ **(多) 一指標一概念（A.11 嚴讀）** | 93 須重擬 7–8 keys（＋`monitoring_color` 是否獨立／同事實兩表徵） | 草稿鍵作廢；U1-93 本卡宜勾「緩登／重擬」；指標類成本上修 |
| ☐ **俟 Q-R5（knowability 待定錨）再併裁** | 93 不登錄、不拆 | 現行 2 檔消費仍屬缺口顯性化未入庫；不解阻 U1-93 |
| ☐ **其他**：____________ | | — |

> **本輪備註（U1×2-B）**：2-B 已採建議「(單)」；**U1-93 已補裁＝登錄（單概念）**（2026-08-03 17:50+08）⇒ dry SQL 見 `reports/augur_w2_u1_binding93_dry_sql_propose_20260803.md`（仍禁執行）。

---

## 必裁③｜W2-1 多欄承載形

> 決定 Phase 2／3 資料形狀；Live：**67** 條多值欄通道；選 (b) 時列數膨脹風險至展開面 **~472**。  
> **本輪已裁**：**(a) 分隔字串（建議＝最小 schema 動）**（2026-08-03 Steward）。

| 選項 | 內容 | 後果（一行） |
|---|---|---|
| ☑ **(a) 分隔字串（建議＝最小 schema 動）** | 單欄 `source_column` 存 CSV／分隔名單 | 零 DDL；解析約定須釘死；多欄語意弱、易歧義 |
| ☐ **(b) 一欄一 binding 列** | 同表多概念／多欄各一列（先例 Delisting 2／3） | 正規、可 `resolve`；列數膨脹（最壞逼近 472 量級） |
| ☐ **(c) 改 schema** | `source_columns text[]` 或子表 `world_channel_binding_column(...)` | 正規化最佳；**表結構變更＝Steward 專屬**、須另開遷移案 |
| ☐ **其他**：____________ | | — |

---

## U1 圈選｜binding 31／62／93

> Wave＝備料 §2 序 1–3（**U1 優先**）；其餘 20 見草案 §7.1／備料 §2.1——**本卡不強制同批**。  
> 每列勾一主選（可加備註）。**合併預設**（文件）：M3 財報 balance↔income **不合併**（`resolve()` 單 binding）；若要改→先解 Q-R2。

| binding | 表（短） | 建議 concept_key | 共病／殘留 | 圈選（勾一） |
|---|---|---|---|---|
| **31** | BalanceSheet | `tw.financial_statement.balance` | 多值 `type`；與 68 為 M3 合併候補（建議分立）；Q-R5-i 錨不在表內 | ☑ 登錄　☐ 合併入 68（M3）　☐ 不登錄　☐ 緩登　☐ 俟 Q-R5　備註：**已執行**（2026-08-03 19:27:36+08；`decided_by=hugo`；audit `W2-U1-BINDING31-EXECUTED-20260803.md`）；不合併 68 |
| **62** | Shareholding | `tw.foreign_ownership.stock` | Q-R5-iii knowability 兩讀（`RecentlyDeclareDate`）；抽樣 B5（11 值欄→入 6／出 5） | ☑ 登錄　☐ 不登錄　☐ 緩登　☐ 俟 Q-R5　備註：**已裁「登錄」**；**已親簽執行**（`audits/W2-U1-BINDING62-EXECUTED-20260803.md`；Q-R5-iii 殘留寫 provenance） |
| **93** | BusinessIndicator | `tw.business_cycle_indicator`（單）／或多鍵（依 2-B） | **W2-4／A.11**；knowability＝**待定錨**（WM.31⇒不可 as-of，但現正被消費） | ☑ 登錄（依 2-B 粒度）　☐ 不登錄　☐ 緩登　☐ 俟 Q-R5／重擬多鍵　備註：**已裁「登錄」＝2-B 單概念**；**已親簽執行**（`audits/W2-U1-BINDING93-EXECUTED-20260803.md`；A.11 張力／待定錨寫 provenance） |

**可選同批（非 U1 硬要求；「A 乾淨」序 4–6）**

| binding | key | 圈選 |
|---|---|---|
| 86 | `tw.margin_maintenance_ratio.market` | ☐ 登錄　☐ 本批跳過　☐ 不登錄 |
| 35 | `tw.day_trading.stock` | ☐ 登錄　☐ 本批跳過　☐ 不登錄 |
| 70 | `tw.market_capitalization.stock` | ☐ 登錄　☐ 本批跳過　☐ 不登錄 |

---

## 明示｜本次不寫庫

- [x] **本件裁示 ≠ 寫入授權**：不含 `INSERT`／`UPDATE`／`DDL`／親簽執行。  
- [x] 裁完後預設下一動作＝AI 依 **①形制＋③承載** 產出 **dry SQL／propose 文件**（佔位符仍由 hugo 親填）；**實際 `BEGIN`…`COMMIT` 須另下明示**。  
- [x] FZ-keep · 不搶 M-T5 `heavy_slot` · 不代簽 `decided_by`。

---

## 強烈建議同批（非本卡最小集；可略）

| 代號 | 一勾即可 | Steward |
|---|---|---|
| W2-2 | 未落地 B0 可否填欄映射（建議＝**否**） | ☐ 採建議否　☐ 是（須豁免理由）　☐ 另案 |
| W2-6／Q-R7 | 全 PK 值欄（sample 97） | ☐ 另案　☐ 本周裁 |
| Q-R8 | 非 `tw.` 命名（37／50／85） | ☐ 另案　☐ 本周裁 |
| M-W3／M-N7 | 絞殺／vendor 直綁尺 | ☐ 另案（預設） |

---

## 簽核欄（Steward 親勾；AI 空白不預填「准」）

| 項 | 勾選 |
|---|---|
| 必裁① Q-R1 | ☑ 已裁（選項：**(a) 原地 UPDATE（建議）**）　☐ 未裁 |
| 必裁② 範圍＋A.11 | ☑ 已裁（2-A：**P1→P4＋B0／infra 緩登（建議＝維持已拍預設）**／2-B：**(單) 單表單概念（建議＝暫登、後再拆）**）　☐ 未裁 |
| 必裁③ W2-1 | ☑ 已裁（選項：**(a) 分隔字串（建議＝最小 schema 動）**）　☐ 未裁 |
| U1 31／62／93 | ☑ 三條皆有主選（**31＝登錄**；**62＝登錄**；**93＝登錄（2-B 單概念）**）　☐ 僅子集　☐ 未裁 |
| **本卡效力** | ☑ **裁示成立**（下一輪可草 dry SQL／propose）　☐ **撤回／改裁**　☐ 僅留檔不授權下一步 |
| 日期／簽 | **2026-08-03 21:18:59+08**＝binding **93 已親簽 COMMIT**（`decided_by=hugo`）；**21:15:03+08**＝binding **62**；**19:27:36+08**＝binding **31**；**19:05+08**＝honesty 通行證已發放（限 31／62／93）；先前 17:50＋17:34＋16:55 見上；**U1 三條皆已執行** |

**簽核摘要（建議原文照抄）**

| 軸 | Steward 裁 | 卡上「建議」原文（照抄） |
|---|---|---|
| ① Q-R1 | (a) UPDATE 現行列 | **(a) 原地 UPDATE（建議）** |
| ②-A 納入範圍 | 採建議 | **P1→P4＋B0／infra 緩登（建議＝維持已拍預設）** |
| ②-B A.11／93 粒度 | 採建議 | **(單) 單表單概念（建議＝暫登、後再拆）** |
| ③ W2-1 | 採建議 | **(a) 分隔字串（建議＝最小 schema 動）** |
| U1 | **31＋62＋93 登錄**（93＝**2-B 單概念**） | **31＋62＋93＝皆已執行** |
| honesty | **已發放**（限 31／62／93 dry→親簽窗） | 31／62／93 皆已消費（窗內試點結束） |
| 後續 | **U1 試點關閉**；AskQuestion＝commit 文件／守夜班 | 31／62／93 各見執行 audit |

**拍板碼（選填，裁後由人填）**：`W2-CUT-20260803-U1-31` ＋ `W2-CUT-20260803-U1-62` ＋ `W2-CUT-20260803-U1-93` ＋ `FZ-keep` ＋ `NO-DB-THIS-CARD`  
（附帶 honesty 通行證：**已發放**——限 U1 31／62／93 dry→親簽執行窗；**仍不自動 COMMIT**。）

**Dry SQL 稿／執行狀態**  
| binding | 檔 | 狀態 |
|---|---|---|
| **31** | `reports/augur_w2_u1_binding31_dry_sql_propose_20260803.md` | **已執行**（`audits/W2-U1-BINDING31-EXECUTED-20260803.md`） |
| **62** | `reports/augur_w2_u1_binding62_dry_sql_propose_20260803.md`（不與 31 混） | **已執行**（`audits/W2-U1-BINDING62-EXECUTED-20260803.md`） |
| **93** | `reports/augur_w2_u1_binding93_dry_sql_propose_20260803.md`（**2-B 單概念**；不與 31／62 混） | **已執行**（`audits/W2-U1-BINDING93-EXECUTED-20260803.md`） |

**簽核摘要 audit**：`audits/W2-U1-HONESTY-PASSPORT-ISSUED-20260803.md` · **31**：`audits/W2-U1-BINDING31-EXECUTED-20260803.md` · **62**：`audits/W2-U1-BINDING62-EXECUTED-20260803.md` · **93**：`audits/W2-U1-BINDING93-EXECUTED-20260803.md`

---

## AskQuestion（裁後下一刀）

1. ☑ **授權草 SQL（仍 dry）**——依本卡形制產出親簽範本／propose，**不執行**　← **31／62／93 dry 稿已交付**  
2. ☑ **honesty 通行證**——**已發放**（限 U1 31／62／93 dry→親簽窗；2026-08-03 19:05+08）  
3. **先只裁必裁① Q-R1**——其餘擱置；SQL 形狀未定前不做多概念草擬（已裁，歷史項）  
4. **守夜班**——本卡凍結；不碰 heavy_slot／evolution／寫庫  

**下一刀呈裁（請 Steward 勾）**  
☐ ~~補裁 U1-62~~（已裁＝登錄）　☐ ~~補裁 U1-93~~（已裁＝登錄／2-B 單概念）  
☑ ~~補裁附帶 honesty 通行證~~（**已發放** 2026-08-03 19:05+08；限 31／62／93 dry→親簽窗）  
☑ ~~親簽執行 binding 31~~（已 COMMIT；`decided_by=hugo`；2026-08-03 19:27:36+08）  
☑ ~~親簽執行 binding 62~~（已 COMMIT；`decided_by=hugo`；2026-08-03 21:15:03+08）  
☑ ~~親簽執行 binding 93~~（已 COMMIT；`decided_by=hugo`；2026-08-03 21:18:59+08；2-B 單概念）  
☐ **守夜班**（22:5x prerun／23:00 TWEVO；本卡凍結、不搶 heavy_slot）　☐ **先 commit 文件**（audit＋決策卡＋dry 稿；零 push 除非另授）  

---

## Trace

| 宣稱 | 出處 |
|---|---|
| 必裁三條原文 | 解阻計畫 §6 |
| U1＝31／62／93；執行序 | Phase1 §2.1；計畫 §1.2 桶 U1 |
| Live (10,23,65,98)／9.2%／472／67／DRAFT23 | Phase1 附錄 A |
| Q-R1 兩造＋SQL 先決 | 草案 §6／§7 |
| A.11 vs 單概念 | 抽樣 §2 binding 93；結構題 W2-4 |

*完。卡本體歷史裁示區仍「裁≠寫庫」；**31／62／93 已另案親簽執行**（audit 上）。零 git commit（本輪）。*
