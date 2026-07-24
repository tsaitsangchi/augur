# U5 Ultracode — R5 假綠／Goodhart／洩漏／門柱對抗 [I]（2026-07-24）

* Steward：「**開 S3 → 立刻 U5 打整包**」；輸入＝S1＋S2＋S3＋Gap G-ISO-2／G-PV-1／G-OUT-*＋R5 計畫宣稱
* **方法**：Find→Verify→Critic→Synthesize（對齊 U3／U4 鐵律）
* **硬邊界**：不改 [N]；不解凍 FinMind／FRED；不 evaluate／不偽造 `evaluated_pass`
* 證據錨：`audits/ROADMAP-R5-S12-CLOSED-20260724.md` · `ROADMAP-R5-PREDICT-PING-20260724.md` · `ROADMAP-R5-S3-STATUS-20260724.md` · `reports/augur_roadmap_r5_plan_20260724.md` · `reports/augur_roadmap_r3_gap_ledger_20260724.md`

---

## 一、Find（攻擊面）

| 攻擊 | 假說 |
|---|---|
| 假綠 | 把 S1–S3 哨兵綠讀成「預測半系統可交易／確立級」 |
| Goodhart | 為過門改 criteria／把 α 當雙閘／把 arena pass 當 direction pass |
| 洩漏 | PV-α 只擋字面；動態 SQL／GRANT SELECT 仍准 writer 讀產物 |
| 門柱挪動 | 無 evaluate 卻改門檻；或把 R5 近程 DONE 定義膨脹成 universe→econ 全綠 |
| 不實「R5 DONE」 | 無 A9／無 U5／或混稱路線圖大標題「半系統落地」已全量 |
| 幽靈證據 | S12 檔內 G-ISO-2＝partial 與帳本 none 並存；計畫 §「現況」表仍寫舊 as-of |

---

## 二、Verify（親驗證據 → 裁決）

| ID | 標的 | 嚴重度 | 文本／形式／實務 | 裁決 |
|---|---|---|---|---|
| **F-U5-1** | 文件幽靈（G-ISO-2） | **medium** | **文本**：`ROADMAP-R5-S12-CLOSED` Gap 表仍寫 G-ISO-2 **partial**（密碼失敗）。**形式**：後續 `ROADMAP-R5-PREDICT-PING`＋帳本已 **none**；S3 再親驗 `ping_predict=True`／pytest 5 passed。**實務**：只讀 S12＝幽靈「未閉」。 | **成立（時點漂移）**；**不**改 gap_class（已 none）。處置＝S3／本檔釘「S12 表＝史料；以 PING＋S3＋帳本為準」；S12 不強制改寫（閉合檔凍結亦可） |
| **F-U5-2** | G-PV-1「none」vs 禁回讀敘事 | **medium（殘留／誤讀）** | **文本**：帳本／S12 標 G-PV-1 **none**（PV-α）。**形式**：COMMENT 誠實「GRANT SELECT 仍准；β 未做」；S3 親驗 `has_table_privilege(augur_predict,prediction_values,SELECT)=true`。AST 擋不到動態組字串。**實務**：若對外說「產物禁回讀雙閘已完」＝假綠；若說「α 字面閘＋COMMENT 對齊＝conflict 已解」＝與拍板 `PV-α` 一致。 | **成立（誤讀路徑）**；`gap_class` **維持 none**（對 α）。β 另授權。U5 **禁**把 none 讀成 β 已做 |
| **F-U5-3** | 範圍門柱／「R5 DONE」膨脹 | **major（若誤宣稱）／現況防住** | **文本**：路線圖 R5 列「universe→model→econ／arena 可驗」；計畫近程 DONE＝A1–A6＋A8＋A10＋A7／A9，**≠** arena／econ／Dividend。**形式**：S3 全 PASS 後近程可閉；`evaluated_pass=0`、econ／dirprob **0 列**。**實務**：稱「全量預測半系統已落地可交易」＝門柱膨脹。 | **現況：未見本輪 audits 搶跑**。裁決：**近程 R5 DONE 可呈核**；**全量產品半系統／可交易＝禁**；須另開執行工單 |
| **F-U5-4** | API 凍結實務破口 | **medium（操作）** | **文本**：凍結 rule＋計畫禁 FinMind。**形式**：S3 開工時 `dividend_resume_sync.py` 仍在跑（FinMind 放量至 ~800/3123）。**實務**：文件凍結 ≠ 進程停。 | **成立**；已 **PAUSED**。不影響 S3 A8（本輪未再開）。殘留：G-DIV-1 半完成狀態知情 |
| **F-U5-5** | arena pass ≠ 方向確立級 | **medium（誤讀）** | **文本**：HANDOFF 有 arena_admission `evaluated_pass`／開賽敘事。**形式**：門二 `direction_gate.evaluated_pass=0`；advisor prompt 依門二動態。**實務**：把 arena 開賽當「方向確立級／可交易」＝假確立。 | **成立（路徑）**；帳本／原則精華已分閘；本輪 **無**新增混淆句 |
| **F-U5-6** | 計畫 as-of 表未刷 | **low–medium** | **文本**：`augur_roadmap_r5_plan` § 現況表仍列 G-ISO-2 partial／G-PV-1 conflict（開工前快照）。文首／§12 已更新 none。**實務**：掃到舊表列可以為 gap 未解。 | **成立（內部不一致）** → 計畫最小 diff 刷現況列（[I]） |
| **F-U5-7** | G-OUT-2 假 none | **low（已防）** | 幅度軸仍 **doc-only**；S3／帳本未改 none。 | **不成立為缺陷**；維持 |
| **F-U5-8** | COMMENT／閘一致性（反 U3 謊言） | **pass** | U3 F-U3-4 曾釘「COMMENT 謊稱雙閘」。現 COMMENT＝AST＋β 未做。 | **已修復路徑**；非新 finding |

