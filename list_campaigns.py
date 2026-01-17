#!/usr/bin/env python3
import requests
import json

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def list_campaigns():
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    url = "https://api.apollo.io/api/v1/emailer_campaigns"
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        campaigns = data.get('emailer_campaigns', [])
        print(f"Found {len(campaigns)} campaigns.")
        for i, c in enumerate(campaigns[:10], 1):
            print(f"{i}. {c.get('name')} (ID: {c.get('id')}) - Active: {c.get('active')}")
        
        with open('apollo_campaigns.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        print(response.text)

if __name__ == "__main__":
    list_campaigns()
