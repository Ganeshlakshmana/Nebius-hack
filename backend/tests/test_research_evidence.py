from datetime import date
import pytest
from app.services.research_evidence import assess, official_domain, decision

def evidence(text, url='https://example.com/report', published=None):
    return {'url':url,'summary':text,'published':published}

@pytest.mark.parametrize('text,expected',[
 ('Acme Rail monitors accident/recall databases under its product integrity policy.','policy_or_process'),
 ('Acme Rail has a data breach response procedure.','policy_or_process'),
 ('Acme Rail has not issued a recall.','negated_or_conditional'),
 ('Acme Rail could be fined if it breaches the rules.','negated_or_conditional'),
 ('Acme Rail issued a recall of brake units.','reported_incident'),
 ('Acme Rail filed for bankruptcy.','reported_incident'),
 ('Acme Rail was fined by the regulator.','reported_incident'),
 ('Acme Rail discusses a recall.','ambiguous_risk_mention'),
 ('Other Rail issued a recall of brake units.','identity_unresolved'),
 ('Acme Rail produces sensors.','background'),
])
def test_claim_classification(text,expected):
    result=assess(evidence(text),'Acme Rail',None)
    assert result['classification']==expected
    assert result['verification_status']=='unverified'
    assert result['is_red_flag'] is False
    assert result['supporting_excerpt'] in text

@pytest.mark.parametrize('url,match',[
 ('https://example.com/x','buyer_domain_match'),
 ('https://rail.example.com/x','buyer_domain_match'),
 ('https://example.com.attacker.test/x','unresolved'),
 ('https://notexample.com/x','unresolved'),
])
def test_domain_boundary(url,match):
    assert assess(evidence('Company overview',url),'Acme Rail','example.com')['identity_match']==match

@pytest.mark.parametrize('value',['http://127.0.0.1','http://user:password@example.com','https://example.com:8000','javascript:alert(1)','localhost','example.internal'])
def test_domain_validation(value):
    with pytest.raises(ValueError): official_domain(value)

@pytest.mark.parametrize('published,expected',[('2020-01-01','historical'),('2026-10-01','recent'),('2030-01-01','future_date_review'),(None,'date_unknown')])
def test_date_handling(published,expected):
    assert assess(evidence('Acme Rail company',published=published),'Acme Rail',None,date(2026,10,18))['freshness']==expected

def test_empty_evidence_not_low_risk():
    result=decision({'timeline':[]})
    assert result['status']=='insufficient_evidence' and not result['award_ready']
    assert result['actions'][0]['priority']=='required'

def test_recommendations_reference_only_actual_evidence():
    item=evidence('Acme Rail issued a recall.')
    item.update(assess(item,'Acme Rail',None))
    result=decision({'timeline':[item]})
    refs={ref for action in result['actions'] for ref in action['evidence_ids']}
    assert refs=={item['evidence_id']}
    assert not result['award_ready']

def test_official_domain_does_not_attribute_competitor_incident():
    result=assess(evidence('Other Rail issued a recall. Acme Rail provides technical support.'),'Acme Rail','example.com')
    assert result['classification'] != 'reported_incident'
