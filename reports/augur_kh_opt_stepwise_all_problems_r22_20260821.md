---
title: 本地 AI·KH 閉環自我進化——全問題逐步執行最佳下一步（可先／可同步）r22
status: current_kh_exec_nav
series: kh_optimization_plan
round: r22
date: 2026-08-21
viewpoint: 2026-08-21T15:35+08:00
layer: "[I]"
role: KH **長板選刀**（與市場 B3／tip **分軌**）；後續 KH 開工跟本檔
ssot_code: KH-OPT-R22-20260821
parent_evolve: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
trigger_plan: reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md
supersedes_as_exec_nav:
  - reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
inherits_exec:
  - reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
market_orthogonal: reports/augur_opt_stepwise_all_problems_r22_20260821.md
k9_plan: reports/augur_k9_domain_ft_go_plan_20260813.md
k9_adopted: audits/K9-DOMAIN-FT-PLAN-ADOPTED-20260821.md
kh8_plan: reports/augur_kh8_discrim_plan_first_20260813.md
s0_executed: audits/KH-S0-APPLY-EXECUTED-20260821.md
self_reported: true
---

# 本地 AI·KH 閉環自我進化——全問題逐步執行 r22（2026-08-21 15:35）

> **一句**：S0–S9 全 ok（本窗 drain 63→0）。KH 最佳下一步＝**守穩態**，不是加深、不是他域開訓。  
> **分軌**：不等 08-21 價、不讓 B3 指揮 KH；B3 開火時只讓 `augur_llm.lock`。  
> **長冊仍在**：evolve readout 20260806。本檔＝選刀／可先∥。不創 [N]。

---

## §0 怎麼用

```text
問「KH 下一步」→ 本檔 §1／§1b
問「市場下一步」→ r22 市場開工鎖（本檔不答 tip／B3）
禁：用假 B3／hold-#1 擋 KH；用 KH 進度擋／催 B3
```

**Hard doors（KH only）**

```text
FZ/GATE-keep(知識) | T0 no-web-dialog-approve | T2-system-ok
| PDF-C-no-ASR | ASR=owned_local+local_private only
| no-KH10 | KH8-prod-stop-at-7 | E-keep-until-θ
| no-relax-θ | no-fake-depth8 | ingest S0-S9 | apply=opt-in
| no-calendar-fake-evolve | AUTO-LIFT 碼預設 off；禁抬>KH2
| 有 item 引文禁假「無此內容」 | 空包不進化 | 禁整庫回填當修無回覆
```

---

## §1 決策卡｜現在該做什麼？（KH）

LIVE **2026-08-21 15:35+08**（親查 `--check`）：

| 錨 | 值 |
|---|---|
| S0 kh0_breach | **0**（本窗 `KH-S0-apply-go` 63→0） |
| items | 286 339 |
| eligible | 146 338 |
| S3 游標 lag | zh／en **0** |
| priority_hit | **∅** → no-op |
| admit_depth | 0:139 613 · 7:146 001 · **9:2**（預存；≠本槍抬層） |
| 問法矩陣 `--offline` | **PASS**（本窗） |
| KH8 disc | 仍 **ok=False**（08-13 plan-first；本窗未重跑母體） |
| K9 分隊 | **adopted** A–E；**未訓**；S8 仍 not_auto |

| 問 | 答 |
|---|---|
| **KH 全線最佳下一步** | **守穩態。** `--check` 保持 ∅。不開 K8／K9 訓／K10。S0 再 FIRE 才另 `KH-S0-apply-go`。 |
| **可先（此刻、不等價）** | 問法 `--offline`（已 PASS）；可選 `kh_private_smoke` 輕抽；T0 抽樣守；compact 運維。 |
| **可同步** | 上列彼此可並行；B3／長 LLM 開火則讓路。 |
| **不要做** | 默 `--apply`；放寬 θ；假 depth≥8；他域 FT 無單隊 GO；C1 灌預測；空包當進化；PDF-C 接 ASR |

```text
paste（KH 選刀鎖，不是市場 B3、不是 K9 開訓）:
  KH-OPT-R22 | S0=0 | S3=0 | E-keep | stop-at-7
  | no-fake-depth8 | no-relax-θ | apply=opt-in
  | no-K9-train | no-K10 | no-KH10 | no-market-axis
```

---

## §1b 四欄

### 須 GO（本檔不夠）

