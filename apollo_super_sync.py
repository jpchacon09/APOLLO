#!/usr/bin/env python3
"""
Apollo Super Sync v1 - Enriquecimiento multicanal
Utiliza people/match y emailer_campaigns para un mapeo completo.
"""

import csv
import requests
import json
import time
from datetime import datetime

# Configuración
APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"
PAUSE = 0.5

def load_campaigns():
    try:
        with open('apollo_campaigns_mapping.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def super_sync(limit=50):
    print("="*80)
    print(f"APOLLO SUPER SYNC - Procesando {limit} contactos")
    print("="*80)

    campaign_map = load_campaigns()
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }

    # Leer TablaBase.csv
    try:
        with open('TablaBase.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contactos = list(reader)
            fieldnames = reader.fieldnames
    except Exception as e:
        print(f"Error: {e}")
        return

    # Preparar para guardar
    contactos_a_procesar = [c for c in contactos if c.get('EMAIL_LIMPIO', '').strip() and not c.get('apollo_last_sync_at', '').strip()][:limit]
    
    print(f"Pendientes: {len([c for c in contactos if not c.get('apollo_last_sync_at', '').strip()])}")
    
    for i, contacto in enumerate(contactos_a_procesar, 1):
        email = contacto.get('EMAIL_LIMPIO', '').strip()
        print(f"[{i}/{len(contactos_a_procesar)}] Enriching {email}...")
        
        try:
            # 1. Match Person
            resp = requests.post("https://api.apollo.io/api/v1/people/match", headers=headers, json={"email": email})
            if resp.status_code == 200:
                data = resp.json().get('person', {})
                
                # Update basic fields if empty
                if not contacto.get('Cargo') or contacto.get('Cargo') == 'Dueña': # Update generic ones
                    contacto['Cargo'] = data.get('title', contacto.get('Cargo'))
                
                if not contacto.get('Linkedin'):
                    contacto['Linkedin'] = data.get('linkedin_url', '')
                
                contacto['apollo_last_sync_at'] = datetime.now().isoformat()
                
                # Check active sequences
                active_seqs = data.get('active_sequences', [])
                if active_seqs:
                    seq = active_seqs[0]
                    seq_id = seq.get('emailer_campaign_id')
                    contacto['apollo_sequence_id'] = seq_id
                    contacto['campaña'] = campaign_map.get(seq_id, seq.get('name', ''))
                    contacto['step_numero'] = seq.get('current_step_number', '')
                    print(f"   → Active Sequence: {contacto['campaña']}")
                
                # 2. Try history if no active sequence found or to complement
                # (We do this only if rate limit allows, here we keep it simple with match first)
                
            elif resp.status_code == 429:
                print("   ⚠ Rate limit reached.")
                break
            else:
                print(f"   ✗ Failed: {resp.status_code}")
                contacto['apollo_last_sync_at'] = datetime.now().isoformat() # Mark as tried
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            
        time.sleep(PAUSE)

    # Guardar cambios
    with open('TablaBase.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contactos)

    print("\n✓ Proceso completado. TablaBase.csv actualizada.")

if __name__ == "__main__":
    super_sync(20) # Batch de 20 para probar
