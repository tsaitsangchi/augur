# 臂批接力報告(S-5/A′/v2 對照)——2026-07-28

## 一、S-5:pack pp_3ab2efebb04e 去留(人閘;規則=對話預註冊 2026-07-28)
run@2026-07-28 10:36:27 hash=aeff01c18ace(INVALID 註記,數字僅參考):總 F=0.76 P=0.5818 A=0.16
  L1_RETRIEVED: F=0.7600 P=1.0000
  L2_NO_RETRIEVAL: P=0.2333
  L3_ABSENT: A=0.3333
  L4_AMBIG: A=0.0000
對照 behavior 同集:F=0.9667 P=0.6167 A=0.2712(INVALID)
**規則判:建議 retire**——R1 一票否決:L1.F=0.7600 < 1.0(新尺實質扣分)
執行唯 hugo 親跑(二選一):
  retire: UPDATE local_model_version SET status='retired' WHERE version_id='pp_3ab2efebb04e';
          (退場後 serving 空缺——advisor 回 base 行為,需知悉)
  keep:   UPDATE local_model_version SET eval_result = eval_result || '{"s5_keep_ratified":"hugo"}' WHERE version_id='pp_3ab2efebb04e';

## 二、A′(A13) 首判(verify_evolution_acceptance 摘錄)
  ── 三軸驗收 A0–A13(v2 §7+A′;唯讀) ──
  ○ A13 A′:任一受測臂於能力格 ≥weak(勝 floor∧mismatched∧robot)且 ≥2 run 複現

## 三、v2 凍結集逐格 F(能力格 scoped 視窗 (0.500,1.000])
| arm | B1_FAITHFUL | B3_AMBIGUITY | C1_ZH_EXISTENCE | C2P_ZH_PAIR |
|---|---|---|---|---|
| ceiling | 1.000 | 1.000 | 1.000 | 1.000 |
| floor | 0.000 | 0.000 | 0.500 | 0.500 |
| mismatched | 0.000 | 0.000 | 0.000 | 0.000 |
| robot | 0.958 | 1.000 | 0.500 | 0.500 |
| shuffled | 0.000 | 0.000 | 0.472 | 0.458 |
(v2 活臂 0——待臂落地;A′ 須活臂能力格嚴格 >0.500 且 ≥2 run 皆勝)
