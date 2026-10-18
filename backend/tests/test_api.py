from fastapi.testclient import TestClient
from app.main import app


def test_core_api_and_dataset_grounding():
    with TestClient(app) as client:
        health = client.get("/health").json()
        assert health["dataset_rows"] == 10_000
        assert health["internal_agent_auth"] == "hmac-sha256"

        listed = client.get("/suppliers", params={"limit": 3, "sort_by": "total_risk"}).json()
        assert len(listed["items"]) == 3
        assert listed["total"] == 10_000

        profile = client.get("/suppliers/SUPP_00018").json()["profile"]
        assert profile["supplierID"] == "SUPP_00018"

        explanation = client.get("/suppliers/SUPP_00018/explain").json()
        assert explanation["total"] == profile["Total_Risk_Index"]
        assert explanation["contributions"]

        compared = client.post("/compare", json={"ids": ["SUPP_00012", "SUPP_00018"]}).json()
        assert len(compared["suppliers"]) == 2

        chat = client.post("/chat", json={"message": "Compare SUPP_00012 and SUPP_00018"}).json()
        assert chat["validated"] is True
        assert "SUPP_00012" in chat["answer"]


def test_simulated_ops_and_agent_handoffs():
    with TestClient(app) as client:
        response = client.post("/operations/scenario?supplier_id=SUPP_00001", json={"action": "start", "seed": 42})
        assert response.status_code == 200
        payload = response.json()
        assert payload["source"] == "simulated_feed"
        assert payload["alert"]["supplier_id"] == "SUPP_00001"
        assert payload["research"]["status"] == "partial"
        assert payload["alternatives"]["alternatives"]
        assert client.get("/operations/alerts").json()["items"]

        status = client.get("/operations/status", params={"ids": "SUPP_00001"}).json()
        assert status["items"][0]["source"] == "simulated_feed"


def test_compare_rejects_more_than_twenty():
    with TestClient(app) as client:
        response = client.post("/compare", json={"ids": [f"SUPP_{number:05d}" for number in range(1, 22)]})
        assert response.status_code == 422
