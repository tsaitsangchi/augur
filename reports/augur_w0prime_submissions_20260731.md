# W0′ 三份呈案（2026-07-31）——D8 治權檔增修／D1＋D2 SUNSET／D5 告警 sink

> **性質**：[I] **呈案**。依 `AUGUR-MC v1.6 §8.1`（Agent 不得參與修憲與解釋）與
> `RULING-2026-028` 第 2 點（**參與＝實質判斷之作成——規範內容之選擇、判準之定奪、
> 條文措辭之取捨、findings 之處置決定**），本檔僅陳列可驗事實與並列選項。
> **逐則標記制**：每則標【可驗事實】或【待認定·S#】；推論句一律附所依條文並標明係涵攝。
> **不設總括免責句**——對抗審查指出總括免責會降低讀者對內文語句之戒備，效果與宣稱相反。
>
> **產製**：workflow `wf_870a86db-274`（4 路蒐集＋2 路對抗，6 agent／315 工具呼叫／0 錯誤），
> 全程唯讀、未投遞 `governance_queue`、未改任何治權檔。
> **對抗審查已修正之處**：角色邊界路提出 16 則（2 critical），逐則反映於下文；
> 完整性路之補列選項亦已納入。
>
> **⚠ 背景檔之性質標記**：`reports/augur_execution_roadmap_20260731.md` **:99／:120 含繕打者之
> 執行層建議語**（「我的建議：讓它崩」／「建議只改 :240，不動 :111／:223」），屬 [I] 無拘束力；
> 其 :120 之範圍主張**已被本輪 F10 證明不完整**（同型殘留實為六處），本呈案不採其結論。

---

# 呈案 A｜D8 治權檔增修

## A.1 標的一：模擬專章 :240

### 可驗事實

【可驗事實】專章 :240 逐字：「- **未寫入任何 DB**、未建立 `governance_proposal` 列——依總則，提案之提出與議決屬 Steward。」
位於附三「繕打者未做之事（誠實界定）」節之四個 bullet 之一。該節標題**無日期錨**（對比附一 :212 明載「2026-07-31 唯讀」）。

【可驗事實】同檔 :3「**生效**：2026-07-31，經 `governance_proposal` **gp_86c8063fc688**」、
:9、:86 均以「已建立 governance_proposal 列」為前提。

【可驗事實】該句**逐字存在於凍結之 `diff_text` 第 247 行**——即此文字原生於提案文本身，
非 enact 後編輯所致。凍結文與生效檔在此句上**目前一致**。

【可驗事實】`trg_gov_proposal_immutable` 對 `status IN ('rejected','enacted')` 之列**任何 UPDATE 與 DELETE 一律 RAISE**
（連 `decision_note` 單欄補述亦被拒）。故該列已無就地補述通道。
（射程：該 trigger 為 `BEFORE DELETE OR UPDATE`，**INSERT 不在其內**；併 `submit` 路徑無 `isatty` ⇒
新增提案列無機械閘。）

【可驗事實】`status` 值域 `('pending','approved','rejected','enacted','withdrawn')`——**無 `superseded`**。
`proposal_id = 'gp_' + sha256(title+diff)[:12]` ⇒ 修訂後全文必得新 id。

### 本句含三個可分離命題（對抗審查 R1：不得以單一時態框架收束）

| 命題 | 內容 | 狀態 |
|---|---|---|
| **時態** | 「未寫入任何 DB」 | 【可驗事實】與 :3 並列，二者關係**屬 Steward 認定** |
| **行為主體** | 提案列由誰建立 | 【可驗事實】四列 `proposed_by` **全為 `claude`**；`submit` 路徑無 TTY 閘 |
| **規範命題** | 「依總則，提案之提出與議決屬 Steward」 | 【待認定·S1】`MC §8.5(a)` 逐字「受本憲章約束之任何**規格作者**得書面提案」——**未保留予 Steward**；「規格作者」全檔僅 :501／:524 使用、**無定義條**。大憲章第 3 節點為「人類授權門：晉升須經人類**核准**」＝核准非提出 |

**⇒ 若僅以「時態過時」為由改字，等於以沉默處理行為主體與規範命題兩項。**

### 選項（措辭為示例，取捨屬 Steward）

