"""N8 OpenAI 相容殼 — /v1/chat/completions 協定 ↔ advise() 的薄 adapter(零編排、零寫入)。

🎯 讓任何 OpenAI client(Open WebUI/curl)接上 augur 顧問:殼只做協定翻譯,
   **唯一編排出口=advisor.advise()**(不重造管線、無第二編排器——含空檢索誠實句分支全在 advise 內);
   guard fail → 回固定誠實句閉集 NO_KNOWLEDGE_RESPONSE(P9 建議值:沿用不擴;非 LLM 原輸出);
   guard verdict 以**機械模板**附於回覆尾部(分隔線區隔、零 LLM 內容);
   偽 SSE:先回 role chunk(keepalive)、全文過閘後才分塊 emit(stream:true × guard 全文後置閘之唯一合規形);
   API key 收任意值(本地);**對諮詢資料面(knowledge_*/philosophy_*/feature/prediction/chat_*)唯讀零寫
   不變(命門 5/6);唯一例外=deliberation_* 審議帳本**(前台 ultracode 檔經 effort→engine 既有寫點落帳;
   advisor package 自身零 SQL 寫入語句——命門修訂文 2026-07-11 拍板 P3,程式層保證+file_grep 可驗)。
   住 advisor package=自動入 AST 隔離稽核(P14)。stdlib http.server 實作、零新增依賴。
   前台檔位(F1):body.model 承載 tier(augur-{4b,8b}-{fast,think,ultra});config 旗標關=行為逐位元同現行。
守 #1/#8/#15(經 advise+guard 落地)· #18(oai_compat=領域名詞)· 計畫 §3-S7 N8/§6(UI 軸:殼=穩定契約)。
"""
import json
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from augur.advisor.advise import advise
from augur.advisor.guard import NO_KNOWLEDGE_RESPONSE
from augur.advisor.payload import empty_payload

MODEL_ID = "augur-advisor"
DEFAULT_PORT = 8399
_SEP = "\n\n---\n"          # LLM 文本與機械尾註之分隔線(尾註零 LLM 內容)


def models_payload(cfg=None):
    """GET /v1/models 回應體。tiers 關(預設)=唯一 model=augur-advisor(現行形制);
    tiers 開=列全部 tier 並附 augur_tier 擴充欄(tok_per_s=DB 實測現算、非硬編;OpenAI 協定容忍額外欄)。"""
    if not (cfg and cfg.get("enabled")):
        return {"object": "list",
                "data": [{"id": MODEL_ID, "object": "model",
                          "created": int(time.time()), "owned_by": "augur"}]}
    from augur.advisor import effort
    data = []
    for tid, t in sorted(cfg.get("tiers", {}).items()):
        speed = effort.probe_speed(t["model"])
        label = f"{t['model'].split(':')[1]}·{t['effort']}"
        if t["effort"] == "ultra":
            label += f"(審議引擎={cfg.get('ultra', {}).get('engine_model', 'qwen3:4b')};白話={t['model']};分鐘級)"
        data.append({"id": tid, "object": "model", "created": int(time.time()), "owned_by": "augur",
                     "augur_tier": {"model_tag": t["model"], "effort": t["effort"],
                                    "tok_per_s": speed, "label": label,
                                    "engine_model": cfg.get("ultra", {}).get("engine_model")
                                    if t["effort"] == "ultra" else None}})
    return {"object": "list", "data": data, "augur_default_tier": cfg.get("default_tier")}


def _last_user_content(messages):
    """取最後一則 user 訊息文字(殼=單回合 adapter;OpenAI content 可為 str 或 parts list)。"""
    for m in reversed(messages or []):
        if m.get("role") == "user":
            c = m.get("content")
            if isinstance(c, str):
                return c.strip()
            if isinstance(c, list):
                return "\n".join(p.get("text", "") for p in c
                                 if isinstance(p, dict) and p.get("type") == "text").strip()
    return ""


def _verdict_note(result):
    """guard verdict 機械尾註(零 LLM 內容;值全出自 advise() 回傳結構)。"""
    v = result["guard"]
    lines = [f"[augur-guard] pass={str(v['pass']).lower()} issues={len(v['issues'])} "
             f"citations={len(result['citations'])} lex={len(result['lex_entries'])}"]
    lines += [f"[augur-guard] issue: {i}" for i in v["issues"]]
    return "\n".join(lines)


