import os, requests, yaml, datetime, json, urllib.parse

def discover_urls(rules, serp_api_key):
    q = '(' + ' OR '.join(rules['keywords']) + ') internship "Summer 2026"'
    params = {'q': q, 'engine': 'google', 'api_key': serp_api_key, 'num': 20}
    resp = requests.get('https://serpapi.com/search.json', params=params, timeout=30)
    resp.raise_for_status()
    urls = []
    for item in resp.json().get('organic_results', []):
        urls.append(item['link'])
    return urls