| 槍 | 要貼的句 | 做完 |
|---|---|---|
| S0 再破口 | `KH-S0-apply-go` | kh0_breach→0；`up_to=0` |
| S3 lag | 點名 concordance catch-up | **本窗已跑** pending=0（zh／en 游標已頂） |
| K9 adopt | `K9-DOMAIN-FT-plan-adopt` | **本窗已閉**；分隊 A–E 生效；**仍不訓** |
| K9 首隊 FT | `K9-DOMAIN-FT-C-quant-go` | 本窗兩槍 limit=1000×2；累計落地 91；depth=7；殘 5444 另句 |
| KH8 下一刀 | `KH8-DISCRIM-A3-…-go` 或雙明示 L3 | 母體仍可能 ok=False |
| K10 C1 | 另 GO；標隔離 | 禁默加權 predict |
| 問法 LIVE 矩陣 | 明示（連庫／可碰 LLM） | FAIL→修問法，不整庫回填 |
| AUTO-LIFT 常駐 | 運維旗＋抽測 | 禁抬 >KH2 |

### 可先（現在就能做）

| # | 做 | 不做 | 本窗 |
|---|---|---|---|
| **C0** | `python scripts/kh_ingest_trigger.py --check` | `--apply` 除非 S0 FIRE＋GO | **已跑** ∅ |
| **C1** | `python scripts/kh_query_form_matrix.py --offline` | 把 PASS 當加深 | **已跑 PASS** |
| **C2** | 可選 `kh_private_smoke.py` 輕抽 | ASR→PDF-C | 未跑（可∥） |
| **C3** | 守 T0：抽樣無 web／對話 approve | 對話裸放行來源 | 守 |
| **C4** | compact／逐步口吻運維（8b＋編號約束） | 當缺件回填 | 守 |

### 可同步

C0 ∥ C1 ∥ C2 ∥ C3 ∥ C4。  
**不可同步**：`--apply`、K9 訓、KH8 L3、K10、長 LLM 與 B3 搶鎖。

### 禁

KH10；放寬 MIN_MINORITY_MASS；宣稱 depth≥8 進化成功；日曆假進化；空 SSE 寫庫；假「無此內容」有 cite；整庫回填修無回覆；抬 >KH2。

---

## §2 全問題板（KH）

> 🟢＝本窗不當工單。❄／禁＝不要排進「可先」。

### 2.1 訊號／底線／閉環

| # | 對應 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **K0** | S0／K-01 | D-Data 破口 | `--check`；FIRE 才 `KH-S0-apply-go` | check＝是 | 避開長 LLM | 🟢 0 |
| **K1** | S3 | items 游標 lag | 追上另句 | 本窗＝否 | — | 🟢 0；本窗 catch-up 確認 |
| **K2** | 階 A–C | ingest 階梯 | 守 apply 選開 | — | — | 🟢 |
| **S1** | 新 item | 擴大入庫 | 有界 QUAL；不日曆進化 | 監看＝是 | 是 | 🟢 delta=0 |
| **S2** | 新 eligible | 命中池擴大 | 可選 readout 抽 1 | 監看＝是 | 是 | 🟢 delta=0 |
| **S4** | parser skip | Writer／ASR | 同族≥3 才 plan | **否** | — | 🟢 0 |
| **S5** | 假拒 | 有件卻「無此內容」 | 走 cite 閘；禁回填 | 複現才開 | 文件＝是 | 🟢 閘在 |
| **K16** | S5 碼 | 假 decline 閘 | 保持載入 | — | — | 🟢 已入倉 |
| **K17** | K16 回歸 | 閘＋8399 套 | 盯同類標題題 | 抽樣＝是 | 是 | 🟢 |
| **K3** | S6／K-02c | AUTO-LIFT | 碼 off；禁抬 >KH2 | **否**（抬層） | 旗監看＝是 | 🟢／禁抬層 |
| **K4** | S7 | 私有 smoke | `kh_private_smoke.py` | **是**（輕） | **是** | 🟢 可選 |
| **K6** | S7 | ASR 對聽 | 可選抽樣 | **是**（輕） | **是** | 🟢 |
| **K5** | PDF-C | Doc1 純圖 | hold；不 OCR 硬開 | **否** | — | 🟢 hold |
| **K7** | 口吻 | 8b 逐步／4b 弱 | 守 8b＋編號；4b 不當產品尺 | 運維＝是 | 是 | 🟢 8b |
| **K13** | ext+ask | 檔名.ext＋問句 | 已硬化；修問法必跑矩陣 | 矩陣＝是 | 是 | 🟢 |
| **K14** | 問法閉集 | 回歸矩陣 | `--offline` 可先；LIVE 另句 | offline＝是 | 是 | 🟢 本窗 offline PASS |
| **K15** | D-FillAuto | 欄位=值 | 守；擴包另句 | — | — | 🟢 |
| **K-02b** | 地板 | D-Answer 抽測 | 可續 live 抽 | **是** | **是** | 🟢 stub |
| **K-05** | 治權 | T0／T2 | 守；抽樣 | 抽樣＝是 | 是 | 🟡 守 |