def _citations_block(citations):
    """系統逐字引文區塊(R2 架構:原文由系統提供、非 LLM 產出=保證逐字正確、公版可溯源、零幻像)。
    citations 為 advise() 檢索所得真兆列;此文本不經 LLM、不經 guard 逐字閘(它本身就是被引的原文)。"""
    if not citations:
        return ""
    # Mode B(附加檔)之引用不得掛「公版可溯源」(私有附檔非公版)——依 source_url 前綴切換標頭(#15 不誤標)
    attached = all((getattr(c, "source_url", "") or "").startswith("附加文件:") for c in citations)
    out = ["── 你附加的文件(系統逐字附上、僅本次對話、不入庫)──" if attached
           else "── 引經據典(系統逐字附上、公版可溯源)──"]
    for i, c in enumerate(citations):
        head = "《%s》%s" % (getattr(c, "work_title", "?"), getattr(c, "thinker", "") or "")
        chap = getattr(c, "chapter", "") or ""
        out.append("[%d] %s%s" % (i + 1, head, (" — " + chap) if chap else ""))
        out.append("    " + (getattr(c, "text", "") or "").strip()[:400])
        out.append("    (源:%s)" % (getattr(c, "source_url", "") or ""))
    return "\n".join(out)


def _reply_text(result):
    """對外回覆文本(R2 架構:模型只給白話解讀)。**公版「引經據典」逐字區塊一律不顯示**(用戶 directive
    2026-07-05 入憲/憲章 v1.30.0)——guard 內部仍以 citations 逐字校驗(honesty gate 不變、只隱藏呈現);
    Mode B 附加檔區塊【保留】(用戶自帶文件之助讀、非公版引經據典)。
    guard pass → LLM 解讀;guard fail(公版)→ 系統狀態句(不倒原文、不謊稱「無此內容」);皆附機械尾註。"""
    passed = result["guard"]["pass"]
    cites = result["citations"]
    attached = bool(cites) and all((getattr(c, "source_url", "") or "").startswith("附加文件:") for c in cites)
    if passed:
        body = result["response"]
    elif attached:
        body = "(顧問白話解讀因不合逐字引用規則被機械閘攔下;以下為附加檔原文,供你自行研讀)"
    else:
        # guard fail(公版):不倒引經據典原文(用戶 directive)→ 回誠實固定句閉集(不自造新句;
        # 閉集受憲章 v1.25.0 控、不得執行層自改;此為既有測試 guard_fail_returns_fixed_honest_closed_set 之判準)
        body = NO_KNOWLEDGE_RESPONSE
    parts = [body]
    if attached:                        # 僅 Mode B 附加檔顯示逐字區塊;公版引經據典一律不顯示(用戶 directive)
        parts.append(_citations_block(cites))
    parts.append(_verdict_note(result))
    return _SEP.join(parts)


