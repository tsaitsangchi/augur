# SIGN-B 首批落帳：兩現役符號一致性（2026-08-01 14:55）

> 登錄冊 A1；授權鏈＝SIGN-B-go 判式簽核（2026-07-28）＋Steward 2026-07-31「要回頭補」
> （射程 all_active）。執行＝`verify_sign_consistency.py --run --record
> --features inst_cumflow_position_120d,lending_fee_rate_mean_20d`（h=20,60 提拔漏斗口徑）。

## stdout 全文

```
═══ 符號一致性檢查(SIGN-B;判式=點估計+5 bootstrap 全同號==map.direction)═══
  --record:判定將落帳 feature_sign_check(每個 h 一列)
同尺同窗:as-of panels=102(2018-01-31..2026-06-30);h=[20, 60]
  ✓ inst_cumflow_position_120d: PASS(map.direction=+1) h20:PASS(IC均值+0.0095,n=102) h60:PASS(IC均值+0.0331,n=100)
  ✓ lending_fee_rate_mean_20d: PASS(map.direction=-1) h20:PASS(IC均值-0.0755,n=22) h60:PASS(IC均值-0.0831,n=20)

合計:PASS 2/FAIL 0/不可判 0(不可判=人閘,非通過;全 h 同 PASS 才過=保守,落註)
```

## 落帳驗收

`feature_sign_check` 恰 4 列（2 特徵 × h∈{20,60}）、verdict 全 PASS、附 n_panels 與 code_sha。

## 對裁決之影響（誠實更新，見呈案單 A2/A4 項補註）

mean_20d 之**符號證據現為 PASS**（IC 負向與 map.direction=−1 一致、5 bootstrap 全同號）
——呈案單原「三重依據」（FAIL 帳＋零符號證據＋語意不可考）**去掉一腳**。
殘餘除役依據＝run 20 G-PROM FAIL（seed 不穩定）＋**語意不可考/零產生器（無法續建新 panel）**。
後者獨立成立：符號再一致，下一個 panel 起就是空值。裁決仍屬 Steward。
