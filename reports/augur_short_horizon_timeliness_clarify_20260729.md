# 短 horizon 時效性複核／日曆日 vs 交易日釐清（2026-07-29）

**性質**：[I] 釐清／時效複核報告（#16）｜ **非**全量訓練完成宣稱｜ **不**改治權判準／[N]  
**動因**：hugo「開賽後 AI 先做時效性複核再拍」（HANDOFF §4.5 #2）；同日用戶授權「所有 working 開始跑」——本檔只釐清短 horizon 殘留拍板點，**不**自行開全量 `train_ranker --run`。  
**守**：#9/#10/#15 真兆（DB 唯讀＋既有報告）· 預測↔API 正交（庫內 as-of；**零** FinMind／FRED）· FREEZE≠禁預測  
**讀序**：原計畫 → 裁決 → 結案釐清 → 本檔；HANDOFF §1 活躍計畫②標籤見 §5（**過期**）。

---

## 0. 三十秒裁決（複核結論）

| 問 | 答 |
|---|---|
| 「30/60 天」該用日曆還是交易日？ | **對用戶說法採日曆日語意**；**模型單位一律交易日**。建議正式釘：**P30←H20**（≈29 日曆日）、**P60←H40**（≈58 日曆日）。 |
| 既有 **H60** 是什麼？ | **60 交易日** ≈ **87 日曆日（~3 個月）**——**不是**「60 日曆日」。主欄相對強弱／部署主戰場仍是 H60；短 horizon 矩陣是 **旁支對照**，不取代 H60。 |
| 原計畫 W1–W5 還要重做嗎？ | **否**。`augur_short_horizon_plan_closure_20260711.md` 已建議結案；庫內 artifact／ledger／機率層仍在（as-of **2026-05-31**）。 |
| HANDOFF「未執行、待拍板＋釐清」？ | **標籤過期**。待拍的是：**正式認可日曆對映**＋是否做 **as-of 前推**（見 §6）；不是「從頭訓練」。 |
| 要不要立刻開某個 train slice？ | **不建議立刻全量／H20·H40 重訓**。可選最小下一步＝**HANDOFF 標籤更正**＋（另令）`core_universe`→`predict_asof` @ G1-PIN，**仍非**重跑四關。 |

---

## 1. 日曆日 vs 交易日（建議正式釘死）

### 1.1 單位 SSOT（code 已定、非待發明）

- `walkforward`／`train_ranker --horizon`：**horizon＝交易日**（`scripts/train_ranker.py` 說明；embargo＝`h + 62` 交易日）。
- 近似換算（計畫／裁決沿用）：**1 交易日 ≈ 1.45 日曆日**（台股）。

### 1.2 對映表（建議拍板採納——與顧問 `prob_note` 已落地一致）

| 用戶說法（日曆語意） | 建議 horizon | ≈日曆日（DB `calendar_days`） | 與「交易日字面」 |
|---|---|---|---|
| 「未來約 30 天」 | **H20** | **29** | 若硬解成 30 **交易日**→無現役模型；不建議另開 H30 |
| 「未來約 60 天」 | **H40** | **58** | 若硬解成 60 **交易日**→那是 **H60**（≈87 日曆日）——**語意錯位** |
| （既有主戰場） | **H60** | **87** | 「約一季／三個月」量級，勿稱「60 天」 |
| （較長對照） | **H120** | **174** | 顧問 P120；偏差大、須明示 |

**建議拍板句（擇一即可）**：

> **SH-CAL-yes**：用戶「30／60 天」＝**日曆日語意**；系統對映 **P30←H20、P60←H40**；**H60＝60 交易日≈87 日曆日**，不作「60 天」答覆主欄。單位 SSOT＝交易日。不新開 H30。

**對偶否決句（不建議）**：

> ~~SH-CAL-td：用戶「30／60 天」＝交易日 → 則對映 H30（不存在）／H60~~ ——與已上線機率附欄、裁決報告、結案釐清衝突，且會把「60 天」誤綁到 ~3 個月的 H60。

### 1.3 為何不是「重釐清未知」

原計畫 §1（2026-07-09）已列同一張對映表並把「日曆 vs 交易日」列為拍板前確認。之後：

- 裁決報告表頭已寫死單位＝交易日＋日曆近似；
- 顧問 `payload.py` 固定用語：`P30←H20 ≈29 日曆日…dead`／`P60←H40 ≈58…thin_unestablished`；
- 結案釐清（2026-07-11）視 W5 已被機率層升級取代。

**殘留＝Steward 書面一句認可**，不是技術未定。

