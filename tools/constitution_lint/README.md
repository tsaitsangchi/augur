# constitution_lint — §8.3 機器稽核雙 linter（骨架）

把憲章從「文件」變成「CI 可強制的制度」的最高槓桿基建。依《憲章展開總綱》§5.4、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39–45`。**純標準庫、零外部依賴**（CI 免安裝套件）。

> **治權自動化止於「判定與阻擋」，不及於「執行變更」** —— 本工具只報 finding／回非零退出碼，決不改內容、決不自動 apply 或合併（`AUGUR-MC v1.3 §P5.W2`）。

## 兩支 linter

| linter | 管什麼 | 檢查 |
|---|---|---|
| **compliance_lint** | 規格生效 | WM.40 front-matter 閉集欄位＋空值/空集顯式（error）／WM.41 七節齊備＋**固定序**（error）＋四項 (a)-(d) 覆蓋（warning／advisory）／WM.42 緊張節／WM.43 DEFER 雙向／WM.44 形式充分性覆蓋（warning）。**接受 minor 版落差不誤紅**。error＝規格不生效力。 |
| **audit_lint** | code 合憲 | 引用鏈雙合法終點（K→Evidence→Observation ∪ 明示宣告之假設，P4.E6）、Action→Identity 六元組、Knowledge 五元組、Confidence 存在性。以 AUD-01/03/10/11 為 failing 種子。 |

## 用法

```bash
python -m tools.constitution_lint --selftest                    # 紅綠自檢（WM v1.0 綠 / 壞樣本紅）
python -m tools.constitution_lint compliance specs/*.md         # 規格生效 lint
python -m tools.constitution_lint audit <code-dir> [--policy legacy|greenfield]
```

退出碼：任一目標有 error → 1；否則 0。`--policy greenfield`＝新 code merge 當下 finding 即 error；`legacy`（預設）＝既有系統以補正期追蹤（finding 為 warning）。

## 現況（骨架 v0.1）

**已完備（對真實輸入實測）：**
- compliance_lint 對 **AUGUR-WM v1.0 自檢綠**（含 `mc-version v1.2` vs 現行 v1.3 之 minor 落差正確判 info、不誤紅）；對 ONT/ID/KS 三草案聲明皆正確 PASS（兩種聲明編排——獨立標題式與單標題粗體子節式——皆認）；對三反例（無聲明/缺欄/缺原則節）正確判紅。
- audit_lint 框架 + 三示範種子規則，對 augur code 重現已知審計發現（AUD-01 之 37 檔 vendor 直綁、AUD-10 留痕表缺 actor 欄）。
- CI 定義：`tools/constitution_lint/github-workflow.yml`（selftest + 全規格 compliance-lint）。**啟用方式**：複製至 `.github/workflows/constitution-lint.yml`（需具 `workflow` scope 之推送權限；現行 gh OAuth token 無此 scope，故暫存為參考檔待 P5/具權限者啟用）。

**骨架邊界（隨後續階段強化，見總綱）：**
- **WM.41 四項 (a)-(d)** 為 **warning／advisory**（缺項不阻斷、hollow 七節仍 PASS）；升 error 會誤紅合法草案（如 ID draft 之 P5 不適用節），故完全強制待後續階段。七節齊備與固定序為 error（已強制）。
- WM.44 形式充分性目前為 **warning 級覆蓋報告**（有邊界比對，避免 EV.1 被 EV.10 掩蓋）；完全強制須待 MC [N] 條款嚴格枚舉（`mc_clauses.py` 現為正則骨架，含 §n 章與 §n.m 子條，另 Layer 2–7 之上層規格 [N] 條款枚舉未實作）。
- 多圍籬區塊時取首個具體聲明（非佔位）；真實規格每檔單一真聲明，此假設未觸發。
- audit_lint 完整規則集與語義嚴格度隨 **L3（Identity）/L4（Confidence）充任** 收緊（版本化 linter）；K→E→Observation 鏈完整性靜態稽核為 stub。
- linter 設為 **merge-gate（強制）** 留待總綱階段 9；本階段 CI 僅 error 阻斷、warning/info 不阻斷。
- audit_lint 於 augur **code repo** 之 CI 接線為後續（本 repo CI 僅跑 compliance_lint）。

## 檔案

- `model.py` — Finding/Severity/LintResult
- `mc_clauses.py` — 憲章 [N] 條款枚舉（WM.44 用）
- `compliance_lint.py` — 規格生效檢查器
- `audit_lint.py` — code 合憲骨架
- `__main__.py` — CLI + 紅綠 selftest
- `fixtures/` — selftest 正例（good_minimal）＋三反例
