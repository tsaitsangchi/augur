# KH-ATA-SCHED＋FZ-keep CLOSED（2026-07-28）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/KH-ATA-SCHED-APPROVED-20260728.md`（Steward 原文 `KH-ATA-SCHED`＋`FZ-keep`）  
> **不含**：`KH-ATA-EXEC` 外部 OA 放量；來源 approve／activate；FinMind／FRED 解凍

## 一、做了什麼

| 項 | 狀態 | 摘要 |
|---|---|---|
| **unit** | ✅ | `~/.config/systemd/user/augur-ata-advance.{service,timer}`；SSOT 生成＝`install_services.sh` |
| **ExecStart** | ✅ | `advance_knowledge_terminal.py --apply --limit 200 --stages sentences embed`（**僅庫內**；無 fulltext） |
| **節奏** | ✅ | `OnCalendar=*-*-* 04:00:00`＋`Persistent=true`（避開 03:30 embed／06:15 L2） |
| **日誌** | ✅ | `~/ata_advance.log`（`StandardOutput`／`StandardError=append:`） |
| **enable** | ✅ | `systemctl --user enable --now augur-ata-advance.timer`；`list-timers` 下次＝翌日 04:00 |
| **dry-run** | ✅ | 僅印 `build_sentences`／`embed_knowledge`＋`--limit 200`；輸出**無** approve／activate |
| **FZ-keep** | ✅ | 零市場 API；未開 `KH-ATA-EXEC` |

## 二、dry-run 真兆（本輪）

```
池量: pending=107540 ft_no_sent=0 sent_no_emb=498
[sentences] .../build_sentences.py --scope items --limit 200
[embed] .../embed_knowledge.py --layer sentence --language en --scope items --limit 200
dry-run 完畢（零執行）。
```

## 三、硬邊界核對

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 不含外部 OA（無 `--stages fulltext`） | ✅ |
| timer 不呼叫 approve／activate／HUMAN_ONLY | ✅（unit＋dry-run＋ATA 骨架禁 transition） |
| 素養不進預測 | ✅ |

## 四、操作備忘

| | |
|---|---|
| **何時跑** | 每日 **04:00**（本地；`Persistent=true` 補漏跑） |
| **limit** | **200**（可用 env `ATA_ADVANCE_LIMIT` 於重跑 `install_services.sh` 時覆寫） |
| **停** | `systemctl --user disable --now augur-ata-advance.timer` |
| **手跑一次** | `systemctl --user start augur-ata-advance.service` |
| **日誌** | `~/ata_advance.log` |

## 五、變更檔

- `install_services.sh` — 新增 ata-advance service／timer；uninstall／enable 清單  
- `audits/KH-ATA-SCHED-APPROVED-20260728.md`／本 CLOSED  
- `HANDOFF.md` — 近程一句  

## 六、下一步（仍另碼）

- **`KH-ATA-EXEC`** — 有界外部 OA（≠解凍市場 API）  
- 市場 API：**仍凍**（`FZ-keep`）
