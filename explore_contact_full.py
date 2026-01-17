#!/usr/bin/env python3
import requests
import json

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def explore_full(email):
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"--- Exploring everything for {email} ---")
    
    # 1. Match Person
    print("\n1. POST /people/match")
    url_match = "https://api.apollo.io/api/v1/people/match"
    resp_match = requests.post(url_match, headers=headers, json={"email": email})
    if resp_match.status_code == 200:
        person_data = resp_match.json().get('person', {})
        print(f"   Name: {person_data.get('name')}")
        print(f"   Title: {person_data.get('title')}")
        print(f"   Org: {person_data.get('organization', {}).get('name')}")
        
        # Check sequences
        sequences = person_data.get('active_sequences', [])
        print(f"   Active Sequences: {len(sequences)}")
        for i, seq in enumerate(sequences, 1):
            print(f"     - Seq {i}: {seq.get('name')} (ID: {seq.get('emailer_campaign_id')})")
            
        person_id = person_data.get('id')
    else:
        print(f"   Match failed: {resp_match.status_code}")
        person_id = None

    # 2. Search Messages
    print("\n2. POST /emailer_messages/search")
    url_search = "https://api.apollo.io/api/v1/emailer_messages/search"
    resp_search = requests.post(url_search, headers=headers, json={"email_address": email})
    if resp_search.status_code == 200:
        messages = resp_search.json().get('emailer_messages', [])
        print(f"   History: {len(messages)} messages")
        for i, msg in enumerate(messages[:3], 1):
            campaign = msg.get('emailer_campaign', {})
            print(f"     - Msg {i}: {msg.get('status')} | {campaign.get('name')} | Step: {msg.get('step_number')}")
    else:
        print(f"   Search failed: {resp_search.status_code}")

    # 3. Get Contact Details (if we have ID)
    if person_id:
        print(f"\n3. GET /contacts/{person_id}")
        # Sometimes the ID from match works here, sometimes it needs a different prefix
        url_contact = f"https://api.apollo.io/api/v1/contacts/{person_id}"
        resp_contact = requests.get(url_contact, headers=headers)
        if resp_contact.status_code == 200:
            print("   Contact details fetched!")
        else:
            print(f"   Contact detail failed: {resp_contact.status_code}")

if __name__ == "__main__":
    explore_full("jeimmy.oviedo@gmail.com")
