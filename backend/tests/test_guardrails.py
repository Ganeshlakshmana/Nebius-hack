"""One test per guardrail documented in backend/app/agents/<agent>/GUARDRAILS.md."""
from fastapi.testclient import TestClient

from app.agents.chat.agent import ChatAgent
from app.main import app
from app.services.search_gateway import clean_search_term, strip_html


def test_chat_validator_flags_ids_missing_from_tool_output():
    assert ChatAgent.unsupported_ids({"answer": "SUPP_00001 is best", "components": [{"props": {"id": "SUPP_00001"}}]}) == []
    assert ChatAgent.unsupported_ids({"answer": "SUPP_00002 is best", "components": []}) == ["SUPP_00002"]
    with TestClient(app) as client:
        result = client.post("/chat", json={"message": "Explain SUPP_00018"}).json()
        assert result["validated"] is True
        assert "validation_errors" not in result


def test_live_orders_dedupes_open_alerts_and_reset_clears_overlay():
    with TestClient(app) as client:
        client.post("/operations/scenario", json={"action": "reset"})
        first = client.post("/operations/scenario?supplier_id=SUPP_00002", json={"action": "start"}).json()
        second = client.post("/operations/scenario?supplier_id=SUPP_00002", json={"action": "start"}).json()
        assert second["alert"]["alert_id"] == first["alert"]["alert_id"]
        assert second["alert"]["deduplicated"] is True
        assert second["source"] == "simulated_feed"
        client.post("/operations/scenario", json={"action": "reset"})
        assert client.get("/operations/alerts").json()["items"] == []
        assert client.get("/suppliers/SUPP_00002").json()["profile"]["supplierID"] == "SUPP_00002"


def test_news_offline_returns_status_not_findings():
    with TestClient(app) as client:
        result = client.get("/signals/SUPP_00018").json()
        assert result["signals"] == []
        assert result["status"] in {"provider_not_configured", "no_results"}
        assert result["limitations"]
        assert client.get("/signals/SUPP_99999").status_code == 404


def test_search_terms_and_snippets_are_sanitised():
    assert clean_search_term('Acme" OR "x\n\tRail') == "Acme OR x Rail"
    assert len(clean_search_term("a" * 500)) == 200
    assert strip_html("<b>Recall</b> <script>x</script>notice") == "Recall x notice"


def test_research_rejects_company_name_empty_after_cleaning():
    with TestClient(app) as client:
        assert client.post("/research", json={"company": '""""'}).status_code == 422
        ok = client.post("/research", json={"company": 'Example "Rail" Co'}).json()
        report = client.get(f"/research/{ok['research_id']}").json()
        assert report["company"] == "Example Rail Co"
        assert report["status"] == "partial"
        assert report["budget_used"]["searches"] <= 15
        assert all(item["url"] for item in report["timeline"])


def test_scenarios_exclude_alerted_and_never_return_source():
    with TestClient(app) as client:
        result = client.post("/scenarios/what-if", json={"supplier_id": "SUPP_00018", "limit": 5}).json()
        ids = [a["supplierID"] for a in result["alternatives"]]
        assert "SUPP_00018" not in ids and len(ids) == 5
        distances = [a["profile_distance"] for a in result["alternatives"]]
        assert distances == sorted(distances)
        filtered = client.post("/scenarios/what-if", json={"supplier_id": "SUPP_00018", "limit": 5, "exclude_alerted": True}).json()
        assert not any(a["active_ops_alert"] for a in filtered["alternatives"])
        assert client.post("/scenarios/what-if", json={"supplier_id": "SUPP_99999"}).status_code == 404


def test_memo_escapes_input_and_rejects_bad_ids():
    with TestClient(app) as client:
        memo = client.post("/memos/shortlist", json={"ids": ["SUPP_00012", "SUPP_00018"], "chosen": "SUPP_00012",
                                                      "note": "<script>alert(1)</script>"})
        assert memo.status_code == 200
        assert "<script>alert(1)</script>" not in memo.text
        assert "&lt;script&gt;" in memo.text
        assert "simulated" in memo.text
        assert client.post("/memos/shortlist", json={"ids": ["SUPP_00012", "SUPP_99999"]}).status_code == 422
        assert client.post("/memos/shortlist", json={"ids": ["SUPP_00012"], "chosen": "SUPP_00018"}).status_code == 422
        assert client.post("/memos/shortlist", json={"ids": []}).status_code == 422
        assert client.post("/memos/shortlist", json={"ids": [f"SUPP_{n:05d}" for n in range(1, 22)]}).status_code == 422
        assert client.post("/memos/shortlist", json={"ids": ["SUPP_00012"], "note": "x" * 2001}).status_code == 422
