#!/usr/bin/env python3
"""
Script para explorar la API de Apollo y ver todos los campos disponibles
Usaremos diferentes endpoints y parámetros
"""

import requests
import json
import time

APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"
test_email = "jeimmy.oviedo@gmail.com"

def probar_endpoint(nombre, url, method="POST", payload=None, headers_extra=None):
    """Prueba un endpoint y guarda la respuesta"""
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    if headers_extra:
        headers.update(headers_extra)

    print(f"\n{'='*80}")
    print(f"PROBANDO: {nombre}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    if payload:
        print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'='*80}")

    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=payload, timeout=30)
        else:
            response = requests.get(url, headers=headers, params=payload, timeout=30)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Guardar respuesta completa
            filename = f"apollo_response_{nombre.replace(' ', '_').lower()}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Respuesta guardada en: {filename}")

            # Mostrar estructura básica
            print(f"\nEstructura de la respuesta:")
            for key in data.keys():
                if isinstance(data[key], list):
                    print(f"  - {key}: lista con {len(data[key])} elementos")
                    if data[key] and len(data[key]) > 0:
                        print(f"    Campos del primer elemento:")
                        for subkey in data[key][0].keys():
                            print(f"      • {subkey}")
                elif isinstance(data[key], dict):
                    print(f"  - {key}: objeto con {len(data[key])} campos")
                else:
                    print(f"  - {key}: {type(data[key]).__name__}")

            return data
        elif response.status_code == 429:
            print(f"✗ Rate limit alcanzado. Esperando 1 hora...")
            return None
        else:
            print(f"✗ Error: {response.text}")
            return None

    except Exception as e:
        print(f"✗ Excepción: {str(e)}")
        return None

# Nota: Debido al rate limit de 400 llamadas/hora, solo voy a hacer UNA llamada
# y voy a pedir TODOS los campos posibles

print("EXPLORACIÓN COMPLETA DE LA API DE APOLLO")
print("Vamos a hacer UNA llamada con el máximo de información posible")

# Endpoint 1: Search emailer messages con email_address (el que ya usamos)
data1 = probar_endpoint(
    "Search Emailer Messages (POST)",
    "https://api.apollo.io/api/v1/emailer_messages/search",
    method="POST",
    payload={
        "email_address": test_email,
        "page": 1,
        "per_page": 100  # Máximo por página
    }
)

if data1:
    print("\n" + "="*80)
    print("ANÁLISIS DETALLADO DE LOS DATOS RECIBIDOS:")
    print("="*80)

    messages = data1.get('emailer_messages', [])
    print(f"\nTotal de mensajes: {len(messages)}")

    if messages:
        print(f"\nPRIMER MENSAJE COMPLETO:")
        print(json.dumps(messages[0], indent=2, ensure_ascii=False))

        print(f"\n\nCAMPOS ÚNICOS ENCONTRADOS EN TODOS LOS MENSAJES:")
        all_keys = set()
        for msg in messages:
            all_keys.update(msg.keys())
        for key in sorted(all_keys):
            print(f"  • {key}")

print("\n" + "="*80)
print("EXPLORACIÓN COMPLETADA")
print("Revisa los archivos JSON generados para ver la estructura completa")
print("="*80)
