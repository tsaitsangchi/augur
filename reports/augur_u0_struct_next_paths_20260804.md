# U0-STRUCT｜37／80／97 俟下機械備料路徑（2026-08-04）

> **位階**：[I] 備料 checklist。**依據**：`audits/U0-STRUCT-378097-20260804.md`。  
> **硬界（80／97）**：僅 prep／設計／唯讀探針；**零** Registry INSERT／UPDATE／honesty／COMMIT，除非另收 go。  
> **37**：jp-ok unlocked → REGISTRY-GO 已由 SYNC4 **EXECUTED**（見下表）；殘＝`Adj_Close` 第二通道。

---

## 總覽

| binding | 鍵 | 主狀態 | 可先做（prep） | 須 Steward go 才動 |
|---:|---|---|---|---|
| **37** | `jp.daily_bar` | **EXECUTED**｜jp-ok unlocked | —（殘：`Adj_Close` 第二通道） | ✅ REGISTRY-GO 已消費（SYNC4） |
| **80** | `tw.corporate_action.split` | 俟拆｜出口登事件欄 | 第二 binding 欄位切分設計；事件欄 vs 漲跌停參考態 | 拆綁定確認 → `登事件欄`＋`REGISTRY-GO` |
| **97** | `tw.futures.daily_bar` | 俟偵測器｜出口不登／再裁 | 全 PK 表值欄偵測器設計／fixture | 偵後 map 裁 **或** `不登`；登才 `REGISTRY-GO` |

---

## 37 · `jp.daily_bar`（JapanStockPrice）

**允許（俟下）**

- [x] 整理 observation 欄：`Open,High,Low,Close,Volume` vs **出欄** `Adj_Close`（W2-3／WM.15 衍生）→ `reports/augur_u0_37_jp_ok_checklist_20260804.md`
- [x] 草擬第二 binding／derived 通道註記（文件／dry SQL **ROLLBACK only**，不 COMMIT）
- [x] Q-R8 命名空間／跨市場軸一句呈案（供 Steward `jp-ok`）

**出口／寫庫狀態**

- [x] Steward：`Q-R8=jp-ok` → **unlocked**（`audits/U0-37-JP-OK-20260804.md` @11:23+08）
- [x] dry SQL（W2 form；observation 已知欄；`ROLLBACK`）→ unlock §4＋`audits/U0-37-DRY-SQL-20260804.md`
- [x] `REGISTRY-GO: binding=37 + honesty=37 + decided_by=hugo` → **EXECUTED**（`audits/U0-37-REGISTRY-EXECUTED-20260804.md` @11:34+08；honesty 已消費）

**殘（非本批）**

- [ ] `Adj_Close` 第二 binding／derived 鍵（人裁）

---

## 80 · `tw.corporate_action.split`（TaiwanStockSplitPrice）

**允許（俟下）**

- [x] 事件欄切分草案：**入** `before_price,after_price,type`；**出／第二概念** `max_price,min_price,open_price`（A.26／W2-5）→ `reports/augur_u0_80_split_binding_sketch_20260804.md`
- [x] 第二 binding 角色命名與 `channel_role` 建議（文件層）
- [x] 與既有 `tw.corporate_action.ex_dividend` 平行敘事對齊（不寫庫）

**須 go**

- [ ] 拆第二 binding **綁定裁示**（人確認 id／角色）
- [ ] **登事件欄**＋未來 `REGISTRY-GO`（**非今日**）

---

## 97 · `tw.futures.daily_bar`（TaiwanFuturesDaily）

**允許（俟下）**

- [x] 偵測器設計：全欄 PK 時仍能標出事實載體 9 欄（close／OHLC／settlement／spread／volume／OI…）→ `reports/augur_u0_97_detector_sketch_20260804.md`
- [x] 紅／綠 fixture（#35：先驗紅；餵真 PK 表型）— **草圖**；未寫碼
- [x] 偵後 map 選項紙（登／維持俟／不登）— **不預勾**

**須 go**

- [ ] 偵測完成後 Steward 裁 map，**或**終局 `U0-97: 不登`
- [ ] 若登 → 另句 `REGISTRY-GO`＋honesty（未授）

---

## 平行不阻塞

A1 監看／P1-DRIFT 呈案／G3／HANDOFF 刷新——與本備料互不搶 Registry COMMIT。

---

*完。37＝EXECUTED；80／97 仍 prep／俟 go。*
