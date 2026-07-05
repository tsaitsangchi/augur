#!/usr/bin/env python
"""依企業管理原則一鍵建 RBAC 群組(群組規劃計畫 reports/augur_rbac_group_plan_20260705.md §2 矩陣落地)。

🎯 這支在做什麼(白話):把「群組規劃計畫」§2 職能部門→domain 授權矩陣一次落地到 PostgreSQL——
   註冊授權邊界域(is_authz_boundary=true)→ 建職能群組 → 授權 group→domain。全冪等(ON CONFLICT、
   可重跑不重複)、單一交易、複用 manage_rbac_user 之 cmd_add_domain/create_group/grant_domain(#12 不重造 INSERT)、
   落 knowledge_access_audit(#10)。矩陣＝決策層拍板(§8.2#1/#3,2026-07-05「照預設全建」);**落地後 SSOT＝
   permission_group/group_domain_grant 表**(本 script＝一次性 seed、非 SSOT;跨機遷移用 pg_dump 該二表)。
   醫療生技部＝選配(§6.1 預設 off);`--with-medical` 才建(生技/製藥企業啟用)。
   本 script 不建帳號、不派人入組(那走 manage_rbac_user;群組結構與人事分離、組織調整=改成員零改權限)。
守 #5(最小權限/SoD)· #10(授權落稽核)· #29(資料驅動、冪等、指令矩陣、個別可執行)· 憲章 v1.29.0 §8.2。

執行指令矩陣:
  python scripts/build_rbac_enterprise_groups.py                 # 無參數:印矩陣摘要(不寫、安全預設)
  python scripts/build_rbac_enterprise_groups.py --dry-run       # 預覽將建什麼(不寫)
  python scripts/build_rbac_enterprise_groups.py --build         # 落地 7 群組 + 26 邊界(冪等;可重跑)
  python scripts/build_rbac_enterprise_groups.py --build --with-medical   # 併建醫療生技部(+10 域、8 群組)
"""
import argparse
import sys
from types import SimpleNamespace

import _bootstrap  # noqa: F401
from augur.core import db
import manage_rbac_user as m

# domain → 繁中 label(§4 授權邊界域字典;cmd_add_domain 會 upsert label_zh)
DOMAIN_LABELS = {
    "mgmt_philosophy": "經營哲學", "business_mgmt": "企業管理",
    "organization_mgmt": "組織管理", "rd_mgmt": "研發管理",
    "finance_mgmt": "財務管理", "accounting_mgmt": "會計管理",
    "investment_mgmt": "投資管理", "production_mgmt": "生產管理",
    "engineering": "工程", "chemistry": "化學", "materials_science": "材料科學",
    "energy_materials": "能源材料", "solar_materials": "太陽能材料",
    "chemical_engineering": "化學工程", "electronics": "電子",
    "physics_and_astronomy": "物理與天文", "physics": "物理",
    "computer_science": "資訊科學", "mathematics": "數學",
    "economics_econometrics_and_finance": "經濟計量與財務",
    "business_management_and_accounting": "企業管理與會計",
    "decision_sciences": "決策科學", "environmental_science": "環境科學",
    "energy": "能源", "psychology": "心理學", "social_sciences": "社會科學",
    # 醫療生技(選配)
    "medicine": "醫學", "health_professions": "醫事專業",
    "biochemistry_genetics_and_molecular_biology": "生化遺傳與分子生物",
    "pharmacology_toxicology_and_pharmaceutics": "藥理毒理與藥劑",
    "immunology_and_microbiology": "免疫與微生物", "neuroscience": "神經科學",
    "biology": "生物", "nursing": "護理", "dentistry": "牙醫", "veterinary": "獸醫",
}

# 群組 → 授權 domain(§2 企業職能矩陣;職能部門對映/最小權限/職責分離/需知)
CORE_GROUPS = {
    "經營管理層": ["mgmt_philosophy", "business_mgmt", "organization_mgmt", "decision_sciences"],
    "研發部": ["rd_mgmt", "engineering", "chemistry", "materials_science", "energy_materials",
             "solar_materials", "chemical_engineering", "electronics", "physics_and_astronomy",
             "physics", "computer_science", "mathematics"],
    "財務部": ["finance_mgmt", "economics_econometrics_and_finance"],
    "會計部": ["accounting_mgmt", "business_management_and_accounting"],
    "投資部": ["investment_mgmt", "economics_econometrics_and_finance", "decision_sciences", "finance_mgmt"],
    "生產營運部": ["production_mgmt", "engineering", "environmental_science", "energy"],
    "組織人資部": ["organization_mgmt", "psychology", "social_sciences"],
}
MEDICAL_GROUP = {
    "醫療生技部": ["medicine", "health_professions", "biochemistry_genetics_and_molecular_biology",
               "pharmacology_toxicology_and_pharmaceutics", "immunology_and_microbiology",
               "neuroscience", "biology", "nursing", "dentistry", "veterinary"],
}


def _matrix(with_medical):
    groups = dict(CORE_GROUPS)
    if with_medical:
        groups.update(MEDICAL_GROUP)
    boundary = sorted({d for ds in groups.values() for d in ds})
    return groups, boundary


def _print_plan(groups, boundary):
    print(f"企業管理 RBAC 群組矩陣:{len(groups)} 群組、{len(boundary)} 授權邊界域\n")
    for g, ds in groups.items():
        print(f"  ● {g}({len(ds)} 域)")
        print("      " + "、".join(f"{d}[{DOMAIN_LABELS.get(d, d)}]" for d in ds))
    print(f"\n  授權邊界域({len(boundary)}):" + "、".join(boundary))


def build(cur, groups, boundary):
    for dom in boundary:                               # 1) 註冊授權邊界域(is_authz_boundary=true)
        m.cmd_add_domain(cur, SimpleNamespace(domain=dom, label=DOMAIN_LABELS.get(dom, dom),
                                              authz_boundary=True, investment=False))
    for gname, doms in groups.items():                 # 2) 建群組 + 3) 授權 group→domain
        m.cmd_create_group(cur, SimpleNamespace(group=gname))
        for dom in doms:
            m.cmd_grant_domain(cur, SimpleNamespace(group=gname, domain=dom, confirm=True))


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--with-medical", action="store_true", dest="with_medical",
                    help="併建醫療生技部(§6.1 選配;預設 off)")
    a, _ = ap.parse_known_args()

    groups, boundary = _matrix(a.with_medical)
    if not (a.build or a.dry_run):
        print(__doc__.split("執行指令矩陣:")[1])
        _print_plan(groups, boundary)
        return
    if a.dry_run:
        print("[dry-run] 將建立(不寫入):\n")
        _print_plan(groups, boundary)
        return
    with db.connect() as conn, db.transaction(conn) as cur:
        build(cur, groups, boundary)
    print(f"\n✓ 落地完成:{len(groups)} 群組、{len(boundary)} 授權邊界域"
          f"(冪等;派人入組走 manage_rbac_user --add-to-group)")


if __name__ == "__main__":
    main()
