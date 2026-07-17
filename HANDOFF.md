# Augur 憲章 Repo — 交接文件

* **快照日**：2026-07-17
* **性質**：[I] 資訊性（不創設義務；權威悉依憲章與各層生效規格之 [N] 條款）
* **給誰**：接手本 repo 的人或 Agent

---

## 一句話現況

**L0–L6 已生效、L7 草擬完成但充任受阻。M2（全棧貫通）未達成 —— 且這是正確的**：本輪造出的機器 gate 證明，先前六層賴以充任的「形式關卡全綠」有假陽性成分，四份**已生效**規格共有 **39 個憲章誤標**。

## 兩個 repo（刻意分離）

| repo | 內容 | 位置 |
|---|---|---|
| **augur-constitution**（私有） | 本 repo。治權：憲章、L1–L7 規格、裁決、審計、linter | `/home/giga/augur` |
| **augur**（公開） | 程式碼實作 | `github.com/tsaitsangchi/augur`；本機參考 clone 在 `ref_augur/augur`（**已 gitignore**，勿提交） |

見 [ARCHITECTURE-OVERVIEW.md](ARCHITECTURE-OVERVIEW.md)（2 層 × 8 層 × 2 repo 對映）、[CONSTITUTIONAL-ROLLOUT-PLAN.md](CONSTITUTIONAL-ROLLOUT-PLAN.md)（九階段總綱）。

## 八層狀態

| Layer | 規格 | 狀態 | 誤標（新 gate 實測） |
|---|---|---|---|
| L0 Meta-Constitution | `constitution/META-CONSTITUTION.md` | ✅ **v1.3 生效** | — |
| L1 World Model | `specs/WORLD-MODEL-SPECIFICATION.md` | ✅ v1.0 生效 | 0 |
| L2 Ontology | `specs/ONTOLOGY-SPECIFICATION.md` | ✅ v1.0 生效 | 0 |
| L3 Identity | `specs/IDENTITY-SPECIFICATION.md` | ✅ v1.0 生效 | 🔴 **12** |
| L4 Knowledge System | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | ✅ v1.0 生效 | 🔴 **15** |
| L5 Cognitive Kernel | `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | ✅ v1.0 生效（§8.2 延後） | 🔴 **7** |
| L6 Agent Runtime | `specs/AGENT-RUNTIME-SPECIFICATION.md` | ✅ v1.0 生效（**含 §8.2 人類審查**） | 🔴 **5** |
| L7 Infrastructure | `specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md` | 🔴 **草稿，充任受阻** | 9 ＋ 擴欄 1 |

裁決：`constitution/RULING-2026-00{2,3,4,5,6,7}-*.md`；修訂登錄 `constitution/AMENDMENT-LOG.md`（AL-2026-001…011）。

---

## 本輪最重要的發現（接手者務必先讀）

### 1. 形式關卡（linter）曾連續三輪綠燈而實質錯誤並存

L7 草稿三輪對抗審查全數 **go=false**（阻斷 7 → 8 → 9），而 `tools/constitution_lint` **三輪都 error 0**。實證病灶：

* **F4 被標為「Automation First」**（真值 = Knowledge Without Identity）、**F5「Answer First」**（真值 = Intelligence Without Evidence）—— 代號對、內容全錯，骨架檢查只查「代號有沒有出現」故綠燈。
* 改對標籤後，**落點仍是幽靈引用**：F4 掛 L7.21，而 L7.21 五款無一課予欄位義務。

### 2. 病灶是跨層系統性的，不是 L7 獨有

新增之 **WM.44-LABEL** 檢查（標籤須為憲章原文）實測七份規格：

```
L1 0 ｜ L2 0 ｜ L3 12 ｜ L4 15 ｜ L5 7 ｜ L6 5 ｜ L7(draft) 9+1
                  └────── 39 個誤標在已生效規格 ──────┘
