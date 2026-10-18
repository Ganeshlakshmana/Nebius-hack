"""Contract-aware commercial scenarios. Inputs are buyer attestations, never legal findings."""
from datetime import date, datetime, timezone
from decimal import Decimal
from itertools import combinations
from math import floor
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from app.services.sourcing import SourcingRequest, evaluate

class Contract(BaseModel):
    status: Literal['unknown','none_confirmed','existing'] = 'unknown'
    reference: str = Field(default='',max_length=200)
    reviewer: str = Field(default='',max_length=100)
    scope_confirmed: bool = False
    start_date: date | None = None
    end_date: date | None = None
    notice_date: date | None = None
    constraints: Literal['unknown','clear','restricted'] = 'unknown'
    notes: str = Field(default='',max_length=1000)

    @model_validator(mode='after')
    def dates(self):
        if self.start_date and self.end_date and self.start_date>self.end_date:
            raise ValueError('Contract starts after its end date')
        return self

class Offer(BaseModel):
    supplier_id: str
    reference: str = Field(min_length=1,max_length=200)
    unit_price: Decimal = Field(ge=0,max_digits=12,decimal_places=2)
    fixed_cost: Decimal = Field(default=Decimal("0"),ge=0,max_digits=12,decimal_places=2)
    currency: str = Field(pattern=r'^[A-Z]{3}$')
    unit: str = Field(min_length=1,max_length=50)
    capacity: int = Field(ge=1,le=100000000)
    minimum_order: int = Field(default=1,ge=1,le=100000000)
    lead_days: int = Field(ge=0,le=3650)
    payment_days: int = Field(default=30,ge=0,le=365)
    valid_until: date
    comparable_scope: bool = False
    demo: bool = True
    contract: Contract = Field(default_factory=Contract)

    @model_validator(mode='after')
    def capacity_check(self):
        if self.minimum_order>self.capacity:raise ValueError('Minimum order exceeds capacity')
        return self

class CommercialRequest(BaseModel):
    sourcing: SourcingRequest
    offers: list[Offer] = Field(min_length=1,max_length=20)
    mode: Literal['simulation','review'] = 'simulation'
    currency: str = Field(default='EUR',pattern=r'^[A-Z]{3}$')
    unit: str = Field(default='each',min_length=1,max_length=50)
    max_suppliers: int = Field(default=2,ge=1,le=3)
    max_share: float = Field(default=1,gt=0,le=1,allow_inf_nan=False)
    risk_ceiling: float = Field(default=100,ge=0,le=100,allow_inf_nan=False)

    @model_validator(mode='after')
    def ids(self):
        ids=[o.supplier_id for o in self.offers]
        if len(ids)!=len(set(ids)):raise ValueError('One comparable quote per supplier is supported')
        if any(i not in self.sourcing.supplier_ids for i in ids):raise ValueError('Quotes must reference shortlisted suppliers')
        return self

