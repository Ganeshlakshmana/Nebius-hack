"""Decision support over observed scores; never a component qualification."""
from itertools import product


def decision_brief(items: list[dict], weights: dict[str, float]) -> dict:
    complete = [item for item in items if item['component_score'] is not None]
    scenarios = []
    # Exercise all combinations of +/-20% relative changes, then normalize.
    for multipliers in product((.8, 1.2), repeat=len(weights)):
        varied = {col: weight * scale for (col, weight), scale in zip(weights.items(), multipliers)}
        total = sum(varied.values())
        varied = {col: weight / total for col, weight in varied.items()}
        scores = {item['supplier_id']: sum(f['score'] * varied[f['column']] for f in item['factors']) for item in complete}
        if scores:
            best = min(scores.values())
            scenarios.append([sid for sid, score in scores.items() if abs(score-best) < 1e-8])
    best_score = min((item['component_score'] for item in complete), default=None)
    leaders = [item['supplier_id'] for item in complete if item['component_score'] == best_score]
    for item in items:
        item['sensitivity'] = {'top_rank_scenarios': sum(item['supplier_id'] in winners for winners in scenarios),
                               'scenarios_tested': len(scenarios)}
        item['dominated_by'] = []
        if item['component_score'] is None:
            continue
        own = {f['column']: f['score'] for f in item['factors']}
        for other in complete:
            values = {f['column']: f['score'] for f in other['factors']}
            if all(values[c] <= own[c] for c in weights) and any(values[c] < own[c] for c in weights):
                item['dominated_by'].append(other['supplier_id'])
    return {'award_ready': False, 'screening_leaders': leaders,
            'ranking_stability': 'insufficient_comparison' if len(complete) < 2 or len(complete) != len(items) else 'stable_in_tested_scenarios' if all(set(w) == set(leaders) for w in scenarios) else 'sensitive_to_priorities',
            'sensitivity_method': 'All combinations of +/-20% relative changes to each illustrative weight, normalized to sum to one. Scenario counts are not probabilities or confidence scores.',
            'scenarios_tested': len(scenarios), 'qualification_coverage': 'No verified component qualification evidence supplied',
            'buyer_actions': [
                {'owner': 'Engineering / quality', 'request': 'Component specification fit, applicable approval scope, test records and batch traceability', 'status': 'evidence_required'},
                {'owner': 'Procurement', 'request': 'Confirmed capacity, lead time, commercial quote and contingency source', 'status': 'evidence_required'},
                {'owner': 'Lifecycle / maintenance', 'request': 'Spares support horizon, repair plan, end-of-life notice and obsolescence mitigation', 'status': 'evidence_required'},
                {'owner': 'Supplier assurance', 'request': 'Critical sub-tier dependencies and recovery plan; cybersecurity capability for connected components', 'status': 'evidence_required'}]}