def chat_completion(body, llm_fn, payload_fn=empty_payload, retrieve_fn=None,
                    k=6, cmpl_id=None, created=None, scope=None, picking_payload_fn=None,
                    model_id=None, extra_block=None, prefix_note=None):
    """POST /v1/chat/completions 主邏輯(非串流形;串流由 handler 以偽 SSE 分塊同一結果)。

    唯一編排出口=advise();殼不碰檢索/prompt/guard 細節。scope=(is_super, allowed_domains) 由 handler
    自 session 解析(RBAC P3,§4.3)、一路傳達檢索;None → 下游 fail-closed deny(非「不濾」)。
    payload_fn=一般/知識題之空 payload(去雜訊);picking_payload_fn=選股題之真實 as-of 預測 payload
    (D4,計畫 §5.2)——依 relevance.picking_intent(query) 分派,選股意圖 → 真 payload、否則 → payload_fn
    (勿新造編排器,唯一出口仍 advise())。picking_payload_fn=None → 一律走 payload_fn(向後相容)。
    回 OpenAI chat.completion dict(額外帶 augur_guard 結構欄);請求不合法 raise ValueError(handler 轉 400)。
    """
    if not isinstance(body, dict):
        raise ValueError("request body 非 JSON object")
    query = _last_user_content(body.get("messages"))
    if not query:
        raise ValueError("messages 內無 user 內容")
    attach = body.get("augur_attach")
    if isinstance(attach, dict) and (attach.get("text") or "").strip():
        # Mode B(對話「+」附加檔只問這次):本回合注入附加檔檢索 + 文件助讀 prompt + KnowledgePayload
        # → guard_knowledge 數字雙源;仍走同一 advise()+guard。Mode B lambda 顯式 scope=None(附檔是用戶自帶、
        # 不 RBAC domain 收窄;**禁 **kw 靜默吞——否則一般模式 scope 也被丟成 fail-open,§4.4)。
        from augur.philosophy.retrieval import retrieve_attached
        from augur.advisor.prompt import build_attached_prompt
        from augur.advisor.payload import KnowledgePayload
        doc_text, doc_title = attach["text"], (attach.get("title") or "附加文件")
        result = advise(query, KnowledgePayload(as_of="attached", domain="attached"), llm_fn, k=k,
                        retrieve_fn=lambda q, k=k, scope=None: retrieve_attached(q, doc_text, doc_title, k=k),
                        prompt_fn=build_attached_prompt, scope=scope)
    else:
        # D4 payload 分派(計畫 §5.2-2):選股意圖 → 真實 as-of 預測 payload;否則 → payload_fn(去雜訊)。
        from augur.advisor.relevance import picking_intent
        active_fn = picking_payload_fn if (picking_payload_fn is not None and picking_intent(query)) else payload_fn
        result = advise(query, active_fn(), llm_fn, k=k, retrieve_fn=retrieve_fn, scope=scope)
    content = _reply_text(result)
    if prefix_note:                     # ultracode 不合格題之誠實 fallback 說明(機械一行、前置)
        content = prefix_note + _SEP + content
    if extra_block:                     # ultracode 裁決區塊(§1.4 機械模板;guard 後硬隔線併入、不繞 guard)
        content = content + _SEP + extra_block
    return {
        "id": cmpl_id or f"chatcmpl-augur-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": created or int(time.time()),
        "model": model_id or MODEL_ID,
        "choices": [{"index": 0, "finish_reason": "stop",
                     "message": {"role": "assistant", "content": content}}],
        "augur_guard": {"pass": result["guard"]["pass"], "issues": result["guard"]["issues"],
                        "citations": len(result["citations"]), "lex_entries": len(result["lex_entries"])},
    }


# ── 偽 SSE(先 role chunk keepalive、全文過閘後分塊 emit)──
def _chunk(cmpl_id, created, delta, finish=None, model_id=None):
    return ("data: " + json.dumps({
        "id": cmpl_id, "object": "chat.completion.chunk", "created": created,
        "model": model_id or MODEL_ID,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]},
        ensure_ascii=False) + "\n\n")


def role_event(cmpl_id, created, model_id=None):
    """SSE 首 chunk(role/keepalive):advise() 可達分鐘級,先回此 chunk 防 client 逾時斷線。"""
    return _chunk(cmpl_id, created, {"role": "assistant"}, model_id=model_id)


def content_events(completion, size=160):
    """全文(已過閘)分塊 emit + finish + [DONE](偽 SSE 尾段)。"""
    text = completion["choices"][0]["message"]["content"]
    mid = completion.get("model")
    for i in range(0, len(text), size):
        yield _chunk(completion["id"], completion["created"], {"content": text[i:i + size]}, model_id=mid)
    yield _chunk(completion["id"], completion["created"], {}, finish="stop", model_id=mid)
    yield "data: [DONE]\n\n"


