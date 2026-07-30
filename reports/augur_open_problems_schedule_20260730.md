# 全專案開放問題總表×最佳化解決行程（2026-07-30 10:30）——列畢即自動執行

> [I] hugo「所有問題詳細列出＋最佳化自排行程＋自動執行」。問題全數今日親驗現況；行程按「事件驅動優先、零車道即時做、重活排隊」最佳化。

## 一、開放問題全表（P=問題、D=債、R=風險；含現況證據）

| # | 類 | 問題 | 現況 | 解 |
|---|---|---|---|---|
| P1 | R | **behavior INVALID 再發風險**：LANE-GOV 後首輪未落，若仍有題超 1200s（無爭道下）→ A′ 再卡 | valid run=0、round1 ~14:00 落 | 事件批①：落地即判——VALID→A′ 鏈；INVALID→**T-RETRY 裁決包**即呈（題級重試=換尺、對照臂重跑便宜） |
| P2 | P | **R3 外隊發布日未親驗**：3 面 TSFM replay 門懸空不可評 | 門 approved、無資料 | **即時批：web 親驗 HF model card**（本檔執行段） |
| P3 | D | staging 殘留已促升 lending_rate 列（雙住所） | staging 17,072×2 | 即時批：清 rate_mean（促升畢）；**留 vw**（未促升候選） |
| P4 | D | 孤 panel 補全未驗（nohup 撞 FV-GUARD） | **已驗完整**（2,848 股＞鄰枚）✓ | 已結 |
| P5 | P | **INTERACT wave-2 未跑**：7 顆有值有向、四關未過（(b) 差 1 的主路徑） | 車道滿 | 事件批②：own_daily 或 M2 先收者讓道即跑（工具零改、覆蓋對齊已內建） |
| P6 | R | **M2 月頻成本未證**：快取後單 cutoff 成本未實測 | 掃中 | 監看批：首 5 cutoff 節奏>15min/枚→改季頻先行 |
| P7 | D | 門評可判性顯示層 estimand-盲（誤示 OOS=0） | 化妝債 | 低批：判器檔非急務不動，記錄於此 |
| P8 | D | eval_local_model 進度 flush（hash 內不可輕改） | -u 已繞 | 低批：僅在下次合法換尺時捎帶 |
| P9 | P | INTEG-H2：513 pending 題未接線 | LLM 道長期被佔 | 事件批③：A′ 批後排入 llama 道 |
| P10 | R | SUNSET (a) 日曆風險：live 60 clusters ≈ 10 月底才到 | 2/60 | 無人為槓桿（replay 不得餵 live 門）；如實陳列 |
| P11 | D | 教訓未固化記憶（尺陷阱 6 連發、便宜尺寸先行) | 本檔執行段 | 即時批：2 則記憶落檔 |
| P12 | P | advisor guard_pass 接線（chip 舊案） | hugo 側 chip | 積壓不阻塞 |
| P13 | D | HANDOFF.md 未涵本週（跨機 SSOT 舊化） | 並行 session 常改 | 低批：週末封存時一併 |

## 二、最佳化行程（三批制）

**即時批（現在、零車道，本 turn 執行）**：P2 web 親驗 → P3 staging 清理 → P11 記憶固化 → 本檔封存。
**事件批（通知驅動）**：①behavior round1 落（~14:00）→ VALID 則 A′ 鏈全放（接力報告→三件包→round2 確認複現）／INVALID 則 T-RETRY 裁決包；②own_daily／M2 先收者→讓道跑 wave-2（P5）→ 存活者促升呈簽＝(b) 達標路徑；③A′ 批後→INTEG-H2 接線（P9）＋own_daily 門＋W2 十年判讀。
**監看批**：M2 節奏（P6，首 5 cutoff）；08-03 live 批二（W2-a 預案凍結待觸發）。

## 三、即時批執行記錄（同檔補記）

- P4 已結（完整性 2,848 股實證）。
- P2／P3／P11 執行結果見 commit 與下方補記。

## 補記：即時批執行完畢（同日）

- **P2 ✅**：三隊發布日 web 親驗入 replay 計畫補記（合法窗全足 60+ clusters；R3 排事件批）。
- **P3 ✅**：staging 清 `lending_fee_rate_mean_20d` 17,072 列（vw 候選保留）。
- **P4 ✅**：孤 panel 完整性實證（2,848 股＞鄰枚；FV-GUARD 撞擊僅尾端重複 upsert）。
- **P11 ✅**：兩則教訓記憶落檔（同尺前置檢查表／便宜尺寸先行）。
