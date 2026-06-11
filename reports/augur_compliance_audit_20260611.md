# augur 治權合規審查 (2026-06-11)

**範圍**：`src/augur/` 全 code（core / ingestion / features / universe / audit）+ `scripts/`，對照 5 治權檔（v1.4.0）。
**方法**：3 Explore agent 並行審查（raw / feature-universe / audit-scripts）+ 主審親自驗證關鍵 finding。
**誠實聲明（#15）**：findings 皆 `file:line` source-traceable；標明「agent 報」vs「主審已驗證」。

---

## 總體判定：**高度合規**

code 無實質違反 18 原則。findings 集中於「**v1.4.0 doctrine 已入憲、code 尚未落地**」+ 少數文件/運維細節，**非 code 邏輯違反**。三基石 #1 source-pure / #8 anti-leakage / #15 誠實 在 feature/universe/audit 嚴守。

| 層 | 評級 | 摘要 |
|---|---|---|
| **feature / universe**（builder/core_gate） | 範本級 ✓ | #1 純 API 數學轉換無補值、`np.isfinite` 濾掉算不出即缺列；#8 `WHERE date<=t`+`.shift(1)` 時點乾淨；#9 無硬編值（窗 5/20/60/120/252 為市場標準）；#10 純完整度 gate 無評分排名。**0 違反** |
| **audit / reconcile** | A+ ✓ | #7 byte 對帳 4 類 + 2026-06-11 三修嵌入（`_key`→`_norm`、roster-scoped、verdict incomplete、VARCHAR-date guard）；heal=重跑 sync 非 hand-patch（#1/#12）；extra_in_db 只報不刪。**0 違反** |
| **raw**（core/ingestion） | ~90% ✓ | #2 API 權威/#3 純通用無白名單/#4 intraday 守門/#5 型別/#6 冪等resume/#17 限速 + 標頭慣例全符合；唯 `OUT_OF_UNIT` 註解待同步 v1.4.0 |
| **scripts** | A / B | `daily_maintenance` 薄 CLI 典範；`full_market_sync` docstring 環境特定 |

---

## Findings（分級，已驗證）

### 中 — v1.4.0 doctrine → code 落地落差（系統性，呼應待辦 (b)）

1. **`ingest.py:28-32` `OUT_OF_UNIT` 註解仍舊語意**〔主審已驗證〕：寫「低於/外於系統『個股 × 日』單位 → 不收 raw」「無法不空抓地可靠抓」——v1.4.0 已把 `OUT_OF_UNIT` 重定義為「**規模物理不可行之 operational 暫緩**（非資料維度排除）」。code 排除這三個（券商分點/權證/鉅額）邏輯**仍正確**（確因規模），唯「為何排除」的理由註解需改。
2. **`sync.py` by-維度-id 通用多維度抓取未實裝**〔agent 報，主審認同〕：v1.4.0 #18 新增「需特殊維度 id → 補通用多維度抓取」，sync 目前僅 market/per-stock/by-date 三模式；canonical-probe 用 `full_start=1990` 死點未修（News/DividendResult 誤判為 not-by-date-capable）。**這是 augur 真正抓進總經/衍生品/外股/商品資料的關鍵**。
3. **`full_market_sync.py:10` docstring「macOS caffeinate」環境特定**〔主審已驗證〕：augur 跨機（WSL2/雲機）不通用，應改通用「需主機不睡眠（依環境設電源）」。

### 低 — 計畫中 / 運維

4. **audit 五鏡 #11 未實作**〔agent 報〕：訓練前特徵稽核（IC/sign/共線/leave-one-out/SHAP/purged-CV），憲章 PHASE 9。F2 後待補、非現在路徑——誠實標明非遺漏。
5. **`full_market_sync` 無內部定時 heartbeat watchdog**〔agent 疑慮〕：靠外部 monitor + DB-driven resume；#21 報告為「每 dataset 完成」非「每 5 分鐘定時」。功能足夠、非違反。

---

## 核心洞察

**唯一系統性落差 = v1.4.0 doctrine 已入憲、code 未落地**（findings 1-3）。其餘為計畫中功能（五鏡 #11）或運維細節。code 本體高度紀律化——feature/universe/audit 達範本水準，raw 管線僅差 v1.4.0 註解同步。

## 建議（待用戶授權，不擅自 commit/改 doctrine）

- **護欄內可立即做**（純文件/註解、可逆、不需 API）：finding 1（`OUT_OF_UNIT` 註解同步 v1.4.0）+ finding 3（`full_market_sync` docstring 通用化）。
- **需 API 護欄**：finding 2（by-維度-id 抓取 + canonical 死點修）——code 可寫，但驗證需 API 探測放量。
- **F3 後**：finding 4（五鏡 #11，PHASE 9）。
