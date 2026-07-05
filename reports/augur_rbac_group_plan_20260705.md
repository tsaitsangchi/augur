# augur RBAC 群組規劃計畫（企業管理為最高原則）

🎯 **白話**：RBAC 機制（P1–P4）已就緒、目前 fail-closed（非 super 看不到任何 domain）。本計畫依**企業管理原則**（職能部門對映／最小權限／職責分離／需知原則／層級）把現存 40 個知識 domain 規劃成**權限群組 → domain 授權矩陣**。

> **✅ 已建置（2026-07-05，用戶「照預設全建」拍板 §8.2#1）**：7 職能群組 + 26 授權邊界域 + grant 矩陣**已落地 DB**（`scripts/build_rbac_enterprise_groups.py --build`，冪等）；`local_private` 擁有者收窄**已接線**（讀路徑 `clean_item_sql`/`retrieve_all`、寫路徑 `acquire_local_files.py --owner-user-id`）。醫療生技部（§6.1）預設未建、`--with-medical` 可加。**尚待你做**：建帳號 + 派人入組（`manage_rbac_user.py --create-user/--add-to-group`）——群組結構已備、人事你填。
守原則 #5（最小權限/職責分離）· #1（RBAC 只作用讀取可見性、不觸預測）· #19（決策層拍板前先攤清）· 憲章 v1.29.0（RBAC 準則 (i)-(vi)、works 側已裁）。日期：2026-07-05。

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

## 4. `is_authz_boundary` 拍板清單（§8.2#3，授權前置）— ✅ 2026-07-05 已拍板

> **〔用戶拍板 2026-07-05〕依企業管理為最高原則，§2 矩陣所 grant 之 26 域全數升 `is_authz_boundary=true`**（每個可授的 domain 才能成為授權邊界、否則 `--grant-domain` fail-closed 擋下）。**判準＝「該域已對映某企業職能且被某群組需知」才升邊界**（能抓≠該授、§0.2 最小權限）；未被任何群組 grant 的 14 域（§3 未歸屬 + 生醫選配未啟用時）**維持 `is_authz_boundary=false`**、留 superuser 個案處置。

**26 個授權邊界域**（8 管理 + 18 知識）：
- 管理（8）：`mgmt_philosophy`·`business_mgmt`·`organization_mgmt`·`rd_mgmt`·`finance_mgmt`·`accounting_mgmt`·`investment_mgmt`·`production_mgmt`
- 知識（18）：`engineering`·`chemistry`·`materials_science`·`energy_materials`·`solar_materials`·`chemical_engineering`·`electronics`·`physics_and_astronomy`·`physics`·`computer_science`·`mathematics`·`economics_econometrics_and_finance`·`business_management_and_accounting`·`decision_sciences`·`environmental_science`·`energy`·`psychology`·`social_sciences`

> **企業管理理據（為何是這 26）**：邊界＝「劃入某部門需知範圍」的域。管理 8 域＝八大職能部門本職；知識 18 域＝各部門**需知**之技術/財經/組織素養域（研發→11 技術科學域、財務/會計/投資→3 財經商管域、生產→環境/能源、組織→心理/社科）。**生醫 10 域**（medicine 等）＝選配、**僅生技/製藥企業啟用時**才一併升邊界（§6.1）；一般企業維持 false、留 superuser。
> **domain 標註正確性＝安全命門**（§6.6）：一旦域成授權邊界，入庫時 domain 標錯＝越權洩漏。上線前以 `audit_domain_hygiene.py --audit` 校核既有標註無誤（見 §5 CLI 步驟 0）。

---

## 4.5 `local_private` 跨使用者歸屬（誰的 private 誰能看；§8.2#4）— ✅ 2026-07-05 已拍板

> **〔用戶拍板 2026-07-05〕依企業管理為最高原則**：私有上傳＝**個人工作文件**，採**最小權限 + 需知 + 職責分離**——**擁有者本人 ＋ superuser 才看得到，跨使用者/跨部門一律 fail-closed 看不到**。

| 內容類 | `corpus_class` | 擁有欄 | 可見範圍（誰能看） | 收窄機制 |
|---|---|---|---|---|
| **個人私有上傳** | `local_private` | `owner_user_id` = 上傳者 | **擁有者本人 ＋ superuser** | `AND (x.owner_user_id = %s OR <is_super>)`（**擁有者收窄**，非 domain 收窄） |
| **owner 未定**（legacy/NULL） | `local_private` | `NULL` | **僅 superuser**（無法判擁有者→不外洩、fail-closed） | 回填前強制 |
| **（選配）部門共享私有** | `local_private` | `owner_group_id`（未來欄） | 群組成員 ＋ superuser | 需加 `owner_group_id` 欄、需拍板（§6.6） |

**企業管理三原則落地**：
1. **最小權限**：私有預設只有本人看得到（＋superuser 治理需知）；非本人、非同群組一律看不到。
2. **職責分離（SoD）**：A 的私有絕不洩漏給 B——**即便同部門亦然**（除非升「部門共享私有」選配、需拍板）。
3. **需知原則**：私有＝個人需知；superuser＝系統治理需知（備份/稽核/交接/離職接管）。

