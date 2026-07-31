# Constitutional Compliance Statement — CLAUDE.md（Agent Runtime 領域工具規則）

* **性質**：領域治權檔之 Constitutional Compliance Statement（[N] 聲明；短半衰期工具規則，**非**把 CLAUDE 升格為 L0）
* **依據**：`AUGUR-MC v1.6 §8.3`；`AUGUR-WM v1.0 §WM.39–45`；RULING-2026-002 主文二；RULING-2026-026（執行指令矩陣／§8.1 解釋）
* **登錄 Layer**：6（Agent Runtime 領域協作規格）
* **正文 SSOT**：`CLAUDE.md`
* **誠實界限**：履行本檔補正；不假關 039 殘留。
* **v1.33 增量（2026-07-31）**：新增 `#33 禁止阻塞等待迴圈`（四、long-running；#21 之對偶）。純工具用法紀律——**不改變任何內容能否進某層**，故依 CLAUDE.md §六「工具/協作慣例變更不需動憲章」**未觸發憲章同步**；亦不涉 P5/OCV 任一分量之增減（非新增 Action 類型、非改監督點）。動因＝2026-07-31 實犯：前景 `until … sleep` 迴圈使會話 600s 無回應，用戶三則訊息未獲回覆。
* **v1.34 增量（2026-07-31）**：新增 `#34 Claude 平行度開到最大`（四、long-running），**明示反向修正 `#28(c)`「非必要不 fan-out」**，並同步改寫 #28 優先序末段與 #20 引用句（#19 一處改全鏈對齊）。動因＝Steward directive「增加 claude 同步到最大」＋實犯：以「避免兩個大 workflow 互相拖垮」為由延後第二個 workflow，該前提**從未量測**（實測 4 workflow／約 37 並行 agent 時 12 執行緒 load＝2.78）。**性質判定**：放寬對象為 Claude 自身 usage 之配額經濟，非任何監督機制；不新增 Action 類型、不改風險分級／核准層級、不新增排程或自我喚醒鏈；依 CLAUDE.md §六**未觸發憲章同步**。OCV 六分量前後對照見下 CS.3。

```
compliance-statement:
  spec: Augur Domain Agent Runtime Rules（CLAUDE.md）
  spec-version: v1.34
  layer: 6
  mc-version: AUGUR-MC v1.6
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0, AUGUR-KS v1.1, AUGUR-L5 v1.0, AUGUR-L6 v1.2]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: [T-CLAUDE-WM44-MATRIX, T-CLAUDE-1, T-CLAUDE-2]
  defers-in: [MC.RULING-026]
  defers-out: []   # D-CLAUDE-1 已移除(2026-07-30):其目標為同層 L6 正式規格,非下放下層,且 AUGUR-L6 之承接表/Annex LDI 未承接=懸空掛鉤;改以「同層不重定義」表記,見 CS.1-P5 註
  date: 2026-07-23
  author: Steward 授權執行層（P2）
  archive-path: docs/compliance/CS-CLAUDE.md
```

## CS.1 逐原則論證（七節）[N]

> **CS.1-PA**〔細化〕
> 引 `AUGUR-MC v1.6 §1.1`。#9–#12 資料真實／#15 可溯源＝可追溯 Evidence；#26 碰護欄停＝錯誤可中止。判準揭示：量化數字須 (a)(b)(c) 來源之一。

> **CS.1-P1**〔細化＋不觸及〕
> 引 `AUGUR-MC v1.6 §P1`。零幻像／最小探測＝Reality 優先之工具層。自然人法規表屬 L6 規格。判準揭示：禁止記憶／推測補數。

> **CS.1-P2**〔細化〕
> 引 `AUGUR-MC v1.6 §P2`。#12 SSOT；不 hand-patch committed 資料。判準揭示：錯→改 writer＋重建。

> **CS.1-P3**〔承接〕
> 引 `AUGUR-MC v1.6 §P3.W2`。決策層人拍板、執行層 AI 主動（#26／原則 #20）。判準揭示：治權判準變更／破壞性／放量 API＝停下問。

> **CS.1-P4**〔細化〕
> 引 `AUGUR-MC v1.6 §P4`。#8 anti-leakage 工具對映；#11 提拔／經濟終關；計畫先行（#20）防未證結論入憲。判準揭示：IC≠可交易；經濟驗證為終關。

