"""Buyer-authored requirement gates, separate from supplier-risk screening."""
from datetime import date, datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from app.services.data_tools import DataTools

class Requirement(BaseModel):
    id: str = Field(min_length=1,max_length=60)
    text: str = Field(min_length=3,max_length=500)
    mandatory: bool = True

class Evidence(BaseModel):
    supplier_id: str
    requirement_id: str
    status: Literal['missing','under_review','verified','failed','not_applicable'] = 'missing'
    reference: str = Field(default='',max_length=500)
    reviewer: str = Field(default='',max_length=100)
    rationale: str = Field(default='',max_length=1000)
    valid_until: date | None = None
    demo: bool = False

class SourcingRequest(BaseModel):
    component: str = Field(min_length=2,max_length=100)
    application: str = Field(min_length=3,max_length=1000)
    quantity: int = Field(ge=1,le=100000000)
    delivery_date: date
    supplier_ids: list[str] = Field(min_length=1,max_length=20)
    requirements: list[Requirement] = Field(min_length=1,max_length=30)
    evidence: list[Evidence] = Field(default_factory=list,max_length=600)
    weights: dict[str,float] = Field(default_factory=lambda:{'Quality_Risk_Score':.4,'Operational_Resilience_Score':.3,'Compliance_Risk_Score':.3})

    @model_validator(mode='after')
    def unique_inputs(self):
        ids=[r.id for r in self.requirements]
        keys=[(e.supplier_id,e.requirement_id) for e in self.evidence]
        if len(ids)!=len(set(ids)) or len(keys)!=len(set(keys)):
            raise ValueError('Duplicate requirement or evidence entries')
        if any(e.supplier_id not in self.supplier_ids or e.requirement_id not in ids for e in self.evidence):
            raise ValueError('Evidence must reference a selected supplier and existing requirement')
        return self

def evaluate(request: SourcingRequest, tools: DataTools) -> dict:
    comparison=tools.compare(request.supplier_ids,request.weights)
    if comparison.get('error'):
        raise ValueError(comparison['error'])
    today=datetime.now(timezone.utc).date()
    items=[]
    for row in comparison['suppliers']:
        checks=[]
        for req in request.requirements:
            evidence=next((e for e in request.evidence if e.supplier_id==row['supplierID'] and e.requirement_id==req.id),None)
            status=evidence.status if evidence else 'missing'
            reason='No evidence recorded' if evidence is None else evidence.rationale
            if evidence and status in {'verified','not_applicable'}:
                if not all(v.strip() for v in [evidence.reference,evidence.reviewer,evidence.rationale]):
                    status='under_review';reason='Reference, reviewer and scope/applicability rationale are required'
                elif evidence.demo:
                    status='under_review';reason='Demo evidence cannot satisfy a real qualification requirement'
                elif evidence.valid_until and evidence.valid_until<request.delivery_date:
                    status='under_review';reason='Evidence expires before the requested delivery date'
                elif evidence.valid_until and evidence.valid_until<today:
                    status='under_review';reason='Evidence has expired'
            checks.append({'requirement':req.model_dump(),'status':status,'reason':reason,'evidence':evidence.model_dump(mode='json') if evidence else None})
        failed=any(c['requirement']['mandatory'] and c['status']=='failed' for c in checks)
        open_checks=[c for c in checks if c['requirement']['mandatory'] and c['status'] not in {'verified','not_applicable'}]
        state='blocked' if failed else 'evidence_required' if open_checks else 'ready_for_authorized_review'
        if request.delivery_date<today:
            state='brief_needs_revision'
        items.append({'supplier_id':row['supplierID'],'company':row['Supplier Name'],'screening_score':round(row['custom_score'],2),
                      'qualification_state':state,'checks':checks,'mandatory_open':len(open_checks),'award_ready':False})
    items.sort(key=lambda i:(i['screening_score'],i['supplier_id']))
    eligible=[i for i in items if i['qualification_state']=='ready_for_authorized_review']
    return {'generated_at':datetime.now(timezone.utc).isoformat(),'brief':request.model_dump(mode='json'),
            'weights':comparison['custom_weights'],'items':items,'review_candidates':[i['supplier_id'] for i in eligible],
            'recommendation': 'Compare commercial and engineering terms for the review candidates; obtain authorized sign-off.' if eligible else 'No supplier has cleared the recorded mandatory requirements. Resolve the evidence gaps before choosing.',
            'limitations':['Weights and requirements are buyer-defined, not Siemens-approved rules.',
                          'Reviewed evidence is user-attested; document authenticity and legal applicability are not independently verified.',
                          'CSV suppliers are anonymized. No actual component manufacturing capability is inferred.',
                          'Risk rank cannot override a failed or missing mandatory requirement. This packet is not an award authorization.']}
