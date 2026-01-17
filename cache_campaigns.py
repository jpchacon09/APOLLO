#!/usr/bin/env python3
import requests
import json

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def cache_campaigns():
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    url = "https://api.apollo.io/api/v1/emailer_campaigns/search"
    
    response = requests.post(url, headers=headers, json={"per_page": 100})
    if response.status_code == 200:
        data = response.json()
        campaigns = data.get('emailer_campaigns', [])
        mapping = {c['id']: c['name'] for c in campaigns}
        
        with open('apollo_campaigns_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        print(f"Cached {len(mapping)} campaigns.")
    else:
        print(f"Failed to fetch campaigns: {response.status_code}")

if __name__ == "__main__":
    cache_campaigns()
