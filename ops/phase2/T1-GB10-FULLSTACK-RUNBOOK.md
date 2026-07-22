# T1 執行手冊：全棧集中 GB10（`aitopatom-b96e`）

* **性質**：[I] 營運手冊，不創設 [N] 義務；不取代 ENVIRONMENT-SPEC／L7.50（正式登錄仍待 Steward）。
* **裁決**：2026-07-22 Steward 選 **T1**——PostgreSQL + qdrant + 應用 + ollama 皆落本機。
* **正典應用碼（暫定，待書面確認）**：`/home/giga/augur-code-work`
* **憲章／工具 repo**：`/home/giga/augur`
* **架構約束**：全部套件／映像必須支援 **aarch64**。

---

## 完成定義（Definition of Done）

1. `python3 ops/phase2/operability_probe.py`：ollama／GPU／**PG**／**qdrant**／應用碼皆非 ABSENT（PG／qdrant = UP）。
2. 本機 `augur` 庫可連；至少一張業務表可 `SELECT count(*)`（數字以實查為準）。
3. 正典樹能 import 核心模組；**一條** advisor 或審議煙霧（極小輸入）有明確成功或失敗紀錄。
4. `ops/machines/packs/aitopatom-b96e/` NOTES 更新為「全執行節點（T1）」；探測證據入 `ops/phase2/`。

---

## 第 0 步｜取證（先跑；結果決定還原來源）

在 **GB10 終端**執行，把輸出存檔或貼回：

```bash
# 0.1 身分與空間
hostname; uname -m; free -h | head -2; df -h / | tail -1
docker --version
groups | tr ' ' '\n' | grep -E 'docker|sudo' || true

# 0.2 正典應用樹
ls -la /home/giga/augur-code-work | head -30
test -f /home/giga/augur-code-work/.env && echo "HAS_.env" || echo "NO_.env"
test -d /home/giga/augur-code-work/.git && (cd /home/giga/augur-code-work && git remote -v && git branch -v | head -5)
ls /home/giga/augur-code-work/pyproject.toml /home/giga/augur-code-work/requirements*.txt 2>/dev/null

# 0.3 本機是否已有 dump／備份（可能沒有——資料可能仍在 WSL2）
find /home/giga -maxdepth 4 -type f \( -name '*.dump' -o -name '*augur*.sql*' -o -name '*.backup' \) 2>/dev/null | head -40
ls -lah /home/giga/augur/backups 2>/dev/null | head -20

# 0.4 基線探測
cd /home/giga/augur
python3 ops/phase2/operability_probe.py
./ops/machines/packs/aitopatom-b96e/setup_check.sh
```

**閘門**：若 `NO_.env` 且無 dump → 必須先從 WSL2／備份管線取得憑證與資料，**禁止**空庫假裝生產。

---

## 第 1 步｜用 Docker 起 PostgreSQL（建議 port 5432，僅本機）

> 選 Docker：本機已有 docker 29.x；映像用官方多架構（含 arm64）。若你無 docker 權限，改 micromamba userspace（見附錄）。

```bash
# 1.1 資料目錄（本機、不進 git）
mkdir -p /home/giga/augur-data/postgres
mkdir -p /home/giga/augur-data/qdrant

# 1.2 設定密碼（自行改；勿提交 git、勿貼到公開頻道）
export POSTGRES_PASSWORD='改成強密碼'
export POSTGRES_USER=augur
export POSTGRES_DB=augur

# 1.3 啟動（僅綁 127.0.0.1）
docker rm -f augur-postgres 2>/dev/null || true
docker run -d --name augur-postgres \
  --restart unless-stopped \
  -e POSTGRES_PASSWORD \
  -e POSTGRES_USER \
  -e POSTGRES_DB \
  -v /home/giga/augur-data/postgres:/var/lib/postgresql/data \
  -p 127.0.0.1:5432:5432 \
  postgres:17

# 1.4 等就緒
for i in $(seq 1 30); do
  docker exec augur-postgres pg_isready -U augur -d augur && break
  sleep 2
done

# 1.5 探測（應變 UP）
cd /home/giga/augur
python3 -c "from ops.phase2.operability_probe import probe_pg; print(probe_pg(5432))"
# 或整支：
python3 ops/phase2/operability_probe.py | sed -n '/PostgreSQL/,+1p'
```

可選：裝 `psql` 客戶端方便操作：

```bash
sudo apt-get update && sudo apt-get install -y postgresql-client
PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U augur -d augur -c 'SELECT version();'
```

**pgvector**（若應用需要）：

```bash
# 映像若無 vector 擴充，改用帶 pgvector 的映像，例如（名稱以當日 Docker Hub 為準，須 arm64）：
# ankane/pgvector 或 pgvector/pgvector:pg17
# 換映像前請先停掉空容器，避免蓋掉已有資料卷。
```

---

## 第 2 步｜起 qdrant（6333，僅本機）

```bash
docker rm -f augur-qdrant 2>/dev/null || true
docker run -d --name augur-qdrant \
  --restart unless-stopped \
  -v /home/giga/augur-data/qdrant:/qdrant/storage \
  -p 127.0.0.1:6333:6333 \
  qdrant/qdrant:v1.18.2

curl -sf http://127.0.0.1:6333/ | head -c 200; echo
cd /home/giga/augur && python3 ops/phase2/operability_probe.py | sed -n '/qdrant/,+1p'
```

