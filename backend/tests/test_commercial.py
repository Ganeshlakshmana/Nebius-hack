from datetime import date,timedelta
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:yield c

def payload():
    return {'mode':'simulation','max_suppliers':2,'max_share':.7,'sourcing':{'component':'Demo isolator','application':'Same specification and cost basis','quantity':100,'delivery_date':str(date.today()+timedelta(days=60)),'supplier_ids':['SUPP_00012','SUPP_00731'],'requirements':[{'id':'fit','text':'Engineering evidence reviewed'}]},
    'offers':[{'supplier_id':s,'reference':'DEMO-'+s,'unit_price':p,'currency':'EUR','unit':'each','capacity':100,'minimum_order':10,'lead_days':10,'valid_until':str(date.today()+timedelta(days=30)),'comparable_scope':True,'demo':True} for s,p in [('SUPP_00012',10),('SUPP_00731',20)]]}

def test_split_set_optimizes_cost_and_share(client):
    d=client.post('/commercial/evaluate',json=payload()).json()
    assert d['options'][0]['total_cost']==1300
    assert [a['quantity'] for a in d['options'][0]['allocations']]==[70,30]
    assert d['award_ready'] is False and d['synthetic']

def test_real_mode_blocks_synthetic_and_missing_gates(client):
    p=payload();p['mode']='review';d=client.post('/commercial/evaluate',json=p).json()
    assert d['status']=='no_feasible_set'

@pytest.mark.parametrize('patch',[
    {'currency':'USD'}, {'unit':'kg'}, {'comparable_scope':False},
    {'valid_until':str(date.today()-timedelta(days=1))},{'lead_days':90},
    {'contract':{'constraints':'restricted'}},
])
def test_incomparable_or_unavailable_quote_not_ranked(client,patch):
    p=payload();p['offers'][0].update(patch)
    d=client.post('/commercial/evaluate',json=p).json()
    assert not d['options']

def test_unknown_contract_not_claimed_existing(client):
    d=client.post('/commercial/evaluate',json=payload()).json()
    assert not any(a['type']=='contract_expiry' for a in d['alerts'])
    assert any(a['type']=='contract_review' for a in d['alerts'])

def test_expiry_and_notice_alerts(client):
    p=payload();p['offers'][0]['contract']={'status':'existing','end_date':str(date.today()+timedelta(days=20)),'notice_date':str(date.today()-timedelta(days=1))}
    d=client.post('/commercial/evaluate',json=p).json()
    assert {'contract_expiry','notice_deadline','delivery_coverage'} <= {a['type'] for a in d['alerts']}

def test_no_fake_fallback(client):
    p=payload();p['max_share']=1;p['offers']=p['offers'][:1]
    d=client.post('/commercial/evaluate',json=p).json()
    assert not d['negotiation_briefs'][0]['fallback_available']

def test_minimum_order_infeasible(client):
    p=payload()
    for o in p['offers']:o['minimum_order']=60
    assert not client.post('/commercial/evaluate',json=p).json()['options']

def test_fixed_cost_changes_winner(client):
    p=payload();p['max_share']=1;p['offers'][0]['fixed_cost']=2000
    d=client.post('/commercial/evaluate',json=p).json()
    assert d['options'][0]['allocations'][0]['supplier_id']=='SUPP_00731'
    assert d['options'][0]['total_cost']==2000

@pytest.mark.parametrize('change',['duplicate','unknown','negative','bad_dates'])
def test_invalid_request(client,change):
    p=payload()
    if change=='duplicate':p['offers'][1]['supplier_id']=p['offers'][0]['supplier_id']
    if change=='unknown':p['offers'][0]['supplier_id']='SUPP_99999'
    if change=='negative':p['offers'][0]['unit_price']=-1
    if change=='bad_dates':p['offers'][0]['contract']={'start_date':'2027-01-01','end_date':'2026-01-01'}
    assert client.post('/commercial/evaluate',json=p).status_code==422

def test_monitor_requires_configuration(client,monkeypatch):
    from app.config.settings import settings
    monkeypatch.setattr(settings,'commercial_api_key','')
    assert client.post('/commercial/scan').status_code==503

def test_monitor_auth_and_refresh(client,monkeypatch):
    from app.config.settings import settings
    monkeypatch.setattr(settings,'commercial_api_key','local-test-secret')
    assert client.post('/commercial/evaluate',json=payload()).status_code==401
    headers={'X-Railwise-Key':'local-test-secret'}
    assert client.post('/commercial/evaluate',json=payload(),headers=headers).status_code==200
    assert client.post('/commercial/scan',headers=headers).status_code==200
    cases=client.get('/commercial/alerts',headers=headers).json()['cases']
    assert cases and any(c['scanned_at'] for c in cases)
    assert client.get('/commercial/alerts').status_code==401
