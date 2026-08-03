# M-T3 備料：17 列 pending_auto 之處置證據（2026-08-03）

> **性質**：[I] 唯讀備料（SSOT `augur_optimization_master_plan_20260803.md` 第 5 步指派「AI：17 列逐列 gate_json 摘要備料」）。
> **結論先講**：**17 列全部是「標的已消失」的重複提案** ⇒ 今晚 run 22 標 superseded **實質無損**，
> 不需要在 23:00 前開人裁窗。r4 Q10（晉升單位＝feature 或 (principle,feature)）之裁點**不因此消失**，但**今晚不急**。

## §1 17 列全貌（現查 2026-08-03 11:0x）

| feature | 列數 | action | 八閘型態 |
|---|---|---|---|
| `cycle_position_252d` | 1（q555） | promote | **八閘全 PASS** |
| `debt_ratio` | 5（q565·566·567·568·569） | demote | PROM=FAIL_SIGN／ECON=FAIL／SIGN=FAIL |
| `gov_bank_net_buy_60d` | 2（q576·577） | demote | 同上 |
| `top_holders_pct` | 2（q652·653） | demote | 同上 |
| `market_cap_log`／`momentum_5d`／`volume_gini_20d`／`volume_gini_60d`／`volume_max_share_20d`／`volume_max_share_60d`／`volume_surge_5_60` | 各 1 | demote | 同上 |

合計 **17 列／11 個相異 feature**（1 promote＋16 demote）。同 feature 之多列 ＝ **不同 `principle_id`**
（如 `debt_ratio` 對應 principle 85／109／114／120／125）——此即 r4 Q10 之現象面。

## §2 關鍵證據：這 17 列的標的都已不存在

現查 `evolution_production_feature_set`：

| feature | prodset 現狀 | 該 pending 列還有意義嗎 |
|---|---|---|
| `cycle_position_252d` | **active**（來源 **q556**） | ✗ 晉升已由 q556 完成（hugo 08-02 親簽）；q555 為同 feature 舊世代孤兒 |
| `debt_ratio` | removed（q242） | ✗ 已除役，demote 提案無標的 |
| `gov_bank_net_buy_60d` | removed（q249） | ✗ 同上 |
| `top_holders_pct` | removed（q300） | ✗ 同上 |
| `volume_gini_20d`／`60d` | removed（q305／q306） | ✗ 同上 |
| `volume_max_share_20d`／`60d` | removed（q307／q308） | ✗ 同上 |
| `market_cap_log`／`momentum_5d`／`volume_surge_5_60` | **不在 prodset** | ✗ 從未進生產集，除役無對象 |

⇒ **除役提案的標的早已除役；晉升提案的標的早已晉升**。17 列皆為事後重複。

覆核指令：
```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT feature, set_status, source_queue_id FROM evolution_production_feature_set ORDER BY feature"
```

## §3 建議

**讓 run 22 自動標 superseded（不開人裁窗）**——理由：

1. **無實質損失**（§2 機械證明）：被標的 17 列，其處置結果早已落地於 prodset。
2. **留痕不刪**：`superseded` 為終態標記、列本身保留（I5B-甲 設計），事後可完整回溯。
3. **人裁窗的成本大於收益**：17 列逐列 TTY 親簽 ≈ 30-60 分鐘，換到的是對「已完成之事」再蓋一次章。

**但下列兩點須明確保留**（不因本建議而關閉）：

- **r4 Q10 仍待裁**：晉升單位是 `feature` 還是 `(principle, feature)`？現行 I5B 謂詞用 `feature=%s`（不分 principle、不分 action）。若日後裁為 `(principle, feature)`，則 I5B 謂詞須同步改，否則會誤殺同 feature 不同 principle 的合法列。**今晚無此風險**（§2 已證 17 列皆無標的），但**下一輪有新 pending 時就有**。
- **I5B 謂詞不分 action**：本次恰好無害（promote 那列也是孤兒）。日後若出現「同 feature 同時有合法 promote 與 demote 提案」，此謂詞會把兩者一起收掉。建議列入 r4 Q10 同批裁決。

## §4 誠實邊界

- 本備料只證「17 列之標的已不存在」，**未證**「supersede 對下游零影響」——`promotion_queue` 之消費端（週報 (b)／AGO 決策包／A8 驗收）我未逐一追查其對 `superseded` 狀態的處理。若你要更強的保證，可於 run 22 後跑一次 `report_applygo_readiness.py` 與週報比對。
- 本判斷為 AI self-reported（#32a）；§2 之表可用上列指令零 AI 獨立覆核。
