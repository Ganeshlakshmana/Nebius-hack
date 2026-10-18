"""Conservative, auditable evidence triage. Labels are routing hints, not verified facts."""
from datetime import date, datetime, timezone
import hashlib
import ipaddress
import re
from urllib.parse import urlsplit, urlunsplit


def official_domain(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    parsed = urlsplit(value.strip() if '://' in value else 'https://' + value.strip())
    host = (parsed.hostname or '').lower().rstrip('.')
    if parsed.scheme not in {'http', 'https'} or parsed.username or parsed.password or parsed.port or not re.fullmatch(r'[a-z0-9.-]+', host) or '.' not in host:
        raise ValueError('Provide a public company domain, such as example.com, without credentials or ports')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('Use a company domain, not an IP address')
    if host.endswith(('.local', '.localhost', '.internal')):
        raise ValueError('Use a public company domain')
    return host.removeprefix('www.')


def canonical_url(url: str) -> str:
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/'), p.query, ''))


def _words(text: str) -> str:
    return ' '.join(re.findall(r'[a-z0-9]+', text.lower()))


def assess(item: dict, company: str, domain: str | None, today: date | None = None) -> dict:
    today = today or datetime.now(timezone.utc).date()
    text = item.get('summary', '') + '\n' + item.get('extracted_excerpt', '')
    host = (urlsplit(item['url']).hostname or '').lower().removeprefix('www.')
    anchored = bool(domain and (host == domain or host.endswith('.'+domain)))
    name = _words(company)
    mentioned = bool(name and re.search(r'\b'+re.escape(name)+r'\b', _words(text)))
    identity = 'buyer_domain_match' if anchored else 'name_mention_only' if mentioned else 'unresolved'
    # Preserve exact supporting sentence; never turn a keyword alone into an incident.
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text) if s.strip()]
    event = re.compile(r'\b(recalled|recalling|filed for bankruptcy|declared insolven\w*|suffered (?:a |an )?(?:data |security )?breach|was fined|were fined|filed a lawsuit|was sued|imposed sanctions|issued a recall|announced a recall)\b', re.I)
    policy = re.compile(r'\b(policy|policies|procedure|procedures|monitoring|prevention|training|databases|code of conduct|whistleblow\w*)\b', re.I)
    negative = re.compile(r'\b(no|not|never|denies|denied|without|prevent|preventing|hypothetical|could|may|might|if)\b', re.I)
    concern = re.compile(r'\b(recall\w*|bankrupt\w*|insolven\w*|lawsuit|breach|sanction\w*|fined)\b', re.I)
    candidates = [s for s in sentences if concern.search(s)]
    incident = next((s for s in candidates if event.search(s) and not negative.search(s) and (re.search(r'\b'+re.escape(name)+r'\b', _words(s)) or (anchored and re.search(r'\b(we|our company)\b', s, re.I)))), None)
    if identity == 'unresolved':
        kind = 'identity_unresolved'
    elif incident:
        kind = 'reported_incident'
    elif any(negative.search(s) for s in candidates):
        kind = 'negated_or_conditional'
    elif candidates and any(policy.search(s) for s in candidates):
        kind = 'policy_or_process'
    elif candidates:
        kind = 'ambiguous_risk_mention'
    else:
        kind = 'background'
    published = item.get('published')
    try:
        published_date = date.fromisoformat(str(published)[:10])
        age = (today-published_date).days
        freshness = 'future_date_review' if age < 0 else 'historical' if age > 365 else 'recent'
    except (ValueError, TypeError):
        freshness = 'date_unknown'
    return {'evidence_id': 'E-' + hashlib.sha256(canonical_url(item['url']).encode()).hexdigest()[:10],
            'identity_match': identity, 'source_host': host,
            'source_type': 'buyer_supplied_company_domain' if anchored else 'external_unverified',
            'classification': kind, 'supporting_excerpt': incident or (candidates[0] if candidates else sentences[0] if sentences else '') ,
            'freshness': freshness, 'triage_method': 'conservative_rules_v1',
            'verification_status': 'unverified',
            'potential_concern': kind == 'reported_incident', 'is_red_flag': False}


def decision(report: dict) -> dict:
    evidence = report['timeline']
    incident = [e for e in evidence if e['classification'] == 'reported_incident']
    ambiguous = [e for e in evidence if e['classification'] == 'ambiguous_risk_mention']
    actions = []
    if not report.get('official_domain'):
        actions.append({'priority': 'required', 'action': 'Confirm legal entity, official domain, manufacturing site and subsidiary relationship.', 'evidence_ids': []})
    if incident:
        actions.append({'priority': 'required', 'action': 'Review reported incidents, establish affected products and sites, and obtain remediation or resolution evidence. Reports are not verified findings.', 'evidence_ids': [e['evidence_id'] for e in incident]})
    if ambiguous:
        actions.append({'priority': 'review', 'action': 'Clarify ambiguous risk mentions before treating them as incidents.', 'evidence_ids': [e['evidence_id'] for e in ambiguous]})
    actions.extend([
        {'priority': 'required', 'action': 'Obtain component specifications, applicable qualification evidence and test results for the intended application.', 'evidence_ids': []},
        {'priority': 'required', 'action': 'Confirm capacity, lead time, price, traceability, spares support and contingency arrangements with the supplier.', 'evidence_ids': []}])
    return {'status': 'insufficient_evidence' if not evidence else 'review_required', 'award_ready': False,
            'summary': f"{len(incident)} reported-incident candidate(s); {sum(e['classification']=='policy_or_process' for e in evidence)} policy/process source(s). No supplier approval is established.",
            'actions': actions, 'identity': 'buyer_supplied_domain_not_independently_verified' if report.get('official_domain') else 'unresolved',
            'coverage': {'sources': len(evidence), 'extracted_pages': sum(bool(e.get('extracted_excerpt')) for e in evidence),
                         'unknown_dates': sum(e['freshness']=='date_unknown' for e in evidence)},
            'limitations': ['Rule-based triage is conservative and may miss incidents or misread context.', 'Distinct websites are not proof of independent corroboration.', 'Source publication date is not necessarily incident date.', 'No results does not establish low risk.']}
