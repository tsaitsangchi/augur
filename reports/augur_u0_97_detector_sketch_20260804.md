# U0-97｜全 PK 值欄偵測器設計草圖（prep only · 2026-08-04）

> **位階**：[I]。**依據**：U0-STRUCT＝**俟偵測器｜不登**；W2-6／Q-R7；抽樣 binding 97＝B1（機械值欄＝0）。  
> **硬界**：本輪只設計／fixture 草圖；**不**實作入庫、**不**改 production detector、零 Registry。

---

## 1. 問題（親證敘事）

`TaiwanFuturesDaily`：catalog／實體 **13／13 欄入 PK** → 現行「非 PK＝值欄」啟發式 → **值欄數＝0**，但事實載體存在：

| 角色 | 欄 |
|---|---|
| **鍵** | `futures_id`,`contract_date`,`date`,`trading_session` |
| **事實載體（9）** | `open`,`max`,`min`,`close`,`settlement_price`,`spread`,`spread_per`,`volume`,`open_interest` |

同型母體至少 10 條（抽樣 W2-6）——修 detector 應泛化，非只 hardcode 97。

---

## 2. 函式草圖（擬）

```text
enumerate_value_columns(binding_row, live_cols, pk_cols) -> list[str]
```

**規則草案（須 #35 先驗紅）**：

1. 若 `len(live_cols - pk_cols) > 0` → 維持現行：非 PK＝值欄。  
2. 若 **全欄 ∈ PK**（B1）：改走 **carrier 覆寫**：  
   - 來源 A：`column_catalog` 中文名／`inferred_type` 標為量價／量能者；  
   - 來源 B：顯式 allowlist 表（**資料住 DB**，禁 Python 寫死長表——CLAUDE #29(b)；種子可一次性 migrate）；  
   - 來源 C：鍵名啟發式（`*_id`／`date`／`session`／`contract*` → 鍵；其餘 → 候選載體）——僅輔助，須 fixture 雙向。  
3. 回傳載體欄；**0 載體且全 PK** → 誠實 `undetectable`（不假綠自動配對）。

---

## 3. Fixture 草圖（#35）

| 臂 | 輸入 | 期望 |
|---|---|---|
| 綠 · 97 型 | 13 欄全 PK＋9 載體名 | 回 9 載體；非空 |
| 紅 · 真全鍵 | 僅 id／date 類全 PK、無量價名 | `undetectable` 或空＋旗標；**不得**假配對 True |
| 綠 · 常態 | 非全 PK 表 | 與舊啟發式一致（回歸不漂） |

**凡新鎖必先驗紅**（弄壞 carrier 規則 → 綠臂變紅）。本輪**不**落地測試碼。

---

## 4. 偵後 map 選項紙（不預勾）

```text
U0-97-DETECT-DONE: map=<提案或否>
```

或終局：

```text
U0-97: 不登
```

若登 → 另句 `REGISTRY-GO`＋honesty（STRUCT 未授）。

---

## 5. Prep checklist

| # | 項 | 狀態 |
|---|---|---|
| 1 | 偵測器設計（全 PK 仍標 9 載體） | ✅ 本檔 §2 |
| 2 | 紅／綠 fixture 草圖 | ✅ 本檔 §3（未寫碼） |
| 3 | 偵後 map 選項紙 | ✅ 本檔 §4 |
| 4 | 實作＋先驗紅＋Steward 裁 | ☐ 另授 |
| 5 | REGISTRY／不登終局 | ☐ 待人 |

---

*完。俟偵測器備料；零寫庫。*