| 案 | 內容 | 射程 | 不可逆性 | 執行主體 |
|---|---|---|---|---|
| **A1** | 於該 bullet 加時點限定詞（如「〔至本文定稿時〕」），**不增刪原分句** | 僅時態 | 低（文字） | 須 Steward 指定；專章 9.3「Agent 不得自行修訂本專章」 |
| **A2** | A1 ＋ 加交叉引用（如「其後之投遞與議決見檔頭 gp_86c8063fc688」） | 時態＋指引 | 低 | 同上；**注意此非純時態補正**，會改變該 bullet 語用 |
| **B** | 另開一件 `governance_proposal` 記載補正 | 時態（新列留痕、原列不動） | 中（新列亦不可改） | **本輪未投遞係依任務指派限制，非依條文禁止**；投遞是否為 Agent 得為之行為，**未見禁止亦未見授權條文，屬待認定·S1** |
| **C** | 一併處理六處時態殘留（:212／:223／:226／:231／:239／:240） | 全檔 | 低（文字量較大） | 同 A1 |
| **D** | 維持原文不動 | — | 無 | **留痕草擬（對稱要件）**：於大憲章修訂歷程或新 `governance_proposal` 列記「經 Steward 認定，專章附三維持原文，理由＝……」 |

【可驗事實】同型時態殘留共**六處**：:212（自稱草案，**有日期錨**）／:223（`getpass` 事實已被 W0-1 推翻，屬附一有日期之親驗表）／:226（「須併陳」未來式）／:231（「得即刻議決」未來式）／:239（「以 TTY approve 為拍板」未來式）／:240。
**【待認定·S2】改動範圍（僅 :240／六處全改／不動）屬 Steward。**

## A.2 標的二：GOVERNANCE-MAP 未登錄專章

【可驗事實】`constitution/GOVERNANCE-MAP.md` 全文 5,025 bytes，對「專章」「模擬」**零命中**。
【可驗事實】專章 9.1 逐字「登錄為憲章第三部之下位專章」；大憲章第三部起於 :88、
「下位專章登錄」節位於 :213-218、第四部起於 :220。
**【待認定·S7】9.1 之登錄義務是否已由大憲章 :213-218 履行、GOVERNANCE-MAP 補登是否為其所命——屬涵攝，本輪不認定。**

選項：**甲** 補登（草擬文字比照既有條目格式）／**乙** 不補登（留痕：記明認定理由）。

## A.3 標的三：README:30 與原則精華:7 之版號

【可驗事實】二者皆停在 v1.51.0（2026-07-30），其後 v1.52.0／v1.53.0／v1.54.0 三次升版未同步。
【可驗事實】大憲章修訂歷程有 **28 次**「同步：原則精華第 5 行對憲章版本之交叉引用」之明文慣行；
**v1.47.0 起該同步清單不再出現**。成因未查得說明【UNKNOWN】——是刻意廢止、體例改版副作用、
抑或逐次遺漏，親查僅能確認現象。

【可驗事實】同型落後另有 **CLAUDE.md:43**「大憲章 v1.51.0『普遍晉升路徑』」。該檔已在
`check_treaty_refs` 之 entries 內（W0-2 今日 HEAD 才擴入），因該行不含 `STATUS_MARKERS` 而未被抓到。

**【待認定·S9】各處版號屬「史述」（通則一 (d) 應凍結）抑或「規範引用」（應同步）。**
通則一 (d) 之機器判準只界定兩型：「含日期＋完成式＝史述」「無日期之從屬／義務句＝規範引用」；
README:30「治權已立（…憲章 v1.51.0…）」屬**無日期之現況宣告句**＝**兩分支皆不完全該當之第三型，
條文本身未界定**。

**⚠ 尺之射程須揭露（對抗審查 R12）**：`check_treaty_refs` 之 `entries` 與 `STATUS_MARKERS` 兩層過濾
**皆由施作者（AI）選定**，未查得 Steward 核示【UNKNOWN】。故其 RC=1 為**該尺之判定**，
非獨立於本專案之外部證據。

選項：**甲** 只改二處版號／**乙** 併同 CLAUDE.md:43 等六處一次處理／**丙** 不改，改為推進
`<!--lint:KEY-->` 綁定機制（債 #16／W2-11）／**丁** 不動（留痕：記明認定理由）。
（P2-8 逐字：「該用的是那個機制，不是更勤快地手抄」——甲／乙屬手抄路徑。）

