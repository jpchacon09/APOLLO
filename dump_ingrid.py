#!/usr/bin/env python3
import requests
import json

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def dump():
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    # Match Ingrid
    url_match = "https://api.apollo.io/api/v1/people/match"
    payload_match = {"email": "ingridaristizabal@surticosmeticos.com"}
    resp_match = requests.post(url_match, headers=headers, json=payload_match)
    
    if resp_match.status_code == 200:
        data = resp_match.json()
        person = data.get('person', {})
        print(f"Ingrid Person ID: {person.get('id')}")
        
        # Now try to get contact details using this ID
        url_contact = f"https://api.apollo.io/api/v1/contacts/{person.get('id')}"
        resp_contact = requests.get(url_contact, headers=headers)
        
        if resp_contact.status_code == 200:
            print("Successfully fetched contact:")
            print(json.dumps(resp_contact.json(), indent=2))
        else:
            print(f"Contact fetch failed: {resp_contact.status_code}")
            print(resp_contact.text)
    else:
        print(f"Match failed: {resp_match.status_code}")

if __name__ == "__main__":
    dump()
