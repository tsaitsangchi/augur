# KH #1h live LLM 錨題 — EXECUTED 2026-08-06

```text
KH-ANCHOR-REGRESSION-1h-live-executed | FZ/GATE-keep | model=qwen3:4b | size_vram=0
```

## 結果（誠實）

| 輪 | 條件 | 結果 |
|---|---|---|
| Q1／Q2 | timeout 700s、未鎖 `num_predict` | **逾時**（CPU 跑 4b） |
| Q1b | `num_predict=480`、cite≈1717、timeout 1200s | **~501s**；hit **277948**；guard **pass**；**非** NO_K；但輸出**未**成 `1.2.3.`，中段洩「我需要從這些…」，`num_predict` 截斷 |

## 判讀

- 管線（readout／compact／命中）**live 仍成立**。  
- **逐步條列品質**受弱 GPU／短 `num_predict`／模型想題洩漏限制；stub 回歸已綠不足代表 live 口吻。  
- 建議：serve 預設 `options.num_predict` 與 compact 對齊；或加中段想題剥；有 VRAM 時重抽。

## 計畫

§4 **#1h** live → 🟡 管線綠／口吻未達；stub ✅ 不變。

*executed。*
