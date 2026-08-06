# KH #1b D-Answer 地板＋#2 錯料可見 — EXECUTED 2026-08-06

```text
KH-1b-1B2-SAMPLE-executed | FZ/GATE-keep | stub-llm | no-DB-mutation
# 同步於 #1e 後；計畫 §4 #1b／#2
```

## #1b（D-Answer 地板 · stub）

| 案 | 設定 | 期望 | 結果 |
|---|---|---|---|
| A | admin／讀出錨題 | hit 277948、有 readout、非 NO_K、guard | ✅ |
| B | deny scope／同題 | 誠實 `知識庫中無此內容`、無 cite | ✅ |
| C | admin／RMAN 路徑問 | hit 277948、compact、非 NO_K | ✅ |
| D | admin／「什麼是知行合一」 | **不得**掛假錨 277948 | ✅ |

`1B_ALL_OK`

## #2（錯料可修正可見 · 不寫庫）

| 項 | 內容 |
|---|---|
| 錨 | `item_id=277948` · `knowledge_item_text` 可 UPDATE |
| 程序 | 人改一句 content → 再跑 Q1／Q4 → cite／答應反映新文；可回滾 |
| 本帳 | **未**對庫執行 UPDATE（no-DB-mutation）；只釘入口＋程序 |

## 計畫

- §4 **#1b** → ✅ 抽測帳  
- §4 **#2** → ✅ 程序釘住（人實改另次回合）  
- K-02b／K-07 運維抽樣可續，非 blocker  

*executed。*
