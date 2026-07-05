"""OpenAI 相容顧問殼 server — 起 augur advisor 的 /v1 端點(N8 薄 CLI;WebUI 接線用)。

🎯 只解析參數+組 llm_fn+起 server;協定與回覆全在 augur.advisor.oai_compat,
   編排唯一出口=advisor.advise()(殼零編排、對全部表唯讀零寫)。
   guard fail=固定誠實句閉集(P9 建議值);guard verdict 機械尾註附於每則回覆。
   WebUI 接線形制(P10:唯一 model=本殼、零 Ollama 直連、title/tags/follow-up 停用)須用戶拍板後才配置。
守 #29(四件事:無參數=印矩陣+操作值、資料驅動零 hardcode 查詢、單一參數化工具、矩陣+實測)·
   #18(serve_advisor_openai=動作動詞片語)· #28(本地常駐零 usage)· 計畫 §3-S7 N8/§5 SOP[8]。

執行指令矩陣:
  python scripts/serve_advisor_openai.py                          # 無參數=印本矩陣+目前操作值(不起 server,安全預設)
  python scripts/serve_advisor_openai.py --serve                  # 起 server(預設 127.0.0.1:8399;llm=Ollama qwen3:8b)
  python scripts/serve_advisor_openai.py --port 8399              # 指定 --port 亦視為起 server(SOP 相容)
  python scripts/serve_advisor_openai.py --serve --mock-llm       # 免 Ollama 煙測(llm_fn=固定句;檢索/guard 仍走真管線)
  python scripts/serve_advisor_openai.py --serve --model qwen3:8b --timeout 300
  OLLAMA_BASE_URL=http://localhost:11434 python scripts/serve_advisor_openai.py --serve
  curl -s http://127.0.0.1:8399/v1/models
  curl -s -X POST http://127.0.0.1:8399/v1/chat/completions -H 'Content-Type: application/json' \
       -d '{"model":"augur-advisor","messages":[{"role":"user","content":"安全邊際是什麼?"}]}'
"""
import argparse
import os
import sys

import _bootstrap  # noqa: F401  (scripts 個別可執行,#29a)

from augur.advisor import oai_compat, ollama


def _mock_llm(prompt):
    """煙測用固定回覆(零數字零引號 → 不觸 guard 數字/引文閘;僅驗殼與管線接縫)。"""
    return "(mock-llm)已依 prompt 完成組裝;此為煙測固定回覆、非真實解讀。"


def main(argv=None):
    ap = argparse.ArgumentParser(description="OpenAI 相容顧問殼(唯一編排出口=advise();唯讀零寫)")
    ap.add_argument("--serve", action="store_true", help="起 server(無此旗標且無 --port=只印矩陣+操作值)")
    ap.add_argument("--host", default="127.0.0.1", help="綁定位址(預設 127.0.0.1,僅本機)")
    ap.add_argument("--port", type=int, default=None, help=f"埠(預設 {oai_compat.DEFAULT_PORT};給值即視為 --serve)")
    ap.add_argument("--model", default=None, help="Ollama model tag(預設 OLLAMA_MODEL env → qwen3:8b;操作值)")
    ap.add_argument("--timeout", type=float, default=None, help="LLM 單回合秒數(預設 OLLAMA_TIMEOUT env → 300)")
    ap.add_argument("--mock-llm", action="store_true", help="llm_fn=固定句(免 Ollama;檢索/guard 仍真)")
    ap.add_argument("--k", type=int, default=6, help="檢索引文數(預設 6)")
    ap.add_argument("--insecure-loopback-admin", action="store_true", dest="insecure_loopback_admin",
                    help="無身分 header 之請求當單機 admin(super);預設關=fail-closed(紅隊 HIGH:預設 super 會令忘設機密時 RBAC 靜默失效)")
    args = ap.parse_args(argv)

    port = args.port if args.port is not None else oai_compat.DEFAULT_PORT
    model = args.model or os.environ.get("OLLAMA_MODEL", ollama.DEFAULT_MODEL)
    if not (args.serve or args.port is not None):
        print(__doc__)
        print(f"目前操作值:host={args.host} port={port} model={model} "
              f"base_url={ollama.base_url()} timeout={args.timeout or os.environ.get('OLLAMA_TIMEOUT', ollama.DEFAULT_TIMEOUT)}s "
              f"payload=example_payload(示範;真實 as-of 整合屬後續)")
        return 0

    # R2 調校 2026-07-04:低溫(0.15)=忠實照抄真兆原文少觸 guard 逐字閘;think=False=關 qwen3 推理段
    # (弱 4GB GPU 上大幅提速、避 400s 逾時);num_predict 上限=有界輸出。
    llm_fn = _mock_llm if args.mock_llm else ollama.make_llm_fn(
        model=model, timeout=args.timeout, think=False, strip_quotes=True,
        options={"temperature": 0.15, "num_predict": 900})
    # 死點① 接線(計畫 §三):對話端組合檢索=work(哲學/文學)+item(知識/財經/本機檔),
    # 否則抓來的知識/item 零命中(retrieve_fn=None 只走 work 側)。access_scope='public'(對外)。
    from augur.philosophy.retrieval import retrieve_all
    from augur.advisor.payload import empty_payload    # 一般問答不注入示範選股(精準度 §2.4 D-1)
    secret = os.environ.get("AUGUR_INTERNAL_SECRET")
    if not secret and not args.insecure_loopback_admin:
        print("⚠ 未設 AUGUR_INTERNAL_SECRET 且未開 --insecure-loopback-admin:所有請求 fail-closed deny(無引文);"
              "請設機密(前台送 X-Augur-Session)或單機測試加 --insecure-loopback-admin。", flush=True)
    srv = oai_compat.make_server(args.host, port, llm_fn, payload_fn=empty_payload, retrieve_fn=retrieve_all, k=args.k,
                                 internal_secret=secret, insecure_loopback_admin=args.insecure_loopback_admin)
    print(f"augur-advisor 殼啟動 http://{args.host}:{port}/v1 "
          f"(llm={'mock' if args.mock_llm else model};payload=example_payload 示範;唯讀零寫;Ctrl-C 停)",
          flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("收到中斷,關閉 server。", flush=True)
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
