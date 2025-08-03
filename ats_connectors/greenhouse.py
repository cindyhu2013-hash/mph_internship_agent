import requests
import time
import json
import re
from bs4 import BeautifulSoup

def parse_greenhouse(url):
    """Parse Greenhouse ATS with timeout handling"""
    start_time = time.time()
    
    try:
        print(f"    [GREENHOUSE] Starting to parse: {url}")
        
        # Extract board ID from URL if it's a Greenhouse board URL
        board_id = None
        if 'boards.greenhouse.io' in url:
            # Extract board ID from URL like https://boards.greenhouse.io/companyname
            board_id = url.split('boards.greenhouse.io/')[-1].split('/')[0]
        
        if not board_id:
            print(f"    [GREENHOUSE] No board ID found in URL, trying to detect from page")
            # Try to detect Greenhouse from the page content
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                # Look for Greenhouse indicators in the page
                if 'greenhouse' in response.text.lower() or 'gh_jobs' in response.text:
                    # Try to extract board ID from JavaScript
                    board_match = re.search(r'board_id["\']?\s*:\s*["\']?([^"\']+)', response.text)
                    if board_match:
                        board_id = board_match.group(1)
            except Exception as e:
                print(f"    [GREENHOUSE] Error detecting board ID: {e}")
        
        if board_id:
            print(f"    [GREENHOUSE] Found board ID: {board_id}")
            jobs = fetch_greenhouse_jobs(board_id)
        else:
            print(f"    [GREENHOUSE] No Greenhouse board detected")
            jobs = []
        
        elapsed = time.time() - start_time
        print(f"    [GREENHOUSE] Completed in {elapsed:.2f}s: {len(jobs)} jobs found")
        return jobs
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    [GREENHOUSE] Error after {elapsed:.2f}s: {e}")
        return []

def fetch_greenhouse_jobs(board_id):
    """Fetch jobs from Greenhouse API"""
    jobs = []
    
    try:
        # Greenhouse API endpoint
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_id}/jobs"
        
        response = requests.get(api_url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        data = response.json()
        
        for job in data.get('jobs', []):
            # Check if job matches our criteria
            if is_relevant_job(job):
                job_data = {
                    'title': job.get('title', ''),
                    'organization': job.get('location', {}).get('name', ''),
                    'location': job.get('location', {}).get('name', ''),
                    'url': f"https://boards.greenhouse.io/{board_id}/jobs/{job.get('id')}",
                    'description': job.get('content', ''),
                    'department': job.get('departments', [{}])[0].get('name', '') if job.get('departments') else '',
                    'date_posted': job.get('updated_at', ''),
                    'job_id': job.get('id', ''),
                    'ats_type': 'greenhouse'
                }
                jobs.append(job_data)
                
    except Exception as e:
        print(f"    [GREENHOUSE] Error fetching jobs: {e}")
    
    return jobs

def is_relevant_job(job):
    """Check if job is relevant for MPH internships"""
    title = job.get('title', '').lower()
    content = job.get('content', '').lower()
    departments = [dept.get('name', '').lower() for dept in job.get('departments', [])]
    
    # Keywords that indicate MPH/public health relevance
    mph_keywords = [
        'mph', 'public health', 'epidemiology', 'biostatistics', 'health policy',
        'global health', 'environmental health', 'health promotion', 'health education',
        'community health', 'health administration', 'health informatics',
        'health services research', 'health equity', 'health disparities'
    ]
    
    # Keywords that indicate internship/fellowship
    internship_keywords = [
        'internship', 'intern', 'fellowship', 'summer program', 'graduate program',
        'student', 'trainee', 'apprentice'
    ]
    
    # Check if job title or content contains relevant keywords
    for keyword in mph_keywords:
        if keyword in title or keyword in content:
            for intern_keyword in internship_keywords:
                if intern_keyword in title or intern_keyword in content:
                    return True
    
    # Check departments
    for dept in departments:
        for keyword in mph_keywords:
            if keyword in dept:
                return True
    
    return False