## A.4 標的四：原則精華:7

同標的三之判準問題。**【待認定·S10】**

## A.5 程序面（三標的共用）

【可驗事實】`GOVERNANCE-ANNEX.md` L20-22 三級門檻：原則級（書面裁決＋理由＋存檔，議決即生效，
Sole Steward 期間不強制公示；並須滿足 §8.5(b) 二要件）／minor（書面裁決＋理由＋存檔，無公示）／
**patch（逕行為之，登錄即可）**。

【可驗事實】L69 補後句逐字：「patch 之**性質認定屬 Steward 保留事項**；施作得由幕僚（含 Agent）為之，
惟須依 Steward 核示、逐案留痕，並依 `RULING-2026-028` 第 3 點於施作後受**非施作者之獨立核驗**。
**Agent 不得自行認定某變更屬 patch**。」
**⚠ 結構位置**：該補後句在**檔尾修訂表之後**（L69），**不在第 2 條本文**（L16-28）；
只讀第 2 條第 3 款本文者只會看到 L22「逕行為之，登錄即可」。且附則修訂表僅列 v1.0／v1.1 兩列，
**2026-07-30 寫入該補後句之變更在修訂表中無對應列**。

【可驗事實】`MC §8.1 解釋之界線` 逐字：「凡解釋之效果該當下列任一者，視為修訂——
(a) 課予新類型之義務；(b) 使先前於現行門檻下不可能之修訂類型成為可能；
**(c) 移除或削弱既有制衡（含公示、獨立核驗、人類介入點）**。屬解釋抑或修訂有疑義時，
採『屬修訂』之保守解讀。」

【可驗事實】`AMENDMENT-LOG.md` 最後一列＝AL-2026-045／2026-07-23；
**領域大憲章 v1.48.0–v1.54.0 共五次升版全部未入 AL**。是否為缺漏，本輪不認定。

---

# 呈案 B｜D1＋D2 SUNSET 落日與 apply_allowed

## B.1 凍結判準（逐字，criteria_sha `65eda893…`）

```
期限：2026-10-31
(a) arena 至少結算一批且方向門有可讀數；或
(b) evolution_production_feature_set active 由 2 成長，且每一新成員通過符號一致性檢查；或
(c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。
全未達成：三軸整體停止、帳本封存、不得換 trigger_code 重開。
```

【可驗事實】`evaluated_at=NULL`、`approved_by=hugo`、`approved_at=2026-07-27T15:31:50`。

## B.2 (a) 路：實作判準與凍結逐字不同義

【可驗事實】**live arena 軌**：`direction_arena_prediction` distinct `pred_date`＝6、
**已結算 cluster＝2**、13,392 列（4,128 已結算）。全表 `horizon_td` 僅 {5}。

【可驗事實】**approved 門之 min_clusters**：36（3 門，`own_stack_rolling`／h=20/40/82）、
250（5 門 live 表 ＋ 4 門 replay 表）、頂層無值（2 門 meta_replay）。
**36-門之估計量在 live 表列數＝0**（`model_key='own_stack_rolling'` 零列、`horizon_td<>5` 零列）
⇒ 其 cluster 計數恆為 0，屬**無資料源**而非速率不足。

【可驗事實】**到 250 之天花板算式**：以每交易日 1 cluster（07-27 起 cron 生效後之實測速率）、
5 交易日結算延遲，07-31～10-30 共 62 交易日 ⇒ 上限＝現有 2 ＋已出單未到期 4 ＋新增 57＝**63**，
缺口 187。達 250 需自今日起 **253 個交易日**（外推約 2027-08，2027 交易日曆不在 DB，精確日期 UNKNOWN）。
**⇒ 以「live 方向門達 min_clusters 而被 evaluate」為路徑，在 deadline 前算術上不可能。**

