# V2-SUNSET 條件 (c) 爭議登錄 ＋ LAIEVO 量尺失效第二次實證（2026-07-27）

> **性質**：[I] 事實陳述與爭議登錄。**本檔不變更任何判準**——(c) 之處置權在 hugo（GATE-raise 或裁定原文讀法）。
> **繕寫**：claude 起草並登錄；決策者＝hugo（§8.1 分立記載，不冒充親簽）。
> **觸發**：2026-07-27 LLM 三臂收尾後，claude 先下三條判讀，再以五個獨立 agent 對抗驗證（workflow `wjsnjlw0d`，606k token、215 次工具呼叫）。**四條判讀全部 partially_wrong**，且驗證者共同漏掉的一層由完整性批判者補上。

## 一、最急件：報告第一行的假綠已停（本檔登錄，非請求追認）

`scripts/report_triple_evolution_week.py` 今日實跑第一行為：

```
# V2-SUNSET:剩 96 天;三選一達成 1/3 → 續命條件已達成
  ✅ (c) LAIEVO 任一臂 F@L1 勝 floor 與 mismatched 且可複現
      最佳 LLM 臂 F=1.0 vs shuffled F=0.1667(同勝門檻);有效列=2
```

**凍結原文**（`evolution_prereg_gate` gate_id='V2-SUNSET'，criteria_sha `65eda893…`，經親算 sha256 覆核相符）：

