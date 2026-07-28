# P4/P5 通路計畫（SRC-QUALIFY）——REGIME-MAP 判入倉之 probe 證據波＋pacing 政策落值

> **性質**：[I] 計畫書（#20 計畫先行；hugo 2026-07-28「P4/P5通路擬草案」）。**拍板前零實作**。
> **位置**：SRC-AUTO（`augur_source_auto_review_plan_20260728.md`）§八預告之「P4/P5 通路＝下一提案」——本案即該提案。承 REGIME-MAP-v1（已核）：P1 路乙已可判入，但判入倉全數卡 P4_probe（probe 零證據）與 P5_pacing（pace/quota/est_scale 全 NULL）。

## 一、目標與邊界

讓「license 已由人簽規則判為 public_domain/cc_whitelist」的 re3data 倉，以**機械可驗**方式補齊 P4（probe 證據）與 P5（限速前置）——之後 SRC-AUTO 既有管線（P2 抽核 20 → `--run` 週上限 50）才有非空的「可自動」桶。**本案不改審批規則、不碰 approve 動作、不接 harvest**。

## 二、承重事實（2026-07-28 親驗五件，全 (b) DB query／code 事實）

| # | 事實 | 含義 |
|---|---|---|
| F1 | harvest 兩路選源皆須 `query_template` 非空（`harvest_knowledge.py:100-117`）；re3data 列全空 | **批准≠抓取**：active 後不入任何排程 |
| F2 | re3data 全 3,507 列 `enabled=False`；SRC-AUTO run() 不碰 enabled；harvest 亦要求 `s.enabled` | **雙重隔離**：auto-approve 後＝「license/probe 已驗之休眠池」；點火（enabled+query_template+adapter）＝另案 |
| F3 | 協定分佈（2,301 已充實）：REST 460／**OAI-PMH 270**／FTP 244／other 199…；**P1 路乙過 335，其中具 OAI-PMH＝48**（外推全量 ~510／~73） | 唯 OAI-PMH 有標準機械探法（`?verb=Identify`）；REST 異質、裸 2xx＝弱證據 |
| F4 | `est_scale` 型別 **TEXT**、全庫零既有值；`judge_source` 之 `est <= EST_SCALE_CAP` 在 est 非 NULL 時將 **str-vs-int TypeError 崩**（現靠全 NULL 短路倖存） | 提前拆彈：P5 謂詞須 int 強轉（非數字＝誠實 fail）；est_scale 慣例由本案首定 |
| F5 | `review_log.action` CHECK 封閉枚舉（propose/probe/approve/activate/suspend…）；probe CLI 不變式＝「純寫 review_log 證據、不改 approval_status」（其 docstring 明文） | pacing 落值之 provenance 不入 review_log 新 action，改記 `adapter_config->'pacing'`；probe 波與落值步**分離** |

## 三、設計：兩步分離（網路證據步 × 純 DB 落值步）

```
P1 路乙判入 ∩ 具 OAI-PMH 端點(首波 ~73 倉)
  ── 步① probe 證據波(有網路;#24/#25) ──────────────
  │  每倉兩個最小請求:
  │    GET {oai}?verb=Identify                → http_status+repositoryName(格式實證)
  │    GET {oai}?verb=ListIdentifiers&metadataPrefix=oai_dc(僅首頁)
  │                                           → resumptionToken@completeListSize(若倉提供)
  │  寫 review_log(action='probe', probe_result={http_status,protocol:'OAI-PMH',url,
  │    elapsed_ms,complete_list_size?,note})——與既有 probe 列同形狀,P4 查核零改
  ── 步② pacing 落值(零網路、純 DB、oracle 可裁) ────
  │  凡「P1 過 ∩ 近 30 日 2xx OAI-PMH probe」:
  │    pace_seconds/quota_limit ← source_pacing_policy(protocol='OAI-PMH')之人簽值
  │    est_scale ← probe 證據之 complete_list_size(倉自報真數;無則留 NULL=誠實不過 P5)
  │    provenance ← adapter_config->'pacing'={policy:'v1',probe_review_id,at}
  ── 既有管線(零新機制) ─────────────────────────────
     dry 重分桶 → 「可自動」桶首次非空 → P2 抽核 20(hugo) → --run 週上限 50
```