【可驗事實·本輪新查】**replay 軌已越過 250**：`direction_arena_replay` **4,791,845 列、
已結算 cluster＝2,798**（2015-01-05～2026-06-30）。其中 **4 個 replay 門仍 `status='approved'`、
`evaluated_at=NULL`**，其估計量之 cluster 已達 2,798 ≥ 250。另 2 門已於 07-30 判出完整統計量
（`dgate_replay_mc_bootstrap_5`：verdict=fail、n_panels=2798、overall_hit=0.5118、hac_eff_t=0.633、
p=0.26342、ECE .0405 pass、`display_tier=never_shown`；`dgate_replay_momentum_20_5` 同型）。

【可驗事實】**實作判準 vs 凍結逐字之落差**：週儀表實作為
`a_done = settled > 0 and gate_ok > 0`，其中 `gate_ok = count(*) WHERE status='evaluated_pass'`，
現為 **0**（12 門為 `evaluated_fail`）。凍結逐字則為「至少結算一批且方向門**有可讀數**」——
「至少結算一批」已於 2026-07-26 以 4,128 列滿足；「有可讀數」在 07-30 已有兩門輸出完整統計量。
**【待認定·S11】「有可讀數」是否須為 `evaluated_pass`；replay 軌之門是否算「方向門」。**

## B.3 (b) 路：現況與阻塞

【可驗事實】active＝2（`inst_cumflow_position_120d`／`lending_fee_rate_mean_20d`）、removed 7。
【可驗事實】**基線組成已位移**：07-26 拍板當日之 active 2＝{`inst_cumflow_position_120d`, `volume_gini_60d`}；
後者於 07-29 12:27 由 R6 規則 `R3-sign-refuted-demote` **自動 demote**，`lending_fee_rate_mean_20d` 於同日 13:07 promote。
`audits/V2-SUNSET-C-DISPUTED-20260727.md` §五 **S-6** 已登錄此爭點待裁。

【可驗事實】`apply_allowed` 四列**全為 false**；開輪 INSERT 硬寫 false（`run_evolution_iteration.py:202`），
自測以字面比對反鎖。I5 在 `allow_apply=False` 時**記 rc=0**（非失敗），故整輪可 `succeeded` 而 prodset 一列不動。
【可驗事實】crontab TWEVO 行**無 `--allow-apply`、無 `--gate-ref`**。

【可驗事實】**開閘後之算術上限＝active 2→3，且僅能經 `cycle_position_252d` 一個特徵**
（`promotion_queue` pending_auto 中 action='promote' 僅涵蓋 2 個特徵，其一已在 active；
`--dry-run` 實跑顯示 `cycle_position_252d` 全部被 R2(d)「單輪 promote 上限 1」hold）。

【可驗事實】**(b) 所要求之「符號一致性檢查」未接線**：機械尺 `verify_sign_consistency.py` 存在，
但**全 repo 唯一呼叫端為 `run_meta_replay.py:98,147`**——`apply_evolution_promotions.py` 與
`run_evolution_iteration.py` **零呼叫**；且該支自測逐字鎖「唯讀:零 UPDATE/INSERT」
⇒ **檢查結論無存放處**。

## B.4 (c) 路：現況

【可驗事實】現行判定尺（`4183475c5089`／`aeff01c18ace`）逐臂：
ceiling 1.0｜**robot 1.0**｜behavior 0.9667（2 run，其一 `is_invalid=true`，valid 者 1 個）｜
pack 0.76/0.80｜floor 0.3333｜shuffled 0.1667｜mismatched 0.0。
週儀表判定：「首半（嚴格同勝）之臂＝['behavior','pack']；複現（≥2 run 皆勝）之臂＝**無**」。

【可驗事實】`audits/S4-EVAL-SET-GO-CLOSED-20260730.md` 逐字：「能力量測 SSOT＝v2 集；
舊集 `4183475c5089` 僅史料／行為對照，**不得**再引其 robot=1.000 作能力宣稱。」
【可驗事實】**v2 集（`4e15a143ff4b`）無 L1 層**（層別為 B1/B2/B3/C1/C2P）——凍結文字「F@L1」
之 L1 只存在於舊集；且該集**全部受測臂 run 皆 `is_invalid=true`**（逾時／截斷），
**至今 0 個有效受測臂 run**。
【可驗事實】週儀表之選尺規則為「最新非對照臂且 not invalid」，因 v2 集受測臂全 invalid，
實際落回舊集——**與 S4 拍板之「SSOT＝v2 集」現存張力**。

