import os, requests, yaml, datetime, json, urllib.parse, random, time

def discover_urls(rules, serp_api_key):
    """Discover job URLs using direct job board URLs and minimal API calls"""
    urls = set()  # Use set to avoid duplicates
    
    # Strategy 1: Direct job board URLs (no API calls needed)
    direct_job_boards = [
        "https://www.indeed.com/jobs?q=MPH+internship&l=",
        "https://www.indeed.com/jobs?q=public+health+internship&l=",
        "https://www.indeed.com/jobs?q=health+policy+internship&l=",
        "https://www.indeed.com/jobs?q=epidemiology+internship&l=",
        "https://www.linkedin.com/jobs/search/?keywords=MPH%20internship",
        "https://www.linkedin.com/jobs/search/?keywords=public%20health%20internship",
        "https://www.linkedin.com/jobs/search/?keywords=health%20policy%20internship",
        "https://www.glassdoor.com/Job/public-health-internship-jobs-SRCH_KO0,23.htm",
        "https://www.glassdoor.com/Job/MPH-internship-jobs-SRCH_KO0,13.htm",
        "https://www.usajobs.gov/Search/Results?k=MPH%20internship",
        "https://www.usajobs.gov/Search/Results?k=public%20health%20internship",
        "https://www.governmentjobs.com/careers/home?keywords=MPH%20internship",
        "https://www.governmentjobs.com/careers/home?keywords=public%20health%20internship",
        "https://www.ziprecruiter.com/Jobs/MPH-Internship",
        "https://www.ziprecruiter.com/Jobs/Public-Health-Internship",
        "https://www.simplyhired.com/search?q=MPH+internship",
        "https://www.simplyhired.com/search?q=public+health+internship",
        "https://www.careerbuilder.com/jobs?keywords=MPH+internship",
        "https://www.careerbuilder.com/jobs?keywords=public+health+internship"
    ]
    
    # Add location-specific variations for top states
    top_states = ['NY', 'CA', 'MA', 'DC', 'MD']
    for state in top_states:
        direct_job_boards.extend([
            f"https://www.indeed.com/jobs?q=MPH+internship&l={state}",
            f"https://www.indeed.com/jobs?q=public+health+internship&l={state}",
            f"https://www.linkedin.com/jobs/search/?keywords=MPH%20internship&location={state}",
            f"https://www.linkedin.com/jobs/search/?keywords=public%20health%20internship&location={state}"
        ])
    
    urls.update(direct_job_boards)
    
    # Strategy 2: Organization-specific career pages (no API calls)
    org_career_pages = [
        "https://jobs.cdc.gov/",
        "https://jobs.nih.gov/",
        "https://careers.who.int/",
        "https://www.fda.gov/about-fda/working-fda/jobs-fda",
        "https://www.epa.gov/careers",
        "https://jobs.jhu.edu/",
        "https://jobs.brassring.com/TGnewUI/Search/home/HomeWithPreLoad?partnerid=25240&siteid=5341",
        "https://your.yale.edu/work-yale/careers",
        "https://opportunities.columbia.edu/",
        "https://careers.umich.edu/",
        "https://jobs.ucop.edu/",
        "https://hr.mycareer.ucla.edu/",
        "https://jobs.berkeley.edu/",
        "https://careersearch.stanford.edu/",
        "https://bu.silkroad.com/epostings/",
        "https://tufts.taleo.net/",
        "https://hr.emory.edu/careers/",
        "https://unc.peopleadmin.com/",
        "https://hr.uw.edu/jobs/",
        "https://humanresources.umn.edu/jobs",
        "https://www.pittsource.com/",
        "https://careers.duke.edu/",
        "https://www.vanderbilt.edu/work-at-vanderbilt/",
        "https://jobs.mayoclinic.org/",
        "https://my.clevelandclinic.org/careers",
        "https://www.kaiserpermanentejobs.org/",
        "https://massgeneralbrigham.wd5.myworkdayjobs.com/wday/cxs/massgeneralbrigham/Careers/jobs",
        "https://bmc.wd1.myworkdayjobs.com/wday/cxs/bmc/External/jobs",
        "https://boards.greenhouse.io/danafarber",
        "https://www.bcbs.com/careers",
        "https://jobs.cvshealth.com/",
        "https://jobs.cigna.com/",
        "https://careers.unitedhealthgroup.com/",
        "https://www.pfizer.com/careers",
        "https://jobs.jnj.com/",
        "https://jobs.merck.com/",
        "https://www.novartis.com/careers",
        "https://careers.roche.com/",
        "https://careers.gsk.com/",
        "https://careers.astrazeneca.com/",
        "https://careers.bms.com/",
        "https://careers.lilly.com/",
        "https://careers.amgen.com/",
        "https://gilead.wd1.myworkdayjobs.com/",
        "https://careers.biogen.com/",
        "https://careers.regeneron.com/",
        "https://moderna.wd1.myworkdayjobs.com/",
        "https://careers.apha.org/",
        "https://www.cancer.org/about-us/careers.html",
        "https://careers.heart.org/",
        "https://www.redcross.org/about-us/careers.html",
        "https://path.org/careers/",
        "https://www.psi.org/careers/",
        "https://www.fhi360.org/careers",
        "https://www.rti.org/careers",
        "https://www.abtassociates.com/careers",
        "https://www.icf.com/careers",
        "https://www.mathematica.org/careers",
        "https://www.norc.org/AboutUs/Pages/careers.aspx",
        "https://www.westat.com/careers",
        "https://www.battelle.org/careers",
        "https://careers.boozallen.com/",
        "https://www2.deloitte.com/us/en/careers.html",
        "https://www.mckinsey.com/careers",
        "https://careers.bcg.com/",
        "https://www.bain.com/careers/"
    ]
    
    urls.update(org_career_pages)
    
    # Strategy 3: Limited API search for current year internships (only 2 calls)
    try:
        # Search for current year internships
        params = {
            'q': '"MPH internship 2026" OR "public health internship 2026"', 
            'engine': 'google', 
            'api_key': serp_api_key, 
            'num': 20,
            'gl': 'us',
            'hl': 'en'
        }
        
        resp = requests.get('https://serpapi.com/search.json', params=params, timeout=30)
        resp.raise_for_status()
        
        for item in resp.json().get('organic_results', []):
            urls.add(item['link'])
        
        time.sleep(3)  # Longer rate limiting
        
        # Search for major job boards
        params = {
            'q': 'site:indeed.com OR site:linkedin.com OR site:glassdoor.com "MPH internship"', 
            'engine': 'google', 
            'api_key': serp_api_key, 
            'num': 15,
            'gl': 'us',
            'hl': 'en'
        }
        
        resp = requests.get('https://serpapi.com/search.json', params=params, timeout=30)
        resp.raise_for_status()
        
        for item in resp.json().get('organic_results', []):
            urls.add(item['link'])
            
    except Exception as e:
        print(f"WARNING: API search failed, using direct URLs only: {e}")
    
    # Convert set back to list and filter out non-job URLs
    filtered_urls = []
    for url in urls:
        # Filter out non-job related URLs and social media
        if any(keyword in url.lower() for keyword in ['job', 'career', 'internship', 'position', 'opportunity', 'employment']):
            if not any(social in url.lower() for social in ['tiktok.com', 'instagram.com', 'facebook.com', 'twitter.com']):
                filtered_urls.append(url)
        elif any(domain in url.lower() for domain in ['indeed.com', 'linkedin.com', 'glassdoor.com', 'usajobs.gov', 'governmentjobs.com', 'ziprecruiter.com', 'simplyhired.com', 'careerbuilder.com']):
            filtered_urls.append(url)
        elif any(org.lower() in url.lower() for org in rules.get('preferred_organizations', []) if isinstance(org, str)):
            filtered_urls.append(url)
    
    print(f"Discovered {len(urls)} total URLs, filtered to {len(filtered_urls)} job-related URLs")
    return filtered_urls[:30]  # Limit to top 30