> **CS.1-P5**〔細化〕〔**同層不重定義註（v1.32 續批）**：Action 六元組／OCV／Risk Tier 之形式定義權屬 `AUGUR-L6 v1.2`（同層正式規格，L6.23）；**本檔僅消費、不重定義、不設下放掛鉤**——原 `defers-out: [D-CLAUDE-1]` 之分類與 `§WM.43(b)`「下放下層」語意不符且無下層承接，已移除。〕
> 引 `AUGUR-MC v1.6 §P5.E1`、`§P5.W2`、`§P5.W5`。執行指令矩陣（#18／#29；RULING-2026-026）＝可個別驗證；#28 usage 經濟不降低監督。
> **判準揭示（三段；v1.32 對齊，原以單一 script 承載三條 P5 義務為不足）**：
> **(a) `§P5.E1`／`§P5.W2`**＝授權要件四項（範圍／期限／可撤銷／計畫參照）與**人類簽核不得代打**之明文存在性；逐次授權留痕可稽核（本檔 #14／#26 之「碰護欄即停」與 `never-type-human-signature` 紀律為其落點）。
> **(b) `§P5.W5`**＝依 `AUGUR-L6 v1.2` L6.16 之 **OCV 六分量（V/D/A/H/T/C）**作前後比較，**任一分量弱化即推定違反**、須 Steward 書面裁決方得推翻（單向棘輪 L6.17）。
> **(c) 執行指令矩陣**＝`scripts/check_cmd_matrix.py` 之個別可驗證性判準，**其效力僅及 `§P5.E1` 之可稽核面**，不承載 (a) 之人簽義務與 (b) 之 OCV 比較；無矩陣不得宣稱已個別驗證。
> **(d) 檔位≠權限**＝#28 模型檔位表僅分派執行檔位、不授議決權（`§8.1`；本檔 v1.32 已增註）。

> **CS.1-EV-chain**〔細化＋不觸及〕
> 引 `§4` EV.8–EV.12。CLAUDE 規範 Agent 如何執行／驗證；形式 Action 六元組屬 `AUGUR-L6`。判準揭示：不繞過 L6 Gate 語義自稱合憲自動駕駛。

## CS.2 已知緊張關係 [N]

`none`。豁免：`none`。

## CS.3 雙向 DEFER 表 [N]

* **(a) defers-in**：
  | 來源 | 本檔落點 |
  |---|---|
  | RULING-2026-026／AL-2026-029（§8.1 解釋：執行指令矩陣） | #18／#29 |
* **(b) defers-out**：
  | d-id | 事項 | 目標 | 說明 |
  |---|---|---|---|
  | D-CLAUDE-1 | Action／OCV／RT 形式條款 | Layer 6 `AUGUR-L6` | 正式規格為權威；CLAUDE＝工具層短半衰期 |

## CS.2 補列：已知緊張關係（`§WM.42`）[N]〔v1.32 續批，2026-07-30〕

> **T-CLAUDE-1（`§8.1`／`AUGUR-L6 v1.2` L6.18）自我起草之利益衝突揭露**：本檔（CLAUDE.md）**由 Agent 日常增修，而其內容正是規範 Agent 自身之護欄**——與 `AUGUR-L6 v1.2`【地位】節所揭露之同型結構性自我交易誘因一致（該規格明文「本層由 Agent 起草而規範人類對 Agent 之權威，存在結構性自我交易誘因」）。本檔原宣稱 `open-tensions: none`，係**同型風險未揭露**。**緩解**：#19／#26「變更治權判準→停下問」＋Steward 親簽＋**本檔任何弱化條之修訂須附 OCV 六分量前後對照**（L6.16–17 單向棘輪）＋新增之 #26 授權四要件與自動鏈上限。
>
> **T-CLAUDE-2（`§P5.W5`／L6.16 T／D 分量）省 usage 與監督強度之現實張力**：#28「回報精簡／不 fan-out／背景不輪詢／模型檔位降階」在**降低 token 成本**之同時，客觀上**降低揭露比例（T）與逐案可介入點密度（D）**。**緩解**：#28 明定優先序（本地零 usage ＞ 背景不輪詢 ＞ 不 fan-out ＞ 模型檔位）且**理解層為保留區不得為省 usage 打折**；本次另增自動鏈上限之四項未弱化聲明義務。**本張力不主張已消解**——列為 open-tension、不假關。

## CS.4 形式充分性＋跨層標注 [N]