【可驗事實】靈魂 v1.10.0 §三判準三逐字：「須設 ceiling／floor／mismatched 對照臂；
**橡皮圖章式的「一律同意」必須落在地板以下**——若「全部同意」就能得高分，該尺無效。」
判準五：「須於**兩輪以上**獨立回合復現。」
**【待認定·S8】SUNSET (c) 凍結文字不含 robot 臂；靈魂判準三含之。二者衝突時何者優先。**
（`RULING`／`no-goalpost`：凍結判準不得事後挪動。）

## B.5 落日之機械現況

【可驗事實】**全 repo 無任何 code 依 2026-10-31 觸發停止／封存／禁重開**。
最接近之槓桿 `evolution_kill_switch`（TRI-HALT）為**手動**，且只有 `run_philosophy_evolution.py` 與
`apply_evolution_promotions.py` 兩處讀它——arena 出單／結算／LAI／RAW 五個入口**零讀取**。
⇒ 今日之「落日」在機械層為**純文字約定**。

## B.6 選項（並列；執行主體與授權須 Steward 明示指定）

> **共同要件**：下列凡涉實跑者，依 `CLAUDE.md #26` 授權四要件（範圍／期限或結束條件／可撤銷／
> 所繫計畫參照）＋授權時點留痕。**本輪 agent 未取得任何執行授權。**

| 案 | 內容 | 不可逆性 | 依據／須注意 |
|---|---|---|---|
| **①** | 接受落日，並依專章 §5.4「誠實的無能宣告為合法產出」形式留檔 | 低（文字） | 專章 §5.4 已入憲之合法產出形式 |
| **②** | 對 4 個 replay approved 門執行 `evaluate` | **高**——判過即不可撤回、同 spec 假說終局 | 受 `_assert_clean_tree` 前置；執行主體與授權須明示 |
| **③** | crontab TWEVO 行補 `--allow-apply --gate-ref` | **位階待認定——字面命中大憲章 :331 (a)** | 大憲章 :331 (a) 逐字「凡**移除人簽要件**、減少人類介入點…一律認定為『重大判準修正』——須升 minor、記修訂歷程、並附 **OCV 六分量前後對照**…不得以『文字澄清』名義為之」；`CLAUDE.md #26` 自動鏈上限 (b) 四項對照。標的正是把 `TWEVO-APPLY-go` 由 hugo 親跑改為 cron 自動 |
| **④** | 於現行判定尺補一次受測臂 run | 中（佔 LLM 車道；產生新 run 列） | **效果**：週儀表判定式輸出將翻為 True（**實作層**）；**是否等同凍結文字 (c) 之達成屬 Steward 認定**。`V2-RUBRIC-GO` 之自我拘束：claude 不主動排第二次同臂重跑去閉合 SUNSET 條款 |
| **⑤** | 於 v2 集跑出有效受測臂 run（需先解 `is_invalid` 之逾時／截斷） | 中 | 執行主體與授權須明示 |
| **⑥** | 修改 SUNSET criteria | **高·不許** | `audits/V2-ADOPTED-SUNSET-20260726.md` 逐字：「升嚴須走 GATE-raise，**放寬一律不許**；本檔一經 commit，修訂唯增列、不回改（P4.E3）」 |
| **⑦** | 另立新 gate 承接（不動 SUNSET） | 中 | 須新 `criteria_sha`＋人簽 |
| **⑧** | 為落日後果補機械強制（現為純文字約定） | 低（純新增，不刪改既有） | — |
| **⑨** | 不作為（維持現狀至 deadline） | — | **留痕草擬（對稱要件）**：記明認定理由與屆期處置 |

## B.7 併同揭露之兩項

【可驗事實】**另一處寫死門檻**：`settle_arena_labels.py:48` `GATE_TRIGGER_CLUSTERS = 60`，
:267 計分板印「確立門檻 60」、:296 自測反鎖該常數。live 無任一門之 min_clusters 為 60。
每日 21:30 結算 cron 尾行持續印「方向門自動觸發:未達(2/60)」。（與 W0-3 同型、**尚未修**。）

【可驗事實】**(b) 產能管道現況**：`evolution_run` 17 列中 **7 列 `status='running'`**。
W0-0（逾時捕捉）已於 HEAD `77e28bd` 落地，run 17（13:21:55 起）已跑新碼；7 列殭屍為舊碼遺留，
回填屬 UPDATE＋人簽。

