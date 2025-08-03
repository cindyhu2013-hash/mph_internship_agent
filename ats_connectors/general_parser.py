import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def parse_general_job_board(url):
    """Parse general job boards like Indeed, LinkedIn, Glassdoor, etc."""
    start_time = time.time()
    
    try:
        print(f"    [GENERAL] Starting to parse: {url}")
        
        # Determine the job board type
        job_board_type = get_job_board_type(url)
        print(f"    [GENERAL] Detected job board type: {job_board_type}")
        
        if job_board_type == 'indeed':
            jobs = parse_indeed(url)
        elif job_board_type == 'linkedin':
            jobs = parse_linkedin(url)
        elif job_board_type == 'glassdoor':
            jobs = parse_glassdoor(url)
        elif job_board_type == 'usajobs':
            jobs = parse_usajobs(url)
        else:
            jobs = parse_generic_job_board(url)
        
        elapsed = time.time() - start_time
        print(f"    [GENERAL] Completed in {elapsed:.2f}s: {len(jobs)} jobs found")
        return jobs
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    [GENERAL] Error after {elapsed:.2f}s: {e}")
        return []

def get_job_board_type(url):
    """Determine the type of job board from URL"""
    domain = urlparse(url).netloc.lower()
    
    if 'indeed.com' in domain:
        return 'indeed'
    elif 'linkedin.com' in domain:
        return 'linkedin'
    elif 'glassdoor.com' in domain:
        return 'glassdoor'
    elif 'usajobs.gov' in domain:
        return 'usajobs'
    else:
        return 'generic'

def parse_indeed(url):
    """Parse Indeed job listings"""
    jobs = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for job cards/containers
        job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|card|result|listing'))
        
        for card in job_cards[:10]:  # Limit to first 10 jobs
            job = extract_job_from_indeed_card(card, url)
            if job and is_relevant_job(job):
                jobs.append(job)
                
    except Exception as e:
        print(f"    [GENERAL] Error parsing Indeed: {e}")
    
    return jobs

def parse_linkedin(url):
    """Parse LinkedIn job listings"""
    jobs = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for job cards/containers
        job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|card|result|listing'))
        
        for card in job_cards[:10]:  # Limit to first 10 jobs
            job = extract_job_from_linkedin_card(card, url)
            if job and is_relevant_job(job):
                jobs.append(job)
                
    except Exception as e:
        print(f"    [GENERAL] Error parsing LinkedIn: {e}")
    
    return jobs

def parse_glassdoor(url):
    """Parse Glassdoor job listings"""
    jobs = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for job cards/containers
        job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|card|result|listing'))
        
        for card in job_cards[:10]:  # Limit to first 10 jobs
            job = extract_job_from_glassdoor_card(card, url)
            if job and is_relevant_job(job):
                jobs.append(job)
                
    except Exception as e:
        print(f"    [GENERAL] Error parsing Glassdoor: {e}")
    
    return jobs

def parse_usajobs(url):
    """Parse USAJobs listings"""
    jobs = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for job cards/containers
        job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|card|result|listing'))
        
        for card in job_cards[:10]:  # Limit to first 10 jobs
            job = extract_job_from_usajobs_card(card, url)
            if job and is_relevant_job(job):
                jobs.append(job)
                
    except Exception as e:
        print(f"    [GENERAL] Error parsing USAJobs: {e}")
    
    return jobs

def parse_generic_job_board(url):
    """Parse generic job board"""
    jobs = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for job cards/containers
        job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|card|result|listing'))
        
        for card in job_cards[:10]:  # Limit to first 10 jobs
            job = extract_job_from_generic_card(card, url)
            if job and is_relevant_job(job):
                jobs.append(job)
                
    except Exception as e:
        print(f"    [GENERAL] Error parsing generic job board: {e}")
    
    return jobs

def extract_job_from_indeed_card(card, base_url):
    """Extract job data from Indeed job card"""
    try:
        # Try to find title
        title_elem = card.find(['h2', 'h3', 'a'], class_=re.compile(r'title|job-title'))
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # Try to find company
        company_elem = card.find(['span', 'div'], class_=re.compile(r'company|employer'))
        company = company_elem.get_text(strip=True) if company_elem else ''
        
        # Try to find location
        location_elem = card.find(['span', 'div'], class_=re.compile(r'location|place'))
        location = location_elem.get_text(strip=True) if location_elem else ''
        
        # Try to find job URL
        job_link = card.find('a', href=True)
        job_url = urljoin(base_url, job_link['href']) if job_link else ''
        
        if title and job_url:
            return {
                'title': title,
                'organization': company,
                'location': location,
                'url': job_url,
                'description': '',
                'ats_type': 'indeed'
            }
    except Exception as e:
        print(f"    [GENERAL] Error extracting Indeed job: {e}")
    
    return None

