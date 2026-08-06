# LOCAL-KH-CONCORDANCE-1e — GO 2026-08-06

```text
LOCAL-KH-CONCORDANCE-1e-go | FZ/GATE-keep | no-SIM-apply | backfill-local-eligible
# 問題: local＋eligible 有句無 concordance → exact 路徑盲（錨 277948＝0 列）
# 規模: ~163 件／~970 句（zh 966＋en 4）；主游標 concordance_items_zh=1815403 未追上
# 作法: build_concordance.py --backfill-local-eligible [--run]
#       ※ 不推進 concordance_items_{zh,en} 主游標（另 key／或無 meta）
# 驗: 277948 n_conc>0；抽樣 exact retrieve 可命中；計畫 §4 #1e／Ρ0.4
```

*go。*
