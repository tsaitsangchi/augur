# 來源審批半自動化計畫（SRC-AUTO）——機械謂詞自動批＋本地 AI 僅諮詢/僅收緊

> **性質**：[I] 計畫書（#20 計畫先行；hugo 2026-07-28「可做計畫書改為依本地AI判斷自動審批嗎?」）。**拍板前零實作**。
> **痛點實查**：`knowledge_source` **proposed 積壓 3,528**（全 `generic_json`、license 全未定、跨 5 域，主體為 re3data 目錄型倉儲）；現行 approve 走 TTY＋superuser CLI（「唯人」），review_log 全譜＝ratify 69／probe 7／approve 3——**逐源人批 3,528 不可行**，自動化訴求成立。

## 一、誠實在前：「依本地 AI 判斷」直接裁決，撞四條現行憲政

| # | 撞什麼 | 原文/出處 |
|---|---|---|
| 1 | **能抓≠該抓、新領域入庫＝決策層人拍板**（憲章知識層多域擴充準則） | 入庫准入是治權判準；AI 裁決＝拆人閘 |
| 2 | **LLM 意見零證據力**（本地審議引擎憲政，hugo 2026-07-11 拍板） | 讓 LLM 當審批官＝與自家審議憲政自相矛盾 |
| 3 | **本地 AI 能力尚無 A′ 證據**（v2 集今晚首判；舊集已證其分數多為格式可達） | 把大門交給能力未證的模型＝用未校準儀器當守門員 |
| 4 | **利益衝突（最重）**：來源入庫 → 成為 LAIEVO 教材母體 → **模型在選自己的教材** | Goodhart 直通車：模型會系統性偏好「讓自己好答」的來源；今天整天在修的正是這類自我強化假訊號 |

故本計畫**不做** AI 裁決。但你已兩次採用的 **PME-AUTO-B 同型**（人簽規則一次、機器在規則內自動：R1–R7、R2 auto-APPLY）完全適用——把「判斷」換成「機械謂詞」，AI 只留兩個零裁決權角色。

## 二、三層審批管線（核心設計）

```
proposed ──► L-M 機械謂詞層(六謂詞全過 → auto-approve;唯一自動路)
                P1 license ∈ {public_domain, cc_whitelist}——查「provider license 白名單表」
                   (人 seed、帶 citation;#29b 資料驅動,新 provider=INSERT 非改碼)
                P2 domain ∈ 既核域集(hugo 已拍過的域;新域=必人)
                P3 adapter ∈ 既有 adapter(零新碼;generic_json 在列)
                P4 probe 通過(既有 probe CLI:可達+格式+單筆最小樣本 #25)
                P5 est_scale ≤ 上限 且 pace/quota 已設(#24 限速前置)
                P6 (AUTHORITY-TIER-go 過後)tier ∉ {T3,T4}(廠商/媒體=必人)
      ├──► L-A 本地 AI 諮詢層(**零裁決權**):對 probe 樣本產 80 字摘要+風險旗標,
      │       只寫 review_log.reason 供人快掃;意見零證據力、不進任何謂詞
      ├──► L-V 本地 AI 否決權(**只嚴不鬆**):AI 可標 hold_for_human(升人閘),
      │       **不可放行**——方向不對稱與「GATE 只升不降」同構,合憲
      └──► 人閘保留域:新 domain/新 adapter/新 license 類/T3-T4/suspend-resume/白名單表增列
```

**留痕與監督**（P5.W5：監督形式改變、總量不降）：每筆 auto-approve 寫 `review_log(actor='auto_rules_v1', reason=六謂詞逐項結果+規則版本)`；R6 週日 digest 加「本週自動審批」段供掃視認領；admin `/gov` 頁 governed 口徑同步計入。**開閘節流**：每週自動批上限 50 源（首月），無事故再議提額——3,528 不一次開。

**事故熔斷**：任一自動批之源被事後 suspend／或 harvest 首輪撞 license 爭議 → 自動批**全域暫停**、餘量退回人閘，待人查明才復。

## 三、(a) Table schema（v1.39.0）

| 表 | 動作 |
|---|---|
| `source_license_whitelist`（**新**） | `(provider_pattern TEXT PK, license_regime TEXT CHECK(∈四值), citation TEXT NOT NULL, decided_by TEXT NOT NULL, decided_at)`——P1 的資料側；**人 seed 帶可核出處**（如 re3data＝CC BY 4.0 目錄、其收錄倉儲各自 license 逐 pattern 判）。誠實閘：DELETE 拒、UPDATE 須 GUC |
| `knowledge_source` | **零 DDL**（P6 之 tier 欄屬 AUTHORITY-TIER-go 另案） |
| `knowledge_source_review_log`（既有） | 零 DDL；auto-approve 寫 `actor='auto_rules_v1'`、`reason`＝謂詞逐項 JSON 字串 |