---

# 呈案 C｜D5 告警 sink 選型

## C.1 可用通道實查

【可驗事實】本機**無 `mail`／`msmtp`／`sendmail`／`mailx`／`ssmtp`**。
`notify-send` 存在但**送不達**（`dbus.service` inactive、`DISPLAY`／`WAYLAND_DISPLAY` 皆 unset、
無 notification daemon）。`curl`／`logger`／`systemd-cat` 皆在。
【可驗事實】journald **持久化已開**（`/var/log/journal` 存在、`Storage=auto`、已佔 1.0G）；
`journalctl --user` 可讀；hugo 屬 `adm` 群故 system journal（cron 側）亦可讀。
【可驗事實】DB 內**無任何告警帳本表**（唯一近似者 `knowledge_source_health` 為 API 限流健康錶、0 列）。
【可驗事實】repo 全量 grep `notify-send|webhook|slack|telegram|smtp|sendmail|pushover|ntfy` **零命中**
⇒ 三案皆為從零新建。

## C.2 四項此前未載之發現（直接改變選項評估）

【可驗事實·關鍵】**6 支常駐服務之 OnFailure 在現行組態下數學上永不觸發**：
逐支 `Restart=on-failure`＋`RestartSec=5`＋`StartLimitIntervalUSec=10s`／`StartLimitBurst=5`。
OnFailure 僅在 unit 進入 `failed` 時觸發；`Restart=on-failure` 下唯有 start limit 被打破才進 failed。
但 `RestartSec=5` ⇒ 10 秒窗內最多發生 3 次啟動 < burst 5 ⇒ **start limit 不可達**。
**掛 OnFailure 到這 6 支＝掛一盞在現行參數下永不亮的燈**；要真覆蓋須同時改 `RestartSec` 或
`StartLimitIntervalSec`，或改用健康探針型偵測。

【可驗事實】**7 支 timer 驅動之 oneshot exit code 紀律良好**（逐支 `sys.exit(main())` 型）
⇒ 對這 7 支掛 OnFailure **是真有效力的**。

【可驗事實·關鍵】**`run_evolution_chain.sh` 恆 exit 0**——無 `set -e`、無 `trap`、無顯式 `exit`，
brace group 末句為 `echo`；header 自陳「各步失敗不斷鏈」。該鏈含八段（harvest×5／self_seek×2／
evolve_cycle／verify_eval_set_validity）。**⇒ 每日唯一之演化總鏈對任何 exit-code 型 sink 覆蓋率＝0。**

【可驗事實】**cron 串接語意逐條不同**：第 7 條以 `;` 串 ⇒ 整行 rc＝末段 rc，`--run` 失敗被吞掉；
第 8 條以 `&&` 串 ⇒ 語意正確。兩者不能同一模板套用。

【可驗事實】**`flock -n` 搶不到鎖 exit=1（＝設計上的正常跳過）** ⇒ 裸 `|| alert` 會把「單槽鎖忙碌」誤報。
`man flock` 載 `-E`／`--conflict-exit-code` 可改碼。

【可驗事實·庫內既有正解】`augur-admission-assist.service:10-11` 已解過同題：
「先跑；若非零則回頭再探一次鎖，鎖仍忙即 exit 0、否則 exit 1」。
（殘留競態：兩次探鎖之間鎖可能易手，判定非 100% 精確。）

【可驗事實·活體樣本】`audit_watchdog.sh` ＝「sink 自己安靜壞掉」之現成案例：
:16 取 log 最後一行**不檢查時效**、:18-20 命中 `✅ PASS` 即 exit 0；而 `~/audit_retry.log` mtime 停在
**2026-07-15**（16 天）⇒ `~/audit_watchdog.log` 今日仍每 30 分寫「audit 已綠、無需動作」。
**訊號源（log 檔）與判準源（DB）分離＋無新鮮度檢查＝告警器活著、標的死了、燈是綠的。**

## C.3 cron 側 live-vs-SSOT 漂移三處（任何 D5 改法之前置）

