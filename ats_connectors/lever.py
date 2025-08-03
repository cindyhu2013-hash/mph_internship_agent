import requests
import time

def parse_lever(url):
    """Parse Lever ATS with timeout handling"""
    start_time = time.time()
    
    try:
        print(f"    [LEVER] Starting to parse: {url}")
        
        # For now, return empty list since parser is not implemented
        # TODO: implement actual Lever parsing logic
        result = []
        
        elapsed = time.time() - start_time
        print(f"    [LEVER] Completed in {elapsed:.2f}s: {len(result)} jobs found")
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    [LEVER] Error after {elapsed:.2f}s: {e}")
        return []