**擁有權指派（何時寫 `owner_user_id`）**：ingest（webupload Mode A）當下、從登入 session 的 `user_id` 寫入 `owner_user_id`——**上傳者即擁有者**；未登入不得 ingest（P4 已 gate）。

**既有 NULL 回填**：現存 `local_private` items（`owner_user_id` NULL）→ 指派給 `admin`（唯一既有 superuser 帳號）或維持 superuser-only 直到人工判定擁有者。

**三路徑收窄總表**（RBAC 讀取三分）：

| 內容類 | 收窄軸 | 非 super 已登入看得到？ |
|---|---|---|
| **works**（哲學/文學公版經典） | 無（對全登入者公開，§6.5） | ✅ 全部（未登入 deny） |
| **knowledge / 財經 items** | **domain 群組 grant** | 僅所屬群組被 grant 的 domain |
| **local_private** | **擁有者 `owner_user_id`** | 僅本人上傳的（＋superuser） |

---

## 5. 落地 CLI（照憲章計畫完整性＝機制執行指令）

### 5.0 一鍵全建（已執行 2026-07-05；冪等可重跑）
§2 矩陣的**邊界 + 群組 + grant 一次落地**——矩陣資料驅動（`CORE_GROUPS` 字典）、複用 `manage_rbac_user` 之 cmd 函式（#12）、單一交易、落稽核：
```bash
python scripts/build_rbac_enterprise_groups.py               # 無參數:印矩陣(不寫)
python scripts/build_rbac_enterprise_groups.py --dry-run     # 預覽
python scripts/build_rbac_enterprise_groups.py --build       # 落地 7 群組+26 邊界(已執行)
python scripts/build_rbac_enterprise_groups.py --build --with-medical   # 併醫療生技部(§6.1)
```
建帳號 + 派人入組（人事，另走）：
```bash
python scripts/manage_rbac_user.py --create-user --username alice        # getpass 密碼
python scripts/manage_rbac_user.py --add-to-group --username alice --group 研發部
python scripts/manage_rbac_user.py --explain-access --username alice     # 驗:應列研發部 12 域
```

### 5.1 逐項 CLI（granular；調單一授權/新部門用）

> 順序：拍板邊界 → 建群組 → 授權 → 建人 → 派組。範例（研發部）：

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

## 6. 決策狀態（決策層 §8.2）

### 已拍板（2026-07-05）
- **§6.5 works 側 A/B 裁決 ＝ B「對所有登入者公開」**（§8.2#5）：哲學/文學公版經典原文＝全體共享素養底座，對**所有已登入使用者公開、不 domain 收窄**（CLEAN 閘仍過），未登入 fail-closed deny。**已入憲章 v1.29.0（RBAC 準則 (vi)）＋ code（`retrieval.retrieve`）＋ 測試（T3）**。
- **§4 授權邊界 ＝ §2 矩陣 26 域**（§8.2#3）：依企業管理，被某群組需知的 26 域升 `is_authz_boundary=true`；生醫 10 域選配（見 §6.1）、其餘留 false。
- **§4.5 local_private 歸屬 ＝ 擁有者本人 ＋ superuser**（§8.2#4）：私有＝個人工作文件、最小權限/需知/SoD、跨使用者 fail-closed。
- **superuser ＝ `admin`**（§8.2#2）：既有 bootstrap 帳號、密碼 `admin`（⚠️ 弱、對外前須改）。

### 仍待你拍板（影響建群範圍）
1. **§6.1 企業型態**：是否啟用「醫療生技部」（§2 選配）？決定生醫 10 域（medicine 等 12262 列）納入群組（並升邊界）或全留 superuser。**預設＝不啟用**（一般企業）。
2. **§6.2 經營層 vs superuser**：`admin` 已 superuser；「經營管理層」群組要不要建（多人經營團隊 → 用群組；單一老闆 → superuser 即可）。**預設＝建群組**（可擴充）。
3. **§6.3 職責分離嚴格度**：投資部是否可讀 `finance_mgmt`（§2 現給）？嚴格 SoD 可收回、只留 `investment_mgmt`+econ。**預設＝§2 現況**。
4. **§6.4 未歸屬域**（§3）：貴企業是否有 agricultural/arts 等特定需求？**預設＝不授、留 superuser**。
5. **§6.6 部門共享私有（選配）**：是否要 `local_private` 可設群組擁有（`owner_group_id`、部門內共享）？需加欄、需拍板。**預設＝不做**（純個人私有）。

> **執行授權**：你已授權「照計畫往下做不用再問」（2026-07-05 入憲 §8.1）。上列 5 項若採**預設值**，我即可依 §5 CLI **產生完整建群腳本**（26 邊界 + 8 群組 + grant 矩陣 + local_private code 接線）供你一鍵落地；任一項要調整，指出即改。**本計畫＝政策設計**，群組與授權「誰看什麼」屬你（§8.2）。
