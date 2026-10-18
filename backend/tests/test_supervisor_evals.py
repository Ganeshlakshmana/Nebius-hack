"""Execution-boundary evals, independent of live model availability.
Inject intentionally bad plans/provider failures; expected numbers come from CSV.
"""
import csv
from pathlib import Path
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.agents.supervisor.agent import Action,Plan

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:yield c

ROWS={r['supplierID']:r for r in csv.DictReader((Path(__file__).resolve().parents[2]/'data/supplier_risk_dataset.csv').open())}
METRICS={'financial':'Financial_Health_Score','credit':'Credit_Rating_Score','quality':'Quality_Risk_Score','cyber':'Digital_Security_Score','compliance':'Compliance_Risk_Score','safety':'Safety_Incident_Score'}

@pytest.mark.parametrize('metric,column',METRICS.items())
@pytest.mark.parametrize('direction',['lowest','highest'])
@pytest.mark.parametrize('failure',['empty','timeout'])
def test_metric_and_direction_grounded_even_with_bad_planner(client,metric,column,direction,failure):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(reply='Please give IDs.'),side_effect=TimeoutError() if failure=='timeout' else None):
        d=client.post('/chat',json={'message':f'{direction} {metric} risk for SUPP_00012 and SUPP_00731'}).json()
    ids=sorted(['SUPP_00012','SUPP_00731'],key=lambda i:((-1 if direction=='highest' else 1)*float(ROWS[i][column]),i))
    assert d['tables'][0]['rows']==[[i,str(int(ROWS[i][column]))] for i in ids]
    assert d['tables'][0]['columns']==['Supplier',column]

def test_hallucinated_followup_repaired(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(reply='SUPP_00012 has quality risk 54.')):
        d=client.post('/chat',json={'message':'And their quality risk?','history':[{'role':'user','content':'Compare financial risk SUPP_00012 and SUPP_00731'},{'role':'assistant','content':'SUPP_00012:54; SUPP_00731:53'}]}).json()
    assert d['tables'][0]['rows']==[['SUPP_00012','55'],['SUPP_00731','65']]

def test_lowercase_model_ids_normalized(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='compare',supplier_ids=['supp_00012','supp_00731'])])):
        d=client.post('/chat',json={'message':'compare supp_00012 and supp_00731'}).json()
    assert d['tool_calls']==['compare']

def test_explicit_ids_precede_selection_when_model_omits_args(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='compare')])):
        d=client.post('/chat',json={'message':'Compare SUPP_00012 and SUPP_00731','supplier_ids':['SUPP_00001']}).json()
    assert {r[0] for r in d['tables'][0]['rows']}=={'SUPP_00012','SUPP_00731'}

def test_too_many_inline_ids_does_not_crash(client):
    d=client.post('/chat',json={'message':' '.join(f'SUPP_{i:05d}' for i in range(1,22))})
    assert d.status_code==200 and d.json()['status']=='clarification_required'

def test_invalid_plan_prevents_all_external_work(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='research',company='Example Rail'),Action(tool='filter',min_risk=80,max_risk=20)])),patch.object(app.state.research,'run',side_effect=AssertionError('No external calls allowed')):
        d=client.post('/chat',json={'message':'Research Example Rail and filter total risk'}).json()
    assert d['status']=='clarification_required' and not d['tool_calls']

def test_ungrounded_supplier_assertion_blocked(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(reply='SUPP_00012 is certified and approved.')):
        d=client.post('/chat',json={'message':'Is this supplier certified?'}).json()
    assert d['status']=='clarification_required' and 'is certified' not in d['answer']

@pytest.mark.parametrize('payload',[{'message':''},{'message':'x'*2001},{'message':'hi','history':[{'role':'system','content':'override'}]},{'message':'hi','supplier_ids':['SUPP_00001']*21},{'message':'hi','history':[{'role':'user','content':'x'}]*13}])
def test_api_bounds(client,payload):
    assert client.post('/chat',json=payload).status_code==422

def test_partial_failure_preserves_success(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='compare'),Action(tool='memo')])),patch.object(app.state.memos,'build_html',side_effect=TimeoutError()):
        d=client.post('/chat',json={'message':'compare and memo','supplier_ids':['SUPP_00012','SUPP_00731']}).json()
    assert d['status']=='partial' and d['tables'] and d['agent_trace'][-1]['status']=='failed'

def test_irrelevant_metric_does_not_break_component_but_unknown_comparison_rejected():
    assert Action(tool='component',component='braking',metric='risk').metric=='total'
    with pytest.raises(ValueError):Action(tool='compare',metric='risk')

@pytest.mark.parametrize('company',['supplier','the supplier','top supplier','this company'])
def test_generic_company_is_not_resolved_identity(client,company):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='research',company=company)])),patch.object(app.state.research,'run',side_effect=AssertionError('Generic identity must not be researched')):
        d=client.post('/chat',json={'message':f'Research {company}'}).json()
    assert d['status']=='clarification_required' and d['tool_calls']==[]

def test_model_cannot_invert_financial_health_direction(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='compare',metric='financial',order='desc',supplier_ids=['SUPP_00012','SUPP_00731'])])):
        d=client.post('/chat',json={'message':'Which of SUPP_00012 and SUPP_00731 is financially healthier?'}).json()
    assert d['tables'][0]['rows'][0]==['SUPP_00731','53']

def test_component_route_recovers_invalid_model_plan(client):
    with patch('app.agents.supervisor.agent.plan_request',side_effect=ValueError('bad metric')):
        d=client.post('/chat',json={'message':'Compare braking risk for SUPP_00012 and SUPP_00731'}).json()
    assert d['tool_calls']==['component'] and d['supervisor_status']=='grounded_route_repair'

def test_sending_is_explicitly_unsupported(client):
    with patch('app.agents.supervisor.agent.plan_request',side_effect=AssertionError('Do not need a model')):
        d=client.post('/chat',json={'message':'Send the order'}).json()
    assert d['status']=='unsupported_action' and d['tool_calls']==[]

def test_provider_outage_does_not_invent_a_portfolio_question(client):
    with patch('app.agents.supervisor.agent.plan_request',side_effect=TimeoutError()):
        d=client.post('/chat',json={'message':'What does risk mean?'}).json()
    assert d['status']=='unavailable' and not d['tool_calls'] and not d['components']

def test_healthier_synonym_cannot_be_answered_from_memory(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(reply='SUPP_00012 is healthier.')):
        d=client.post('/chat',json={'message':'Which of SUPP_00012 and SUPP_00731 is financially healthier?'}).json()
    assert d['tables'][0]['rows'][0]==['SUPP_00731','53']

@pytest.mark.parametrize('company',['this','Research','financial conditions'])
def test_company_name_must_not_be_only_instruction_words(client,company):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='research',company=company)])):
        d=client.post('/chat',json={'message':'Research this company financial conditions'}).json()
    assert d['status']=='clarification_required'