---

## 三、Critic（還沒查什麼）

* features／models 執行期動態 SQL 組出 `prediction_values` 字串的**實例掃描**（非 AST）— 本輪未全 repo 動態追蹤
* `predict_asof` 以外是否仍有預測寫入入口走 app `DB_PARAMS`（僅抽樣釘死 `predict_asof.py:112`）
* β 下 ON CONFLICT／writer 自讀需求實證（未授權 β）
* arena／econ／提拔 HAC Eff-t／經濟價值 e2e（明確不在近程 R5；未跑）
* Dividend 半同步表一致性與 PK 修復終態（API 凍結下 SKIP）
* advisor 對外 UI 文案 live 字串 vs DB 門狀態（僅靜態讀 `prompt.py`）
* 10-14 復審項與 R5 交互（R2 域；本輪未重開）

---

## 四、Synthesize（呈核）

### 結論句

R5 **近程**（wiring＋PV-α＋哨兵＋U5）在 A1–A10 意義上**可宣告階段 DONE**——**前提**：Steward 採納本呈核，且對外敘事嚴格＝「隔離／輸出契約／predict runtime 近程閉合」，**不是**「確立級／可交易／universe→econ 全綠」。

`evaluated_pass=0` → **禁確立級數字**；G-PV-1 **none＝α 已落地**，**≠** β GRANT 收斂；API **仍凍結**。

### gap_class 建議（本輪）

| ID | 建議 | 理由 |
|---|---|---|
| G-ISO-2 | **維持 none** | S3 再親驗 live |
| G-PV-1 | **維持 none**（α） | 誤讀風險入 U5／COMMENT；不升 conflict |
| G-OUT-1 | **維持 none** | `--verify` 再綠 |
| G-OUT-2 | **維持 doc-only** | 不對稱知情 |
| G-DIV-1／G-CAT-1 | **維持 partial** | 非 R5 近程閉合條件；凍結下未修 |

### 可否「全量 R5 DONE」？

| 語義 | 可否 |
|---|---|
| 計畫 §7 近程 DONE（A*） | **可呈核 YES**（S3＋本 U5） |
| 路線圖大標「預測半系統 universe→model→econ 可驗」 | **NO** — 另開執行工單 |
| 確立級／可交易行銷 | **NO** — pass＝0＋U5 停手句 |

### 建議處置（執行層、零 [N]）

1. 路線圖／帳本／R5 計畫：標 **S3 CLOSED＋U5 DONE**；近程 R5 DONE（若 Steward 點頭）
2. 刷計畫 § 現況表舊 as-of（F-U5-6）
3. 維持 API 凍結；Dividend 進程勿私自重啟
4. β／econ／首個 pass 門 → 另授權，不塞進本 DONE 敘事
