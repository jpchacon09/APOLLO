#!/usr/bin/env python3
"""
Apollo Data Enrichment Engine v2
Utiliza múltiples endpoints de Apollo para máximo enriquecimiento
"""

import csv
import requests
import json
import time
from datetime import datetime
from typing import Dict, Optional

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"
HEADERS = {
    'X-Api-Key': APOLLO_API_KEY,
    'Content-Type': 'application/json'
}

def enrich_contact_from_apollo(email: str) -> Dict:
    """
    Enriquece un contacto usando múltiples endpoints de Apollo
    """
    enriched_data = {
        'name': None,
        'title': None,
        'linkedin_url': None,
        'organization_name': None,
        'organization_industry': None,
        'organization_size': None,
        'phone': None,
        'city': None,
        'state': None,
        'country': None,
        'has_apollo_data': False
    }
    
    try:
        # 1. People Match - Datos básicos del contacto
        match_url = "https://api.apollo.io/api/v1/people/match"
        match_payload = {"email": email}
        
        response = requests.post(match_url, headers=HEADERS, json=match_payload, timeout=10)
        
        if response.status_code == 200:
            person = response.json().get('person', {})
            
            if person:
                enriched_data['has_apollo_data'] = True
                enriched_data['name'] = person.get('name')
                enriched_data['title'] = person.get('title')
                enriched_data['linkedin_url'] = person.get('linkedin_url')
                enriched_data['city'] = person.get('city')
                enriched_data['state'] = person.get('state')
                enriched_data['country'] = person.get('country')
                
                # Phone numbers
                phone_numbers = person.get('phone_numbers', [])
                if phone_numbers:
                    enriched_data['phone'] = phone_numbers[0].get('sanitized_number')
                
                # Organization data
                org = person.get('organization', {})
                if org:
                    enriched_data['organization_name'] = org.get('name')
                    enriched_data['organization_industry'] = org.get('industry')
                    enriched_data['organization_size'] = org.get('estimated_num_employees')
                
                print(f"✓ Enriquecido: {enriched_data['name'] or email}")
            else:
                print(f"○ No encontrado en Apollo: {email}")
        
        elif response.status_code == 429:
            print(f"⚠ Rate limit alcanzado")
            time.sleep(2)
        
    except Exception as e:
        print(f"✗ Error enriqueciendo {email}: {str(e)}")
    
    return enriched_data

def enrich_tablabase(limit: int = 100):
    """
    Enriquece TablaBase.csv con datos de Apollo
    """
    print("="*80)
    print("APOLLO ENRICHMENT ENGINE V2")
    print("="*80)
    
    # Leer TablaBase
    with open('TablaBase.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        contactos = list(reader)
        fieldnames = list(reader.fieldnames)
    
    # Agregar nuevas columnas si no existen
    new_fields = ['apollo_name', 'apollo_title', 'apollo_linkedin', 'apollo_org', 
                  'apollo_industry', 'apollo_org_size', 'apollo_phone', 
                  'apollo_city', 'apollo_state', 'apollo_country']
    
    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    
    # Contactos a enriquecer (que tienen email pero no nombre o datos incompletos)
    to_enrich = []
    for c in contactos:
        email = c.get('EMAIL_LIMPIO', '').strip()
        if not email:
            continue
        
        # Enriquecer si:
        # - No tiene nombre O
        # - El nombre está vacío O
        # - No tiene datos de Apollo
        if (not c.get('Contacto') or 
            c.get('Contacto').strip() == '' or 
            not c.get('apollo_name')):
            to_enrich.append(c)
    
    print(f"\n📊 Estadísticas:")
    print(f"   Total contactos: {len(contactos)}")
    print(f"   Con email: {sum(1 for c in contactos if c.get('EMAIL_LIMPIO'))}")
    print(f"   A enriquecer: {len(to_enrich)}")
    print(f"   Límite de procesamiento: {limit}")
    print()
    
    # Procesar
    processed = 0
    enriched_count = 0
    
    for i, contacto in enumerate(to_enrich[:limit], 1):
        email = contacto.get('EMAIL_LIMPIO', '').strip()
        print(f"[{i}/{min(limit, len(to_enrich))}] Procesando: {email}")
        
        # Enriquecer desde Apollo
        apollo_data = enrich_contact_from_apollo(email)
        
        if apollo_data['has_apollo_data']:
            # Actualizar con datos de Apollo
            if apollo_data['name']:
                contacto['apollo_name'] = apollo_data['name']
                # Si no tiene nombre en Contacto, usar el de Apollo
                if not contacto.get('Contacto') or contacto.get('Contacto').strip() == '':
                    contacto['Contacto'] = apollo_data['name']
            
            if apollo_data['title']:
                contacto['apollo_title'] = apollo_data['title']
                # Actualizar cargo si está vacío o es genérico
                if not contacto.get('Cargo') or contacto.get('Cargo') in ['', 'Dueña', 'Dueño']:
                    contacto['Cargo'] = apollo_data['title']
            
            contacto['apollo_linkedin'] = apollo_data['linkedin_url'] or ''
            contacto['apollo_org'] = apollo_data['organization_name'] or ''
            contacto['apollo_industry'] = apollo_data['organization_industry'] or ''
            contacto['apollo_org_size'] = str(apollo_data['organization_size'] or '')
            contacto['apollo_phone'] = apollo_data['phone'] or ''
            contacto['apollo_city'] = apollo_data['city'] or ''
            contacto['apollo_state'] = apollo_data['state'] or ''
            contacto['apollo_country'] = apollo_data['country'] or ''
            
            # Actualizar LinkedIn si no existe
            if apollo_data['linkedin_url'] and not contacto.get('Linkedin'):
                contacto['Linkedin'] = apollo_data['linkedin_url']
            
            # Actualizar teléfono si no existe
            if apollo_data['phone'] and not contacto.get('CELULAR1'):
                contacto['CELULAR1'] = apollo_data['phone']
            
            enriched_count += 1
        
        processed += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    # Guardar
    with open('TablaBase.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contactos)
    
    print()
    print("="*80)
    print(f"✓ Proceso completado")
    print(f"   Procesados: {processed}")
    print(f"   Enriquecidos: {enriched_count}")
    print(f"   Tasa de éxito: {(enriched_count/processed*100) if processed > 0 else 0:.1f}%")
    print("="*80)

if __name__ == "__main__":
    enrich_tablabase(limit=50)  # Procesar 50 contactos por ejecución
