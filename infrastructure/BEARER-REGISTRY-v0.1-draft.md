# Bearer Registry v0.1-draft [I]——六角色物理載體對映之首版登錄（提交 Steward）

* **日期**：2026-07-18｜**依據**：AUGUR-L7 v0.1-draft L7.10（七欄最低欄集）、L7.11（六角色語義欄）
* **地位**：**草案登錄** [I]——L7 未充任前本登錄不生 L7.10 之權威效力；現行載體值均為本機實測（ENVIRONMENT-SPEC 2026-07-18 快照），非轉抄。**欄 (4)(5)(6) 於多數列尚缺**，依 L7.10「缺任一欄者登錄不成立」，本表之地位為**盤點＋缺口清單**，非已成立之登錄——缺什麼、誰補、怎麼補，逐列明列。

| # | §5 角色 | (3) 現行載體值 [I]（實測） | 七欄成立度與缺口 |
|---|---|---|---|
| 1 | World State System of Record | **PostgreSQL 17.9**（apt pgdg，`augur` 庫 55GB；append-only 憲章表＋19 守衛 trigger＋owner 分離施工中） | (1)(2)(3)(7)✅；**缺 (4) 相容性驗證紀錄（x86_64 原生 apt 建置——可補）、(5) 退出程序、(6) 刪名測試紀錄** |
| 2 | World Relationship Representation | **PostgreSQL 17.9 同庫**（關聯以關聯式表承載；**無圖資料庫**——MC Appendix A 之 Neo4j 為非約束性例示，未安裝） | 同上；另需 (2) 語義判準逐條驗證：identity lineage 承載現況＝entity_registry／identity_lifecycle_event（零列，Phase 2 起用） |
| 3 | Semantic Memory | **qdrant 1.18.2**（127.0.0.1:6333，運行中） | (1)(2)(3)(7)✅；**缺 (4)(5)(6)**；語義判準「輸出恆為候選斷言」之機器強制待 Phase 6 消費閘 |
| 4 | World Understanding Engine | **Cognitive Kernel 自研**（augur-code：deliberation／verifiers／core_gate；模型輔助＝ollama qwen3:4b/8b，GTX 1650 4GB GPU 加速〔實測 VRAM 卸載〕） | (3) 之「版本」＝git SHA（活服務跑 /home/hugo 副本——**雙副本現實使版本錨定不唯一，為缺口**）；缺 (4)(5)(6) |
| 5 | World Action Layer | **Agent Runtime 自研**（watchdog／selfheal／daily_maintenance 腳本＋TTY 唯人閘） | 同上；行動六元組載體（authorization_grant／automation_action_log）已 apply、零列（Phase 3 起用） |
| 6 | Controlled External Interface | **四個 serving 進程**（advisor_openai／admin_console／chat_ui／probability_ui，hugo 側常駐）＋FinMind ingest 通道（限流 0.7s） | **單一執法點（§P5.E2）尚未物理化**——四進程各自為政、無統一 pre-commit 閘：**六列中最大缺口**，落點＝Phase 3/4 之 L7.44 單一執法點設計 |

## 缺口彙總（補齊路徑）

1. **(4) 架構相容性驗證紀錄**：PG／qdrant／ollama 均為 x86_64 原生建置——一次盤點可補（機械）。
2. **(5) 可替換性證明**：六列全缺——各載體之退出程序與遷移計畫，屬 L7.12 義務，充任後首批。
3. **(6) 刪名測試紀錄**：六列全缺——逐列跑 L7.4 刪名測試並留痕（機械）。
4. **角色 6 單一執法點**：實質工程，＝移轉計畫 Phase 3（行動六元組）＋L7.44 之落地，最重。
5. **角色 4/5 版本錨定**：雙副本現實（hugo 活服務／giga 工作副本）使 git SHA 不唯一——Phase 1 步 7（hugo 側切換）後應歸一。

## 提請 Steward

本表為 L7.10 之**首版盤點草稿**：(a) 六角色之現行載體對映是否如實？(b) 缺口補齊順序是否照上列 1→5？(c) L7 充任後本表轉正式登錄（七欄補齊者逐列成立）。