【可驗事實】`bash install_cron.sh`（無參數＝唯讀 diff）實跑得三處差異：
1. `evolve_self_seek` 行：live 有 `flock -w 3600`，SSOT `:34` **無**（且 :33 註解逐字「不碰 ollama,故不入鎖」與 live 互相矛盾）。
2. 週儀表行：live 檔名凍結為 `evolution_week_20260727.md`，SSOT `:49` 為 `$(date +%Y%m%d)`。
3. TWEVO 行：live 有 `--slot-wait 10800`，SSOT `:52-59` **無**（註解已於 W0-0 更新為「實測 60-88 分」）。

⇒ 跑 `install_cron.sh --apply`（`:110` 為**整段替換**）會同時把 self_seek 的 flock 拆掉、
把 TWEVO 的有界等待改回預設 0。（行程計畫 W1-6 只記了第 3 處，**實為三處**。）

【可驗事實】**週儀表檔名在安裝當下被凍結**：`:27` 為**未加引號之 heredoc**，`:49` 之 `$(date …)` 於安裝當下即被命令替換
⇒ (a) 週儀表每週以單 `>` 覆寫同一檔、無歷史；(b) 無參數 diff **永遠非空**，「一致，無須 --apply」之綠燈永不出現。
（`:57` 註解本身警告過同一陷阱。）

【可驗事實】`install_cron.sh:86-87` 之 `chk "路徑不寫死 hugo"` 用 `grep -qv`——只要任一行不含該 pattern 即 rc=0，
而 AUGUR_BLOCK 內大量註解行本就不含 ⇒ **恆真**。屬債 #14 同族；D5 若改該檔並倚賴其 `--selftest` 驗收會拿到假綠。

## C.4 選項（並列）

| 案 | 內容 | 實作成本 | 換機負擔 | 失敗自身會不會靜默 | 對債 #7 之覆蓋率 |
|---|---|---|---|---|---|
| **甲** | 本地 log ＋ **DB 告警帳本表** | 中（新表 DDL＋一支 alert 腳本＋unit template） | 隨 git（DDL 在 repo；表隨 dump） | 可查（帳本有列＝有發生；可加新鮮度檢查） | 7 支 oneshot 全覆蓋；6 常駐須併同改 Restart 參數；cron 須逐條處理串接語意 |
| **乙** | 外部推送（webhook／ntfy 等） | 中（需憑證＋新 `.env` 鍵） | **不隨 git**（憑證人工重建，同 §3 之 `.env` 負擔） | 送失敗可能靜默（需回執機制） | 同甲；另**【待認定·S12】是否違 `#28` 本地優先** |
| **丙** | 僅 journal ＋ 每日彙整腳本 | 低（一支腳本＋一個 timer） | 隨 git | 彙整腳本自身失敗需另一層 | 覆蓋較粗（無即時性）；但不受 6 常駐之 start-limit 問題影響 |
| **丁** | 不作為 | — | — | — | **留痕草擬（對稱要件）**：記明認定理由 |

**子決策一｜flock 假警報處置**：(i) 比照 `augur-admission-assist` 之二次探鎖模式（庫內既有）／
(ii) 用 `flock -E <code>` 指定專屬退出碼／(iii) 於 alert 側白名單該退出碼。

**子決策二｜`install_cron.sh` 漂移處置順序**：(i) 先修 SSOT 再談新增／(ii) 併同新增一次處理。

## C.5 須 Steward 認定之點

- **【S12】** 乙案是否違 `CLAUDE #28` 本地優先。
- **【S13】** 新增 sink 是否觸發 `#26` 自動鏈上限之四項對照義務（新增排程＝延長背景編排？）。
- **【S14】** 屬解釋抑或修訂（`MC §8.1` 解釋之界線 (a)(c)——「課予新類型之義務」／
  「移除或削弱既有制衡」；本案方向為**增強**，是否仍須依 §8.5 程序）。

---

## 附：本呈案未做之事

- 未執行任何變更；未投遞 `governance_queue`；未改任何治權檔；未跑任何 `evaluate`。
- 未認定 S1–S14 任一項；未推薦任何案。
- 未受獨立核驗（`RULING-2026-028` 第 3 點）——本檔由繕打者合成，宜由非施作者核驗。
- **射程缺口揭露**：角色邊界對抗路只收到四路中之二路（D8、SUNSET），**D5 與程序路未受該路審查**。
