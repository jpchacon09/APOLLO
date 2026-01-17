#!/usr/bin/env python3
import requests
import json

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def test_contact():
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # We got this ID from the previous match
    person_id = "696ab58275e775001dd545b9"
    
    # Try getting contact details
    url = f"https://api.apollo.io/api/v1/contacts/{person_id}"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(response.text)

if __name__ == "__main__":
    test_contact()