---

## 2. 與既有 H60 的關係

| 維度 | H60（主） | H20／H40（短 horizon 計畫） |
|---|---|---|
| 角色 | 部署主欄相對強弱；advisor 主排序欄 | 「30／60 天」誠實附欄／矩陣對照 |
| 經濟裁決（2026-05-31 矩陣） | 未確立（薄） | H20 **判死**；H40 **未確立（薄）** |
| 是否被短計畫「取代」 | **否** | 旁支；H60 仍獨立 |
| 用戶「60 天」 | **不應**直接回 H60 | **應**回 H40（日曆語意）＋ caveat |
| 重訓優先 | PME／prodset 熱路徑已另軌（n=2 等） | **不**因「working 開跑」自動重訓短 horizon |

誠實邊界不變：短 horizon **更弱**（H20 經濟判死；越長相對越不薄）——交付物是**可信度標籤**，不是可靠漲跌預言。

---

## 3. 時效性：計畫／HANDOFF／庫內現況（2026-07-29 親查）

### 3.1 文件時間線

| 日期 | 檔 | 狀態含義 |
|---|---|---|
| 07-09 | `augur_prediction_short_horizon_model_plan_20260709.md` | plan-first；待拍＋釐清單位 |
| 07-09 | `augur_short_horizon_verdict_20260709.md` | H20 死／H40·H60·H120 薄 |
| 07-11 | `augur_short_horizon_plan_closure_20260711.md` | **建議結案**（W1–W5 完成或被取代） |
| 07-12 | HANDOFF §4.5 #2 | 「開賽後時效複核再拍」← **本檔履行** |
| 07-24 | `PREDICT-ORTHOGONAL-RETROACTIVE-APPROVALS` #9 | 短 horizon 計畫 **追溯 yes（史料）**；結案建議已引 |
| 07-29 | **本檔** | 釐清單位＋HANDOFF 過期標籤＋最小下一步 |

### 3.2 庫內唯讀快照（本機 DB；零外部 API）

| 物件 | 現況 |
|---|---|
| `model_registry` RankRidge | H20／40／60／120 各 2（feats `ce62866b`／`3a4e66fa`）；H82×1 |
| `prediction_values` | 五 horizon × 339 列；**max panel＝2026-05-31**；in_portfolio≈33／horizon |
| `prediction_probability` | H20 `dead` cal=29；H40／60／82／120 `thin_unestablished` cal=58／87／119／174；panel **僅 2026-05-31** |
| `revalidation_ledger` | H20／40／60／120 有 B／D／R（H60 另有 C）；as_of **2026-05-31** |
| `trial_ledger` | H20／40／60／120 各 8 |
| `feature_values` | min 2007-12-31 → **max 2026-06-30**（36 panel 日）；@06-30 有特徵 |
| `core_universe_asof` | **max＝2026-05-31**（344 列）；**@2026-06-30＝0** |
| `arena_admission_gate` | `arena_adm_5305655ad1cd` **evaluated_pass**；G1-PIN **asof＝2026-06-30** |

**判讀**：短 horizon **訓練／驗證／機率 artifact 仍釘在 FREEZE 快照 2026-05-31**；arena／panel 特徵已到 **G1-PIN 2026-06-30**，但 **宇宙表未跟到 06-30** → 無法在不補 universe 的前提下，誠實宣稱「已用 G1-PIN 日出短 horizon 單」。

### 3.3 相對原 FREEZE 敘事的時效差

- 原計畫綁「只讀 as-of 2026-05-31」——**驗證矩陣仍正確可複現於該釘**。
- 系統其後：解凍→live 增量、arena G1-PIN 06-30、預測↔API 正交——**允許**庫內 as-of 前推預測，**不**等於必須重跑短 horizon 四關，也 **≠** 解凍 FinMind／FRED。
- 結案後未再要求「用更新 as-of 重判 H20／H40」——若要做，屬**新決策切片**（§6），不是原 W1–W5 未完成。

### 3.4 結案殘留（仍有效、非本複核阻斷）

承 closure §3：RankGBDT 未入 registry；H82 缺 B／D ledger；顧問 e2e 問答未在結案當日重測。本輪**未**重跑 live「2330 未來 30 天?」（#7 誠實）。

---

## 4. 可執行最小下一步（由窄到寬；皆零 API）

