"""finmind.py fetch 重試/退避回歸測試（monkeypatch requests，不打 live API；clean-room）。

覆蓋 2026-06-11 修正：_RETRY_STATUS 納 5xx gateway 暫時錯誤退避重試（TotalInstitutional 502）；
應用層錯誤（參數/token）立即拋不重試；單日型 dataset（News：size-too-large、end_date 須 none）自動移除 end_date 重抓單日。
"""
import pytest

from augur.ingestion import finmind


class FakeResp:
    def __init__(self, status, payload=None, json_raises=False):
        self.status_code = status
        self._payload = payload
        self._json_raises = json_raises

    def json(self):
        if self._json_raises:
            raise ValueError("not JSON (e.g. 502 HTML gateway page)")
        return self._payload


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    # 略過 _pace 限速 + 退避 sleep，加速測試（monotonic 照常）
    monkeypatch.setattr(finmind.time, "sleep", lambda *a, **k: None)


def test_retry_status_includes_5xx_and_ratelimit():
    for s in (500, 502, 503, 504, 402, 429, 403):
        assert s in finmind._RETRY_STATUS


def test_5xx_non_json_retry_then_success(monkeypatch):
    # 502/503 回 HTML(非 JSON) → 退避重試 → 200 成功（不因 resp.json() 崩）
    seq = iter([FakeResp(502, json_raises=True), FakeResp(503, json_raises=True),
                FakeResp(200, {"status": 200, "data": [{"a": 1}]})])
    monkeypatch.setattr(finmind.requests, "get", lambda *a, **k: next(seq))
    assert finmind.fetch("X") == [{"a": 1}]


def test_429_honors_retry_after_then_success(monkeypatch):
    seq = iter([FakeResp(429, {"retry_after": 1}), FakeResp(200, {"status": 200, "data": []})])
    monkeypatch.setattr(finmind.requests, "get", lambda *a, **k: next(seq))
    assert finmind.fetch("X") == []


def test_app_error_no_retry(monkeypatch):
    # HTTP 200 但 body status≠200（參數/token 錯）→ 立即拋、不重試
    calls = [0]

    def fake_get(*a, **k):
        calls[0] += 1
        return FakeResp(200, {"status": 400, "msg": "parameter data_id can't be none"})

    monkeypatch.setattr(finmind.requests, "get", fake_get)
    with pytest.raises(finmind.FinMindError):
        finmind.fetch("X")
    assert calls[0] == 1  # 無重試


def test_5xx_exhausted_raises(monkeypatch):
    monkeypatch.setattr(finmind.requests, "get", lambda *a, **k: FakeResp(502, json_raises=True))
    with pytest.raises(finmind.FinMindError):
        finmind.fetch("X", max_retries=2)


def test_success_returns_data_list(monkeypatch):
    monkeypatch.setattr(finmind.requests, "get",
                        lambda *a, **k: FakeResp(200, {"status": 200, "data": [{"x": 1}, {"x": 2}]}))
    assert finmind.fetch("X", data_id="2330") == [{"x": 1}, {"x": 2}]


def test_single_day_dataset_removes_end_date(monkeypatch):
    # 單日型 dataset（FinMind size-too-large、end_date 須 none，如 News）：帶 end_date → 自動移除後重抓單日
    seen_end = []

    def fake_get(*a, **k):
        has_end = k["params"].get("end_date") is not None
        seen_end.append(has_end)
        if has_end:
            return FakeResp(200, {"status": 400, "msg": "dataset X size is too large, "
                                  "we only send one day data, so end_date parameter need be none."})
        return FakeResp(200, {"status": 200, "data": [{"date": "2024-01-01 03:00:00"}]})

    monkeypatch.setattr(finmind.requests, "get", fake_get)
    out = finmind.fetch("X", data_id="2330", start_date="2024-01-01", end_date="2024-01-31")
    assert out == [{"date": "2024-01-01 03:00:00"}]
    assert seen_end == [True, False]   # 首帶 end 被拒 → 移除 end 重試（第二次不帶 end，無無限遞迴）


def test_end_none_msg_without_end_param_no_recurse(monkeypatch):
    # msg 含 end_date/none 但本就沒帶 end_date → guard 不誤觸發移除（防無限遞迴）→ 直接拋、不重試
    calls = [0]

    def fake_get(*a, **k):
        calls[0] += 1
        return FakeResp(200, {"status": 400, "msg": "end_date parameter need be none"})

    monkeypatch.setattr(finmind.requests, "get", fake_get)
    with pytest.raises(finmind.FinMindError):
        finmind.fetch("X", data_id="2330", start_date="2024-01-01")   # 無 end_date
    assert calls[0] == 1
