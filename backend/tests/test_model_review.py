import json
import pytest
from app.services.model_review import validate_review, review_evidence
from app.config.settings import settings

SOURCES=[{"evidence_id":"E-1","text":"Acme has a policy to prevent safety recalls.","identity_match":"name_mention_only"}]
def result(**patch):
    return json.dumps({"findings":[dict({"evidence_id":"E-1","classification":"policy_or_process","quote":"policy to prevent safety recalls","interpretation":"A policy, not a reported incident.","buyer_question":"Request applicable product test evidence."},**patch)]})

def test_valid_source_quote():
    assert validate_review(result(),SOURCES)[0]["verification_status"]=="unverified_model_interpretation"

@pytest.mark.parametrize("patch",[
    {"evidence_id":"E-fabricated"}, {"quote":"Acme issued a safety recall yesterday."},
    {"classification":"approved"}, {"award_ready":True}])
def test_invalid_findings_fail_closed(patch):
    with pytest.raises(ValueError): validate_review(result(**patch),SOURCES)

def test_identity_cannot_be_upgraded():
    with pytest.raises(ValueError):
        validate_review(result(classification="reported_incident"),[{**SOURCES[0],"identity_match":"unresolved"}])

def test_duplicate_citations_rejected():
    d=json.loads(result());d["findings"]*=2
    with pytest.raises(ValueError):validate_review(json.dumps(d),SOURCES)

def test_offline_never_calls_provider(monkeypatch):
    monkeypatch.setattr(settings,"offline_mode",True)
    monkeypatch.setattr("urllib.request.urlopen",lambda *a,**k:pytest.fail("Network called"))
    assert review_evidence("Acme",None,[])["status"]=="offline"

def test_provider_failure_falls_back(monkeypatch):
    monkeypatch.setattr(settings,"offline_mode",False)
    monkeypatch.setattr(settings,"llm_api_key","test")
    monkeypatch.setattr(settings,"llm_model","test")
    def fail(*a,**k):raise TimeoutError()
    monkeypatch.setattr("urllib.request.urlopen",fail)
    assert review_evidence("Acme",None,[{**SOURCES[0],"summary":SOURCES[0]["text"]}])["status"]=="unavailable_or_invalid"