**為何兩步分離**：步①是唯一網路行為者（證據入 review_log 可溯 #10）；步②純 DB＝本地審議引擎 oracle 可裁域（#28），且守 F5「probe CLI 純證據」不變式。

**est_scale 慣例（本案首定）**：存倉自報 `completeListSize` 之十進位字串（如 `'8214'`）＝「probe 當日倉宣告記錄數」。>50,000 → P5 誠實不過＝必人（本來就是煞車）；倉不提供 → NULL → 不過 P5（不編數 #9）。

## 四、(a) Table schema

**新表一張**（政策值＝「決定行為的資料」→ 住 DB #29b；沿用 `src_whitelist_guard()` 誠實閘）：

```sql
CREATE TABLE IF NOT EXISTS source_pacing_policy (
    protocol     TEXT PRIMARY KEY,            -- 'OAI-PMH'(首波唯一列)
    pace_seconds NUMERIC NOT NULL CHECK (pace_seconds >= 1.0),   -- 不低於 acquire 預設
    quota_limit  INTEGER NOT NULL CHECK (quota_limit > 0),
    citation     TEXT NOT NULL CHECK (btrim(citation) <> ''),
    decided_by   TEXT NOT NULL CHECK (btrim(decided_by) <> ''),
    decided_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- + pace_pol_row/pace_pol_stmt trigger(同 src_whitelist_guard:DELETE/TRUNCATE 拒、UPDATE 須 GUC)
```

**既有表讀寫落點**（零 DDL）：

| 表 | 讀/寫 | 欄位 |
|---|---|---|
| `knowledge_source` | 讀 | `adapter_config->'re3data'->'apis'/'licenses'`（端點與 P1 判入） |
| `knowledge_source` | **寫**（步②） | `pace_seconds`／`quota_limit`／`est_scale`（TEXT，十進位字串）／`adapter_config||'pacing'` |
| `knowledge_source_review_log` | **寫**（步①） | `action='probe'`、`probe_result` jsonb（同既有形狀＋`complete_list_size`）|
| `license_regime_map` | 讀 | 步①②之 P1 判入複用 `classify_licenses()` |
| `source_pacing_policy` | 讀 | 步②政策值 |

## 五、(b) Python 程式規畫

| 檔 | 動作 | 職責與簽名 |
|---|---|---|
| `scripts/migrate_source_whitelist_ddl.py` | 擴（同支第三表） | `source_pacing_policy`＋雙 trigger；斷言 4→6；`--apply/--dry-run/--selftest` |
| `scripts/probe_knowledge_source.py` | 擴（新模式） | `--re3data-wave [--limit N]`：選「P1 路乙過 ∩ 具 OAI-PMH ∩ 無近 30 日 probe」逐倉兩請求；純函式 `pick_oai_endpoint(apis)`、`parse_identify(xml)`、`parse_list_size(xml)`（fixture selftest）；步調 1.5s／連 5 錯熔斷 rc=75／resume＝跳過已有新鮮 probe；`--re3data-probe-one`＝#25 單倉先行。**不變式不破**：仍純寫 review_log |
| `scripts/set_source_pacing.py`（新，動詞片語） | 新 | 零網路：`--dry-run`（列將落值倉+值來源）／`--run`（UPDATE 三欄+provenance）／`--selftest`；冪等（已有 pacing provenance 者跳過）；est_scale 唯取 probe 證據之 `complete_list_size`，無則誠實跳過並計數 |
| `scripts/auto_review_sources.py` | 修一處 | **F4 拆彈**：P5 之 est 以 `int(str)` 強轉、非數字/負數＝誠實 fail；selftest 加 3 鎖（文字數字過/垃圾文字不過/超限不過） |

## 六、護欄與停損

