# augur 抓取最佳化設計方案 — catalog-driven 計畫式 sync（限流內最少 token + 最快 + 保留對帳）

**性質**：純設計計畫（**不動 code、先評估**）。clean-room（#16/#17）：只依 5 治權檔 + `docs/datasets_zh.md`（本 session 實證 catalog）+ live API 事實。
**目標**：在 FinMind 限流內，用**最少 API 呼叫**、**最快完成**全市場全史 sync，**保留對帳**（降為輕量 attestation，守 #7 不歸零）。
**緣由**：6/24 token 到期前須抓完 sponsor 資料；現行 adaptive-probing 有可省的 overhead 與次優模式。

---

## 0. 結論先講（#15）
- **最少 token + 最快（限流內）**：✅ 做得到，`datasets_zh.md` 是關鍵 enabler。**最大單筆省下＝季/月頻表改 by-date**（財報每表 ~3100 calls → ~140 calls）。
- **對帳**：保留，但從「每表重對帳」降為「**(a) sync 批次自證 + (b) 抽樣 attestation + (c) 排除已知修訂窗**」，呼叫大減、仍守 #7。
- **不可逾邊界（#26）**：所有省 token 只作用「模式/範圍/排程」；**絕不**為省呼叫砍資料誠實（三敵零容忍）。

---

## 1. 核心構想：計畫式（planned）取代 探測式（adaptive-probing）

| | 現行（adaptive） | 本方案（planned + adaptive fallback） |
|---|---|---|
| 決定抓法 | 每表 probe（寬窗分類 + canonical 2330 + by-date 試 ≈ 7 calls/表）| **讀 `datasets_zh.md` 的 🔌 模式 + 📅 範圍 + data_id 來源**，0 probe |
| 模式選擇 | canonical 2330 通就 per-stock（不管是否次優）| **逐表選呼叫最少模式**（見 §2）|
| 退路 | — | planned 模式回非預期 → 退回 adaptive probe（穩健不脆） |

→ 省下探測 overhead ≈ **7 × 83 ≈ 580 calls**；更重要是讓「模式選擇」可全域最佳化。

---

## 2. ⭐ 最少 token：逐表選「呼叫最少」的抓取模式

**決策規則**（每表取 min）：
```
per-stock 模式呼叫 ≈ N_stocks（≈3100，逐股各 1 call 拿全史）
by-date  模式呼叫 ≈ N_distinct_dates（由 📅 最早日期 × 頻率 推算）
by-dim-id 模式呼叫 ≈ N_dimension_ids（各 1 call，總經/契約）
→ 選最小者
```
`N_distinct_dates` 由 catalog 的 **📅 最早日期 + 資料頻率** 算出：

| 頻率 | N_dates（最早→今） | vs per-stock 3100 | 最優模式 |
|---|---|---|---|
| **季頻**（財報三表）| ~140（35 年×4）| **140 ≪ 3100** | **by-date（大省）** |
| **月頻**（月營收）| ~290（24 年×12）| 290 < 3100 | **by-date** |
| 日頻・長史（Price 1994）| ~7800 交易日 | 3100 < 7800 | per-stock |
| 日頻・短史（2020 後新表）| ~1500 | 1500 < 3100 | by-date |

**最大省 token 點（catalog 才看得出）**：
- **財報三表（BalanceSheet/FinancialStatements/CashFlow）：per-stock ~3100 → by-date ~140 calls/表**。3 表省 ~**8,900 calls**。
- **月營收**：~3100 → ~290，省 ~**2,800 calls**。
- 同理檢視每張 per-stock 表，凡 `N_dates < N_stocks` 即改 by-date。

> ⚠️ 正確性前提：by-date 對 per-stock 表須 **roster-scoped**（只留 roster 內 stock_id、排除權證）——此修正**已在 `reconcile.py` 且落地端 sync 須一致**；季頻 by-date 須用「報表期別日」當查詢日（FinMind 該欄即季底日）。

**其他省點**：
- canonical 2330 探測結果**重用**（免 walk 時重抓 2330，~per-stock 表數）。
- 已落地表用 catalog 的 📅 + DB `max(date)` 只抓**增量**（resume，免重walk；但見 §6 增量用 by-date 更省）。
- 排除 augur 不抓的 real-time/OUT_OF_UNIT（catalog 已標）。

**推估總省**：探測 580 + 季月頻改 by-date ~12k + 2330 重用 ~數十 → **~13k+ calls**（占全 sync 數萬呼叫的 ~20-25%）。

---

## 3. 最快（限流內）：受 6000/hr 封頂下的最優

- **瓶頸是限流、非程式**：start rate 受 `_pace`（~1/0.8s）+ `_quota_gate`（≤5800 暫停）鎖死；16 並發只重疊在途請求、不提高發送率（IP 對外速率不變，#24）。
- **「最快」= 最少呼叫 × 最高安全速率**：§2 砍呼叫 → 同速率下**更快完成**（wall-clock 正比於呼叫數）。
- **速率調校（#27 可控逼近，授權後）**：以 production 當 sustained 載具，逐級試 `0.8s→0.7s→…` 持續性驗證；崩即退一級。**不被單次觀測錨定**，但重覆驗證才入操作值。
- **不可硬衝**：見 throttle 訊號即停（#25）；重試風暴=惡化路徑（#24）。故「最快」有硬上限，非無限快。

