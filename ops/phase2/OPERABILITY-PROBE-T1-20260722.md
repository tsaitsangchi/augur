========================================================================
Augur Phase 2 可運作探測 [I]（探測而非自陳；唯讀）
hostname=aitopatom-b96e｜python=3.12.3
========================================================================
[  UP   ] ollama (11434)
          模型 3 個：nomic-embed-text:latest, qwen3:30b-a3b, qwen3-coder-next:latest｜已載入：（無常駐載入）
[  UP   ] qdrant (6333)
          qdrant version=1.18.3｜collections=?
[  UP   ] PostgreSQL (5432 標準)
          5432 確為 PostgreSQL（SSLRequest 回 'N'）
[ABSENT ] PostgreSQL (55432 userspace)
          55432 連線失敗：[Errno 111] Connection refused
[  UP   ] GPU / VRAM
          NVIDIA GB10, [N/A], [N/A]
[ INFO  ] 記憶體 / 磁碟
          MemTotal=122 GiB｜/ 總 3936 GB、可用 3537 GB
[ FOUND ] augur 應用碼
          /home/giga/augur（標記：src, scripts, venv, .env, pyproject.toml, .git, tools, constitution） ｜ /home/giga/augur-archive/augur-code-latest（標記：src, scripts, pyproject.toml, .git）
------------------------------------------------------------------------
小結：5/7 項就緒。ABSENT/PARTIAL 即為 Phase 2 待補之縫。
注意：entity_registry(3,491)/advisor/審議引擎一輪 等『應用層』探測，須有 augur 應用碼＋DB 驅動方能實跑；本腳本先確立服務/硬體/碼在否之現實。
