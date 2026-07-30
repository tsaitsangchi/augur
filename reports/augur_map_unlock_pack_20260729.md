# 解鎖加速包——15 列 map 草案（10 hint＋5 候選），逐列你核（2026-07-29）

> [I] 憲政定位：**草案非代填**——每列之 principle 掛鉤與 direction 由你逐列核可才落 DB（同 P2／白名單先例：我出草案、你核）。所有 principle 皆**既有人簽資產**（philosophy 層已帶文獻），零 AI 生成入庫；捷徑依據＝hint 掛**既有原理**時無需新 stanza（新學派新原理才走 stanzas 三空格）。核可後由我以繕打協定執行 INSERT（`provenance` 帶 hint_id／裁決／窗口語意註記）。

## 一、5 候選（A2 符號尺解鎖；第 2 關結果落地前先備好）

| # | feature | 掛原理（既有） | 草案 dir | 依據 |
|---|---|---|---|---|
| 1 | `lending_fee_rate_mean_20d` | p107 融券餘額與出借費率具預測力 | **−1** | 同原理之 `_30d` 列既為 −1；本列＝真 20d 窗（名實分明，不繼承 30d 名實債） |
| 2 | `lending_fee_vw_mean_20d` | p107 | **−1** | 同上（量加權變體） |
| 3 | `days_since_high_126d` | p94 順勢突破（或 p97/p78/p83 任掛） | **−1** | 沿你 DSH-252d 裁決之多數方；實測 IC −0.0487（HAC-t −2.52）同號 |
| 4 | `days_since_high_252d_raw` | 同上 | **−1** | 同族；與 #5 增量預期擇一（誠實註記） |
| 5 | `log1p_days_since_high_252d` | 同上 | **−1** | 同族單調變換 |

## 二、10 hint（RAWEVO 交互結構；全掛既有原理）

| # | hint 特徵 | 掛原理選單（你點一個或多個） | 草案 dir | 依據 |
|---|---|---|---|---|
| 6 | `inst_gross_x_turnover_level`（corr .823） | p95 量價籌碼主力／p99 短窗量能不均／p105 週轉流動性 | **+1** | inst 系既有列全 +1（p79/p89/p95/p96/p115 五掛皆 +1） |
| 7 | `inst_gross_x_volume_level`（.819） | p95／p99 | **+1** | 同上 |
| 8 | `inst_gross_x_money_change`（.758） | p100 短窗法人累計淨流相位 | **+1** | 同上 |
| 9 | `inst_gross_x_volume_change`（.752） | p100／p99 | **+1** | 同上 |
| 10 | `inst_gross_x_turnover_change`（.650） | p100／p95 | **+1** | 同上 |
| 11 | `close_x_sbl_balance_level`（.714） | p107 融券／出借 | **−1** | p107 系 −1（借券壓力×價位） |
| 12 | `market_value_x_revenue_level`（.698） | p80 小市值／p75 營收成長／p96 CANSLIM 綜合 | **【你裁】** | p80 為 −1 系（小市值溢酬）、p75 為 +1 系——交互方向非顯然，不代提 |
| 13 | `close_x_revenue_level`（.762） | p75／p96 | **【你裁】** | 同上（價×營收交互方向非顯然） |
| 14 | `holder_count_x_market_value_level`（.621） | p80／p95 籌碼集中 | **【你裁】** | 股東數↑＝籌碼分散（主力集中度↓？）——方向非顯然 |
| 15 | `close_x_holder_count_level`（.736） | p95／p99 | **【你裁】** | 同上 |

> #12–15 我**不代提方向**：交互結構的預期符號在文獻上非顯然（兩母因子方向相反或籌碼語意雙面）——這正是 direction 人閘存在的原因。你可：給方向／改掛原理／或標 `defer`（留 approved 不入 map、待更多文獻）。

## 三、執行約定

回覆格式例：`MAP-1~11-核可＋12defer＋13defer＋14:-1＋15defer`（任意組合；掛原理要換就寫「6:p99」）。核可後我逐列 INSERT：`principle_factor_map(principle_id, feature, direction, hint_id〔#6-15〕, provenance={"unlock_pack":"20260729","note":"hugo 對話逐列核;claude 繕打 §8.1","window_semantics":…})`——`validated_ic/validated_econ` 留 NULL（那是漏斗跑完才填的欄，不預填 #9）。

## 結案補記（2026-07-30，hugo「有三件，全部處理」）

#12 已於 07-29 補裁落庫（−1 掛 p80）。**#13／#14／#15 defer 定案**：三顆交互之預期方向文獻無開口（#14 之 p95 讀法帶規模混雜、不強掛），hint 維持 approved、不入 map——日後文獻到位或你給一字（如 `14:p95:−1`）隨時補列。unlock pack 全案結：15 列中 12 入 map、3 defer 定案。
