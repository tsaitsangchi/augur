---
title: KH8 A2 · evidence 公式落地設計規格
subtitle: compute_evidence_weight 改版契約；遷移／回歸／與 M3／E 順序
status: design_spec
date: 2026-08-08
viewpoint: 2026-08-08T21:40+08:00
layer: "[I]"
adopt_a2: audits/KH8-DISCRIM-A2-ADOPTED-20260808.md
sim: audits/KH8-DISCRIM-A2-SIM-EXECUTED-20260808.md
m3: audits/KH8-DISCRIM-M3-ADOPTED-20260808.md
e: audits/KH8-DISCRIM-E-ADOPTED-20260808.md
paste: "KH8-DISCRIM-A2-land-spec | FZ/GATE-keep | no-code-yet | E-keep | M3-order | hold-#1"
self_reported: true
---

# KH8-DISCRIM · A2 落地設計規格（2026-08-08）

> **一句**：把已採納的 **A2 改公式** 收成可施作契約——**本檔≠改碼**；施作另 GO。  
> **誠實**：A2-sim 顯示**只改公式、母體仍齊備池**時，全庫 disc 投影仍 **ok=False**（minority≈0.024）。A2 目標＝**分數诚实展开**；生产 disc 綠仍多半要 **M3 答池闸＋標題／薄項入母體** 或公式 v2+。  
> **正交**：hold-#1；E stop-at-7 至**生产** disc 真綠且闸过。

---

## §1 目標／非目標

| 目標 | 非目標 |
|---|---|
| 打破「齊備→≥0.72→high」牆 | 降 `MIN_MINORITY_MASS`（A3／D 禁） |
| `compute_evidence_weight` 纯函式可测 | 默默重算主表无回归 |
| 迁移可回滚、可影子对拍 | 因实验∪影 ok=True 宣 depth≥8 |
| 与 M3：权重≠可答 | advise 直接读 shadow |

---

## §2 公式契约（落地候选 **A2-v1**＝已 sim）

### 2.1 现行（legacy）

```text
score = 0.35*min(cite_n/5,1) + 0.25*T + 0.25*E + 0.15*K − 0.40*C
band  = high≥0.70 | medium≥0.40 | low≥0.15 | absent
# 齐备 T=E=K=1 → 底 0.65；+1句 → ≥0.72 → high
```

### 2.2 A2-v1（Steward 已见 sim；建议为**默认入码候选**）

```text
cite_norm = min(cite_n/8, 1)                 # 满档更陡
plumbing  = 0.12*T + 0.12*E + 0.11*K         # 齐备顶 0.35（旧 0.65）
score     = plumbing + 0.50*cite_norm + 0.15*E*cite_norm − 0.40*C
clip:
  cite_n==0 → score = min(score, 0.35)
  cite_n<=1 → score = min(score, 0.55)       # 禁「几乎无引文却 high」
band 阈值不变（0.70／0.40／0.15）
components 仍写 T/E/K/C/cite_norm + formula 字串 = "A2-v1:…"
```

**sim 结果备忘**：主表投影 → 大量 medium、high≈3k；band minority≈**0.024**仍＜0.05；**分量源不变**故 2′ 仍吃力。

### 2.3 A2-v2（可选；另 sim2 后才锁）

仅当 v1 入码后仍要「主表 alone 冲 θ」再开，例如：更陡 cite、或把 T 改为「有句且非唯一齐备」之连续质量。**未锁；禁无 sim 上库。**

### 2.4 刻意不做

| 不做 | 因 |
|---|---|
| 只改 band 切点（A3） | 假分级 |
| 相对秩当唯一 band（A4）独用 | 双尺混乱；可后续加「排序用」旁路 |
| 公式里写死 domain 白名单 | 策展／授权分家 |

---

## §3 码触点（实作地图）

| 点 | 路径 | 变什么 |
|---|---|---|
| **纯函数** | `src/augur/knowledge/evidence.py` → `compute_evidence_weight` | 公式＋components.formula |
| **自测** | 同档 `--selftest` | 锁：齐备+1句 **不得 high**；0句 **不得 ≥medium 顶**；旧测若绑 0.72 则改写预期 |
| **写库路径** | evidence upsert／reevaluate 脚本（现有 KH8 重算入口） | 调纯函数即可 |
| **消费** | `band_for_score`／honest view／synthesis | **不改**阈值 unless 另裁 |
| **disc** | `population_discriminates`／`MIN_MINORITY_MASS=0.05` | **不改 θ** |

禁：在 `advisor/advise.py` 特判分数。

---

## §4 迁移波（另 GO 才跑）

| 波 | 内容 | 准／禁 |
|---|---|---|
| **L0** | 本规格＋adopt 对照 | 只文件 |
| **L1** | 码：A2-v1 纯函数＋selftest 绿 | 不写主表 |
| **L2** | dry-run／影子列 `score_a2` 对拍 N=全主表或 20k | 不覆写 score |
| **L3** | 双明示后批次 UPDATE 主表 weight（可按 item_id 段） | 禁与 B3 同窗抢盘；可回滚 SQL |
| **L4** | 主表 `population_discriminates` 复测；**若仍 False＝预期诚实** | 不降 θ；不抬 8 |
| **L5** | 与 **M3 pool-gate** 汇合后再议标题／影合并 | 无闸禁并 |

回滚：保留 `components.formula`／批次 `run_id`；可重跑 legacy 函数覆写（legacy 公式进 git 标签或 `compute_evidence_weight_legacy`）。

---

## §5 回归锁（L3 前后必跑）

| # | 案 | 过门 |
|---|---|---|
| R1 | 锚题 277948 readout（super scope） | 仍命中；非「无此内容」 |
| R2 | `python -m augur.knowledge.evidence --selftest` | 全过 |
| R3 | `run_kh_chain --check` | KH0 破口 0；KH8 主表 ok 字面诚实 |
| R4 | 随机 20 有文 item：band 与 cite_n 同向（多句不无故低于少句） | 人工 spot |
| R5 | hold-#1／watcher | 不因 L3 被杀 |

---

## §6 与 E／M3／hold 顺序（纪律）

```text
推荐序:
  hold-#1 日更主轴
  → L1/L2（码＋干跑）∥ M3-pool-gate 码闸（不合并）
  → L3 主表重算（另明示）
  → 若要生产 disc 绿: M3 合并（闸已绿）± 影
  → 另裁撤 E（stop-at-7）——不得自动
```

| 状态 | 可否宣称 KH8 进化成功 |
|---|---|
| 仅 L1／实验∪影 ok | **否** |
| L3 后主表仍 False | **否**（诚实） |
| 主表 True 且答池闸过且 Steward 撤 E | **可议** |

---

## §7 验收（本规格档）

1. 锁 A2-v1 公式原文与「齐备+1句不得 high」。  
2. 写清：v1 **不保证**主表 disc 绿。  
3. 迁移 L0–L5、回归 R1–R5、与 M3／E 顺序。  
4. **未改码、未写库。**

---

## §8 Paste

```text
KH8-DISCRIM-A2-land-spec | FZ/GATE-keep | no-code-yet | E-keep | M3-order | hold-#1
# 下一刀候選:
KH8-DISCRIM-A2-L1-go | code+selftest | no-write-main
KH8-DISCRIM-M3-pool-gate-go | no-merge
```

*完。[I] design_spec。*
