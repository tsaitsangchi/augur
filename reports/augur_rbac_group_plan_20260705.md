# augur RBAC 群組規劃計畫（企業管理為最高原則）

🎯 **白話**：RBAC 機制（P1–P4）已就緒、目前 fail-closed（非 super 看不到任何 domain）。本計畫依**企業管理原則**（職能部門對映／最小權限／職責分離／需知原則／層級）把現存 40 個知識 domain 規劃成**權限群組 → domain 授權矩陣**，供決策層拍板。**本計畫＝政策設計提案（§8.2#1／#3 永遠人決策），非執行**——AI 不自建群組；你拍板後用 CLI 落地（末章）。
守原則 #5（最小權限/職責分離）· #1（RBAC 只作用讀取可見性、不觸預測）· #19（決策層拍板前先攤清）· 憲章 v1.28.0（RBAC 準則）。日期：2026-07-05。

> **據實接地（#1）**：40 域由 `knowledge_domain` 字典 + `knowledge_item` 內容量直查（非臆造）。8 管理域＝企業職能；32 為知識/學術素養域。

---

## 0. 企業管理 RBAC 五原則（設計最高準則）

1. **職能部門對映**：群組＝企業職能部門（研發/財務/會計/投資/生產/組織），非個人。組織調整＝改群組成員，零改權限結構。
2. **最小權限（least privilege）**：每群組只授**該職能所需** domain——管理域（本職）＋**需知**之知識素養域；**能抓≠該授**（有此域 ≠ 每群組都給）。
3. **職責分離（SoD）**：利益衝突職能之 domain 不重疊——**會計 ⟂ 投資**（記帳者不決策投資）、**財務 ⟂ 稽核**；跨部門視野只給經營層/superuser。
4. **需知原則（need-to-know）**：知識素養域按職能相關性授（研發→技術科學域；投資→經濟財經域），非「全給」。
5. **層級（hierarchy）**：superuser（系統管理員/最高經營者）不受限；部門群組 scoped；一人可屬多群組（grant 聯集）。

---

## 1. 群組層級（三層）

| 層 | 主體 | 機制 | 說明 |
|---|---|---|---|
| **L0 系統管理員** | `admin`（既有 bootstrap superuser） | `is_superuser=true` | 不受任何 domain 閘、見全部（RBAC 治理者） |
| **L1 經營管理層** | 高階經營者 | 群組`經營管理層`（跨職能治理視野） | 見各部門管理域全局，體現「經營全局視角」 |
| **L2 職能部門** | 各部門人員 | 部門群組（最小權限） | 只見本職 + 需知知識域 |

---

## 2. 群組 → domain 授權矩陣（企業職能對映）

| 群組 | 對映職能 | 管理域（本職） | 需知知識素養域 | SoD 註 |
|---|---|---|---|---|
| **經營管理層** | 高階經營 | `mgmt_philosophy`·`business_mgmt`·`organization_mgmt`·`decision_sciences` | — | 見經營全局、不下沉技術/財務細節 |
| **研發部** | R&D | `rd_mgmt` | `engineering`·`chemistry`·`materials_science`·`energy_materials`·`solar_materials`·`chemical_engineering`·`electronics`·`physics_and_astronomy`·`physics`·`computer_science`·`mathematics` | 技術知識、**不含財務投資** |
| **財務部** | Finance | `finance_mgmt` | `economics_econometrics_and_finance` | **⟂ 會計、⟂ 投資** |
| **會計部** | Accounting | `accounting_mgmt` | `business_management_and_accounting` | **⟂ 投資決策**（記帳≠決策，SoD 核心） |
| **投資部** | Investment | `investment_mgmt` | `economics_econometrics_and_finance`·`decision_sciences`·`finance_mgmt` | **⟂ 會計** |
| **生產營運部** | Production/Ops | `production_mgmt` | `engineering`·`environmental_science`·`energy` | |
| **組織人資部** | HR/Org | `organization_mgmt` | `psychology`·`social_sciences` | |
| **（選配）醫療生技部** | 生技/醫藥企業專屬 | — | `medicine`·`health_professions`·`biochemistry_genetics_and_molecular_biology`·`pharmacology_toxicology_and_pharmaceutics`·`immunology_and_microbiology`·`neuroscience`·`biology`·`nursing`·`dentistry`·`veterinary` | 僅生技/製藥企業啟用，一般企業不建 |

> **一人多群組**：如「研發長」＝經營管理層 ＋ 研發部（grant 聯集，見兩者）。

---