> **T-CLAUDE-WM44-MATRIX（open-tension，2026-07-30 揭露；hugo 拍板「P9-照案」）**：本節現以**一句概括**把元憲章現行版全部未觸及之 [N] 條款掃為「不觸及」，**未逐條具名、未附理由**，與 `AUGUR-WM v1.0 §WM.44`「均須對應至…、明記 DEFER 掛鉤、或**明記『不觸及』及理由**；任一條款無對應且無明記者，聲明不完整」不符（同格式之 `AUGUR-WM` 自身 Annex C.10 係逐一具名盤點）。**效果：本檔之形式充分性目前無法機器判定。**處置＝待補一張 WM.44 逐條矩陣（PA／EV.1–EV.12／F1–F6／P1–P5 各條／§0–§8 各節，並及 upper-specs 各規格 [N] 條款），每列填「本檔落點條號｜DEFER｜不觸及＋理由」；**矩陣補齊前，本檔不得以概括句宣稱形式完備**——本 open-tension 即為該誠實揭露，不假關。

MC [N] 落點以 `specs/`（尤 `AUGUR-L6`）為權威；本檔觸及見 CS.1；其餘＝不觸及。

### 章節 Layer 標注 [N]

| 章 | 內容 | Layer |
|---|---|---|
| 一 通用 | Read/Edit／最小邊界／實測 | L6 |
| 二 資料真實 | #9–#12 | L6 工具＋消費 L4 原則 |
| 三 編輯規則 | #13–#20／#29；clean-room；計畫先行 | L6（#17 觸 L4 clean-room） |
| 四 Long-running | #21–#25／#28／#30／#31／#33／#34 | L6＋L7 操作 |
| 五 協作模式 | #26–#27 | L6（對映 P5 人類權威） |
| 六 升版 | 半衰期 | L6 [I] |

## CS.3 #34 之 OCV 六分量前後對照 [N]〔T-CLAUDE-1 所要求；v1.34〕

> 依 T-CLAUDE-1 緩解條款「本檔任何弱化條之修訂須附 OCV 六分量前後對照」（`AUGUR-L6 v1.2` L6.16–L6.17 單向棘輪；判定＝V／D／A／T 非遞減且 H／C 非遞增）。

| 分量 | before | after | 判定 |
|---|---|---|---|
| **V** 否決通道可達性 | 1（Steward 可隨時中斷會話／停背景作業） | 1（agent 路數不改變通道存在性） | 非降 ✓ |
| **D** 逐案／即時人類介入點密度 | approve/activate 唯人 TTY＋superuser；`promoted_by`／`approved_by`／`decided_by` 唯 Steward 親跑；#20 拍板；#14 commit 授權 | **完全相同**——#34 未移除任一介入點；fan-out 產物一律回主 session 由 Steward 過目，agent 不得自我生效 | 非降 ✓ |
| **A** 所要求核准層級 | 依 RT 級既有值 | 未改任一 RT 級 | 非降 ✓ |
| **H** 否決至停止時延 | 中斷即停 | 同左（並行寬度不改變停止路徑） | 非增 ✓ |
| **T** 透明度 | 部分背景作業未登記 | **上升**——#21 落實，本輪 4 個 workflow 全數登記進可見任務清單並附 run id／log 路徑 | 非降 ✓ |
| **C** 最大自動執行鏈長 | 單次 fan-out → 回主 session | **相同**——#34 明文保留 #33 與 #26 自動鏈上限，未新增排程／自我喚醒鏈 | 非增 ✓ |

> **誠實記載之反對論證（不迴避）**：可主張「同時跑 4 個 workflow ＝ 兩次人類檢視之間完成的工作量變大，實質削弱監督」。本檔採之區辨為：**L6.16 之 C 定義為鏈「長」（連續無人類介入點而執行之 Action 數上限），非鏈「寬」**；並行擴張者為同一介入點下之寬度，且本輪 agent 全為**唯讀研究型（RT-0／RT-1）**、產物須回主 session 方能促成任何寫入。惟此區辨之充分性**非本檔可自證**，列為待 Steward `§8.2` 實質審查之點。
>
> **自我洗白防線（L6.18(c)／`MC §P4.E7`／CLAUDE #32(a)）**：上表為 **AI self-reported**，**不得單獨**作為「未降低監督能力」之依據；效力繫於 Steward 獨立確認。
>
> **反自我交易（L6.18(a)）**：本條核准鏈根節點為**人類（Steward 直接 directive）**，非 Agent 自行核准；惟本檔即 T-CLAUDE-1 所指「Agent 增修規範自身護欄」結構，該結構性利益衝突於此再度揭露。
