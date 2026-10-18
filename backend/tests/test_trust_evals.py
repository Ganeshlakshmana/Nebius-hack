"""Challenge acceptance and adversarial regression cases. Offline, deterministic."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c

@pytest.mark.parametrize('metric,column', [('financial','Financial_Health_Score'),('credit','Credit_Rating_Score'),('quality','Quality_Risk_Score'),('cyber','Digital_Security_Score'),('compliance','Compliance_Risk_Score'),('safety','Safety_Incident_Score')])
def test_metric_faithfulness(client, metric, column):
    ids=['SUPP_00012','SUPP_00450','SUPP_00731']
    rows=[client.get('/suppliers/'+i).json()['profile'] for i in ids]
    answer=client.post('/chat',json={'message':f'Which of {", ".join(ids)} has lowest {metric} risk?'}).json()
    assert answer['components'][0]['props']['metric']==column
    assert answer['components'][0]['props']['items'][0]['supplierID']==min(rows,key=lambda r:(r[column],r['supplierID']))['supplierID']
    assert all(f"{r['supplierID']}: {r[column]:g}" in answer['answer'] for r in rows)

@pytest.mark.parametrize('question', ['Compare SUPP_00012 and SUPP_99999','Explain SUPP_99999','Compare braking risk SUPP_00012 and SUPP_99999'])
def test_no_partial_answer(client,question):
    result=client.post('/chat',json={'message':question}).json()
    assert result['status']=='clarification_required'
    assert not result['components']

@pytest.mark.parametrize('claim',['ISO certified','approved','cheapest','capacity','manufactures','guaranteed'])
def test_no_unsupported_claim(client,claim):
    result=client.post('/chat',json={'message':f'Is SUPP_00012 {claim}?'}).json()
    assert result['status']=='insufficient_evidence'

@pytest.mark.parametrize('weights',[{}, {'Quality_Risk_Score':-1}, {'Quality_Risk_Score':0}])
def test_invalid_weights(client,weights):
    assert client.post('/compare',json={'ids':['SUPP_00012'],'custom_weights':weights}).status_code==422

def test_normalized_weights(client):
    result=client.post('/compare',json={'ids':['SUPP_00012'],'custom_weights':{'Quality_Risk_Score':70,'Safety_Incident_Score':30}}).json()
    assert sum(result['custom_weights'].values())==1
    assert 0<=result['suppliers'][0]['custom_score']<=100

def test_challenge_explanation(client):
    result=client.post('/chat',json={'message':'Why is the Total Risk Index of SUPP_00018 so high?'}).json()
    assert '80' in result['answer'] and 'original formula is not supplied' in result['answer']
    assert result['components'][0]['props']['mode']=='fitted_surrogate'

def test_decision_not_award(client):
    result=client.post('/components/analyze',json={'component':'braking','supplier_ids':['SUPP_00012','SUPP_00450','SUPP_00731']}).json()
    assert result['decision_brief']['award_ready'] is False
    assert result['decision_brief']['scenarios_tested']==16
    assert [i['component_score'] for i in result['items']]==[54.9,61.15,65.75]
    assert all(i['qualification_status']=='unverified' for i in result['items'])

def test_research_followup_and_extract(client,monkeypatch):
    queries=[]
    def search(query,**kwargs):
        queries.append(query)
        return [{'url':'https://example.com/recall','title':'Example Rail issued a recall.','content':'Example Rail issued a recall of its product.','published':None}]
    monkeypatch.setattr(app.state.search,'search',search)
    monkeypatch.setattr(app.state.search,'extract',lambda urls:{'results':[{'url':urls[0],'content':'Page evidence'}],'failed_results':[],'status':'complete'})
    started=client.post('/research',json={'company':'Example Rail','component':'braking'}).json()
    report=client.get('/research/'+started['research_id']).json()
    assert any('official statement' in q for q in queries)
    assert report['budget_used']['deep_dive_rounds']==1
    assert report['timeline'][0]['extracted_excerpt']=='Page evidence'
    assert report['timeline'][0]['severity']=='unassessed'
    assert report['scorecard']=={} and report['red_flags']==[]
    assert len(report['sources'])==1

def test_anonymous_identity_never_searched(client,monkeypatch):
    def fail(*args,**kwargs):
        pytest.fail('Anonymous identity must not trigger web search')
    monkeypatch.setattr(app.state.search,'search',fail)
    started=client.post('/research',json={'company':'SUPP_00018'}).json()
    result=client.get('/research/'+started['research_id']).json()
    assert result['dataset_match'] is None and result['sources']==[]