---

## 4. 對帳（保留、降本）：三層輕量化

**保留 #7 不歸零**（命根：DB↔API 無幻像），但從「每表重抓近窗對帳」降為：

1. **sync 批次自證（最省）**：by-date 抓取時 API 批次**留在記憶體**，直接與落地 DB 列逐 byte 比 → 證「落地忠實」**免重抓**。涵蓋大多 by-date 表的近期。
2. **抽樣 attestation（全史）**：`reconcile_audit` 改為**隨機抽樣**（抽 K 個 (表,日/股) 樣本重抓比對）→ 統計性鐵證，呼叫遠少於逐日全對。樣本失敗才擴大查。
3. **排除已知修訂窗（免假 FAIL/免白抓）**：catalog/記憶已記——PriceAdj 回溯重算、財報最新季未定案、法人 by-date 落後 1-2 日 → 對帳**排除這些不穩窗**，不浪費呼叫、不誤殺。

> 取捨誠實（#15）：抽樣 attestation 是**統計覆蓋非 100% 逐列**——換來大幅省呼叫；樣本量 K 與信心水準須訂（建議分層抽樣：每表抽幾個定案日 + 隨機股）。

---

## 5. as-of 落地模型（讓「資料正確」可持續、且守 #8）

- **append-only / 首見即存**：歷史列 `ON CONFLICT DO NOTHING`（不被後續修訂覆蓋）→ 存的是「**當時可見的 as-of 值**」。
- **修訂另存 vintage**（選配）：若要追修訂，寫入 `*_vintage` 表（保留每次修訂 + 時戳），**不污染主表 as-of**。
- **效益**：(a) 歷史值穩定 → 不需「重對帳到最新」（那本來就是 #8 偷看未來）；(b) 對帳只需證「首見落地忠實」，不必追修訂；(c) anti-leakage 天然正確（建模用 as-of）。
- 對映 catalog 的 anti-leakage 欄（公告日 AnnouncementDate 等）作 as-of 錨。

---

## 6. 架構：三階段（plan → fetch → attest）

```
階段 P 計畫（純讀、0 API）
  讀 datasets_zh.md → 每表產出 fetch-plan：
    {mode, data_id 來源/清單, 日期範圍(📅→今 或 DB max(date)→今), 預估呼叫數}
  全表預估呼叫總和 → token 預算 vs 6/24 額度 → 排序（先抓 sponsor-only/大表）

階段 F 抓取（限流內，resume-safe）
  依 plan 執行最優模式；三層限速防護；增量走 DB max(date)
  planned 模式回非預期 → adaptive probe fallback（不脆）

階段 A 證明（輕量）
  by-date 批次自證（免重抓）+ 抽樣 attestation + 排除修訂窗
  失敗樣本 → 擴大重對該表
```

**token 預算估算（階段 P 即可算、0 API）**：Σ 每表 min(模式呼叫)。可在放量前就知道「能否在 6/24 前抓完」、該砍/該排序什麼。

---

## 7. 風險與防呆
| 風險 | 防呆 |
|---|---|
| catalog 模式/範圍**過時**（FinMind 改）| planned + **adaptive fallback**：回非預期即退回探測 |
| 季頻 by-date 漏報表期別 | 用報表期別日（FinMind date 欄）當查詢日 + 完整性抽查 |
| 抽樣 attestation 漏真錯 | 分層抽樣 + 失敗即擴大 + 關鍵表（價量/還原價）仍較密 |
| 速率逼近觸 throttle | #27 逐級、持續性驗證、見訊號即退一級 |
| as-of 改 ON CONFLICT 影響既有 upsert | 設計層先定：主表 as-of、修訂進 vintage；屬判準變更**須用戶核** |

---

## 8. 凌駕邊界（不可逾，#26）
- 省 token 只作用 **模式/範圍/排程/速率**；**絕不**砍對帳到零、絕不為省呼叫放鬆資料誠實。
- 對帳**降本≠取消**：#7 鐵證保留為抽樣 attestation。
- 改 as-of 模型 / 改對帳判準 = **決策層**，須用戶拍板；其餘（模式選擇/排程/重用）= 執行層可主導。

---

## 9. 落地步驟（分期；每步仍須用戶授權放量）
1. **階段 P 先做（0 API、零風險）**：寫 plan 產生器，輸出全表 fetch-plan + token 預算表 → 用戶過目「省多少、6/24 來不來得及」。
2. **小範圍試**（1-2 表，如財報改 by-date）：實測 by-date 季頻是否真省且 roster-scoped 對帳 PASS。
3. **全面放量**（授權後）：依 plan + 排序（sponsor-only/大表優先）跑；緊盯前段（#25）。
4. **attest**：抽樣 attestation 取代全對；as-of 模型（若採）先小表驗證。

> 本方案為**計畫**；任何 code 變更、放量、改判準前均依治權協議停下確認。
