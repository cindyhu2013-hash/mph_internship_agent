import os, yaml, requests, datetime, argparse, sys, time, signal
from dotenv import load_dotenv
from discovery_module import discover_urls
from utils.dedupe import hash_job, seen_before, remember
from utils.scoring import score
from ats_connectors import parse_greenhouse, parse_lever, parse_workday, parse_brassring, parse_neogov
from ats_connectors.general_parser import parse_general_job_board

load_dotenv()

SHEET_ENDPOINT = os.getenv('SHEET_ENDPOINT')
SERP_API_KEY = os.getenv('SERP_API_KEY')

with open('config/rules.yaml') as f:
    RULES = yaml.safe_load(f)

# Global timeout settings
URL_TIMEOUT = 30  # seconds per URL
PARSER_TIMEOUT = 60  # seconds per parser
TOTAL_TIMEOUT = 600  # 10 minutes total

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

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
    """Route URL to appropriate parser with timeout handling"""
    start_time = time.time()
    
    try:
        # Set timeout for the entire router function
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(PARSER_TIMEOUT)
        
        print(f"  [ROUTER] Starting to process: {url}")
        
        # Try specific ATS parsers first
        if 'greenhouse.io' in url:
            result = parse_greenhouse(url)
        elif 'lever.co' in url:
            result = parse_lever(url)
        elif 'workdayjobs' in url or '/wday/cxs/' in url:
            result = parse_workday(url)
        elif 'brassring.com' in url:
            result = parse_brassring(url)
        elif 'governmentjobs.com' in url:
            result = parse_neogov(url)
        else:
            # Use general parser for job boards
            result = parse_general_job_board(url)
        
        elapsed = time.time() - start_time
        print(f"  [ROUTER] Completed in {elapsed:.2f}s: {len(result)} jobs found")
        
        signal.alarm(0)  # Cancel the alarm
        return result
        
    except TimeoutError:
        elapsed = time.time() - start_time
        print(f"  [TIMEOUT] Router timed out after {elapsed:.2f}s for: {url}")
        return []
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  [ERROR] Router failed after {elapsed:.2f}s for {url}: {e}")
        return []
    finally:
        signal.alarm(0)  # Ensure alarm is cancelled

def post_to_sheet(job):
    """Post job to sheet with error handling and timeout"""
    start_time = time.time()
    
    try:
        resp = requests.post(SHEET_ENDPOINT, json=job, timeout=20)
        resp.raise_for_status()
        elapsed = time.time() - start_time
        print(f"SUCCESS: Posted job '{job['title']}' to sheet in {elapsed:.2f}s")
        return True
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"TIMEOUT: Sheet posting timed out after {elapsed:.2f}s for '{job.get('title', 'Unknown')}'")
        return False
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start_time
        print(f"ERROR: Failed to post job '{job.get('title', 'Unknown')}' to sheet after {elapsed:.2f}s: {e}")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"ERROR: Unexpected error posting job '{job.get('title', 'Unknown')}' after {elapsed:.2f}s: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='MPH Internship Agent')
    parser.add_argument('--test', action='store_true', help='Run in test mode - add test job to sheet')
    parser.add_argument('--validate-only', action='store_true', help='Only validate existing jobs, don\'t post')
    parser.add_argument('--timeout', type=int, default=TOTAL_TIMEOUT, help=f'Total timeout in seconds (default: {TOTAL_TIMEOUT})')
    args = parser.parse_args()
    
    # Set up total timeout
    total_start_time = time.time()
    
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
    
    print(f"Starting job discovery and processing (timeout: {args.timeout}s)...")
    
    # Discovery phase with timeout
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(120)  # 2 minutes for discovery
        urls = discover_urls(RULES, SERP_API_KEY)
        signal.alarm(0)
        print(f"Discovered {len(urls)} URLs to process")
    except TimeoutError:
        print("TIMEOUT: Discovery phase timed out")
        return
    except Exception as e:
        print(f"ERROR: Discovery failed: {e}")
        return
    
    processed_count = 0
    posted_count = 0
    validation_failures = 0
    timeout_count = 0
    error_count = 0
    
    print(f"Processing {len(urls)} URLs...")
    
    for i, url in enumerate(urls, 1):
        # Check total timeout
        elapsed_total = time.time() - total_start_time
        if elapsed_total > args.timeout:
            print(f"TIMEOUT: Total time limit reached ({elapsed_total:.2f}s), stopping")
            break
        
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        url_start_time = time.time()
        
        try:
            # Set timeout for individual URL processing
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(URL_TIMEOUT)
            
            jobs = router(url)
            
            signal.alarm(0)  # Cancel alarm
            
            url_elapsed = time.time() - url_start_time
            print(f"  [URL] Completed in {url_elapsed:.2f}s: {len(jobs)} jobs found")
            
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
                        
        except TimeoutError:
            url_elapsed = time.time() - url_start_time
            print(f"  [TIMEOUT] URL timed out after {url_elapsed:.2f}s: {url}")
            timeout_count += 1
            signal.alarm(0)  # Ensure alarm is cancelled
            continue
        except Exception as e:
            url_elapsed = time.time() - url_start_time
            print(f"  [ERROR] Failed to process URL after {url_elapsed:.2f}s: {url} - {e}")
            error_count += 1
            signal.alarm(0)  # Ensure alarm is cancelled
            continue
    
    total_elapsed = time.time() - total_start_time
    
    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"  Total time: {total_elapsed:.2f}s")
    print(f"  URLs processed: {len(urls)}")
    print(f"  Jobs processed: {processed_count}")
    print(f"  Jobs posted: {posted_count}")
    print(f"  Validation failures: {validation_failures}")
    print(f"  Timeouts: {timeout_count}")
    print(f"  Errors: {error_count}")
    print(f"  Average time per URL: {total_elapsed/len(urls):.2f}s")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