## 3. 未歸屬域處置（least-privilege 預設不授）

以下域無明確企業職能對映，**預設不授任何部門群組**（最小權限；僅 superuser/經營層依需要個案 grant）：
`agricultural_and_biological_sciences`·`arts_and_humanities`·`earth_and_planetary_sciences`·`general`。
理由：企業情境無標準職能需求（能抓≠該授）；若特定企業需要（如農企需 agricultural），再個案拍板加入對應部門。

---

## 4. `is_authz_boundary` 拍板清單（§8.2#3，授權前置）

**凡出現在 §2 矩陣被 grant 的 domain，須先拍板 `is_authz_boundary=true`**（否則 `--grant-domain` 被擋、fail-closed）。共需拍板 **26 個授權邊界域**（8 管理 + 18 知識）：
- 管理（8）：`mgmt_philosophy`·`business_mgmt`·`organization_mgmt`·`rd_mgmt`·`finance_mgmt`·`accounting_mgmt`·`investment_mgmt`·`production_mgmt`
- 知識（18）：`engineering`·`chemistry`·`materials_science`·`energy_materials`·`solar_materials`·`chemical_engineering`·`electronics`·`physics_and_astronomy`·`physics`·`computer_science`·`mathematics`·`economics_econometrics_and_finance`·`business_management_and_accounting`·`decision_sciences`·`environmental_science`·`energy`·`psychology`·`social_sciences`

> **domain 標註正確性＝安全命門**（§6.6）：一旦域成授權邊界，入庫時 domain 標錯＝越權洩漏。上線前應以 `audit_domain_hygiene.py` 校核既有標註無誤。

---

## 5. 落地 CLI（拍板後執行；照憲章 v1.27.0 計畫完整性＝機制執行指令）

> **執行者＝決策層人**（§8.2；AI 不自動跑）。順序：拍板邊界 → 建群組 → 授權 → 建人 → 派組。範例（研發部）：

```bash
# (1) 拍板授權邊界（§4 清單逐一;此處示範研發相關）
python scripts/manage_rbac_user.py --add-domain --domain rd_mgmt   --label 研發管理 --authz-boundary
python scripts/manage_rbac_user.py --add-domain --domain engineering --label 工程   --authz-boundary
python scripts/manage_rbac_user.py --add-domain --domain chemistry   --label 化學   --authz-boundary
# … materials_science / energy_materials / … 等研發需知域比照

# (2) 建群組
python scripts/manage_rbac_user.py --create-group --group 研發部

# (3) 授權群組可讀 domain（每域一列;--confirm）
python scripts/manage_rbac_user.py --grant-domain --group 研發部 --domain rd_mgmt     --confirm
python scripts/manage_rbac_user.py --grant-domain --group 研發部 --domain engineering --confirm
python scripts/manage_rbac_user.py --grant-domain --group 研發部 --domain chemistry   --confirm
# … 其餘研發需知域比照

# (4) 建人、派組（密碼走 getpass）
python scripts/manage_rbac_user.py --create-user --username alice
python scripts/manage_rbac_user.py --add-to-group --username alice --group 研發部

# (5) 驗證
python scripts/manage_rbac_user.py --explain-access --username alice   # 應列 研發部 → rd_mgmt/engineering/…
```
其餘部門（財務/會計/投資/生產/組織/經營層）比照 §2 矩陣。**加新部門/調授權皆 INSERT、零改碼（#29b）**。

---

## 6. 待你拍板 / 調整（決策層）

1. **企業型態**：是否啟用「醫療生技部」（§2 選配）？決定 32 知識域中生醫類（medicine 等 12262 列）是否納入任何群組，或全留 superuser。
2. **經營層 vs superuser**：`admin` 已 superuser；「經營管理層」群組是否需要，或高階經營者直接給 superuser？（建議：多人經營團隊 → 用群組；單一老闆 → superuser 即可）
3. **職責分離嚴格度**：投資部是否可讀 `finance_mgmt`（§2 給了）？嚴格 SoD 可收回、只留 `investment_mgmt`+econ。
4. **未歸屬域**（§3）：貴企業是否有 agricultural/arts 等特定需求？
5. **works 側（哲學/文學語料）**：§8.2#5 A/B 裁決——這些是「投資智慧經典原文」，是否對某些群組（如投資部/經營層）開放？現況非 super 一律 deny。

拍板後我可**產生對映的完整 CLI 腳本**（或依你選定的部門子集），你執行即落地。**本計畫不含執行**——群組與授權是「誰能看什麼」的企業政策，屬你（§8.2）。
