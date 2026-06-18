# augur 跨機交接 — 2026-06-18b(WSL、gated 全 re-run 進行中 + 全檔重讀刷新)

> 換另一台電腦繼續本專案的接手指南。**權威永遠是 repo 5 治權檔 + 實查**;此為導航 + 現況快照。
> ⚠️ **DB、`.env`、運行中的 sync 三者皆不隨 git(每機獨立)→ 新機永遠以實查為準、勿照抄列數。**
> (WSL 版;另有 Mac 版 `augur_cross_machine_handoff_20260618.md`、前一 WSL 版 `_20260617.md`。)

## 0. 一句話現況

本機 WSL2 跑 **gated 全市場 re-run**(選 A 徹底、主動額度閘啟用):重開機後依 `reboot-resume-20260618.md` 重啟,**PHASE 1/2/2b 全 PASS**(FRED 84,766 列 #7 PASS)、`[1/83] GovBank by-date 13,986 列 #7 PASS`、**[2/83] 進行中**、0 真 403。DB **27 表 / 估 ~1.137 億列**、catalog 95 dataset/751 欄。git HEAD **`8dd7e40`**、tag **`reboot-resume-20260618`**(+ `reconcile-scope-fixes-20260618`)。

## 1. 換機第一步(取 code)

```bash
git clone https://github.com/tsaitsangchi/augur.git   # 或既有 repo git pull
git checkout main                                      # HEAD = 8dd7e40
git tag -l | grep 20260618                             # reboot-resume / reconcile-scope-fixes
python -m venv venv && source venv/bin/activate && pip install -e .
cp .env.example .env   # 填 DB_* / FINMIND_TOKEN / FRED_API_KEY(不進 git)
PYTHONPATH=src venv/bin/python -m pytest tests/ -q     # 預期 43 passed
```

## 2. ⚠️ 換機關鍵注意(gate / token / 不雙跑)

- **gate(finmind.py = git 原版主動額度閘啟用)**:新機 token meter 若**正常**(user_count 反映真實用量)→ 直接用原 gate;若**黑箱**(零 call 卻卡 / 不退反漲)→ 參考 Mac 禁閘改法(Mac handoff §5,`_quota_gate` 讀錶但不暫停、純靠 `_pace`+403 冷卻)。**本機 WSL token meter 為真、需 gate 擋 403**(2026-06-18 禁閘實驗 32 worker 全撞 403、已還原;勿在 meter 為真的機台禁閘)。
- **token 大限**:FinMind sponsor **2026-06-24 到期(剩 6 天)**;sponsor-only(分點/tick/snapshot/法人 by-date/可轉債/八大行庫)須趕到期前,之後降 free 抓不到。
- **不雙跑同 token**:若新機與本機 `.env` 用**同一 FINMIND_TOKEN** → 共用 6000/hr rolling 額度,兩機同時放量會互搶配額 / 觸 403。換機前**先停本機 sync** 或兩機用不同 token(先查 .env 實證、勿假設)。

## 3. 本機運行中 sync 之處置(不隨 git、換機前決定)

- **driver** `/tmp/augur_resume_gated.py`(/tmp 重開機會清,內容 = `os.chdir`+`runpy` 跑 `scripts/full_market_sync.py`、不帶 `--new-only` = A 徹底);**log** `/tmp/augur_resume_gated.log`;**進程** pid 6487(setsid、不 drop、DB-driven resume + ON CONFLICT 冪等)。
- **二選一**:
  - (a) **本機續跑完**:確認 **Windows 主機電源不睡眠**(WSL2 隨 Windows 睡→暫停);無 Claude 監控則手動 `tail -f` log / 查 DB。
  - (b) **新機接手**:換機前 `kill 6487` 停本機,避免雙跑搶 token。
- **resume 安全**:中斷可重跑(`full_market_sync.main()` 從 DB `max(date)` resume + 冪等);重開機後照 `reboot-resume-20260618.md` 重啟(確認 DB → #25 IP 健康探測 → 重建 driver → setsid 啟動)。

## 4. 換機 DB 方案(DB 不隨 git、各機獨立)

- **(a) 新機從零重抓**:`build_catalog.py`(建 catalog)→ 依 reboot-resume 步驟跑 `full_market_sync`(趕 6-24 token)。code `8dd7e40` 已含 reconcile per-stock / by-dim-id / FRED vintage 全修法(新機 pull 即有)。
- **(b) pg_restore 搬**(省重抓、token 到期前保險):本機 sync 到段落 → `pg_dump -Fc augur > augur.dump` → 新機 `pg_restore -d augur augur.dump`。

## 5. 本 session(WSL 2026-06-18)做了什麼

1. **全專案重讀 + 記憶刷新**:5 治權檔 + 官方 datasets.md + 29 支 code + 34 報告 + datasets_zh.md;DB 實查(27 表/~1.137 億)、catalog 實查(95/751、中文 100%)、pytest 43 pass。
2. **修 2 處過時記憶**(machine-local memory):憲章 v1.7→**v1.8**、CLAUDE v1.4→**v1.5**、throttle 0.8s→**0.7s/32w**(澄清為 #19 試錯操作值、非凍結)、DB 列數刷新。
3. **依 reboot-resume 啟動 gated 全 re-run**:#25 IP 健康探測(1 列 ✅、額度 3001/6000)→ 放量、選 A 徹底、gate 啟用。
4. **commit `8dd7e40`**(reboot resume 報告)+ push origin/main + **tag `reboot-resume-20260618`** + push。

## 6. 關鍵 operational 知識(memory machine-local、這裡轉移給新機)

- **禁閘只適黑箱 meter token**;**真 meter token(本機 WSL)需 gate 擋 403**(禁閘 = 32 worker 全撞 403)。真額度信號 = IP 健康(單股單日 probe 能抓)+ DB 列數成長,非盲信 user_count。
- **per-stock 日表 reconcile 殘小 VM = 近日修訂漂移**(TWSE 持續修訂近日值)= **benign**(EX=0、抓取當下 byte-faithful、非幻像);要 VM=0 須最終對帳前 heal(但會再漂)。
- **最新日 preliminary→final**:per-stock 抓當日法人未定案、次日刷新(`reconcile_audit.py` 有 `UNSETTLED_BUFFER=2` 緩衝、不計 verdict)。
- **reconcile 須對齊抓取端點**(catalog `reconcile_scope` 路由):roster-scoped→`reconcile_per_stock`、by-dim-id→`reconcile_by_dim_id`、其餘→`reconcile_by_date`。錯配端點 → 假 VM(per-stock 表用 by-date 對)或假 MIS(by-dim-id 表用 by-date 對回空)。
- **FRED vintage 容忍**:FRED 修訂/重對齊日期 → 假 EX;`reconcile_fred` 容忍(值還在、僅日期移 = restatement)、不刪 DB 真值(#12/#15)。
- **throttle 現操作值 0.7s / 32 worker**(非治權凍結、依 #19 逐級試錯;住 finmind.py 單一處)。

## 7. 治權現狀

靈魂 **v1.2.0** · 原則精華 **v1.6.0**(20 條) · 憲章 **v1.8.0**(+catalog 橫切 + 官方 datasets.md 入憲) · CLAUDE **v1.5** · README。三敵(#1 零幻像 / #8 anti-leakage / #15 誠實)。

## 8. 接續 TODO

1. (本機或新機)gated 全 re-run 跑完 **6-83** → 最終 #7 attestation(`scripts/reconcile_audit.py`)→ commit `fullsync_issues` + push(#14 授權)。
2. per-stock 近日修訂 VM **heal**(重抓覆蓋為 API 當前、非 hand-patch);對帳紅旗(extra_in_db)人工判。
3. 全表完整 + 對帳乾淨 → 解凍 → **F3 models + evaluation**(下一主階段、`models`/`evaluation` 空、PHASE 10-11)。

> 放量 / commit / push 一律須用戶明示授權。clean-room #16:零參考 stock_backend。對話繁體中文。