def extract_job_from_linkedin_card(card, base_url):
    """Extract job data from LinkedIn job card"""
    try:
        # Try to find title
        title_elem = card.find(['h3', 'h2', 'a'], class_=re.compile(r'title|job-title'))
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # Try multiple selectors for company name
        company = ''
        company_selectors = [
            ['span', 'div'],  # Basic selectors
            ['span', 'div'],  # Class-based selectors
            ['a'],  # Link-based selectors
        ]
        
        for selector_list in company_selectors:
            for selector in selector_list:
                # Try different class patterns for company
                company_patterns = [
                    r'company|employer',
                    r'job-card-container__company-name',
                    r'job-card-container__primary-description',
                    r'job-card-container__subtitle',
                    r'entity-result__title-text',
                    r'job-card-container__metadata-item'
                ]
                
                for pattern in company_patterns:
                    company_elem = card.find(selector, class_=re.compile(pattern))
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                        if company and len(company) > 2:  # Valid company name
                            break
                if company:
                    break
            if company:
                break
        
        # If still no company, try to extract from any text that looks like a company
        if not company:
            # Look for text that might be a company name
            all_text = card.get_text()
            # Common company indicators
            company_indicators = ['at ', 'with ', 'for ', '•']
            for indicator in company_indicators:
                if indicator in all_text:
                    parts = all_text.split(indicator)
                    if len(parts) > 1:
                        potential_company = parts[1].split('\n')[0].strip()
                        if potential_company and len(potential_company) > 2:
                            company = potential_company
                            break
        
        # Try to find location
        location_elem = card.find(['span', 'div'], class_=re.compile(r'location|place'))
        location = location_elem.get_text(strip=True) if location_elem else ''
        
        # Try to find job URL
        job_link = card.find('a', href=True)
        job_url = urljoin(base_url, job_link['href']) if job_link else ''
        
        # If no company found, use a default
        if not company:
            company = 'Unknown Organization'
        
        if title and job_url:
            job_data = {
                'title': title,
                'organization': company,
                'location': location,
                'url': job_url,
                'description': '',
                'ats_type': 'linkedin'
            }
            
            return job_data
    except Exception as e:
        print(f"    [GENERAL] Error extracting LinkedIn job: {e}")
    
    return None

def extract_job_from_glassdoor_card(card, base_url):
    """Extract job data from Glassdoor job card"""
    try:
        # Try to find title
        title_elem = card.find(['h3', 'h2', 'a'], class_=re.compile(r'title|job-title'))
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # Try to find company
        company_elem = card.find(['span', 'div'], class_=re.compile(r'company|employer'))
        company = company_elem.get_text(strip=True) if company_elem else ''
        
        # Try to find location
        location_elem = card.find(['span', 'div'], class_=re.compile(r'location|place'))
        location = location_elem.get_text(strip=True) if location_elem else ''
        
        # Try to find job URL
        job_link = card.find('a', href=True)
        job_url = urljoin(base_url, job_link['href']) if job_link else ''
        
        if title and job_url:
            return {
                'title': title,
                'organization': company,
                'location': location,
                'url': job_url,
                'description': '',
                'ats_type': 'glassdoor'
            }
    except Exception as e:
        print(f"    [GENERAL] Error extracting Glassdoor job: {e}")
    
    return None

def extract_job_from_usajobs_card(card, base_url):
    """Extract job data from USAJobs card"""
    try:
        # Try to find title
        title_elem = card.find(['h3', 'h2', 'a'], class_=re.compile(r'title|job-title'))
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # Try to find agency
        agency_elem = card.find(['span', 'div'], class_=re.compile(r'agency|department'))
        agency = agency_elem.get_text(strip=True) if agency_elem else ''
        
        # Try to find location
        location_elem = card.find(['span', 'div'], class_=re.compile(r'location|place'))
        location = location_elem.get_text(strip=True) if location_elem else ''
        
        # Try to find job URL
        job_link = card.find('a', href=True)
        job_url = urljoin(base_url, job_link['href']) if job_link else ''
        
        if title and job_url:
            return {
                'title': title,
                'organization': agency,
                'location': location,
                'url': job_url,
                'description': '',
                'ats_type': 'usajobs'
            }
    except Exception as e:
        print(f"    [GENERAL] Error extracting USAJobs job: {e}")
    
    return None

def extract_job_from_generic_card(card, base_url):
    """Extract job data from generic job card"""
    try:
        # Try to find title
        title_elem = card.find(['h3', 'h2', 'h1', 'a'])
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # Try to find company
        company_elem = card.find(['span', 'div'], class_=re.compile(r'company|employer|organization'))
        company = company_elem.get_text(strip=True) if company_elem else ''
        
        # Try to find location
        location_elem = card.find(['span', 'div'], class_=re.compile(r'location|place|address'))
        location = location_elem.get_text(strip=True) if location_elem else ''
        
        # Try to find job URL
        job_link = card.find('a', href=True)
        job_url = urljoin(base_url, job_link['href']) if job_link else ''
        
        if title and job_url:
            return {
                'title': title,
                'organization': company,
                'location': location,
                'url': job_url,
                'description': '',
                'ats_type': 'generic'
            }
    except Exception as e:
        print(f"    [GENERAL] Error extracting generic job: {e}")
    
    return None

def is_relevant_job(job):
    """Check if job is relevant for MPH internships"""
    title = job.get('title', '').lower()
    description = job.get('description', '').lower()
    
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
    
    # Check if job title or description contains relevant keywords
    for keyword in mph_keywords:
        if keyword in title or keyword in description:
            for intern_keyword in internship_keywords:
                if intern_keyword in title or intern_keyword in description:
                    return True
    
    return False 