## 四、(b) Python 程式規畫

| 檔 | 職責 | 簽名 |
|---|---|---|
| `scripts/migrate_source_whitelist_ddl.py`（新） | 白名單表＋誠實閘 | `--apply/--dry-run/--selftest` |
| `scripts/auto_review_sources.py`（新） | 謂詞引擎：逐 proposed 跑 P1–P6 → 全過 auto-approve／部分過留 proposed＋記缺哪項／觸人閘域升 `hold_for_human` | `--dry-run`（**分桶統計**：可自動 n／缺 license n／缺 probe n／必人 n）`--run --limit 50`（週上限）`--selftest` |
| `probe_knowledge_source.py`（既有） | P4 重用（#12 不重造） | 既有矩陣 |
| `report_triple_evolution_week.py` | R6 digest 加「本週自動審批」段（唯讀） | 既有 |
| `serve_admin_console.py` | `/gov` 頁 governed 口徑計入 auto 批；digest 頁同步 | 既有路由擴 |
| L-A/L-V 諮詢與否決 | `local_llm_mcp` 之 `local_summarize` 對 probe 樣本產摘要；輸出僅入 `reason`；含風險詞（paywall/PII/版權聲明異常）→ 標 hold_for_human | 第二階段（P3 後）才接，首月純機械跑 |

## 五、分階段・驗收・停損

| 階段 | 內容 | 驗收（機械） | 停損 |
|---|---|---|---|
| P0 | hugo 拍板 `SRC-AUTO-go` ＋ **白名單表首批人 seed**（我出草案、你逐 pattern 核——license 判定=法務性判斷=人） | 拍板碼＋白名單 ≥1 列 | 未拍不動 |
| P1 | migration＋謂詞引擎＋`--dry-run` 分桶報告（3,528 全量統計） | selftest 綠；dry 分桶數字出爐 | — |
| P2 | **抽核 20 源**：dry 判「可自動」者隨機 20，人工逐一覆核 | 20/20 與人判一致才開閘；任一不一致→修謂詞再抽 | 連兩輪不過→回報重議 |
| P3 | 低量開閘：`--run --limit 50`（週上限）＋R6 digest 段 | 首週 50 源零事故；digest 呈現 | 熔斷條款（§二） |
| P4 | L-A 諮詢＋L-V 否決接線；月報後議提額 | 否決僅單向之 selftest 鎖 | — |

**明確不做**：LLM 放行權（永不）；license 由 AI 判（白名單＝人 seed）；新域自動；3,528 一次全開；繞過 probe 或限速。

## 六、一句話總結

> 你問的「依本地 AI 判斷自動審批」，安全的形態是：**判斷交給人簽過的機械謂詞，本地 AI 只能「多攔」不能「放行」**——3,528 積壓中凡 license 白名單可判、probe 可過、域已核者自動放行（估大宗），真正需要判斷的殘餘才進你的閘。待你一個字：`SRC-AUTO-go`（P0，連同白名單首批草案我隨即出）。

---

## 七、P0–P1 落地實錄＋白名單首批草案（2026-07-28，`SRC-AUTO-go` 後）

**已落地**：`source_license_whitelist` 表（誠實閘：citation/decided_by 禁空、UPDATE 須 GUC）＋`auto_review_sources.py` 謂詞引擎（六謂詞、週上限 50、熔斷、留痕逐謂詞 JSON；selftest 15 條全綠）。

**首輪 dry 分桶（3,528 全量）**：`✅ 可自動 0｜✗ P1_license 3,528`——**fail-closed 如設計**。誠實真相：積壓大宗（~3,520）是 re3data 逐倉儲目錄列，**無 license metadata、多數無 API 端點、pace/quota/est_scale 全未設、probe 全未跑**——它們不是「等審批的來源」，是「等驗證的目錄」。瓶頸不在審批而在**逐倉驗證**，故：

**P1.5 增補提案（re3data 充實步，待你點頭）**：re3data 官方 API 每倉皆公佈 `dataLicense` 與 API 端點——以受控步調（#24）逐倉查詢回填 `note`/端點/license 線索，之後 P1/P4/P5 謂詞才有料可判。約 3,520 次免費 API 呼叫＝放量行為，依 #24/#26 **須你明示**（一字：`SRC-ENRICH-go`）；不點頭則 re3data 大宗誠實留在人工/擱置桶。