| 序 | 動作 | 何時 | 不做什麼 |
|---|---|---|---|
| **M0** | hugo 拍 **SH-CAL-yes**（§1.2）＋認可「計畫已結案／HANDOFF 改標」 | **現在** | 不改 [N]；不改裁決門檻 |
| **M1** | 拍板後改 HANDOFF §1 活躍計畫②＋§4.5 #2 為「已釐清／結案建議已採納」（機械文件） | M0 後 | 不順手開 train |
| **M2**（可選） | 建 `core_universe_asof` @ **2026-06-30**（或明示 live as-of）→ `predict_asof --horizon {20,40,60}` **只出候選分數** | 另令「SH-ASOF-REFRESH」 | **不**自動重跑 revalidate／deflation；**不**改 in_portfolio 部署 |
| **M3**（可選、較重） | 同 as-of 重跑 Stage B／D／R＋裁決報告刷新 | 僅當要「更新薄／死標籤」 | 預期 H20 仍死、H40 仍薄；**禁**確立級宣稱 |
| **禁** | 全量重訓當「working 開跑」預設；FinMind／FRED；把 H60 當「60 日曆日」 | — | — |

安全預設已確認：`python scripts/train_ranker.py --horizon 40`（無 `--run`）只印矩陣、不訓練。

---

## 5. HANDOFF 過期標籤（複核發現）

| 位置 | 現文 | 複核後應讀 |
|---|---|---|
| §1 活躍計畫② | 「**未執行、待拍板+釐清日曆日/交易日**」 | 執行鏈已完成（closure）；待＝**正式 SH-CAL**＋是否 as-of 前推 |
| §4.5 #2 | 時效複核再拍 | **本檔＝複核交付**；拍板點見 §6 |

**HANDOFF 已於 2026-07-29 Steward 拍板後改標**（`SH-CAL-yes`＋`SH-CLOSE-yes`；見 `audits/SH-CAL-CLOSE-APPROVED-20260729.md`）。

---

## 6. 拍板點清單（2026-07-29 更新）

1. ~~**SH-CAL-yes／no**~~ → **已採 `SH-CAL-yes`**（§1.2 日曆對映：P30←H20、P60←H40；H60≠「60 天」）。  
2. ~~**SH-CLOSE-yes／no**~~ → **已採 `SH-CLOSE-yes`**（closure 結案＋HANDOFF 改標）。  
3. **SH-ASOF-REFRESH-yes／no**——是否授權 M2？**本輪未拍（預設 no／延後）**。  
4. **SH-REVAL-yes／no**——是否授權 M3？**本輪未拍（預設 no）**。  
5. **SH-GBDT-REG-yes／no**——是否補 RankGBDT registry？**本輪未拍（預設 no）**。

**本輪已開**：決策切片 SH-CAL＋SH-CLOSE（文件／對映認可）。  
**本輪不開**：train／revalidate／as-of 前推（須另令）。

---

## 7. 拍板句建議（可直接貼回）

```
SH-CAL-yes + SH-CLOSE-yes + SH-ASOF-REFRESH-no + SH-REVAL-no + SH-GBDT-REG-no + FZ-keep
```

含義：認可日曆對映與結案；**暫不**前推 as-of、**不**重跑四關、**不**補 GBDT registry；FinMind／FRED **仍凍**。

若要 freshness：

```
SH-CAL-yes + SH-CLOSE-yes + SH-ASOF-REFRESH-yes（as-of=2026-06-30；僅 universe+predict；禁 reval／禁部署切換）+ FZ-keep
```

---

## 8. 證據索引（#9／#10）

| 來源 | 用途 |
|---|---|
| DB `model_registry`／`prediction_*`／`revalidation_ledger`／`feature_values`／`core_universe_asof`／`arena_admission_gate` | §3.2 現況 |
| `reports/augur_prediction_short_horizon_model_plan_20260709.md` | 原單位表＋W1–W5 |
| `reports/augur_short_horizon_verdict_20260709.md` | 經濟／DSR 矩陣 |
| `reports/augur_short_horizon_plan_closure_20260711.md` | 結案建議 |
| `audits/PREDICT-ORTHOGONAL-RETROACTIVE-APPROVALS-20260724.md` #9 | 追溯 yes（史料） |
| `src/augur/advisor/payload.py` P6 `prob_note` | 已落地 P30／P60 對映 |
| `scripts/revalidate.py` `B_HORIZONS`／`CD_HORIZONS` | 含 20／40 |
| `scripts/preregister_arena_admission_gate.py` `PIN_ASOF` | G1-PIN 2026-06-30 |

**未做**：全量 train、revalidate --run、FinMind／FRED、改 HANDOFF／治權檔、顧問 live e2e 複測。
