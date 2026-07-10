"""N5 Ollama llm_fn adapter — 本地 Ollama HTTP → advise() 抽象 LLM 界面的薄接頭。

🎯 make_llm_fn() 回 prompt(str)->response(str),接 advise(llm_fn=...)(advise.py:13 既有界面)。
   model tag / base_url / timeout 皆為操作值(env 或參數覆蓋、不寫死於呼叫端;#27 印 log 不鑄 schema);
   qwen3 `<think>` 段機械剝除(strip_think)於過 guard 閘前執行、思考段永不呈現——
   治 guard 假陽性源;剝除規則屬 P8 閘鏈定義之一環(計畫 §3-S7 N5)。
   重試僅限連線層錯誤且次數有界(見訊號即停、不重試風暴,#24 精神);逾時屬預期
   (qwen3:8b 於 4GB GPU 必部分 CPU offload、單回合可達分鐘級,計畫定錨 #16)→ 錯得大聲不硬衝。
守 #1(只轉發 LLM 原輸出、零改寫——剝 <think> 為機械規則非潤飾)· #15(失敗明說不佯稱)·
   #18(ollama=領域名詞)· 計畫 §6 SOP-C(換 LLM=改設定一行,本檔可整支替換)。
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE_URL = "http://localhost:11434"   # 操作值:OLLAMA_BASE_URL env 覆蓋
DEFAULT_MODEL = "qwen3:8b"                    # 操作值:OLLAMA_MODEL env / make_llm_fn(model=) 覆蓋,不寫死
DEFAULT_TIMEOUT = 300.0                       # 秒;操作值:OLLAMA_TIMEOUT env 覆蓋(弱 GPU 分鐘級屬預期)

# G3 host allowlist(憲章 v1.37.0:advisor prompt 含 owned_local citations、永不離本機)——
# 預設僅本機;內網推理主機須明示 OLLAMA_HOST_ALLOWLIST env 逗號分隔加入(仍不得為公網)。
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


def _assert_local_host(final_url):
    """G3 焊點(A-12):建構時斷言「最終 url」host ∈ 本機/內網 allowlist,違者 fail-loud。
    斷言最終組出的 url 而非只 base_url()——防任何組 url 路徑繞過;env 誤設外部端點=把
    owned_local 私有內容送出本機(違 v1.37.0 隱私鐵律),寧可拒起不可默默外送。"""
    host = urllib.parse.urlparse(final_url).hostname or ""
    extra = {h.strip() for h in os.environ.get("OLLAMA_HOST_ALLOWLIST", "").split(",") if h.strip()}
    if host not in (_LOCAL_HOSTS | extra):
        raise RuntimeError(
            f"G3 拒起:llm_fn 端點 host={host!r} 不在本機 allowlist {sorted(_LOCAL_HOSTS | extra)}"
            f"(v1.37.0 owned_local 永不離本機;內網主機須明示 OLLAMA_HOST_ALLOWLIST)")

_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)
_QUOTE_MARKS = str.maketrans({"「": "", "」": "", "『": "", "』": "", "“": "", "”": ""})


def strip_quote_marks(text):
    """R2 架構機械正規化(2026-07-04):剝除模型輸出的引號框(「」『』"")。

    設計依據=模型(qwen3:8b)對名典有強記憶、反射性引用自己背的版本,與公版原文有標點/字差
    → 逐字閘必攔、整段解讀被打掉(實測)。R2 定調:**模型不從事逐字引用**(它做不到精準照抄),
    逐字原文改由系統 citations 逐字提供(oai_compat._citations_block,本即檢索原文=零幻像)。
    剝框後模型文字=純白話評論、不再宣稱 verbatim → guard ①(引文逐字)無可攔;而 guard ②③④
    (數字白名單/未來洩漏/逆向翻轉)仍作用於評論文本 → 數字與行動安全不受影響。與 strip_think 同層。"""
    return (text or "").translate(_QUOTE_MARKS)


def strip_think(text):
    """qwen3 <think> 思考段機械剝除(P8 閘鏈一環):閉合段全刪;
    未閉合(輸出截斷)→ 自 <think> 起全刪(fail-closed,寧空勿漏思考段入閘/入眼)。"""
    out = _THINK.sub("", text or "")
    cut = out.find("<think>")
    if cut != -1:
        out = out[:cut]
    return out.strip()


def base_url():
    """Ollama 端點(操作值):OLLAMA_BASE_URL env,預設 localhost:11434。"""
    return os.environ.get("OLLAMA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def make_structured_llm_fn(schema, model=None, base=None, timeout=None, retries=1, options=None, think=False):
    """組一個 prompt(str)->dict 的結構化 llm_fn(Ollama /api/chat + format=JSON schema;實測 2026-07-10
    qwen3:8b/4b 皆成立)。審議引擎模式 7 之落地:schema 驗證失敗→有界重試(把錯誤回饋進下一輪 prompt)。

    schema:  JSON schema dict(傳 Ollama format=;回傳值已 json.loads 並過 required-keys 檢查)
    think:   預設 False——實測 qwen3:4b 於 think 未壓時思考文**無標籤直接洩進內容**;format 約束本身
             壓住洩漏,但仍固定 think=False 省 ~7× 耗時(裁決步要深思者顯式傳 think=True)
    retries: schema/JSON 解析失敗之有界重試次數(連線層錯誤沿用同界;不風暴 #24)
    失敗 raise RuntimeError(錯得大聲 #15)。G3 host allowlist 同 make_llm_fn(v1.37.0)。
    注意:format 約束下 num_predict 過小會**截斷 JSON**(實測 80 tok 截斷、300 tok 成立)——
    options 未給 num_predict 時預設 512。
    """
    tag = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    url = (base or base_url()) + "/api/chat"
    _assert_local_host(url)   # G3 焊點(v1.37.0)
    limit = float(timeout if timeout is not None else os.environ.get("OLLAMA_TIMEOUT", DEFAULT_TIMEOUT))
    opts = dict(options or {})
    opts.setdefault("num_predict", 512)
    required = list(schema.get("required", []))

    def llm_fn(prompt):
        feedback = ""
        last_err = None
        for attempt in range(retries + 1):
            body = {"model": tag, "stream": False, "think": think, "format": schema,
                    "messages": [{"role": "user", "content": prompt + feedback}], "options": opts}
            req = urllib.request.Request(
                url, data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=limit) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                raise RuntimeError(f"Ollama HTTP {e.code} @ {url} model={tag}: {e.read()[:200]!r}") from e
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                raise RuntimeError(f"Ollama 連線/逾時 @ {url} model={tag}: {e}") from e
            content = (data.get("message") or {}).get("content", "")
            try:
                obj = json.loads(content)
                missing = [k for k in required if k not in obj]
                if missing:
                    raise ValueError(f"缺 required 鍵 {missing}")
                return obj
            except (json.JSONDecodeError, ValueError) as e:   # schema 驗證失敗 → 有界重試,錯誤回饋進 prompt
                last_err = e
                feedback = (f"\n\n[上輪輸出不合 schema:{e};請嚴格輸出含 "
                            f"{required} 鍵之合法 JSON,勿含其他文字]")
        raise RuntimeError(f"structured output {retries + 1} 次皆不合 schema @ model={tag}: {last_err}")

    return llm_fn


def make_llm_fn(model=None, base=None, timeout=None, retries=1, options=None, think=None, strip_quotes=False):
    """組一個 prompt(str)->response(str) 的 llm_fn(advise() 唯一需要的界面)。

    model:   Ollama model tag(預設 OLLAMA_MODEL env → 'qwen3:8b';操作值不寫死)
    base:    端點(預設 base_url())
    timeout: 單次呼叫秒數(預設 OLLAMA_TIMEOUT env → 300)
    retries: 連線層錯誤(connection refused 等)之有界重試次數;HTTP 4xx/5xx 與逾時不重試(不風暴)
    options: dict,原樣傳 Ollama options(如 {'temperature': 0, 'num_predict': 800})
    think:   qwen3 thinking 模式(False=關,不生成 <think> 推理段→弱 GPU 上大幅提速;None=不指定用模型預設)
    strip_quotes: True=剝除輸出引號框(R2 架構:模型不逐字引用、引用由系統 citations 負責,見 strip_quote_marks)
    回傳之 llm_fn 已含 <think> 機械剝除;失敗 raise RuntimeError(錯得大聲,#15)。
    """
    tag = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    url = (base or base_url()) + "/api/generate"
    _assert_local_host(url)   # G3 焊點:建構時斷言最終 url(v1.37.0;換模不鬆動,A-12)
    limit = float(timeout if timeout is not None else os.environ.get("OLLAMA_TIMEOUT", DEFAULT_TIMEOUT))

    def llm_fn(prompt):
        body = {"model": tag, "prompt": prompt, "stream": False}
        if think is not None:
            body["think"] = think
        if options:
            body["options"] = dict(options)
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        last_err = None
        for attempt in range(retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=limit) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                out = strip_think(data.get("response", ""))
                return strip_quote_marks(out) if strip_quotes else out
            except urllib.error.HTTPError as e:            # 服務端有回應 → 不重試(非連線層)
                raise RuntimeError(f"Ollama HTTP {e.code} @ {url} model={tag}: {e.read()[:200]!r}") from e
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                if isinstance(getattr(e, "reason", None), TimeoutError) or isinstance(e, TimeoutError):
                    raise RuntimeError(
                        f"Ollama 逾時(>{limit:.0f}s)@ {url} model={tag};弱 GPU 分鐘級屬預期,"
                        f"調 OLLAMA_TIMEOUT 或換更小 model(SOP-C)") from e
                last_err = e
                if attempt < retries:
                    time.sleep(1.0 * (attempt + 1))        # 有界短退避,僅連線層
        raise RuntimeError(f"Ollama 連線失敗 @ {url} model={tag}: {last_err}") from last_err

    return llm_fn