**白名單首批草案（6 pattern；解鎖的是未來新 proposed 之已知 provider，非 re3data 大宗）**——逐列核後**親跑** INSERT（decided_by 由你簽，AI 不代填）：

| pattern | regime | citation（依據） |
|---|---|---|
| `arxiv%` | cc_whitelist | arXiv API ToU：metadata CC0；全文依逐篇授權 |
| `openalex%` | cc_whitelist | OpenAlex：資料 CC0（docs.openalex.org/license） |
| `crossref%` | cc_whitelist | Crossref metadata：公開再利用（REST API terms） |
| `europepmc%` | cc_whitelist | Europe PMC OA 子集＋open metadata |
| `doaj%` | cc_whitelist | DOAJ metadata CC0 |
| `gutenberg%` / `gutendex%` | public_domain | Project Gutenberg 公版 |

```sql
-- 核可後親跑(每列一句;decided_by 請維持 'hugo'):
INSERT INTO source_license_whitelist (provider_pattern, license_regime, citation, decided_by)
VALUES ('arxiv%','cc_whitelist','arXiv API ToU: metadata CC0','hugo');
-- (其餘五列同式,pattern/regime/citation 依上表)
```

**P2 抽核前提**：白名單 ≥1 列後 dry 才會出現「可自動」桶；屆時抽 20 人工覆核 20/20 一致才 `--run` 開閘。

---

## 八、REGIME-MAP-v1 落地實錄（2026-07-28，「REGIME-MAP-v1 核可」後）

**簽核件（hugo 核可原文範圍）**：R1 CC0／Public Domain／publicdomain-zero／pddl → `public_domain`；R2 URL 含 `/licenses/by/` 或 `/licenses/by-sa/` → `cc_whitelist`；R3 OGL／OGLC → `cc_whitelist`；R4 `odc-by` → `cc_whitelist`；**R-X 其餘一切（other／Copyrights／-nc／-nd／軟體授權／unknown）→ 人閘 fail-closed**；一倉多授權→取最嚴。

**落地**：
- `license_regime_map` 表（`migrate_source_whitelist_ddl.py` 同支擴充；kind∈name|url、regime 僅二值、UNIQUE(kind,pattern)、同誠實閘 lic_map_row/lic_map_stmt）；**10 列 seed**（R1×5/R2×2/R3×2/R4×1），`decided_by='hugo(對話拍板)'`、citation 註繕打鏈（§8.1 不冒充親簽）。
- `auto_review_sources.py` P1 擴為**兩路**：路甲=source_key 白名單（原）；路乙=`classify_licenses()` 純函式吃 `adapter_config->'re3data'->'licenses'` 證據查映射表——**NC/ND code 側一票否決先於映射、name 整詞匹配（防 'OGL' 誤中 'Google'）、url 子字串、多授權取最嚴、任一未映射=None 人閘**。selftest 26 條全綠（含 11 條路乙新鎖）。
- **首輪 dry（enrich 進行中 601/3,507 已充實）**：路乙判入 **61** 源（~10%，與抽樣估 12% 同量級）——如設計移入 `P4_probe` 桶，**不會因映射落地就繞過 probe/pacing**。enrich 全量收槍後全量重分桶；P4/P5 通路（對映射倉之 probe＋pacing 預設）＝下一提案、另簽。

---

## 九、P2 通過＋P3 首批實錄（2026-07-28，`P2-16-核可＋P7-go`）

- **P7 落地**：`pick_endpoint_winners()` 純函式（每 normalized base 取 min(source_key) 代表、已 active 端點封鎖、無端點證據 pass-through）＋4 鎖；dry 分桶=「七謂詞全過 16／P7 重複端點 16」。
- **首批實批 16/16**：與 P2 核可表**逐列完全一致**（機械對帳）。途中撞 `chk_ks_active_needs_approval` 閘＝**正確教訓**——裸 UPDATE 繞不過 approved_by 要求；改走正規 `curation.transition` 兩步（approve→activate、各自留痕），HUMAN_ONLY 之授權鏈=SRC-AUTO-go＋P2-16-核可，`approved_by='auto_rules_v1'` 誠實機器名不冒人簽（curation.py 零改動）。
- **不變式終驗**：16 列全 `enabled=False` 休眠池；入 harvest 排程數=0；週餘額 34/50；熔斷 clear。
- 未簽項不動：`R2-錨定` 未給=R2 pattern 照舊。
