import math
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.component_risk import ComponentRisk, resolve_components


def test_component_ranking_and_chat():
    with TestClient(app) as client:
        result = client.post('/components/analyze', json={'component':'brake pads', 'supplier_ids':['SUPP_00012','SUPP_00450','SUPP_00731']})
        assert result.status_code == 200
        result = result.json()
        assert result['component_id'] == 'braking'
        assert math.isclose(sum(result['weights'].values()), 1)
        scores = [s['component_score'] for s in result['items']]
        assert scores == sorted(scores)
        for item in result['items']:
            assert item['qualification_status'] == 'unverified'
            assert item['component_score'] == round(sum(f['score'] * f['weight'] for f in item['factors']), 2)
            assert item['required_checks']
        answer = client.post('/chat', json={'message':'Compare brake pads for SUPP_00012 and SUPP_00450'}).json()
        assert answer['components'][0]['type'] == 'component_risk'
        assert len(answer['component_analysis']['items']) == 2
        explicit = client.post('/chat', json={'message':'Analyze my shortlist', 'component':'traction', 'supplier_ids':['SUPP_00018']}).json()
        assert explicit['component_analysis']['component_id'] == 'traction'
        assert explicit['component_analysis']['items'][0]['critical_factors']


@pytest.mark.parametrize('component,ids', [('unknown part',['SUPP_00001']),('brakes and motors',['SUPP_00001']),('brakes',['SUPP_99999'])])
def test_analysis_rejects_ambiguous_or_missing_inputs(component, ids):
    with TestClient(app) as client:
        assert client.post('/components/analyze',json={'component':component,'supplier_ids':ids}).status_code == 422


def test_chat_no_selection_and_selection_limit():
    with TestClient(app) as client:
        result=client.post('/chat',json={'message':'Find the best company for a traction motor'}).json()
        assert result['component_analysis']['status'] == 'clarification_required'
        assert result['components'] == []
        assert client.post('/components/analyze',json={'component':'doors','supplier_ids':['SUPP_00001']*21}).status_code == 422
        result=client.post('/components/analyze',json={'component':'doors','supplier_ids':['SUPP_00001']*2}).json()
        assert len(result['items']) == 1


def test_missing_values_and_ties():
    base={'supplierID':'SUPP_00001','Supplier Name':'Example','Total_Risk_Index':40,
          'Quality_Risk_Score':25,'Safety_Incident_Score':25,'Compliance_Risk_Score':25,'Operational_Resilience_Score':25}
    rows=[base,dict(base,supplierID='SUPP_00002'),dict(base,supplierID='SUPP_00003',Quality_Risk_Score=None)]
    tools=SimpleNamespace(get_suppliers=lambda ids:rows,data=SimpleNamespace(csv_path=Path('data.csv')))
    result=ComponentRisk(tools).analyze('braking',[r['supplierID'] for r in rows])
    assert [r['rank'] for r in result['items']] == [1,1,None]
    assert result['items'][-1]['component_score'] is None
    assert result['items'][-1]['missing_metrics'] == ['Quality_Risk_Score']
    assert resolve_components('doorstep investment') == []


def test_component_research_queries(monkeypatch):
    with TestClient(app) as client:
        queries=[]
        monkeypatch.setattr(app.state.search,'search',lambda query,**kwargs: queries.append(query) or [])
        response=client.post('/research',json={'company':'Example Rail Co','component':'brake pads'})
        report=client.get('/research/'+response.json()['research_id']).json()
        assert report['component']=='brake pads'
        assert report['component_qualification']=='unverified'
        assert any('brake pads' in q and 'certification' in q for q in queries)
        assert report['scorecard']=={}


def test_component_routes_are_distinct():
    with TestClient(app) as client:
        catalog_items = client.get('/components/catalog').json()['items']
        assert {item['id'] for item in catalog_items} >= {'braking', 'traction'}
        overlay = client.get('/components', params={'limit': 5}).json()
        assert overlay['source'] == 'simulated_component_dataset'
        assert len(overlay['items']) == 5
        risk = client.get('/suppliers/SUPP_00018/component-risk')
        assert risk.status_code == 200
        assert client.get('/suppliers/SUPP_99999/component-risk').status_code == 404
