import yaml

with open('config/rules.yaml') as f:
    RULES = yaml.safe_load(f)

def score(job):
    s = 0
    loc_ok = any(state.lower() in job.get('state_province','').lower() for state in RULES['preferred_states'])
    if loc_ok: s += RULES['score_weights']['location_match']
    if 'summer 2026' in job.get('term','').lower():
        s += RULES['score_weights']['term_match']
    if job.get('paid', '').lower() in ('paid','yes','stipend'):
        s += RULES['score_weights']['paid']
    # simple example; extend as needed
    return s