### 2.2 加深／他域／隔離（本檔不開）

| # | 對應 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **K8** | S9／K-03 | KH8 鑑別 | **E-keep／stop-at-7**；plan-first 仍 ok=False | **否** | **否** | ❄ |
| **K9** | S8／K-04 | 他域 FT | 殘 DOI 5444 另 limit；**本窗兩槍已跑** | **否** | **否** | 🟡 C 2×1000 已閉 |
| **K10** | K-08 | C1→feat | 另 GO；禁默加權 predict | **否** | **否** | 🔴 隔離 |
| **K11** | parse | `.msg`／rar | skip-hold | **否** | **否** | 🔴 |
| **K12** | K-10 | KH10 | — | **否** | **否** | 禁（≠市場 H10） |
| **depth9** | 預存 | admit_depth=9 有 **2** 件 | **不**當進化成功；不為對齊去抬層 | **否** | — | 🟡 記實 |

---

## §3 閉環 8 節 → 本窗

| 節 | 本窗 |
|---|---|
| 1 製造／准入 | 守既有 raw；不開新 parser 族 |
| 2 D-Data | ✅ breach=0 |
| 3 D-Hit | 守；游標 0 |
| 4 D-Readout | 守；假拒走閘 |
| 5 D-Compact | 守 8b＋凍引文 |
| 6 答對抬層 | 碼在、旗 off；禁 >KH2 |
| 7 加深 KH3–9 | **阻塞**＝K8 未過 |
| 8 回饋 | 人改料另句；禁對話 approve 來源 |

---

## §4 工作包（開跑複製）

### WP-C0｜巡檢（可先）

```text
WHEN: 任意；避開 B3 長 LLM
DO:   python scripts/kh_ingest_trigger.py --check
DONT: 無 FIRE＋GO 卻 --apply
DONE: 本窗 15:25 priority_hit ∅
```

### WP-C1｜問法離線（可先∥）

```text
WHEN: 改問法前／本窗核對
DO:   python scripts/kh_query_form_matrix.py --offline
DONT: LIVE 矩陣當本鎖；PASS 當 KH8 綠
DONE: 本窗 MATRIX PASS (offline)
```

### WP-S0｜drain（須 GO）

```text
WHEN: S0 FIRE 且 Steward 貼 KH-S0-apply-go
DO:   python scripts/kh_ingest_trigger.py --apply   # up_to=0
DONT: 抬層；第二槍 S3
DONE: 本窗已閉 63→0；再破口才重開
```

### WP-K8｜停在 7

```text
WHEN: 永不單靠本檔
DONT: 放寬 θ；無雙明示 L3；宣稱 depth≥8
RETRY: 新 KH8-DISCRIM-*-go
```

### WP-K9｜C 有界 FT 已閉

```text
WHEN: 再灌須另貼 K9-DOMAIN-FT-C-quant-go | limit=N
DONT: 把 skip 當綠；admit>7；全域同時灌
DONE: 槍1落地42 kip-45；槍2落地49 kip-46；depth=7；殘 DOI 5444
```

---

## §5 與市場正交

市場 r22：tip＝08-20；刀 B＝等 08-21 價。  
**不**因市場 WAIT 停 KH 巡檢；**不**因 KH 綠去跑假 B3。

---

## §6 何時刷新（KH r23）

S0 再 FIRE；K9 FT-go；KH8 新 GO；K10 GO；問法 LIVE 矩陣失敗。  
**不因**市場 08-21 心跳單獨改本檔（除非搶 LLM 要記一筆）。

---

## §7 驗收

- [x] S0–S9 LIVE 入板  
- [x] 每列最佳下一步＋可先＋可同步  
- [x] 與 20260813 長板對帳；LIVE 已過期者（S0=63）已覆寫  
- [x] 不開訓、不放寬 θ、不代 commit  

*完。[I] · KH 獨立選刀 r22。*
