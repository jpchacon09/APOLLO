#!/usr/bin/env python3
"""
Script de prueba para ver qué información devuelve la API de Apollo
"""

import requests
import json

# Configuración de Apollo API
APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"
APOLLO_API_ENDPOINT = "https://api.apollo.io/api/v1/emailer_messages/search"

# Probar con un email de ejemplo
test_email = "jeimmy.oviedo@gmail.com"

headers = {
    'X-Api-Key': APOLLO_API_KEY,
    'Content-Type': 'application/json'
}

payload = {
    'email_address': test_email
}

try:
    response = requests.post(APOLLO_API_ENDPOINT, headers=headers, json=payload, timeout=30)

    if response.status_code == 200:
        data = response.json()
        messages = data.get('emailer_messages', [])

        print(f"Total de mensajes encontrados: {len(messages)}")
        print("\n" + "="*80)

        if messages:
            # Mostrar el primer mensaje completo para ver su estructura
            print("ESTRUCTURA DEL PRIMER MENSAJE:")
            print("="*80)
            print(json.dumps(messages[0], indent=2))

            print("\n" + "="*80)
            print("CAMPOS CLAVE DE LOS PRIMEROS 3 MENSAJES:")
            print("="*80)

            for i, msg in enumerate(messages[:3], 1):
                print(f"\n--- Mensaje {i} ---")
                print(f"ID: {msg.get('id')}")
                print(f"Type: {msg.get('type')}")
                print(f"Status: {msg.get('status')}")
                print(f"Step Number: {msg.get('step_number')}")
                print(f"Scheduled At: {msg.get('scheduled_at')}")
                print(f"Sent At: {msg.get('sent_at')}")
                print(f"Subject: {msg.get('subject')}")
                print(f"Body (primeros 100 chars): {msg.get('body', '')[:100]}")

                # Información de la campaña
                campaign = msg.get('emailer_campaign', {})
                print(f"Campaign ID: {campaign.get('id')}")
                print(f"Campaign Name: {campaign.get('name')}")

                # Información del step
                step = msg.get('emailer_step', {})
                print(f"Step ID: {step.get('id')}")
                print(f"Step Type: {step.get('type')}")

                # Template
                template = msg.get('template', {})
                print(f"Template Name: {template.get('name')}")
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Excepción: {str(e)}")
