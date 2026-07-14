"""嵌入規格 SSOT — model_tag／dim／textnorm 世代與 Milvus collection 命名的唯一住所。

🎯 這支在做什麼(白話):嵌入世代三元組(model_tag, dim, textnorm_ver)與其全部衍生命名
   (確定性 slug、collection 名、build_meta/coverage 同步鍵)只住這裡——
   S5 嵌入(embed_knowledge)、S6 serving 索引(vectorindex/export_milvus_index)、
   S7 檢索(philosophy.retrieval)三端 import 同一份,禁 inline 複本、禁文件/SOP 手寫縮寫;
   換嵌入模型=改這裡(SOP-A),collection 名自動換世代、舊世代不覆蓋。
守 #12(單一住所)· #15(slug 確定性:同輸入必同輸出、無隨機)· #18(領域名詞)·
   e2e 計畫 §3-S6/§6(model_tag 含 '/' 為 Milvus 非法字元→縮寫映射函數單一住所=本檔)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.embedspec              # 印用途+公開入口（唯讀）
  python -m augur.knowledge.embedspec --selftest   # 純紅綠自測（零 IO）
"""
import hashlib
import re

# ── 嵌入世代三元組(現行操作值;換模走 SOP-A、換 textnorm/jieba 版走 SOP-E)──────
MODEL_TAG = "intfloat/multilingual-e5-small"
MODEL_DIMS = {MODEL_TAG: 384}   # 已登記模型→維度;未登記=fail loud(異維模型=新表世代,拍板 P6)
TEXTNORM_VER = 1                # textnorm 契約世代(jieba HMM=False+Porter 1980;換 jieba 版=升版+重建)
QUERY_DEVICE = "cpu"            # 查詢端(retrieval 單句)嵌入 device;批量嵌入(embed_knowledge)另用 GPU

_LAYERS = {"sentence": "sent", "lexicon": "lex"}
_SIDES = {"works": "wk", "items": "it"}
# 長度預算:knowledge_build_meta.scope 與 knowledge_coverage_metric.metric_key 皆 VARCHAR(32),
# 同步鍵="mv_"+collection+"_"+language(≤3) → collection 名上限 26。
_NAME_MAX = 26
_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def dim_for(model_tag=MODEL_TAG):
    """已登記模型之向量維度;未登記即 KeyError(fail-closed:不猜維度、不建錯維 collection)。"""
    if model_tag not in MODEL_DIMS:
        raise KeyError(f"model_tag 未登記於 embedspec.MODEL_DIMS: {model_tag!r}(換模先登記 tag+dim,SOP-A)")
    return MODEL_DIMS[model_tag]


def model_slug(model_tag=MODEL_TAG):
    """model_tag → Milvus 合法確定性 slug:token 首字縮寫(≤5)+sha1 前 6 碼(碰撞保險)。
    純函數、零查表狀態;'intfloat/multilingual-e5-small' → 'ime5s30b1cd'。"""
    toks = [t for t in re.split(r"[^0-9a-zA-Z]+", str(model_tag).lower()) if t]
    if not toks:
        raise ValueError(f"model_tag 無可用字元: {model_tag!r}")
    abbr = "".join(t[0] if len(t) > 2 else t for t in toks)[:5]
    return abbr + hashlib.sha1(str(model_tag).encode("utf-8")).hexdigest()[:6]


def collection_name(layer, side, model_tag=MODEL_TAG, textnorm_ver=TEXTNORM_VER):
    """Milvus collection 名=kn_{layer}_{side}_{slug}_tn{ver}(世代入名:換模/換 textnorm=新 collection)。
    layer/side 封閉集之外、超長、非法字元一律 fail loud。"""
    if layer not in _LAYERS:
        raise ValueError(f"layer 不在封閉集 {sorted(_LAYERS)}: {layer!r}")
    if side not in _SIDES:
        raise ValueError(f"side 不在封閉集 {sorted(_SIDES)}: {side!r}")
    name = f"kn_{_LAYERS[layer]}_{_SIDES[side]}_{model_slug(model_tag)}_tn{int(textnorm_ver)}"
    if len(name) > _NAME_MAX or not _NAME_RE.match(name):
        raise ValueError(f"collection 名超出預算({_NAME_MAX})或含非法字元: {name!r}")
    return name


def sync_scope(collection, language):
    """S6 同步鍵(build_meta.scope 與 coverage_metric.metric_key 共用)= mv_{collection}_{language};
    兩欄皆 VARCHAR(32),超長 fail loud(不截斷=不產生歧義鍵)。"""
    key = f"mv_{collection}_{language}"
    if len(key) > 32:
        raise ValueError(f"同步鍵超過 32 字元(DB 欄寬): {key!r}")
    return key


def _selftest():
    """純紅綠自測(零 IO):固化 slug 確定性(#15)、維度登記、命名/長度預算不變式。"""
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    def raises(fn, exc):                                        # 純:確認呼叫拋預期例外
        try:
            fn(); return False
        except exc:
            return True
        except Exception:
            return False

    # slug 確定性(#15:同輸入必同輸出、無隨機;鎖 docstring 記載值)
    chk("model_slug 確定性(冪等)", model_slug(MODEL_TAG) == model_slug(MODEL_TAG))
    chk("model_slug 鎖值 ime5s30b1cd", model_slug(MODEL_TAG) == "ime5s30b1cd")
    chk("model_slug 空 tag→ValueError", raises(lambda: model_slug("!!!"), ValueError))
    # 維度登記(fail-closed:未登記=KeyError、不猜維)
    chk("dim_for 現行=384", dim_for(MODEL_TAG) == 384)
    chk("dim_for 未登記→KeyError", raises(lambda: dim_for("no/such-model"), KeyError))
    # collection 命名:合法集內、長度/正則預算、封閉集外 fail loud
    cn = collection_name("sentence", "works")
    chk("collection_name 格式", cn == "kn_sent_wk_ime5s30b1cd_tn1")
    chk("collection_name ≤26 且合法字元", len(cn) <= _NAME_MAX and bool(_NAME_RE.match(cn)))
    chk("collection_name 壞 layer→ValueError", raises(lambda: collection_name("bad", "works"), ValueError))
    chk("collection_name 壞 side→ValueError", raises(lambda: collection_name("sentence", "bad"), ValueError))
    # 同步鍵:格式與 32 字元 DB 欄寬(不截斷、超長 fail loud)
    chk("sync_scope 格式", sync_scope(cn, "en") == f"mv_{cn}_en")
    chk("sync_scope 超長→ValueError", raises(lambda: sync_scope(cn, "toolonglang"), ValueError))

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.embedspec --selftest;免 DB 免 API)")