```

**鐵證**：同一誤標**逐字跨層複製** —— 「§3 = 公理金字塔/演化鏈總述」在 L5/L6/L7 一模一樣（真值 = Five Immutable Principles）；「§0 = 總則章」三份；「P4.W1 來源崇拜警語」四份。**起草者引用的是彼此的轉述，不是憲章原文。** L5 甚至把 **§8.1 標為「Amendment Log／編號穩定」，而 §8.1 = Constitution Steward** —— 指向完全不同的條。

### 3. gate 自己也犯了同一種病（最深的一層）

獨立審查官以**突變測試**證實：

* **README 宣稱的測試根本不存在**（「以修訂後 WM 副本實證跟隨 WM」）→「以起草者之轉述充作原文」遞迴發生在工具自己的文件上。
* **條款宇宙不完整**：MC §2 定義是 list item 不是 heading，故 **§2.5 Evidence／§2.6 Knowledge／§2.7 Intelligence／§2.10 Confidence 從未進入枚舉** → 「85 條全數涵蓋」是**假陽性**。
* **過半矩陣零檢查**：gate 只認 MC 側代號，TR.D/E/F/G（WM./ONT./ID./KS./L5./L6. 標籤）完全不檢。
* **子字串放行**：「Confidence 單一形式化」因含 `Confidence` 而綠燈。
* **靜默降級**：WM 讀不到時退回硬編碼副本且零 finding —— 程式碼實作了它自己指名為違憲的退路。

**教訓（寫給下一個 Agent）**：**永遠不要採信建造者對自己成品的自陳。** 本 session 每一次重大缺陷，都是獨立對抗審查（尤其突變測試）抓到的，不是自我檢查抓到的。

### 4. 連帶：既有裁決之證據基礎弱於當時所述

`RULING-2026-004/005/006/007` **全部**以「linter PASS（error 0）」＋「缺 0 條」為生效要件。現已知條款宇宙漏了四個核心定義、標籤檢查當時不存在。**這是待裁事項（見下）。**

---

## 等 Steward（人類）裁決的三件事

| # | 事項 | 為何只能人類 |
|---|---|---|
| **#22** | **四份生效規格 39 個誤標**：先更正？或先核發 §8.4 期限豁免？ | 改生效層是 §8.5／§8.6 修憲行為。**CI 接線為 merge-gate 前必須先裁**，否則一啟用即全紅 |
| **#23** | **L6.11 RT-2/RT-3 序異常**（§8.1 書面裁決） | 上層條文**彼此**不相容：L6.11 綁 RT-2 須「可重現驗證」（屬 KS CL.0 之 E3），而 RT-3 僅需「獨立 Data Evidence」（E2）→ 線性閉集上不可同時單調滿足。非 L7 填數值可解消 |
| — | **L7 §8.2 實質審查**（L7 生效前置） | L7 規格**自己明定**「本層之充任不得僅以形式關卡為據」；L7.90(d) 列六項必審 |

**另有一項結構性事實需你決定**：**單一自然人 Steward 使「雙人類獨立核准」物理上不可能成立**（L7.42(f) 要求二憑證不得同一主體持有，而你同時持有 owner 憑證與人類權威憑證）→ 凡須「RT-4 ＋ 雙人核准」者皆不可執行，**連棘輪的推翻程序本身都無法執行**。審查官指出根本解只能靠**拓撲變更**（監督平面移至獨立實體節點）。選項：接受（記為 residual、RT-4 事實上不可用）／指定第二人／拓撲分離。

## L7 尚未修的實質洞（§8.4 級）

* **`§P4.E1` 之 Evidence 欄無不可空義務** —— L7.21(f) 只補了 Source/Identity/instance-type。**Evidence 欄為 NULL 的 Knowledge 列，引擎層不會拒絕寫入**，之後可取得權威地位、成為 Action 依據。而 §P4.E1 是 **§8.4 不可豁免核心（連履行時程都不能豁免）**。
* **L6.11 RT-1/2/3 之「無未裁決致命 Conflict」要件無載體** —— E 階面與量測面兩面俱空；依 L7.45 自訂之規則，該三列登錄**自始無效**。

## 其他未決

* **PR #2**（code repo，`remediation/aud-02-consolidated`）：15 測試全過（真 PostgreSQL），**等你 P5 拍板 apply**。工作區 `/home/giga/augur-code-work`。
* **#21 審計基準重新對齊**：code repo 已前進（HEAD `4951aee`，原則精華 v1.9.1、系統架構大憲章 v1.46.0），AUD-01…26 之基準已漂移。
* **五份治權文件之合規聲明**補正期限 **2026-10-14**（RULING-2026-002 主文二）。
* 階段 3（production apply）阻於缺 production PG 位置＋P5；階段 4（基建部署）阻於 docker 權限。

---

## 給接手 Agent 的紅線

1. **不得修改任何已生效規格**（`specs/*-SPECIFICATION.md` 無 `-draft` 者）—— 那是 §8.5／§8.6 修憲行為。它們紅是事實，屬 Steward 事項。
2. **不得自我充任**、不得宣稱任何規格已生效、不得偽造「§8.2 人類審核已通過」的記錄。充任認定與 §8.2 是 Steward（人類）之權（§8.1／§0.5／§8.6）。
3. **不得自行解釋生效層的條文** —— 遇上層不相容（如 L6.11），正解是**據實揭露 ＋ 保守預設（取較嚴者）＋ 依 §8.1 聲請裁決**。
4. **不得以 linter 綠燈為充任依據** —— 已三度實證其與實質錯誤並存。
5. **不得為了讓數字好看而放寬判準**。gate 硬化後計數上升是**正確結果**。
6. `.env` 含 `GITHUB_TOKEN`（已 gitignore）—— 勿讀取、勿輸出。gh CLI auth 已涵蓋所有操作，該 token 可考慮撤銷。
7. **每段工作完成即 commit + push**（Steward 常設指示）。動工前先 `git fetch` —— 本 repo 曾多次被平行 session 推進。

## 工具與環境

* **§8.3 linter**：`python3 -m tools.constitution_lint {compliance|audit|selftest} <檔>` —— 純 stdlib、無外部相依。見 `tools/constitution_lint/README.md`。CI 檔存在 `tools/constitution_lint/github-workflow.yml`（**未接線**；gh token 缺 `workflow` scope 無法建 `.github/workflows/`）。
* **硬體**：GIGABYTE AI TOP ATOM（NVIDIA GB10）、**ARM64/aarch64**、121GiB 統一記憶體 —— 選型務必確認 aarch64 支援。見 `infrastructure/ENVIRONMENT-SPEC.md`。
* **PostgreSQL**：無 sudo／docker，用 micromamba + conda-forge `postgresql=16` 起 userspace PG 於 `127.0.0.1:55432`。
* **踩過的雷**：`psycopg2.extras.Json` **沒有** `default` 參數 → 須 `Json(x, dumps=lambda o: json.dumps(o, default=str))`。

## 進行中

**背景工作流程 `wbn9hogaf`**：硬化 gate（補條款宇宙、上層標籤檢查、括號名整體比對、真突變鎖、失準發聲）→ 七份規格重掃真實計數。三位驗證官專職**不信任造 gate 者之自陳**（突變測試／獨立枚舉母集／獨立複驗計數）。**預期計數上升。**

---

*本文件為 [I] 交接導覽。權威悉依《Augur Meta-Constitution》及各層生效規格之 [N] 條款。*
