#!/usr/bin/env python3
import requests

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def check():
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # First get contact ID
    url_match = "https://api.apollo.io/api/v1/people/match"
    payload_match = {"email": "jeimmy.oviedo@gmail.com"}
    resp_match = requests.post(url_match, headers=headers, json=payload_match)
    
    if resp_match.status_code == 200:
        contact_id = resp_match.json().get('person', {}).get('id')
        print(f"Contact ID: {contact_id}")
        
        if contact_id:
            # Test touches endpoint
            url_touches = f"https://api.apollo.io/api/v1/contacts/{contact_id}/emailer_touches"
            resp_touches = requests.get(url_touches, headers=headers)
            print(f"Touches Status: {resp_touches.status_code}")
            if resp_touches.status_code == 200:
                print(f"Touches found: {len(resp_touches.json().get('emailer_touches', []))}")
            else:
                print(f"Touches error: {resp_touches.text}")
    else:
        print(f"Match error: {resp_match.status_code}")

if __name__ == "__main__":
    check()
