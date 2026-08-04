# U0-80｜`tw.corporate_action.split` 拆 binding 設計草圖（prep only · 2026-08-04）

> **位階**：[I]。**依據**：U0-STRUCT＝**俟拆｜登事件欄**；抽樣 W2-5／A.21／A.26。  
> **硬界**：今日**不**登事件欄、**不** `REGISTRY-GO`、零 `world_*` 寫入。

---

## 1. 同表兩世界概念

| 概念 | 錨 | 建議欄 | binding |
|---|---|---|---|
| **分割事件** | A.21；ts＝恢復買賣日（catalog「分割恢復買賣日」） | `before_price`,`after_price`,`type` | **80**（既有提案鍵 `tw.corporate_action.split`） |
| **漲跌停／參考態** | A.26 PriceLimit 另一狀態 | `max_price`,`min_price`,`open_price` | **第二 binding**（新 id；人裁後才建） |

平行敘事：既有 `tw.corporate_action.ex_dividend`＝公司行動事件軸；80＝同軸之 split 事件列。

---

## 2. 第二 binding 草圖（文件層）

| 欄 | 建議值（草案，未裁） |
|---|---|
| `source_table` | `TaiwanStockSplitPrice`（同表） |
| `concept_key` | 待裁：`tw.price_limit.ref_state` 或等價（**不預勾**） |
| `channel_role` | 建議 `observation`（參考態觀測；非 derived） |
| `source_column` | 多欄形制 → 共病 **W2-1**（與 7／65 同形；寫庫前須形制裁） |
| `mapping_status` | 未來才 `mapped` |

建議角色標籤（STRUCT 模板曾用）：`role=price_limit_ref`。

---

## 3. 後續 go（人裁；AI 不代勾）

```text
U0-80-SPLIT-BOUND: second_binding=<id> + role=price_limit_ref
U0-80-REGISTER: 登事件欄 + REGISTRY-GO: binding=80[,<id>] + honesty=80 + decided_by=hugo
```

可合併為一句，須 Steward 明示。

---

## 4. Prep checklist

| # | 項 | 狀態 |
|---|---|---|
| 1 | 事件欄 vs 漲跌停欄切分 | ✅ 本檔 §1 |
| 2 | 第二 binding 角色／`channel_role` 建議 | ✅ 本檔 §2 |
| 3 | 與 `ex_dividend` 平行敘事 | ✅ 本檔 §1 |
| 4 | 拆綁定確認（id／角色） | ☐ 待人 |
| 5 | 登事件欄＋REGISTRY-GO | ☐ 非今日 |

---

*完。俟拆備料；零寫庫。*
