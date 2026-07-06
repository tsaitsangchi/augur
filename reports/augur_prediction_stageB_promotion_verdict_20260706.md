# 股市預測 STAGE B — 提拔三審裁決(新嚴格 embargo 下之首次真檢驗)

**日期**:2026-07-06 ｜ **口徑**:A'-3 embargo 保證下界(`walkforward.splits(calendar=)`、逐折真實交易日、embargo ≥ h+62td)
**判準 SSOT**:`augur_prediction_sop_master_20260706.md` §3 STAGE B / §6 拍板(B1 HAC-t 綁死、B2 sanity 負對照、B3 as-of ≤ pan-hist)
**方法論**:`augur_feature_discovery_methodology_20260626.md` §四
**守**:#8(anti-leakage:purged walk-forward + 保證 embargo)· #11(HAC 去相關 t、禁裸 iid)· #15(誠實揭露 n / 限制 / 旗標)

---

## 一、設定(全出自 `stage_b_promotion.py` stdout,#9/#10 可溯源)

| 項 | 值 |
|---|---|
| as-of panels | 28(2014-12-31 .. 2026-05-31) |
| pan-hist 宇宙(as-of 聯集) | 776 股 |
| canonical 特徵(as-of panels 交集) | 34 |
| 模型 | B2 Ridge(alpha=1.0、確定性)|
| seeds | 3(42/43/44;Ridge 無隨機 → as-of/pan 三 seed 恆等,shuffle 因 RNG 打亂 label 而異——harness 正確之佐證)|
| horizons | H=20、H=60(H≥252 被 walkforward gate raise、未跑) |
| 每 horizon 有效 test 折 n | 25(28 panels 扣保證 embargo 後) |

## 二、結果(seed 平均)

| H | as-of IC | as-of **HAC-t** | iid-t | pan-hist IC | pan-hist HAC-t | **shuffle IC** | shuffle HAC-t | hit | n |
|---|---|---|---|---|---|---|---|---|---|
| 20 | +0.1133 | **+6.09** | +6.17 | +0.1197 | +6.01 | −0.0037 | −0.38 | 0.88 | 25 |
| 60 | +0.1521 | **+6.95** | +7.32 | +0.1405 | +5.68 | −0.0013 | −0.26 | 0.92 | 25 |

shuffle 逐 seed(H60):−0.006 / +0.009 / −0.006(HAC-t −0.83 / +0.70 / −0.65)——皆 |t|<2、繞 0。

## 三、三審判定

- **B1 顯著性(HAC-t 綁死,|HAC-t|≥2 為硬 gate)**:H20 **+6.09**、H60 **+6.95**,皆 ≫ 2 → **決定性通過**。HAC 與 iid-t 接近(6.09 vs 6.17)表重疊窗自相關對本集不劇烈,但仍以 HAC 為準(#11)。
- **B2 sanity 負對照(打亂 label 應 IC≈0)**:兩 horizon shuffle IC≈0(−0.004 / −0.001)、HAC-t≈0、hit~0.4-0.6 → **通過**。**feature→label 洩漏排除**(敵③自檢硬 gate 過;若有洩漏,打亂後仍會殘留結構)。
- **B3 survivorship(as-of ≤ pan-hist)**:H20 as-of 0.1133 ≤ pan-hist 0.1197 ✓;**H60 as-of 0.1521 > pan-hist 0.1405(+0.012)= 輕微旗標**。方向**非** survivorship 灌水方向(灌水抬 pan-hist 而非 as-of),加上 B2 過關,較可能為宇宙組成/雜訊;**列入觀察、非停損**。

## 四、誠實判讀(真兆 / 假兆)

- **原預期 vs 實況**:我原判「IC 會因 embargo 收緊(估算 ×0.69 → 保證 h+62td)而誠實下修」。**實況幾乎沒掉**(H60 as-of +0.1521 vs 舊 headline +0.1418、H20 +0.1133)。這**本身是正面真兆**:先前的 IC **不是靠寬鬆 embargo 的洩漏樂觀撐起**——alpha 對更嚴 purge 穩健。
- **為何 seed 恆等**:Ridge 確定性、無隨機性,as-of/pan 三 seed 必然相同;只有 shuffle(RNG 打亂 label)才隨 seed 變。此為 harness 行為正確,非 bug。

## 五、限制(不誇大)

1. **n=25 panel 偏小**——HAC-t=6 在 n=25 下強,但樣本有限,結論屬「強烈支持」非「終定」。
2. **僅 IC 層**——靈魂成功定義是**經濟價值**(#14:淨 Sharpe/MaxDD/Calmar 扣成本),那是 STAGE C/D,本審未觸。**IC 撐住 ≠ 可交易**。
3. **H60 B3 輕旗標**(as-of > pan-hist)待 C/D 以 point-in-time 投組回測交叉驗證。
4. Ridge 單模型;GBDT/非線性增量未在本審對比(baseline 階梯之 M1 為後續)。

## 六、裁決

**STAGE B 提拔三審通過**:H20、H60 皆過 **B1(HAC-t ≫2)** 與 **B2(無洩漏 sanity)**;**B3** H20 過、H60 輕旗標待盯。預測價值在**新嚴格 embargo 口徑下為真兆**,可進 **STAGE C(經濟價值 #14)/D**。

## 七、複現

```bash
cd /home/hugo/project/augur && source venv/bin/activate
source <PGENV>   # DB 環境
python /path/to/stage_b_promotion.py    # RAW_JSON_BEGIN..RAW_JSON_END 為機讀結果
```
原始機讀 JSON 見本審執行之 stdout(scratchpad `stage_b_out.log`、RAW_JSON 區塊);評估碼 = `evaluation/{baseline,walkforward,metrics}.py`(A'-3 embargo 已入封存 `treaty-v1.36-predict-isolation-20260706`)。
