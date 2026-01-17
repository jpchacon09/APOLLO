#!/usr/bin/env python3
import requests
import json

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def list_campaigns():
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    # Try different combinations
    endpoints = [
        "https://api.apollo.io/api/v1/emailer_campaigns/search",
        "https://api.apollo.io/api/v1/emailer_campaigns",
        "https://api.apollo.io/api/v1/emailer_campaigns/list"
    ]
    
    for url in endpoints:
        print(f"Trying {url}...")
        try:
            # For search use POST, for others use GET
            if "search" in url:
                response = requests.post(url, headers=headers, json={})
            else:
                response = requests.get(url, headers=headers)
                
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("SUCCESS!")
                data = response.json()
                print(json.dumps(data, indent=2)[:500])
                return
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    list_campaigns()
