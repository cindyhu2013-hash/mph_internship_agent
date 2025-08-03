import yaml

with open('config/rules.yaml') as f:
    RULES = yaml.safe_load(f)

def score(job):
    """Score a job based on multiple criteria"""
    s = 0
    
    # Location scoring
    if 'preferred_states' in RULES:
        state_province = job.get('state_province', '')
        if isinstance(state_province, str):
            loc_ok = any(state.lower() in state_province.lower() for state in RULES['preferred_states'])
            if loc_ok: 
                s += RULES['score_weights']['location_match']
                print(f"  +{RULES['score_weights']['location_match']} for preferred location")
    
    # Term matching (Summer 2026, etc.)
    title = job.get('title', '')
    description = job.get('description', '')
    if isinstance(title, str) and isinstance(description, str):
        job_text = f"{title} {description}".lower()
        if 'summer 2026' in job_text or '2026' in job_text:
            s += RULES['score_weights']['term_match']
            print(f"  +{RULES['score_weights']['term_match']} for 2026 term")
    
    # Paid position scoring
    paid_field = job.get('paid', '')
    if isinstance(paid_field, str) and paid_field.lower() in ('paid','yes','stipend','compensated'):
        s += RULES['score_weights']['paid']
        print(f"  +{RULES['score_weights']['paid']} for paid position")
    
    # Preferred organization scoring
    if 'preferred_organizations' in RULES:
        org_name = job.get('organization', '')
        if isinstance(org_name, str):
            for preferred_org in RULES['preferred_organizations']:
                if preferred_org.lower() in org_name.lower():
                    s += RULES['score_weights'].get('preferred_org_match', 20)
                    print(f"  +{RULES['score_weights'].get('preferred_org_match', 20)} for preferred organization: {preferred_org}")
                    break
    
    # Keyword matching in title and description
    if isinstance(title, str) and isinstance(description, str):
        job_text = f"{title} {description}".lower()
        
        # Only iterate over the keywords list, not all RULES keys
        keywords = RULES.get('keywords', [])
        for keyword in keywords:
            if isinstance(keyword, str) and keyword.lower() in job_text:
                s += 5  # Small bonus for keyword match
                print(f"  +5 for keyword match: {keyword}")
        
        # Negative term penalties
        if 'exclude' in RULES:
            exclude_terms = RULES['exclude']
            for exclude_term in exclude_terms:
                if isinstance(exclude_term, str) and exclude_term.lower() in job_text:
                    s += RULES['score_weights']['negative_term']
                    print(f"  {RULES['score_weights']['negative_term']} for negative term: {exclude_term}")
        
        # Sector matching (healthcare, government, etc.)
        if any(sector in job_text for sector in ['health', 'medical', 'public health', 'epidemiology']):
            s += RULES['score_weights']['sector_match']
            print(f"  +{RULES['score_weights']['sector_match']} for health sector")
        
        # Bonus for specific MPH-related terms
        mph_terms = ['mph', 'master of public health', 'public health', 'epidemiology', 'biostatistics', 'health policy']
        for term in mph_terms:
            if term in job_text:
                s += 10
                print(f"  +10 for MPH-related term: {term}")
                break
        
        # Bonus for internship-specific terms
        internship_terms = ['internship', 'intern', 'summer program', 'fellowship']
        for term in internship_terms:
            if term in job_text:
                s += 15
                print(f"  +15 for internship term: {term}")
                break
        
        # Penalty for undergraduate-only positions
        if any(term in job_text for term in ['undergraduate only', 'bachelor', 'no graduate', 'student only']):
            s -= 30
            print(f"  -30 for undergraduate-only position")
        
        # Bonus for graduate-level positions
        if any(term in job_text for term in ['graduate', 'masters', 'mph', 'doctoral', 'phd']):
            s += 20
            print(f"  +20 for graduate-level position")
    
    return max(0, s)  # Ensure score doesn't go below 0
