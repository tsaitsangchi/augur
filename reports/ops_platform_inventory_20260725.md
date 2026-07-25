# ops_platform_inventory_20260725 — 本機（DESKTOP-8MQPFS8）軟硬體盤點

> 產出方式：全數為 2026-07-25 本機指令實測輸出（`uname`/`lscpu`/`free`/`df`/`nvidia-smi`/`psql`/`pip list` 等），零推測（守 #9/#10）。

## 一、硬體（2026-07-25 午後複測——同日極限調優後之現況）

| 項目 | 值 |
|---|---|
| 主機 | DESKTOP-8MQPFS8＝Windows 10 家用版 build 19045（32GB RAM）上之 WSL2；**巢狀虛擬化不可用（Win10 限制，經實測 svm 旗標不透傳）** |
| CPU | AMD Ryzen 5 3600（6 核 12 執行緒，x86_64；WSL 分得 12/12） |
| 記憶體 | **25 GiB**（`.wslconfig memory=26GB`＋`autoMemoryReclaim=gradual`） |
| Swap 階層 | 總 **140Gi**＝zram `/dev/zram0` **12.7GB**（lzo-rle、priority 100 先用）＋磁碟 `/dev/sdc` **128GB**（`D:\wsl\swap.vhdx`、priority -2 保底）；WSL2 核心 zram 僅支援 lzo-rle/lzo |
| GPU | NVIDIA GeForce GTX 1650 **4GB**（硬體天花板、不可磁碟擴充）；Driver 560.94；CUDA 12.6（runtime）/ nvcc 12.0（toolkit）；100W 上限 |
| 磁碟 | WSL 根 `/dev/sdd` 1007G（用 235G, 25%）；`C:` 931G（26%）；`D:` 1.9T（58%）；`E:` 3.7T（2%） |

## 二、作業系統

- WSL2 kernel：Linux 6.18.33.2-microsoft-standard-WSL2
- 發行版：Ubuntu 24.04.4 LTS (Noble Numbat)

## 三、軟體堆疊

| 項目 | 版本 |
|---|---|
| Python（系統＝venv 基底） | 3.12.3 |
| 專案 venv | `~/project/augur/venv`（141 套件；殘留 `.venv` 已於 2026-07-25 確認無依賴後移除） |
| augur | 1.0.0（editable install，`pip install -e .`） |
| pandas / numpy | 3.0.3 / 2.4.6 |
| scikit-learn / scipy | 1.9.0 / 1.18.0 |
| xgboost / lightgbm | 3.3.0 / 4.6.0 |
| torch | 2.12.1+cu126（CUDA 12.6 版） |
| sentence-transformers | 5.6.0 |
| qdrant-client | 1.18.0 |
| PostgreSQL | 17.10（Ubuntu 17.10-1.pgdg24.04+1，`postgresql@17-main.service` running） |
| Ollama | 0.32.1（service running；模型：qwen3:8b 5.2GB、qwen3:4b 2.5GB、nomic-embed-text 274MB） |
| Docker | 29.1.3 |
| git / node | 2.43.0 / v18.19.1 |

## 四、資料庫（augur）

- 連線：`.env` 之 `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD`（peer/localhost 免密不通，須帶密碼）
- 大小：**56 GB**；public schema **244 張表**

## 五、服務現況（systemd，2026-07-25 實測）

- running：`postgresql@17-main.service`、`ollama.service`
- **未見**：`augur-chat`/`augur-advisor`/`augur-admin`/`augur-qdrant` 等服務（`systemctl list-units` 無列出；port 6333 curl 無回應）——此機這些服務未掛或未啟動，接續時須依 #31/記憶「crontab/systemd/Qdrant 皆機器本地須重掛」自行重建。

## 六、已知環境備註

- GPU 僅 4GB VRAM：HNSW 建索引×並發有 OOM 前科（見記憶 db-import-tuning-hnsw-oom）。
- WSL2 記憶體 26GB 為配額（主機 32GB 下之有界極限，勿再上調），Windows 主機電源設定影響長跑（#22）。
- 同日極限調優（PG 14 項持久化／Ollama VRAM 優化／zram）之執行紀錄詳 `reports/ops_platform_tuning_plan_20260725.md`。
