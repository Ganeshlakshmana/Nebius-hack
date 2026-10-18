import json

from app.config.settings import settings
from app.db.sqlite_store import AppStore
from app.services.search_gateway import SearchGateway


def test_tavily_search_uses_bearer_auth_and_news_window(tmp_path, monkeypatch):
    captured = {}

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def read(self):
            return json.dumps({"results": [{"title": "Nebius update", "url": "https://example.com/news",
                                             "content": "A recent update", "published_date": "2026-10-17"}]}).encode()

    def fake_urlopen(request, timeout):
        captured["request"] = request
        return Response()

    monkeypatch.setattr(settings, "offline_mode", False)
    monkeypatch.setattr(settings, "tavily_api_key", "test-tavily-key")
    monkeypatch.setattr("app.services.search_gateway.urlopen", fake_urlopen)
    gateway = SearchGateway(AppStore(tmp_path / "state.sqlite3"))

    results = gateway.search('"Nebius" recent news', max_results=5, topic="news",
                             time_range="month", filter_by_published_date=True)

    request = captured["request"]
    body = json.loads(request.data)
    assert request.get_header("Authorization") == "Bearer test-tavily-key"
    assert "api_key" not in body
    assert body["topic"] == "news" and body["time_range"] == "month"
    assert body["filter_by_published_date"] is True
    assert results[0]["published"] == "2026-10-17"
    assert gateway.last_status == "live_results"
