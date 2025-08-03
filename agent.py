import os, yaml, requests, datetime, argparse, sys
from dotenv import load_dotenv
from discovery_module import discover_urls
from utils.dedupe import hash_job, seen_before, remember
from utils.scoring import score
from ats_connectors import parse_greenhouse, parse_lever, parse_workday, parse_brassring, parse_neogov

load_dotenv()

SHEET_ENDPOINT = os.getenv('SHEET_ENDPOINT')
SERP_API_KEY = os.getenv('SERP_API_KEY')

with open('config/rules.yaml') as f:
    RULES = yaml.safe_load(f)

def validate_job(job):
    """Validate job data structure and required fields"""
    required_fields = ['title', 'organization', 'location']
    optional_fields = ['state_province', 'term', 'paid', 'url', 'description']
    
    # Check required fields
    for field in required_fields:
        if field not in job or not job[field]:
            print(f"ERROR: Missing required field '{field}' in job: {job.get('title', 'Unknown')}")
            return False
    
    # Validate field types and content
    if not isinstance(job['title'], str) or len(job['title'].strip()) == 0:
        print(f"ERROR: Invalid title in job: {job}")
        return False
    
    if not isinstance(job['organization'], str) or len(job['organization'].strip()) == 0:
        print(f"ERROR: Invalid organization in job: {job}")
        return False
    
    if not isinstance(job['location'], str) or len(job['location'].strip()) == 0:
        print(f"ERROR: Invalid location in job: {job}")
        return False
    
    # Validate optional fields if present
    for field in optional_fields:
        if field in job and job[field] is not None:
            if not isinstance(job[field], str):
                print(f"WARNING: Field '{field}' should be string, got {type(job[field])} in job: {job.get('title', 'Unknown')}")
    
    return True

def create_test_job():
    """Create a test job for validation purposes"""
    return {
        'title': 'Test MPH Internship Position',
        'organization': 'Test Organization',
        'location': 'New York, NY',
        'state_province': 'NY',
        'term': 'Summer 2026',
        'paid': 'Paid',
        'url': 'https://example.com/test-job',
        'description': 'This is a test job for validation purposes.',
        'date_found': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
        'score': 85,
        'hash': 'test_hash_12345'
    }

def router(url):
    if 'greenhouse.io' in url:
        return parse_greenhouse(url)
    if 'lever.co' in url:
        return parse_lever(url)
    if 'workdayjobs' in url or '/wday/cxs/' in url:
        return parse_workday(url)
    if 'brassring.com' in url:
        return parse_brassring(url)
    if 'governmentjobs.com' in url:
        return parse_neogov(url)
    return []

def post_to_sheet(job):
    """Post job to sheet with error handling"""
    try:
        resp = requests.post(SHEET_ENDPOINT, json=job, timeout=20)
        resp.raise_for_status()
        print(f"SUCCESS: Posted job '{job['title']}' to sheet")
        return True
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to post job '{job.get('title', 'Unknown')}' to sheet: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error posting job '{job.get('title', 'Unknown')}': {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='MPH Internship Agent')
    parser.add_argument('--test', action='store_true', help='Run in test mode - add test job to sheet')
    parser.add_argument('--validate-only', action='store_true', help='Only validate existing jobs, don\'t post')
    args = parser.parse_args()
    
    if args.test:
        print("TEST MODE: Adding test job to sheet...")
        test_job = create_test_job()
        if validate_job(test_job):
            if post_to_sheet(test_job):
                print("TEST SUCCESS: Test job posted to sheet")
            else:
                print("TEST FAILED: Could not post test job to sheet")
        else:
            print("TEST FAILED: Test job validation failed")
        return
    
    if not SHEET_ENDPOINT:
        print("ERROR: SHEET_ENDPOINT environment variable not set")
        sys.exit(1)
    
    if not SERP_API_KEY:
        print("ERROR: SERP_API_KEY environment variable not set")
        sys.exit(1)
    
    print("Starting job discovery and processing...")
    urls = discover_urls(RULES, SERP_API_KEY)
    print(f"Discovered {len(urls)} URLs to process")
    
    processed_count = 0
    posted_count = 0
    validation_failures = 0
    
    for url in urls:
        try:
            jobs = router(url)
            print(f"Processing {len(jobs)} jobs from {url}")
            
            for job in jobs:
                processed_count += 1
                
                # Validate job data
                if not validate_job(job):
                    validation_failures += 1
                    continue
                
                h = hash_job(job)
                if seen_before(h):
                    print(f"SKIP: Duplicate job '{job['title']}' from {job['organization']}")
                    continue
                
                job['hash'] = h
                job['date_found'] = datetime.datetime.utcnow().strftime('%Y-%m-%d')
                job['score'] = score(job)
                
                if job['score'] < 40:
                    print(f"SKIP: Low score ({job['score']}) for '{job['title']}' from {job['organization']}")
                    continue
                
                remember(h)
                
                if args.validate_only:
                    print(f"VALIDATE: Would post job '{job['title']}' (score: {job['score']})")
                else:
                    if post_to_sheet(job):
                        posted_count += 1
                    else:
                        print(f"FAILED: Could not post job '{job['title']}'")
                        
        except Exception as e:
            print(f"ERROR: Failed to process URL {url}: {e}")
            continue
    
    print(f"\nSUMMARY:")
    print(f"  Processed: {processed_count} jobs")
    print(f"  Posted: {posted_count} jobs")
    print(f"  Validation failures: {validation_failures}")
    print(f"  URLs processed: {len(urls)}")

if __name__ == '__main__':
    main()
