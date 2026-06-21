"""fred.py fetch vintage / point-in-time 回歸測試（monkeypatch requests，不打 live API；clean-room）。

覆蓋 FRED vintage 模型：
- vintage=True → ALFRED 全 realtime 範圍參數（realtime_start/realtime_end/output_type）+ 保留各列真 realtime_start。
- vintage=False（Tier A）→ 不帶 realtime 參數、realtime_start 注入觀測日本身（市場當日即知＝PIT，#8）。
- "." → None；每列補 series_id；realtime_end 不存。
- ALFRED 2000-vintage 上限 / 超單頁 → 明確 FredError（不靜默截斷，#15）。
- 429 限流 → 退避重試。
"""
import pytest

from augur.ingestion import fred


class FakeResp:
    def __init__(self, status, payload=None, json_raises=False):
        self.status_code = status
        self._payload = payload
        self._json_raises = json_raises

    def json(self):
        if self._json_raises:
            raise ValueError("not JSON")
        return self._payload


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(fred.time, "sleep", lambda *a, **k: None)


def _serve(payload, capture=None):
    """fake requests.get：回固定 payload；capture 非 None 時把送出之 params 記入（驗參數）。"""
    def fake_get(*a, **k):
        if capture is not None:
            capture.append(k["params"])
        return FakeResp(200, payload)
    return fake_get


# ── vintage 參數 ──────────────────────────────────────────
def test_vintage_true_sets_alfred_params(monkeypatch):
    cap = []
    payload = {"count": 1, "observations": [
        {"date": "2020-01-01", "realtime_start": "2020-02-15", "value": "1.0"}]}
    monkeypatch.setattr(fred.requests, "get", _serve(payload, cap))
    fred.fetch("CPIAUCSL", vintage=True)
    p = cap[0]
    assert p["realtime_start"] == "1776-07-04"
    assert p["realtime_end"] == "9999-12-31"
    assert p["output_type"] == 1


def test_vintage_false_omits_alfred_params(monkeypatch):
    cap = []
    payload = {"count": 1, "observations": [{"date": "2020-01-02", "value": "1.88"}]}
    monkeypatch.setattr(fred.requests, "get", _serve(payload, cap))
    fred.fetch("DGS10", vintage=False)
    p = cap[0]
    assert "realtime_start" not in p
    assert "realtime_end" not in p
    assert "output_type" not in p


# ── realtime_start 語意 ───────────────────────────────────
def test_vintage_keeps_api_realtime_start(monkeypatch):
    # 同一觀測日多版 → 各保留 API 真 realtime_start（供 PIT 取版）
    payload = {"count": 2, "observations": [
        {"date": "2020-01-01", "realtime_start": "2020-02-15", "value": "1.0"},
        {"date": "2020-01-01", "realtime_start": "2020-03-15", "value": "1.1"}]}
    monkeypatch.setattr(fred.requests, "get", _serve(payload))
    rows = fred.fetch("CPIAUCSL", vintage=True)
    assert [r["realtime_start"] for r in rows] == ["2020-02-15", "2020-03-15"]
    assert [r["date"] for r in rows] == ["2020-01-01", "2020-01-01"]


def test_nonvintage_injects_date_as_realtime_start(monkeypatch):
    # 非 vintage：忽略 API 之查詢日 realtime、改注入觀測日本身（市場當日即知）
    payload = {"count": 1, "observations": [
        {"date": "2020-01-02", "realtime_start": "2026-06-21", "value": "1.88"}]}
    monkeypatch.setattr(fred.requests, "get", _serve(payload))
    rows = fred.fetch("DGS10", vintage=False)
    assert rows[0]["realtime_start"] == "2020-01-02"


def test_realtime_end_never_stored(monkeypatch):
    payload = {"count": 1, "observations": [
        {"date": "2020-01-01", "realtime_start": "2020-02-15",
         "realtime_end": "2020-03-14", "value": "1.0"}]}
    monkeypatch.setattr(fred.requests, "get", _serve(payload))
    for vintage in (True, False):
        rows = fred.fetch("X", vintage=vintage)
        assert "realtime_end" not in rows[0]


# ── 值/欄處理 ─────────────────────────────────────────────
def test_dot_value_to_none_and_series_id_added(monkeypatch):
    payload = {"count": 2, "observations": [
        {"date": "2020-01-01", "value": "."},
        {"date": "2020-01-02", "value": "2.5"}]}
    monkeypatch.setattr(fred.requests, "get", _serve(payload))
    rows = fred.fetch("DGS10")
    assert rows[0]["value"] is None and rows[1]["value"] == "2.5"
    assert all(r["series_id"] == "DGS10" for r in rows)


# ── 錯誤處理（不靜默截斷 #15）─────────────────────────────
def test_2000_vintage_cap_raises_with_guidance(monkeypatch):
    body = {"error_message": "There are 5049 vintage dates ... exceeds the maximum "
            "number of vintage dates allowed for this file type (2000)."}
    monkeypatch.setattr(fred.requests, "get", lambda *a, **k: FakeResp(400, body))
    with pytest.raises(fred.FredError) as e:
        fred.fetch("DGS10", vintage=True)
    assert "2000" in str(e.value)


def test_pagination_overflow_raises(monkeypatch):
    # count > 回傳列數 → 超單頁 → 明失敗、不靜默截斷
    payload = {"count": 100001, "observations": [{"date": "2020-01-01", "value": "1.0"}]}
    monkeypatch.setattr(fred.requests, "get", _serve(payload))
    with pytest.raises(fred.FredError) as e:
        fred.fetch("X", vintage=True)
    assert "分頁" in str(e.value) or "單頁" in str(e.value)


def test_app_error_non200_raises(monkeypatch):
    monkeypatch.setattr(fred.requests, "get",
                        lambda *a, **k: FakeResp(400, {"error_message": "Bad Request. api_key invalid."}))
    with pytest.raises(fred.FredError):
        fred.fetch("X")


# ── 限流退避 ─────────────────────────────────────────────
def test_429_retry_then_success(monkeypatch):
    seq = iter([FakeResp(429), FakeResp(200, {"count": 0, "observations": []})])
    monkeypatch.setattr(fred.requests, "get", lambda *a, **k: next(seq))
    assert fred.fetch("X") == []


def test_429_exhausted_raises(monkeypatch):
    monkeypatch.setattr(fred.requests, "get", lambda *a, **k: FakeResp(429))
    with pytest.raises(fred.FredError):
        fred.fetch("X", max_retries=2)
