from datetime import date,timedelta
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c: yield c

def payload():
    return {'component':'Custom vibration isolator','application':'Regional train drawing ABC, load envelope to be verified','quantity':50,'delivery_date':str(date.today()+timedelta(days=90)),
            'supplier_ids':['SUPP_00012','SUPP_00731'],'requirements':[{'id':'fit','text':'Drawing and test scope reviewed','mandatory':True}]}

def record(sid='SUPP_00731',**kw):
    return dict({'supplier_id':sid,'requirement_id':'fit','status':'verified','reference':'DOC-123','reviewer':'Quality reviewer','rationale':'Scope checked against drawing ABC'},**kw)

def test_any_component_and_missing_evidence(client):
    r=client.post('/sourcing/evaluate',json=payload());assert r.status_code==200
    d=r.json();assert not d['review_candidates']
    assert all(i['qualification_state']=='evidence_required' for i in d['items'])
    assert all(i['award_ready'] is False for i in d['items'])

@pytest.mark.parametrize('patch',[{'reference':''},{'reviewer':' '},{'rationale':''},{'demo':True},{'valid_until':str(date.today()+timedelta(days=1))}])
def test_cannot_clear_with_invalid_evidence(client,patch):
    p=payload();p['evidence']=[record(**patch)]
    d=client.post('/sourcing/evaluate',json=p).json()
    assert 'SUPP_00731' not in d['review_candidates']

def test_verified_only_ready_for_review_and_failed_blocks(client):
    p=payload();p['evidence']=[record(),record('SUPP_00012',status='failed')]
    d=client.post('/sourcing/evaluate',json=p).json()
    assert d['review_candidates']==['SUPP_00731']
    assert next(i for i in d['items'] if i['supplier_id']=='SUPP_00012')['qualification_state']=='blocked'
    assert all(not i['award_ready'] for i in d['items'])

@pytest.mark.parametrize('case',['duplicate','unknown','no_requirements','zero_weights','past_delivery'])
def test_bad_inputs(client,case):
    p=payload()
    if case=='duplicate':p['evidence']=[record(),record()]
    elif case=='unknown':p['supplier_ids']=['SUPP_99999']
    elif case=='no_requirements':p['requirements']=[]
    elif case=='zero_weights':p['weights']={'Quality_Risk_Score':0}
    elif case=='past_delivery':p['delivery_date']=str(date.today()-timedelta(days=1))
    r=client.post('/sourcing/evaluate',json=p)
    if case=='past_delivery':assert all(i['qualification_state']=='brief_needs_revision' for i in r.json()['items'])
    else:assert r.status_code==422

def test_not_applicable_requires_review(client):
    p=payload();p['evidence']=[record(status='not_applicable',rationale='')]
    assert not client.post('/sourcing/evaluate',json=p).json()['review_candidates']