---

## 第 3 步｜取得並還原 augur 庫

### 3.1 資料來源（三選一，依第 0 步結果）

| 來源 | 動作 |
|---|---|
| **本機已有 `.dump`** | 記下絕對路徑 → 3.2 |
| **WSL2 仍有活庫** | 在 WSL2：`pg_dump -h 127.0.0.1 -U … -d augur -Fc -f augur_YYYYMMDD.dump`，再 `scp` 到 GB10 |
| **restic／異碟** | 依既有備份程序還原 dump 檔到 GB10（見 phase1 紀錄） |

### 3.2 還原（範例；路徑自行替換）

```bash
# 建議：先還原到沙盒庫演練
PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U augur -d postgres \
  -c "CREATE DATABASE augur_sandbox OWNER augur;"

# 還原到沙盒（-Fc 格式）
pg_restore -h 127.0.0.1 -U augur -d augur_sandbox --no-owner --role=augur \
  /path/to/augur_XXXX.dump

# 抽樣
PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U augur -d augur_sandbox \
  -c "\dt" | head
# 若有 entity 相關表，再 count（表名以實庫為準）

# 沙盒 OK 後，再決定是否還原到生產庫名 augur（可 drop/recreate——僅在確認無唯一資料時）
```

**鐵律**：未經「沙盒還原成功」不得對唯一生產副本做破壞性操作；密碼與 dump **不進 git**。

---

## 第 4 步｜應用接線（`augur-code-work`）

```bash
cd /home/giga/augur-code-work

# 4.1 .env（本機建立；gitignore）
# 至少需要（鍵名以該專案實際為準——先 grep 再填）：
#   DATABASE_URL=postgresql://augur:密碼@127.0.0.1:5432/augur
#   QDRANT_URL=http://127.0.0.1:6333
#   OLLAMA_URL=http://127.0.0.1:11434
grep -E 'DATABASE|POSTGRES|QDRANT|OLLAMA|5432|6333' \
  .env.example .env.sample README* 2>/dev/null | head -40
# 或：
grep -RIn --include='*.py' --include='*.toml' --include='*.md' \
  -E 'DATABASE_URL|QDRANT|OLLAMA' src scripts 2>/dev/null | head -40

# 4.2 venv（aarch64）
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
# 依專案清單安裝（擇一存在者）：
pip install -e '.[dev]' 2>/dev/null || pip install -r requirements.txt

# 4.3 import 煙霧
python -c "import augur; print('import augur OK')" 2>&1 || \
python -c "import sys; sys.path.insert(0,'src'); import augur; print('import OK')" 2>&1
```

### 4.4 應用煙霧（極小；失敗也要記檔）

```bash
# 先列入口，再選一支有 --help／dry-run 的
ls scripts/*advisor* scripts/*deliberat* 2>/dev/null | head -30
# 例（名稱以實檔為準；先 --help）：
# python scripts/deliberate.py --help
# 成功或失敗都寫入：
#   /home/giga/augur/ops/phase2/SMOKE-aitopatom-b96e-$(date +%Y%m%d).md
```

---

## 第 5 步｜驗收與固化

```bash
cd /home/giga/augur
python3 ops/phase2/operability_probe.py | tee ops/phase2/OPERABILITY-PROBE-T1-$(date +%Y%m%d).log
./ops/machines/packs/aitopatom-b96e/setup_check.sh
# （可選）擴充 setup_check 斷言 PG/qdrant UP——另 commit
```

文件更新（通過後）：

- [ ] `packs/aitopatom-b96e/README.md` 角色改「全執行節點（T1）」
- [ ] NOTES：PG/qdrant 端口、資料目錄 `/home/giga/augur-data/`
- [ ] 〔Steward〕是否將 GB10 寫入 `ENVIRONMENT-SPEC.md`／L7.50

---

## 附錄｜無 docker 權限時的 PG 備案（micromamba）

```bash
# 僅在 docker 不可用時
# curl -Ls https://micro.mamba.pm/api/micromamba/linux-aarch64/latest | tar -xvj bin/micromamba
# ./micromamba create -y -n augur-pg -c conda-forge postgresql=17
# 再依 HANDOFF 習慣自建 data dir、initdb、pg_ctl -o "-p 55432"
```

探測腳本已涵蓋 **5432** 與 **55432**。

---

## 風險與紅線

1. **aarch64**：錯誤拉 x86 映像／wheel 會失敗——一律查平台。
2. **55GB 級還原**：磁碟足夠（本機 ~3T 可用），但耗時；先沙盒。
3. **雙副本**：T1 後勿在 WSL2 繼續寫同一邏輯生產庫除非明確唯讀／切換期。
4. **密鑰**：`.env`、`POSTGRES_PASSWORD`、dump 路徑永不 `git add`。
5. **Agent 不得**自行宣告 ENVIRONMENT-SPEC 已生效或 L7 充任。

---

*手冊版本：2026-07-22｜對應拓撲 T1｜主機 aitopatom-b96e*
