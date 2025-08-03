import os, yaml, requests, datetime
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
    resp = requests.post(SHEET_ENDPOINT, json=job, timeout=20)
    resp.raise_for_status()

def main():
    urls = discover_urls(RULES, SERP_API_KEY)
    for url in urls:
        for job in router(url):
            h = hash_job(job)
            if seen_before(h):
                continue
            job['hash'] = h
            job['date_found'] = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            job['score'] = score(job)
            if job['score'] < 40:
                continue
            remember(h)
            post_to_sheet(job)

if __name__ == '__main__':
    main()
