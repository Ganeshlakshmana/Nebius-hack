"""Assert graph execution, not just textual answers."""
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.agents.supervisor.agent import Action,Plan

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:yield c

def test_actual_langgraph_nodes(client):
    assert {'plan','validate','research','compare','memo','respond'} <= set(app.state.supervisor.graph.get_graph().nodes)
    d=client.post('/chat',json={'message':'hi'}).json()
    assert d['orchestrator']=='langgraph' and d['graph_trace']==['plan','respond']

def test_plan_validated_before_each_specialist_dispatch(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='compare'),Action(tool='memo')])):
        d=client.post('/chat',json={'message':'Compare and memo','supplier_ids':['SUPP_00012','SUPP_00731']}).json()
    assert d['graph_trace']==['plan','validate','compare','memo','respond']

def test_rejected_plan_never_enters_specialist_node(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='research',company='Invented Company')])):
        d=client.post('/chat',json={'message':'Research a supplier'}).json()
    assert d['graph_trace']==['plan','validate','respond']
    assert not d['tool_calls']

def test_validation_failure_stops_dispatch(client):
    with patch.object(app.state.supervisor,'_validate_plan',side_effect=RuntimeError('database unavailable')):
        d=client.post('/chat',json={'message':'SUPP_00012'}).json()
    assert d['status']=='unavailable' and d['graph_trace']==['plan','validate','respond']

def test_failed_tool_not_retried_or_claimed_success(client):
    with patch('app.agents.supervisor.agent.plan_request',return_value=Plan(actions=[Action(tool='memo')])),patch.object(app.state.memos,'build_html',side_effect=TimeoutError()) as call:
        d=client.post('/chat',json={'message':'memo','supplier_ids':['SUPP_00012']}).json()
    assert call.call_count==1 and d['status']=='partial'
    assert d['graph_trace']==['plan','validate','memo','respond']
    assert not d['tool_calls']

def test_request_state_isolated(client):
    # Avoid shared database concurrency in this isolation assertion: each greeting
    # must have its own graph state and never retain the previous tool result.
    client.post('/chat',json={'message':'SUPP_00012'})
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:app.state.supervisor.answer('hello'),range(12)))
    assert all(r['graph_trace']==['plan','respond'] and not r['tables'] and not r['tool_calls'] for r in results)
