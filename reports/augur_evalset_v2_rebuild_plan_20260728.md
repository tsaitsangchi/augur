# 凍結集 v2 重建計畫（S-4）＋ 能力判準 A′ 預註冊（S-8）——合併裁決案

> **性質**：[I] 計畫書（#20 計畫先行；hugo 2026-07-28「S-4＋S-8 計畫書交付」）。**拍板前零實作**。
> **上位**：`audits/V2-RUBRIC-GO-20260728.md`（新尺 `ef142e9374c1` 已生效）／`audits/V2-SUNSET-C-DISPUTED-20260727.md` §四（本案要修的五個實證缺陷之出處）。V2-SUNSET 凍結文字**不動**。
> **一句話**：現行凍結集每一格都被零知識格式機通吃（robot 五格 1.000）＝**無任何格能證明能力**；本案重建一個「robot 通不過」的集，並在其上預註冊新能力判準 A′——判準與量尺一起生、一起凍。

---

## 一、為什麼舊集救不回來（僅引已實證者，不重論證）

| # | 缺陷（07-27 對抗驗證實查） | 病灶位置 |
|---|---|---|
| D1 | **層別由題幹表面 100% 可推**（`[檢索片段]`/`[無檢索片段]`/問句欄數），robot 憑此五格全 1.000 | 出題模板 |
| D2 | L1 之 facts **逐字印在題幹**，echo 臂滿分——F@L1 量的是照抄不是知識 | `_l1_l2` 設計 |
| D3 | **L3/L4 的正確行為是常數可達的**：「查無 多筆」四字通吃兩格——因為集內 absent 題全 absent、ambig 題全 ambig，**盲答永遠對** | 無對照孿生 |
| D4 | L4 全部越出宣告領域（17 域、quant_finance/software_engineering 零題）；L3 合成題名字母序連續（`sorted` 後取連續切片）；L1/L2 同 30 個 source_key 配對；L1-CC 答案空間僅 VARCHAR/NUMERIC 二值 | `_l4` 漏 domain 過濾／`_synthetic_absent_titles`／`_l1_l2`／`_cc_rows` |
| D5 | 哨兵 `verify_eval_set_validity.py` 只驗題幹事實與 live DB 相符，不驗 D1–D4 任何一項 | 驗收缺位 |

## 二、v2 設計核心：**對照孿生（contrast twins）**

D3 是根病：只要「同一種題殼永遠對應同一種正確行為」，行為就能被常數複製。修法不是把題殼藏得更深（藏不住，D1 實證），而是**讓同一題殼下的正確行為取決於 DB 真值**：

```
L3′ 存在性孿生:同一題殼問「文獻《X》的出處?」
   ├─ X 實際存在(庫內可查)→ 正確=報出 facts(F 軸計分)
   └─ X 實際不存在        → 正確=拒答(A 軸計分)
   → 盲答「查無」在存在題全滅;盲報 facts 在不存在題全滅;
     **不知道 DB 真值的任何策略,期望 ≤ max(p,1−p)=0.5**(存在/不存在各半)
L4′ 歧義孿生:同一題殼問「《Y》的作者?」
   ├─ Y 對應唯一列 → 正確=單一斷言(F 軸)
   └─ Y 對應多列   → 正確=列候選/明示多筆(A 軸)
   → 盲答「多筆」在唯一題全滅
```

孿生格＝**能力格**（答對需要知道庫裡有什麼）；L1/L2 保留為**行為格**（誠實承認其天花板本就是格式可達——L1 量「忠實用片段」、L2 量「無片段不憑權重」，robot 能過是**設計如此**，不再冒充能力證據）。這個二分寫死在集內（`expect.cell_class ∈ {behavior, capability}`），判讀端與週報永不混用。

**建集時驗收閘（機械、過不了不凍結）**：
- G-R **robot 不得通吃**：對草集實跑 robot 臂，capability 格 robot ≤ **0.60**（理論盲答上界 0.5＋抽樣寬容）；行為格不設此閘（設計即格式可達）。
- G-C ceiling 全格 = 1.000（尺可滿足）。
- G-F floor（最強退化常數）於 capability 格 ≤ 0.60，剖面全數落帳。
- G-D 全題 `domain = ANY(DOMAINS)`；G-T 合成缺席題名非字母序連續；G-I L1 與 L2 source_key 交集 = ∅；G-V 每格答案空間相異值 ≥ 8、同值題數上限 2；G-L 每題事實 live DB 可查核（沿 `verify_eval_set_validity`，擴 D1–D4 檢項）。

## 三、S-8 一併裁：判準 A 退史料 ＋ A′ 預註冊

**判準 A（v2 總控 §637）處置＝退史料，記兩句、不塗改**：
1. 數值門檻通過為真（behavior F@L1 0.933/0.9667 > 0.167 > 0）。
2. 能力語意經對抗驗證不成立（常數字串 0.2333、零知識規則機 1.000 皆越過同一門檻）——此後不得引為能力證據。

**判準 A′（隨 v2 集同批凍結，凍前可改、凍後唯 GATE-raise）**：