# ── stdlib HTTP 層(唯讀;API key 收任意值=不驗 Authorization)──
class AdvisorHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _deps(self):
        s = self.server
        return dict(llm_fn=s.llm_fn, payload_fn=s.payload_fn, retrieve_fn=s.retrieve_fn, k=s.k,
                    picking_payload_fn=getattr(s, "picking_payload_fn", None))

    def _resolve_scope(self):
        """RBAC scope 解析(P3/群組建置,§4.3):回 **(is_super, allowed, user_id)**——有 X-Augur-Internal→驗機密後以
        X-Augur-Session 自查 DB 自 resolve(**絕不信 body/header 帶入的 user_id/allowed_domains/is_super**),user_id
        供 local_private 擁有者收窄;機密不符/session 無效→fail-closed deny (False, ∅, None)。
        **無 internal header → 預設 fail-closed deny**(紅隊 HIGH 2026-07-05:舊 stopgap 預設 super,一旦忘設
        AUGUR_INTERNAL_SECRET 即 chat_ui 不送 header→每人被當 super、RBAC 靜默全失效);單機 admin 免登入之便利
        改為【顯式 opt-in】——僅當 server `insecure_loopback_admin=True`(--insecure-loopback-admin 旗標)才回 super、預設關。"""
        internal = self.headers.get("X-Augur-Internal")
        if internal is not None:                       # 前台已走內部身分通道
            secret = getattr(self.server, "internal_secret", None)
            if not (secret and internal == secret):
                return (False, frozenset(), None)      # 共享機密不符 → fail-closed deny
            from augur.knowledge.identity import verify_session
            from augur.knowledge.access import resolve_allowed_domains
            uid = verify_session(self.headers.get("X-Augur-Session"))
            if uid is None:
                return (False, frozenset(), None)      # 無效 session → deny(絕不 fallback public/全庫)
            is_super, allowed = resolve_allowed_domains(uid)
            return (is_super, allowed, uid)            # user_id 帶下游供私有擁有者收窄
        if getattr(self.server, "insecure_loopback_admin", False):
            return (True, frozenset(), None)           # 顯式 opt-in 單機 admin(預設關;紅隊 HIGH 修)
        return (False, frozenset(), None)              # 無身分通道 → 預設 fail-closed deny(非 super)

    def _send_json(self, status, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path.rstrip("/") == "/v1/models":
            from augur.advisor import effort
            return self._send_json(200, models_payload(effort.load_tiers()))
        self._send_json(404, {"error": {"message": f"unknown path {self.path}", "type": "invalid_request_error"}})

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/chat/completions":
            return self._send_json(404, {"error": {"message": f"unknown path {self.path}", "type": "invalid_request_error"}})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
        except (ValueError, UnicodeDecodeError):
            return self._send_json(400, {"error": {"message": "body 非合法 JSON", "type": "invalid_request_error"}})

        t0 = time.time()
        # ── F1 tier 解析(旗標關={"enabled":False}=全走 legacy 現行路徑;未知 tier 在任何 200 之前 400=V7)──
        tier, tiers_cfg = None, None
        from augur.advisor import effort
        tiers_cfg = effort.load_tiers()
        if tiers_cfg.get("enabled"):
            try:
                tier = effort.resolve_tier(body.get("model"), tiers_cfg)
            except effort.UnknownTierError as e:
                return self._send_json(400, {"error": {"message": str(e), "type": "invalid_request_error"}})

        def _run(cmpl_id=None, created=None, progress_cb=None):
            """一次完整回覆(tier 感知);tier=None → legacy 逐位元同現行。"""
            deps = self._deps()
            if tier is None:
                return chat_completion(body, cmpl_id=cmpl_id, created=created,
                                       scope=self._resolve_scope(), **deps)
            deps["llm_fn"] = effort.make_tier_llm_fn(tier, tiers_cfg)
            extra, prefix = None, None
            if tier.effort == "ultra":
                res = effort.run_ultracode(_last_user_content(body.get("messages")), tiers_cfg,
                                           progress_cb=progress_cb)
                if res.busy:                                   # 單飛忙碌:服務狀態句、不啟 advise(§2.6)
                    return {"id": cmpl_id or f"chatcmpl-augur-{uuid.uuid4().hex[:12]}",
                            "object": "chat.completion", "created": created or int(time.time()),
                            "model": tier.id,
                            "choices": [{"index": 0, "finish_reason": "stop",
                                         "message": {"role": "assistant", "content": effort.BUSY_NOTE}}],
                            "augur_guard": {"pass": True, "issues": [], "citations": 0, "lex_entries": 0}}
                if res.fallback_note:
                    prefix = res.fallback_note                 # 誠實 fallback:一般管線+機械前置說明
                else:
                    extra = effort.verdict_block(res)
                deps["llm_fn"] = effort.make_tier_llm_fn(tier._replace(effort="fast"), tiers_cfg)  # 白話走 fast 參數
            return chat_completion(body, cmpl_id=cmpl_id, created=created, scope=self._resolve_scope(),
                                   model_id=tier.id, extra_block=extra, prefix_note=prefix, **deps)

        if body.get("stream"):
            cmpl_id, created = f"chatcmpl-augur-{uuid.uuid4().hex[:12]}", int(time.time())
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            mid = tier.id if tier else None
            self.wfile.write(role_event(cmpl_id, created, model_id=mid).encode("utf-8"))
            self.wfile.flush()
            if tier and tier.effort == "ultra":
                # worker thread + progress queue(§2.4):進度行=零-LLM 機械模板段;閒置發 heartbeat
                import queue as _q
                import threading as _t
                q = _q.Queue()
                out = {}

                def work():
                    try:
                        out["c"] = _run(cmpl_id, created, progress_cb=lambda m: q.put(m))
                    except Exception as e:
                        out["c"] = {"id": cmpl_id, "created": created, "model": mid,
                                    "choices": [{"message": {"content": f"[augur-error] {e}"}}]}
                    finally:
                        q.put(None)
                _t.Thread(target=work, daemon=True).start()
                idle = float(tiers_cfg.get("progress", {}).get("heartbeat_idle_s", 15))
                while True:
                    try:
                        m = q.get(timeout=idle)
                    except _q.Empty:
                        self.wfile.write(_chunk(cmpl_id, created, {}, model_id=mid).encode("utf-8"))
                        self.wfile.flush()
                        continue
                    if m is None:
                        break
                    self.wfile.write(_chunk(cmpl_id, created,
                                            {"content": f"\n---\n[augur-progress] {m}"},
                                            model_id=mid).encode("utf-8"))
                    self.wfile.flush()
                completion = out["c"]
            else:
                try:
                    completion = _run(cmpl_id, created)
                except Exception as e:                                       # 串流已開 → 內容 chunk 誠實揭露
                    completion = {"id": cmpl_id, "created": created, "model": mid,
                                  "choices": [{"message": {"content": f"[augur-error] {e}"}}]}
            for ev in content_events(completion):
                self.wfile.write(ev.encode("utf-8"))
            self.wfile.flush()
            self.log_message("chat.completion(stream) %.1fs", time.time() - t0)
            self.close_connection = True
            return
        try:
            completion = _run()
        except ValueError as e:
            return self._send_json(400, {"error": {"message": str(e), "type": "invalid_request_error"}})
        except Exception as e:
            return self._send_json(500, {"error": {"message": f"{type(e).__name__}: {e}", "type": "server_error"}})
        self.log_message("chat.completion %.1fs guard_pass=%s",
                         time.time() - t0, completion["augur_guard"]["pass"])
        self._send_json(200, completion)


def make_server(host, port, llm_fn, payload_fn=empty_payload, retrieve_fn=None, k=6,
                internal_secret=None, insecure_loopback_admin=False, picking_payload_fn=None):
    """組好可 serve_forever() 的 ThreadingHTTPServer(依賴以 server 屬性注入 handler)。
    internal_secret=前台↔殼共享機密(X-Augur-Internal;驗身分通道)。
    insecure_loopback_admin=無 header 時是否當單機 admin(super);**預設 False＝fail-closed deny**
    (紅隊 HIGH 修:預設 super 會在忘設機密時令 RBAC 靜默失效);僅單機無多使用者時才顯式開。
    picking_payload_fn=選股題之真實預測 payload builder(D4,計畫 §5.2);None → 一律走 payload_fn。"""
    srv = ThreadingHTTPServer((host, port), AdvisorHandler)
    srv.llm_fn, srv.payload_fn, srv.retrieve_fn, srv.k = llm_fn, payload_fn, retrieve_fn, k
    srv.internal_secret = internal_secret
    srv.insecure_loopback_admin = insecure_loopback_admin
    srv.picking_payload_fn = picking_payload_fn
    return srv
