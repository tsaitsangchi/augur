# 解凍 A-2 牆前準備:修憲草案+證據債清單(2026-07-11 深夜;供 hugo 拍板用)

> **這份是什麼**:擂台計畫 A-2(解凍決策)的全部前置材料一頁式——修憲草案文本、7 筆證據債逐筆盤點
> (本輪已修 1 筆真回歸)、硬前置清單。**本檔全部是建議與草案,零效力;效力唯 hugo 拍板後生效。**

## 1. 修憲草案(as-of' 值由你填;AI 依 #19 跨檔一致執行)

拍板句式建議:「**解凍:as-of 凍結解除,轉 live 增量維運;新 as-of'=滾動(每日 sync 至最新交易日)**」。
須改四處(一處改、全鏈對齊):

| 檔 | 現文 | 草案 |
|---|---|---|
| 原則精華 L77(FREEZE 子條) | 「全系統以 as-of 2026-05-31 凍結快照為據…不追新資料、不為此掛排程」 | 「FREEZE(2026-05-31~2026-0X-XX)已解除〔解凍 GATE unfreeze_06dcb178267d evaluated_pass 為據〕;轉 **live 增量維運**:每日增量 sync+panel 續建為常態;FREEZE 期教訓與判準留檔」 |
| 原則精華 L74/76 | develop-on-frozen-snapshot 敘述 | 同步改為 live 維運敘述(daily_maintenance 槽位已存在) |
| 憲章 L132(預言機三不動②) | 「FREEZE as-of 2026-05-31 不動」 | 「資料期限依解凍後 live 維運;快照組成變更仍唯 freeze_manifest+決策層拍板」 |
| CLAUDE.md L26(工具層引用) | FREEZE 引用段 | 同步 |

程序要件:修憲 commit 時間須 **>2026-07-11 12:08:11**(gate approved_at;G1(b) 機械檢核)——已天然滿足。

## 2. 證據債 7 筆盤點(解凍 GATE 前置=--strict 全綠)

| 債 | 性質 | 處置建議 | 誰動 |
|---|---|---|---|
| ✅ E8_econ_verdict_bound | **真回歸,本輪已修**:`prediction_probability` 被發現只剩 h=82(P20/40/60/120 於昨日 H82 增訓時段消失,元兇無法完全回溯);已用既有 writer 重跑 emit 修復(5×339 列、econ_verdict 正確)→ **green** | 已完成 | AI(#26 自我糾錯) |
| E8_probability_frozen | 斷言基線過時:期望 count=339(單 horizon 時代),現實=1,695(5 horizons 合法擴充) | 更新斷言為 `count=1695 AND horizons=5`,**你確認後我改** | hugo 確認→AI |
| E9_judgestop_frozen | 斷言基線過時:期望 6 列,現實=11(R_robust 5 列係驗證總綱合法新增;frozen 9/11) | 更新斷言,同上 | hugo 確認→AI |
| E5_models_frozen_four | 斷言基線過時:期望 registry 4 模型,現實=15(方向軸 v1/v2 家族合法入籍) | 更新斷言(如「RankRidge 4 列凍結不變」),同上 | hugo 確認→AI |
| E1_raw_reconcile_exit | **真漂移**:raw 表已有越線資料(多表至 06-17/18,byte 對帳 vs 凍結快照必敗)——與擂台審查發現一致(含 PriceAdj 15 檔拼接損傷) | 併入 A-2:解凍後「06-01 起段重抓+損傷修復」為 sync 計畫一部分;或裁定越線段保留+manifest 留痕 | hugo 裁 |
| E2_macro_latent_debt(amber) | 已知債:宏觀延遲,reader 已封門,Tier A 重 sync=解凍後動作 | 解凍即自然清償路徑開啟;或人裁除名 | hugo 裁 |
| E5_survivorship_debt | 已知債:解凍後以真 PIT 名單重估 | 同上 | hugo 裁 |
| E7_h60_ece_outlier(amber) | 非紅(過 Brier 基線);待 V1 判讀 | 人裁定級 | hugo 裁 |

**結論**:7 筆中 3 筆=過時斷言(你一句話我就更新)、3 筆=解凍本身即清償路徑(A-2 併裁)、1 筆=人裁定級。
**無一是「未知的壞」**——全部有名有姓有處置路徑。

## 3. A-2 拍板時的完整 checklist

1. 修憲句拍板(§1 草案;as-of'=滾動 or 固定日,你選)
2. **FinMind sponsor 續訂**(已過期降 Free;standard 級即可覆蓋每日 ~20 requests)
3. 三筆過時斷言更新確認(§2)
4. 越線資料處置裁定(§2 E1;建議=06-01 起 PriceAdj 段重抓)
5. arena gate 預註冊時序裁定(prereg-at-A2;arena plan §1 門二)
6. (已備妥待用)解凍日執行鏈:修憲 commit → 分段 sync → build panels → `preregister_unfreeze_gate.py --evaluate --asof <日>`

## 4. A0 現況(本輪完成)

arena 4 表+3 防篡改 trigger(負向單測×3 全過)、8 候選註冊凍結(K 草案=6 門)、基線隊+自家隊合成冒煙
全過(零 DB 寫、零真實 p_up);市場隊(chronos/timesfm)套件安裝+權重下載+VRAM 實測進行中,結果
以 operational 事由如實記錄(塞不下 4GB=除名)。