> LAIEVO 能力宣稱成立 ⟺ 任一**受測臂**於 v2 集之任一 **capability 格** `evidence_level ≥ weak`（＝同尺嚴格勝過 floor ∧ mismatched ∧ **robot**），**且同臂 ≥2 個獨立 run 皆成立**（run_id attempt 序已可記錄）。行為格之分數只得宣稱「行為合規」，永不得宣稱能力。

SUNSET (c) 凍結文字不動；其「任一臂在 F@L1」自然落在 v2 集的 F 格上由既有對齊實作判讀——A′ 是**更嚴**的能力宣稱標準，兩者並存不衝突（A′ 嚴格蘊含 (c) 首半）。

## 四、(a) Table schema（v1.39.0：零新表；讀寫落點全列）

| 表 | 角色 | v2 變更 |
|---|---|---|
| `local_model_eval_item`（讀寫） | 凍結集本體：`item_id, set_id, layer, prompt, expect(jsonb), source_sample_id, source_key(jsonb), gen_code_hash, created_at` | 零 DDL。新 `set_id`＝新列並存；`expect` 內**新增鍵**：`cell_class`（behavior/capability）、`truth`（exists/absent/unique/ambiguous，孿生真值）、既有 `facts/ssot/candidates` 沿用 |
| `local_model_eval_run`（寫） | 各臂結果（新尺 attempt 序已上） | 零變更；v2 集之 run 以新 set_id 自然分尺 |
| `local_model_eval_set_check`（寫） | 建集驗收帳 | 零 DDL；`check_json` 記 G-R…G-L 逐閘結果與 robot/floor 剖面 |
| `knowledge_item`／`column_catalog`／`field_correlation`（唯讀） | 題源 SSOT | 不動；L3′ 存在側直接取庫內真列、缺席側合成鍵**經庫內反查證無**後才入題 |

## 五、(b) Python 程式規畫

| 檔 | 動作 | 簽名／要點 |
|---|---|---|
| `scripts/build_eval_set.py` | **v2 改寫**（同檔升版，`_gen_hash` 自動換） | `_l3_twins(cur,n)`／`_l4_twins(cur,n)`：同殼孿生各半、真值經庫內實查；`_l4` 補 `domain=ANY(DOMAINS)`；`_synthetic_absent_titles` 改 md5 散選（棄 sorted 連續切片、仍確定性）；`_l1_l2` 拆為不相交 source_key 兩池；`_cc_rows` 改取「型別＋語意陷阱句」雙事實（棄二值退化）；`build(--dry-run)` 內建 G-D/G-T/G-I/G-V 自檢,任一紅即不寫庫 |
| `src/augur/evolution/behavior_rubric.py` | judge 擴 twin 模式 | `judge(raw, expect, source_text)` 依 `expect.truth` 分流：exists/unique→`fact_exact`（含加料否決）、absent→`abstain_ok('absent')`、ambiguous→`abstain_ok('ambig')`——**函式全數沿用，只加分流**；`eval_code_hash` 隨之升版（有意識換尺程序同 07-28） |
| `scripts/eval_local_model.py` | 零邏輯變更 | robot/floor 照跑於新集（robot 對 capability 格之低分即 G-R 之證） |
| `scripts/verify_eval_set_validity.py` | 驗收擴項 | 增 D1–D4 檢查（層殼統計、facts 是否印在題幹之外洩檢、孿生真值與 live DB 一致性重驗） |
| `scripts/verify_evolution_acceptance.py` | A′ 接線 | A4 之 `arms` 證據判讀已在；增 A′ 專檢（capability 格＋≥2 run） |

## 六、分階段・驗收・停損

| 階段 | 內容 | 驗收（機械） | 停損 |
|---|---|---|---|
| P0 | hugo 拍板本計畫（含 A′ 文字） | 拍板碼 `EVALSET-V2-go` | 未拍不動 |
| P1 | builder v2＋rubric twin 分流＋自測 | 各 `--selftest` 綠；`--dry-run` 出草集統計 | — |
| P2 | 草集過八閘（G-R…G-L） | **robot capability 格 ≤0.60**、ceiling=1.000、逐閘落 `eval_set_check` | 任一閘紅→改集不改閘；連 2 輪紅→回報 hugo |
| P3 | 凍結（寫庫、`set_id` 落定）＋離線五臂 | 五臂剖面落帳並出對照表 | — |
| P4 | LLM 臂（behavior/grammar/pack 若在役）×2 run | A′ 首次可判（含複現）；SUNSET (c) 由對齊實作自然判讀 | 臂 100% 截斷→查 harness 不改判準 |
| P5 | 判準 A 退史料登錄＋週報/驗收接 A′ | audit 增列；`verify_evolution_acceptance` A′ 檢綠 | — |

**回滾**：v2 集為新 `set_id` 並存，舊集與全部舊 run 留檔不刪；任何時點可退回只讀舊集（但舊集已證無可證格，退回＝放棄能力量測）。
**成本**：建集＋離線閘為秒級；P4 LLM 臂 2 run ≈ 2×4h45（背景過夜）。**明確不做**：不動 SUNSET 凍結文字、不動 arena/TWEVO/RAWEVO 任何判準、不引外部 API（題源全在庫內，零 usage 零放量）。

---

**待你一個字**：`EVALSET-V2-go`（P0）。拍板即依 P1–P5 自動往下；A′ 文字若要改，改在拍板前——凍結後唯 GATE-raise。
