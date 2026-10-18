"""Live model + actual dataset/services; research retrieval is a labelled fixture.
Run: PYTHONPATH=backend backend/.venv/bin/python backend/evals/run_supervisor.py --output /tmp/eval.json
"""
import argparse,csv,json,time
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import settings

ROOT=Path(__file__).resolve().parents[2]
def check(case,result,research_calls,rows):
    errors=[];calls=result.get('tool_calls',[])
    if 'tools' in case and sorted(calls)!=sorted(case['tools']):errors.append(f"tools expected {case['tools']}, got {calls}")
    for tool in case.get('forbidden_tools',[]):
        if tool in calls:errors.append('forbidden tool: '+tool)
    if 'status' in case and result.get('status')!=case['status']:errors.append('wrong status: '+str(result.get('status')))
    answer=result.get('answer','').lower()
    if case.get('contains','').lower() not in answer:errors.append('missing required explanation')
    if case.get('contains_any') and not any(t in answer for t in case['contains_any']):errors.append('missing caveat')
    if case.get('forbidden_text','\0').lower() in answer:errors.append('unsupported assertion')
    if 'company' in case and research_calls!=[case['company']]:errors.append('wrong company identity')
    if 'metric' in case:
        tables=[t for t in result.get('tables',[]) if t['columns']==['Supplier',case['metric']]]
        expected=sorted(case['ids'],key=lambda sid:((-1 if case.get('descending') else 1)*float(rows[sid][case['metric']]),sid))
        if not tables:errors.append('missing metric table')
        else:
            actual=tables[0]['rows']
            if [r[0] for r in actual]!=expected:errors.append('wrong supplier set or order')
            if any(float(v)!=float(rows[sid][case['metric']]) for sid,v in actual):errors.append('wrong numerical value')
    if 'max_risk' in case:
        values=[r for t in result.get('tables',[]) for r in t['rows']]
        if not values or len(values)>case['limit'] or any(float(r[1])>case['max_risk'] for r in values):errors.append('filter constraints violated')
    if 'memo' in calls and not result.get('memo_html'):errors.append('missing memo artifact')
    if result.get('supervisor_status')=='model_unavailable':errors.append('model unavailable: not a live-model pass')
    return errors

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--repeat',type=int,default=1);p.add_argument('--cases',type=Path,default=Path(__file__).with_name('supervisor_cases.json'));args=p.parse_args()
    if not 1<=args.repeat<=5:raise SystemExit('Repeat must be 1–5 to bound paid calls.')
    if settings.offline_mode or not settings.llm_api_key:raise SystemExit('Requires configured live model; no secret values printed.')
    cases=json.loads(args.cases.read_text())
    rows={r['supplierID']:r for r in csv.DictReader((ROOT/'data/supplier_risk_dataset.csv').open())};records=[]
    with TestClient(app) as client:
        for repeat in range(args.repeat):
            for case in cases:
                history=[]
                for step,c in enumerate(case.get('turns',[case])):
                    research_calls=[]
                    def research(company,**kw):
                        research_calls.append(company)
                        return {'research_id':'eval-fixture','executive_summary':'Evaluation retrieval fixture; no live web claims.','decision':{'summary':'Insufficient evidence'},'limitations':['Not approval'],'timeline':[]}
                    start=time.monotonic()
                    with patch.object(app.state.research,'run',research):
                        try:
                            response=client.post('/chat',json={'message':c['message'],'supplier_ids':c.get('selected',[]),'history':history[-12:]})
                            result=response.json();errors=check(c,result,research_calls,rows) if response.status_code==200 else ['HTTP '+str(response.status_code)]
                        except Exception as exc:result={};errors=[type(exc).__name__]
                    record={'case':case['id'],'step':step,'repeat':repeat,'seconds':round(time.monotonic()-start,2),'errors':errors,'research_calls':research_calls,'result':result};records.append(record)
                    print(('FAIL' if errors else 'PASS'),case['id'],step,errors,flush=True)
                    history += [{'role':'user','content':c['message']},{'role':'assistant','content':(result.get('answer','')+'\n'+json.dumps(result.get('tables',[])))[:4000]}]
                    Path(args.output).write_text(json.dumps({'model':settings.llm_model,'scope':'live supervisor; actual CSV tools; stubbed research retrieval','runs':records,'passed':sum(not r['errors'] for r in records),'total':len(records)},indent=2))
    raise SystemExit(bool(any(r['errors'] for r in records)))
if __name__=='__main__':main()
