# augur 跨機交接 — 2026-06-18(Mac、mac-resume OptionDaily 完成、News 進行)

> 換另一台電腦繼續本專案的接手指南。**權威永遠是 repo 5 治權檔 + 實查**;此為導航 + 現況快照。
> ⚠️ **DB 與 .env 不隨 git(每機獨立)→ 新機永遠以實查為準、勿照抄列數。**
> (Mac 版;另有 WSL 版 `augur_cross_machine_handoff_20260617.md`、WSL 為並行主力、不同 token。)

## 0. 一句話現況

Mac 跑 **mac-resume**(禁用 user_count 黑箱閘、resume 全量抓取):前 20 表 resume + per-stock 對帳重驗完成、**OptionDaily 禁用閘後續抓 2010→2026 全史完成(~28M 列、對帳 PASS、零撞 403)**、現 `TaiwanStockNews` by-date 進行(sync 21/83、對帳 20 PASS / 2 FAIL)。git HEAD **`d8bff7c`**、tag `augur-mac-optiondaily-done-20260618`。

## 1. 換機第一步(取 code)

```bash
git clone https://github.com/tsaitsangchi/augur.git   # 或既有 repo git pull
git checkout main                                      # HEAD = d8bff7c
git tag -l | grep 20260618
python -m venv venv && source venv/bin/activate && pip install -e .
cp .env.example .env   # DB_* / FINMIND_TOKEN / FRED_API_KEY(不進 git)
PYTHONPATH=src venv/bin/python -m pytest tests/ -q
```
**⚠️ 新機 `finmind.py` gate**:Mac 本地**禁用了 user_count 閘**(Mac token 黑箱、零 call 卻卡)、**此改未 commit、git 上是原版主動額度閘**。新機若 user_count 正常 → 直接用 git 原 gate;若新機 token 也黑箱卡死 → 參考 Mac 改法(`_quota_gate` 讀錶 log 但不暫停、純靠 `_pace`+403、見下 §5)。

## 2. 本會話(Mac、2026-06-17~18)做了什麼

1. **optimal_mode 國際股修正**(`184cd7d`):國際股(UK/Europe/US/Japan)`data_id_source="none"` 走 by-date(防誤判 per-stock + 用台股 roster 漏抓)。
2. **FRED vintage 容忍**(`5ce3ad8`):`reconcile_fred` 排 FRED 修訂日期重對齊之假 EX(實證 `BAMLH0A0HYM2` 2023-06-16→06-19 同值 4.15、不刪真值 #12/#15)。
3. **mac-resume 禁用 user_count 閘 + resume(核心)**:Mac token user_count **黑箱**(零 call 卻卡 5146 / 自漲、但 IP 健康實測能抓)→ gate 死等 user_count 退 2900 致 OptionDaily 卡死。解:**禁用 gate user_count 預防暫停閘**(本地改、未 commit)、純靠 `_pace` 0.7s + 撞真 403 之 `QUOTA_COOLDOWN`。→ OptionDaily 從卡死點(2009-12)續抓完成 2026-06、全史 ~28M 列、**零撞 403**,徹底驗證成功。
4. per-stock 對帳重驗修舊假旗(ShortSale EX=68 / 財報三表 → PASS;Institutional 殘 VM=1 近日修訂待 heal)。

## 3. ⭐ Mac mac-resume 進行中(Mac DB、不隨 git)

- **driver**:`/tmp/augur_mac_resume.py`(不進 git、**不 drop**、`full_market_sync.main()` resume)。
- **進度(實查、勿照抄;~12.7h 時點)**:**sync 21/83、對帳 20 PASS / 2 FAIL**(FRED EX=1 已修方法、Institutional VM=1 待 heal)、錯誤 0、403 0。**OptionDaily 完成 ~28M**、當前 `TaiwanStockNews` by-date(~54%、single-day 逐日)。
- **防護**:`caffeinate -dimsu nohup` + SHMM(`btjde3s12`/`bpsnahkjb`)+ resume-safe(DB-driven + 冪等)。log `/tmp/augur_mac_resume.log`。
- **換機後 Mac 處置**:mac-resume nohup 自跑完(News + 後面 62 dataset、含國際股 by-date、跨日);無 Claude 監控則手動查 log/DB。

## 4. 換機 DB 方案

- **新機從零重抓**:跑 `build_catalog.py` + 仿 driver 跑 full_market_sync(code `d8bff7c`)。⚠️ **FinMind token 2026-06-24 到期(剩 6 天)**趕。**gate 注意**:新機 token user_count 正常 → 用原 gate;黑箱卡死 → 參考 Mac 禁用改法(§5)。
- **pg_restore 搬**:Mac mac-resume 或 WSL 跑完 → `pg_dump -Fc` → 新機 `pg_restore`。WSL 主力(token 正常、reconcile per-stock + FRED vintage 都在 git)。

## 5. 關鍵知識(記憶 machine-local、這裡轉移)

- **FinMind user_count 可黑箱卡死/自漲**(Mac token 實證):gate 暫停後零 call 期間 user_count **不退反漲**(5136→5265)、gate 死等退 2900 → 永久卡死(OptionDaily 等高 call 密度表尤易觸發、疑近 token 6-24 到期 + 服務端計數失準)。**真額度信號＝IP 健康(單股單日 probe 能抓)+ DB 列數成長**,非 user_count。Mac 解法:`_quota_gate` 改讀錶 log 但**不暫停**、純靠 `_pace`+403 `QUOTA_COOLDOWN`(撞真 403 才冷卻)。**錶可靠機台用原 gate**。
- **FRED vintage 容忍**(`5ce3ad8`):FRED 修訂/重對齊日期 → 假 EX;`reconcile_fred` 容忍(DB 有 API 無之筆 value 在 API 有同值 → restatement、不計 EX、不刪真值)。
- **per-stock 對帳**(WSL `e8ef8c4`):roster-scoped 表 per-stock 重抓對帳(對齊端點、消 by-date 端點差假 VM);殘餘 VM＝真差異(近日修訂)交 heal。
- **optimal_mode 國際股**(`184cd7d`):國際股 src=none 走 by-date。

## 6. 治權現狀

靈魂 **v1.2.0** · 原則精華 **v1.6.0** · 憲章 **v1.8.0** · CLAUDE **v1.5** · README。三敵(#1/#8/#15)。

## 7. 接續 TODO

1. Mac mac-resume / WSL clean-rebuild 跑完 → 驗證全表完整 + 全表 #7 對帳乾淨(`scripts/reconcile_audit.py`)。
2. **Institutional VM=1 等近日修訂 heal**(重抓覆蓋為 API 當前、非 hand-patch);對帳紅旗統一人判。
3. 全表完整 + 對帳乾淨 → 解凍 F2/F3 → **F3 models + evaluation**(下一主階段、`models`/`evaluation` 空)。

> 放量 / commit / push 一律須用戶明示授權。clean-room #16:零參考 stock_backend。
