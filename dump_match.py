#!/usr/bin/env python3
import requests
import json

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def dump():
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    url = "https://api.apollo.io/api/v1/people/match"
    payload = {"email": "jeimmy.oviedo@gmail.com"}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    dump()