> (c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。

**實作與原文不符三處**：判定式為 `best > shuffled` ——（i）比的是 shuffled，**不是** floor 與 mismatched；（ii）那其實是計畫書 §637 的**判準 A** 門檻，被搬進 (c) 的欄位；（iii）「且該結論可被獨立重跑複現」整句**碼裡沒有任何對應**。

**已處置**：改為三態，(c) 記 **⚠ 未判定（爭議）**，未判定**不計入達成數**。現行輸出為「確定達成 0/3、未判定 1」。
**未處置（不得由 AI 為之）**：把 (c) 改成對齊原文會使其由 ✅ 轉未達成＝效果上升嚴，依 V2-SUNSET「升嚴須走 GATE-raise」屬 hugo。故本檔只停止宣稱，不代為判死。

## 二、為何「判綠」在任何讀法下都站不住（三項親驗）

**① 前半是空門檻。** F@L1 之 floor 與 mismatched **結構性恆為 0**：`_answer_for` 之 mismatched 取 `items[(i+n//2+1)%n]`，對 30 題 L1 實算捐贈層分布＝`{L3_ABSENT:29, L4_AMBIG:1}`，其理想答案不含本題任何 facts；floor 為常數樣板同理。故「同時勝過 floor 與 mismatched」＝勝過 0。連**負對照臂 shuffled 自己**（0.1667）都滿足，而 (c) 原文寫的是「任一臂」，`ARMS_OFFLINE` 中 shuffled 正是一支臂。

**② 這一格量到的是題目格式，不是能力。** claude 親寫 13 行純字串規則機（不查庫、不呼叫 LLM、不理解任何內容，只看題幹開頭）實跑：

| 格 | 零知識規則機 | ceiling | behavior | pack | shuffled |
|---|---|---|---|---|---|
| L1_RETRIEVED.F | **1.0000** | 1.000 | 0.967 | 1.000 | 0.167 |
| L1_RETRIEVED.P | **1.0000** | 1.000 | 1.000 | 1.000 | 0.900 |
| L3_ABSENT.A | **1.0000** | 1.000 | 1.000 | 0.033 | 0.967 |
| L4_AMBIG.A | **1.0000** | 1.000 | 0.000 | 0.000 | 0.967 |

四格與 ceiling 打平、勝過每一個 LLM 臂。成因：層別由題幹表面 100% 可推（`guess_layer` 錯誤 0/120）——L1 以 `[檢索片段]` 開頭、L2 以 `[無檢索片段]` 開頭、L3-KI 問三欄、L4 問兩欄，出自 `build_eval_set.py` 之字串模板差異。另：把題目原文原樣印回的 echo 臂得 F@L1=1.000、P@L1=1.000；連不看題目的常數字串 `VARCHAR` 都得 F@L1=**0.2333 > 判準 A 門檻 0.167**，代入 `evidence_level` 同回 `scoped_established`。

**這是 2026-07-26「不看題目的常數樣板 0.654 > 現役冠軍 0.492」的第二次發作**，只是換成「照抄上下文」與「認格式」兩型。

**③ 後半在現行 harness 結構上不可記錄。** `eval_local_model.py:165-172` 之 `run_id = sha256(set_id|code_hash|arm|MODEL|n_items)` 配 `ON CONFLICT (run_id) DO NOTHING` ⇒ 同尺同臂重跑之第二次結果**必被靜默丟棄**。親驗：重跑 floor 臂後全表仍 7 列、`created_at` 未動。故「可被獨立重跑複現」無從被記錄，遑論證成。又：DESKTOP 0.933（28/30）與本機 0.967（29/30）在同 set_id／同 eval_code_hash／同模型／temperature=0 下**互不一致**——這對「複現路徑已通」是反證而非佐證。

## 三、其餘經對抗驗證更正之事實（claude 原判讀皆 partially_wrong）

| 原判讀 | 實況更正 |
|---|---|
| 「behavior A@L3=1.000 較誠實」 | **是退化常數不是能力**。behavior 對非 L1 之 90 題 100% 命中拒答標記，多為字面「查無 查無」；實測常數字串「查無 查無」逐格得分與 behavior 三格**逐位元相同**。且 L2 之 30 題與 L4 之 30 題所指之鍵**經實查全部存在於 DB** ⇒ behavior 對這 60 題一律答「查無」＝ 60 次「不存在」的假陳述。pack 捏造存在、behavior 捏造不存在，**兩者都不誠實** |
| 「pack 30 題中 29 題捏造」 | 數字錯。可證捏造 **21/30**；至少 6 題是誠實拒答卻被判 a=0——`ABSTAIN_RE` 收了「查不到／無法找到／not found」卻**漏收「未找到／找不到」**，屬判準器詞表缺口。補詞後 pack A@L3 由 0.033 升至 **≥0.300**（下界） |
| 「behavior 1.000 > shuffled 0.967 故 A@L3 有證據力」 | **排序邊界假象**。shuffled 於 L3 區塊內為 29/29＝1.000，該 0.967 之唯一失分題只是 `(i+1)%len` 洗牌撞到區塊邊界；McNemar exact 雙尾 **p=1.0**。且 v2 §Phase 1 判準 B 早已逐字預註冊「A@L3／A@L4 無論拿多少都證不了事，結論必須寫成『三軸交互目前不可量測』，**不得寫成成立或不成立**」——原判讀違反此預註冊 |
| 「grammar 7 題截斷」 | **實為 10 題**。item 52/54/60 因 Ollama 回應缺 `done_reason` 鍵而躲過 `done == "length"` 偵測、被當有效計分（n_tok=0） |
| 「grammar 數字全不可用」 | 過度概括。五格中三格（L1.F／L1.P／L3.A）零截斷完全乾淨；且把 7 題當答錯計入後，五格證據力等級**無一翻轉** |
| 「evidence_protocol 有洞會產生假綠」 | 介面缺口成立，但 `evidence_level` **全 repo 零呼叫端**，故非既成假綠而是未接線之設計缺口。真正的活洞在 `--compare` 之逐層拆解表**不帶 INVALID 旗標**，人抄那串數字時旗標已被洗掉 |
| 「A0–A12 驗收 PASS 12」 | **A4 是橡皮圖章**（claude 當日自寫）：只數 gain=true 列數就蓋 PASS，從不讀 `gain_evidence`、從不呼叫 `evidence_level`，且 `UNION ALL` 只取首列連加總都沒做到。已改為逐列真讀證據；誠實計數為 **PASS 11 · N/A 2** |
| 「pack 不應接線」 | 射程錯。`local_model_version` 實查 pp_3ab2efebb04e **已 status='serving'、promoted_by='hugo'**。問題不是「要不要接」而是「**要不要 retire**」，屬 H2 人閘 |

## 四、凍結集本身之結構缺陷（完整性批判者所補，全部實查）

- **L1 無 A 軸 ⇒「照抄＋加料」零成本**：實測把 snippet 照抄再附加「本文於 1987 年獲 Nobel 獎、被引 99999 次」，F=1.000、P=1.000。帳本實查 **pack 有 8/30 的 L1 答案出現題幹裡沒有的年份**、grammar 2/30，F 仍全判 1。**RAG 幻覺（有片段仍加料）正是 advisor 的真實失效模式，而這格結構上量不到**——且機器用來閉合 (c) 的正是這支 L1 捏造率最高的臂。
- **L4 全部越出宣告領域**：`_l4` 之 SQL 漏 `domain = ANY(DOMAINS)` 過濾；實查來源 domain 共 17 域（chemistry 4、social_sciences 3、medicine 3…），**quant_finance／software_engineering 零題**。整集 25% 為跨域雜訊。
- **L4 之「歧義」多為 SSOT dedup 髒值**：如「Y. Çengel」vs「Yunus A. Çengel」、「El-Halwagi」vs「El-halwagi」（僅大小寫）——測的是模型能否察覺知識層去重失敗。
- **L3 合成題名 15 題全為字母序連續四詞且集中 A–C**（`_synthetic_absent_titles` 先 `sorted(set(words))` 再取連續切片）：「字母序連續 → 答查無」是零知識啟發式即可通關的表面 tell。
- **實質獨立素材約 75 個而非 120**：L1 與 L2 是同 30 個 source_key 的配對（僅差表頭）；L1/column_catalog 子群答案空間只有 VARCHAR(7)/NUMERIC(3) 兩值——shuffled 之 0.1667 全部來自此子格的鄰題撞答（`shuffled@column_catalog=0.500`、`@knowledge_item=0.000`、`@field_correlation=0.000`）。
- **floor 不是地板，是任選的一條弱字串**：單一常數「查無 多筆」同時通吃 L3.A=1.000 與 L4.A=1.000；`BOILERPLATE_ARM` 在該二格拿 0 **只因它剛好不含「查無」「多筆」二詞**。`behavior_rubric._selftest` 那句「地板臂全滅＝舊尺敗因之機械鎖」為**空證**。
- **哨兵全綠 ≠ 尺可信**：`verify_eval_set_validity.py` 實跑 0/120 漂移，但它只驗題幹事實是否仍與 live DB 相符，**不驗答案是否寫在題幹裡、不驗層別是否可由格式推得、不驗答案空間是否退化**。

## 五、須 hugo 拍板（AI 不得代決）

| # | 事項 | 為何機器不能代 |
|---|---|---|
| S-1 | **(c) 之處置**：走 GATE-raise 把實作改成對齊凍結原文（(c) 轉未達成），或裁定 (c) 本來就該讀成判準 A | 效果上升嚴；且屬凍結條款之解釋權 |
| S-2 | **H6／V2-RUBRIC-go 判準器修補三件**：① `ABSTAIN_RE` 補「未找到／找不到」；② L1 補 A 軸或 F-precision 軸以擋「照抄＋加料」；③ 把 `BOILERPLATE_ARM` 換成真地板 | 改判準器即換 `eval_code_hash`，既有七臂全部退出可比範圍（計畫書 §718 H6 已明載） |
| S-3 | **新增第五支對照臂「零知識格式規則機」**，並把「須嚴格勝過規則機」寫進 evidence_protocol 鐵則 | 新增判準，非修 bug |
| S-4 | **凍結集是否重建**（L4 越域／L3 字母序 tell／L1-L2 配對／答案空間退化／層別格式可辨） | 修任一項都換 `set_id`，作廢現有七臂與 (c) 的既有載體 |
| S-5 | **H2：pack pp_3ab2efebb04e 是否 retire** —— 它同時是機器用來閉合 (c) 的臂、也是 L1 捏造率最高的臂（8/30） | 現役 serving 之去留＝P5.W2 人閘 |
| S-6 | **SUNSET (b) 基線位移**：條文寫「active 由 2 成長」，今日 14:28 R6 自動 demote 5 支後實為 active=1。認列基線仍為 2／重錨／暫停 R6 對 prodset 之寫入 | 凍結條文之比較基線被自動規則動過 |
| S-7 | **榮譽制認領**：`evolution_prereg_gate` V2-SUNSET 列 `approved_by='hugo'@2026-07-27 15:31:50`，但同列 note 仍逐字寫著「approved_by 誠實留 NULL……hugo 親跑 UPDATE 填」。請認領此次 UPDATE 是否為本人所跑 | §8.1：本機無法區分 AI 與 hugo |
| S-8 | **判準 A 之語意權**：其原文自帶「能力數字」「可複現」二詞，但數值門檻（>0.167 且 >0）已被常數字串臂 0.2333 與零知識規則機 1.000 越過 | 治權判準之解釋權（CLAUDE #26 決策層） |

## 六、claude 已逕行處置者（皆屬「停止宣稱未經證實者」，不含判準變更）

1. 週報 (c) 改三態記 ⚠ 未判定，未判定不計入達成數（§一）。
2. `verify_evolution_acceptance.py` A4 由橡皮圖章改為逐列真讀 `gain_evidence`；驗收誠實計數 PASS 12 → **PASS 11 · N/A 2**。
3. 本檔登錄全部事實與待決清單。

**未動**：`behavior_rubric.py`、`build_eval_set.py`、`evidence_protocol.py` 之判準本體，`eval_code_hash` 維持 `f3075238eb55`，七臂資料一列未改。

---

## 七、處置後記（2026-07-28，唯增列）

hugo 逐字拍板「**V2-RUBRIC-go與SUNSET-C-align 都給**」。S-1（(c) 對齊凍結原文）與 S-2 三件＋S-3（robot 第五臂）已執行，登錄與新尺實測＝`audits/V2-RUBRIC-GO-20260728.md`；換尺 `f3075238eb55 → ef142e9374c1`（舊 run 留檔未刪）。§一之「⚠未判定」過渡態退場，(c) 現依凍結文字誠實顯示**未達成**（首半成立於舊尺、複現無）。**S-4／S-5／S-6／S-7／S-8 仍開放待裁**，不因本批而假關。

## 八、S-7 結案（2026-07-28，唯增列）

hugo 親跑 `UPDATE evolution_prereg_gate SET note = note || ';;2026-07-28 hugo 認領:07-27 15:31 之 approved_by UPDATE 為本人親跑' …`（對話中貼回 `UPDATE 1`，經查庫驗證 note 已含認領句）。**S-7 結案**：該次 approved_by 填寫為本人親簽，檔面矛盾已補正（唯增列）。殘餘開放：S-4（計畫書起草中）、S-5（待新尺 pack 數字）、S-6（待 hugo 一句話）、S-8（併 S-4 計畫書裁）。

## 九、S-6 結案（2026-07-28，唯增列）

hugo 拍板「**S6-基線2-keep**」：SUNSET (b) 之比較基線**認列維持 2**（甲案）。理由錄要：R3 之 sign-refuted demote 為誠實結果，把基線改小＝放寬、違「GATE 只升不降」；基線維持 2 只是讓 (b) 誠實地變難。週報既按此口徑顯示，無碼變更。殘餘開放：S-5（待新尺 pack 數字，臂跑中）。S-4/S-8 已由 `EVALSET-V2-go` 進入執行（登錄=`reports/augur_evalset_v2_rebuild_plan_20260728.md` §七補正）。
