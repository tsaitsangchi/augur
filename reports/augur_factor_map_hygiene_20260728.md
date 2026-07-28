# principle_factor_map 衛生全掃（②′，2026-07-28）

> [I] 唯讀稽核（hugo「②′」核可）；77 列／39 distinct 特徵全查。發現三類，**零改動**——處置權全在你（fuel-line 人簽域），建議配 stanzas 同場清。

## 一、方向衝突（2 特徵；符號尺現判 UNJUDGEABLE fail-closed）

**共同點：兩案的反方都是 p116（AFML「迭代回饋／誤差修正」＝均值回歸代理）**——趨勢派 vs 均值回歸派的真學派分歧，非資料錯誤：

| 特徵 | 多數方 | 反方 | 經驗數據（參考） |
|---|---|---|---|
| `days_since_high_252d` | **−1 ×4**（p97 超跌買進／p78 距高點過遠反轉／p83 過度反應／p94 順勢突破） | **+1 ×1**（p116） | 表親 `days_since_high_126d` 今日實測 IC=−0.0487、HAC-t=−2.52 → **經驗支持 −1 多數方** |
| `range_position_120d` | **+1 ×3**（p93 盛衰循環／p91 孫子順勢／p77 週期位階） | **−1 ×1**（p116） | 未另測（要我補一筆同口徑 IC 供裁，一字即跑） |

**處置選項**（你裁）：(a) 保留兩派＝該特徵永遠過不了符號尺（誠實但 (b) 線少兩顆可用棋）；(b) 裁定正典方向＝親手刪除少數方 map 列（你簽的資料你有權刪）；(c) 只裁 `days_since_high_252d`（已有經驗證據）、`range_position_120d` 補測後再裁。

## 二、死鏈（3 特徵：map 有列、生產＋候選皆無值）

`macro_regime`／`peg_ratio`／`piotroski_fscore`——各 1 列，映到不存在的特徵（從未建成或已改名）。**留著無害但污染覆蓋統計**；處置＝你刪列或留待未來建成（建議註記即可，不急）。

## 三、窗口語意債＋待補列（接你的 stanzas 場）

- **已知債**：`lending_fee_rate_mean_30d` **非真 30d**（G-PROM-D2 報告記錄在案）——其 map 列方向沿用時**不得**直接等同新真窗 `_20d` 候選；
- **5 候選待補 map 列**（符號尺解鎖鍵，名字須逐字）：`lending_fee_rate_mean_20d`、`lending_fee_vw_mean_20d`、`days_since_high_126d`、`days_since_high_252d_raw`、`log1p_days_since_high_252d`——注意後三者若沿 `days_since_high_252d` 的方向，**先裁完 §一衝突**否則繼承歧義；
- 名帶窗 mapped 特徵共 23 顆（全在生產、清單存檔），除已知債外未見其他名實疑點（機械可查範圍內）。

## 四、覆蓋統計（今日快照）

39 distinct／77 列；37 列有 validated_ic＋validated_econ 值；**來自 hint 的列＝0**（10 則已核 hint 全數待 stanzas 策展入 map）；prodset active（1 顆）有 map 覆蓋 ✓。