def analyze(request: CommercialRequest, tools, today: date | None=None):
    today=today or datetime.now(timezone.utc).date()
    screening=evaluate(request.sourcing,tools)
    profiles={i['supplier_id']:i for i in screening['items']}
    demand=request.sourcing.quantity
    alerts=[]; candidates=[]; eligible=[]
    for offer in request.offers:
        c=offer.contract; sid=offer.supplier_id; profile=profiles[sid]; reasons=[]
        if request.sourcing.delivery_date<today:reasons.append('Delivery date is in the past')
        if offer.currency!=request.currency or offer.unit.strip().casefold()!=request.unit.strip().casefold():reasons.append('Currency or unit is not comparable; no automatic conversion')
        if not offer.comparable_scope:reasons.append('Specification, freight and tax comparison basis not confirmed')
        if offer.valid_until<today:reasons.append('Quote expired')
        if offer.lead_days>(request.sourcing.delivery_date-today).days:reasons.append('Quoted lead time misses delivery date')
        if profile['screening_score']>request.risk_ceiling:reasons.append('Risk exceeds buyer ceiling')
        contract_ready=bool(c.reference.strip() and c.reviewer.strip() and c.constraints=='clear' and (c.status=='none_confirmed' or (c.status=='existing' and c.scope_confirmed and c.start_date and c.end_date and c.start_date<=today<=c.end_date)))
        if request.mode=='review':
            if offer.demo:reasons.append('Synthetic quote cannot support a real recommendation')
            if profile['qualification_state']!='ready_for_authorized_review':reasons.append('Qualification requirements unresolved')
            if not contract_ready:reasons.append('Contract scope or obligations have not cleared review')
        else:
            if c.constraints=='restricted':reasons.append('Recorded contract restriction blocks this scenario')
        if c.status=='unknown' or not contract_ready:
            alerts.append({'supplier_id':sid,'type':'contract_review','message':'Confirm agreement coverage, exclusivity, committed volumes and exit costs before negotiating.'})
        if c.status=='existing' and c.notice_date:
            days=(c.notice_date-today).days
            if days<=60:alerts.append({'supplier_id':sid,'type':'notice_deadline','date':str(c.notice_date),'message':f'Buyer-entered notice deadline: {days} days from today. Verify the clause; no notice has been sent.'})
        if c.status=='existing' and c.end_date and (c.end_date-today).days<=90:
            alerts.append({'supplier_id':sid,'type':'contract_expiry','date':str(c.end_date),'message':'Agreement expired or ends within 90 days. Confirm continuity and renewal terms.'})
        if c.status=='existing' and c.end_date and c.end_date<request.sourcing.delivery_date:
            alerts.append({'supplier_id':sid,'type':'delivery_coverage','message':'Recorded agreement ends before required delivery. Review whether it covers the proposed order.'})
            if request.mode=='review':reasons.append('Contract delivery coverage needs review')
        candidates.append({'supplier_id':sid,'risk':profile['screening_score'],'qualification':profile['qualification_state'],'contract_status':c.status,'demo':offer.demo,'eligible_for_calculation':not reasons,'exclusions':reasons,'reference':offer.reference})
        if not reasons:eligible.append(offer)
    quoted={o.supplier_id for o in request.offers}
    for sid,profile in profiles.items():
        if sid not in quoted:
            candidates.append({'supplier_id':sid,'risk':profile['screening_score'],'qualification':profile['qualification_state'],
                               'contract_status':'unknown','demo':False,'eligible_for_calculation':False,
                               'exclusions':['No quote supplied'],'reference':None})
    # Exhaustive supplier subsets (up to 3). Linear unit costs, fixed fees, integer demand, MOQ and capacity.
    options=[]; cap=floor(demand*request.max_share+1e-9)
    for count in range(1,min(request.max_suppliers,len(eligible))+1):
        for subset in combinations(eligible,count):
            allocation={o.supplier_id:o.minimum_order for o in subset}
            if any(o.minimum_order>min(o.capacity,cap) for o in subset):continue
            remaining=demand-sum(allocation.values())
            if remaining<0:continue
            for o in sorted(subset,key=lambda x:(x.unit_price,x.supplier_id)):
                extra=min(remaining,min(o.capacity,cap)-allocation[o.supplier_id])
                allocation[o.supplier_id]+=extra;remaining-=extra
            if remaining:continue
            cost=sum(o.unit_price*allocation[o.supplier_id]+o.fixed_cost for o in subset)
            risk=sum(profiles[o.supplier_id]['screening_score']*allocation[o.supplier_id] for o in subset)/demand
            options.append({'total_cost':float(cost),'weighted_risk':round(risk,2),'allocations':[{'supplier_id':o.supplier_id,'quantity':allocation[o.supplier_id],'quote_reference':o.reference} for o in subset]})
    options.sort(key=lambda x:(x['total_cost'],x['weighted_risk'],str(x['allocations'])))
    levers=[]
    if options:
        best=options[0]
        for o in eligible:
            alternative=next((x for x in options if all(a['supplier_id']!=o.supplier_id for a in x['allocations'])),None)
            levers.append({'supplier_id':o.supplier_id,'fallback_available':alternative is not None,'fallback_cost':alternative['total_cost'] if alternative else None,
                'questions':[f'Quote reference {o.reference}: request volume tiers without committing volume.',
                             f'Current payment assumption is {o.payment_days} days. Discuss payment timing against price and working-capital needs.',
                             'Confirm delivery slots, acceptance criteria, warranty, traceability and change-control terms.',
                             'Verify restrictions and switching costs before using another supplier as a credible fallback.']})
        alerts.append({'supplier_id':None,'type':'commercial_option','message':f'Lowest modeled cost among feasible sets: {best["total_cost"]:.2f} {request.currency}. This is not a negotiated saving or an award recommendation.'})
    return {'mode':request.mode,'synthetic':any(o.demo for o in request.offers),'generated_at':datetime.now(timezone.utc).isoformat(),
            'currency':request.currency,'unit':request.unit,'demand':demand,'candidates':candidates,'options':options[:5],
            'feasible_sets':len(options),'alerts':alerts,'negotiation_briefs':levers,'award_ready':False,
            'status':'options_for_review' if options else 'no_feasible_set',
            'limitations':['Simulation assumes qualification and contract clearance unless a restriction is recorded; it never establishes real suitability.',
                          'Best means lowest modeled total cost under the stated constraints, not globally best supplier.',
                          'Cost includes entered unit prices and fixed costs only. No FX conversion, tax, freight, inventory, discount tiers or currency forecasting is inferred.',
                          'A split order does not prove independent supply chains. Shared upstream dependencies remain unknown.',
                          'All contract fields and deadlines are buyer-entered; no legal interpretation or independent document verification.',
                          'No negotiation messages, renewal notices, commitments or awards are sent automatically.']}