- **放量授權**：步①＝~73 倉 × 2 請求 ≈ 150 個對**各異主機**之最小 GET（單主機負載=2 請求；步調 1.5s 全程 ~4 分鐘）。仍屬對外放量 → **拍板碼即授權、不另問**；ERR_FUSE=5 連錯熔斷；401/403/timeout＝誠實記 probe 失敗（該倉留人工桶），不重試風暴（#24）。
- **probe 時效**：PROBE_FRESH_DAYS=30——auto-approve 須在 probe 後 30 日內用掉；過期＝dry 重新掉回 P4 桶（機制既有，重跑步①即補）。
- **quota_limit 誠實註記**：現行 acquire 只讀 `pace_seconds`（`acquire_knowledge.py:331`），`quota_limit` 落值後暫屬**宣告值**（enforcement＝未來 harvest 接線案）；P5 謂詞要求「已設」照舊成立，不佯稱已 enforce（#8）。
- **不碰之物**：approval_status（唯 SRC-AUTO `--run` 既有路）；enabled（維持 False 休眠池）；query_template／adapter（harvest 點火另案）；REST/FTP/other 協定（見 §八）。

## 七、分階段・驗收（機械）・停損

| 階段 | 內容 | 驗收 | 停損 |
|---|---|---|---|
| Q0 | hugo 拍板 `P4P5-go`＋**政策值親核**（提案：OAI-PMH `pace_seconds=2.0`／`quota_limit=500`；理由：機構型小主機保守步調；欄位語意見 §六註記）＋est_scale 慣例認可 | 拍板碼；政策一列入表（decided_by 繕打鏈同 REGIME-MAP） | 未拍不動 |
| Q1 | migration 第三表＋probe 擴模式＋set_source_pacing＋P5 拆彈；selftest 全綠；`--re3data-probe-one` 單倉實測（#25） | 三支 selftest 綠＋單倉 probe 列落 review_log 且形狀相容 | 單倉失敗→查明才放量 |
| Q2 | 步①放量（~73 倉；熔斷/resume）→ 步② `--dry-run` 過目 → `--run` 落值 | probe 2xx 數／complete_list_size 命中數／落值倉數三數字誠實呈報 | 熔斷 rc=75 即停 |
| Q3 | dry 重分桶：「✅ 可自動」首次非空 → **P2 抽核 20 交 hugo**（SRC-AUTO 既有關卡，20/20 一致才開 `--run`） | 分桶表＋抽核清單 | 抽核不過→修謂詞再抽 |

## 八、明確不做＋開放點

**不做**：REST/FTP/other 裸 2xx 當 P4 證據（弱證據＝假信心；若日後要收 REST 大宗，另案定「REST 格式實證」判準）；est_scale 估算/編造（唯倉自報數）；本波 approve（仍走 SRC-AUTO 週上限＋P2 抽核）；harvest 點火。

**開放點（不阻拍板，屬 Q0 一併裁）**：O1 政策值 2.0s/500 可改，唯 `pace_seconds ≥ 1.0` CHECK 為底線；O2 若 hugo 認為 completeListSize 缺失倉（OAI-PMH 常見選填）值得救，可另議「ListRecords 首頁計數×頁數上界」估法——**預設不做**（估算＝#9 灰區，寧留人工桶）。

## 九、完整性自審（#20 對抗自問發現表）

| 自問 | 發現與處置 |
|---|---|
| 批准後會不會被 cron 抓爆？ | F1+F2 雙隔離親驗（query_template 空＋enabled=False）→ 不會；寫入 §二 |
| P5 填值後謂詞會不會炸？ | 會——F4 str-vs-int 拆彈列為修補項（§五） |
| probe CLI 不變式會不會被破？ | 差點——初稿曾想讓 probe 順手寫 pace；依其 docstring 明文改兩步分離（§三） |
| provenance 有沒有住所？ | review_log action 枚舉封閉（F5）→ 改 `adapter_config->'pacing'`，含 probe_review_id 可回鏈 |
| 放量規模誠實嗎？ | 73 倉外推自 48/2,301 實測交集，非拍腦袋；全量 enrich 收槍後 Q2 前重算實數 |
| 30 日時效誰維護？ | 既有 PROBE_FRESH_DAYS 機制自然表達；過期倉 dry 自動掉回 P4 桶，無需新機制 |

**待一個字**：`P4P5-go`（含 Q0 政策值；要改值請一併給）。
