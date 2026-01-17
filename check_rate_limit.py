#!/usr/bin/env python3
import requests

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def check():
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    url = "https://api.apollo.io/api/v1/emailer_messages/search"
    payload = {"email_address": "jeimmy.oviedo@gmail.com"}
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 429:
        print("Rate limit active on search endpoint.")
        # print(f"Headers: {response.headers}")
    elif response.status_code == 200:
        print("Search endpoint is available.")
        data = response.json()
        print(f"Messages found: {len(data.get('emailer_messages', []))}")
    else:
        print(f"Unexpected status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    check()
