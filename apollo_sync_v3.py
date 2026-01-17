#!/usr/bin/env python3
"""
Apollo Sync v3 - Enriquecimiento completo de TablaBase.csv
Usa el endpoint emailer_messages/search para obtener el historial de cada contacto.
"""

import csv
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

# Configuración
APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"
APOLLO_API_ENDPOINT = "https://api.apollo.io/api/v1/emailer_messages/search"
MAX_RETRIES = 3
PAUSE_BETWEEN_REQUESTS = 0.5  # segundos para evitar saturar

def buscar_mensajes_apollo(email: str) -> Optional[List[Dict]]:
    """Busca mensajes de email para un contacto específico en Apollo"""
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        "email_address": email,
        "page": 1,
        "per_page": 50
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(APOLLO_API_ENDPOINT, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('emailer_messages', [])
            elif response.status_code == 429:
                print(f"   ⚠ Rate limit alcanzado para {email}. Esperando...")
                return "RATE_LIMIT"
            else:
                print(f"   ✗ Error {response.status_code} para {email}: {response.text[:100]}")
                return None
        except Exception as e:
            print(f"   ✗ Intento {attempt+1} falló para {email}: {str(e)}")
            time.sleep(2)
    
    return None

def sync_apollo():
    print("="*80)
    print("APOLLO SYNC V3 - INICIANDO ENRIQUECIMIENTO")
    print("="*80)

    # 1. Leer TablaBase.csv
    try:
        with open('TablaBase.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contactos = list(reader)
            fieldnames = reader.fieldnames
    except Exception as e:
        print(f"Error leyendo TablaBase.csv: {e}")
        return

    print(f"Total de contactos cargados: {len(contactos)}")

    # 2. Identificar contactos a procesar
    # Procesamos los que tienen email y NO tienen apollo_last_message_id
    contactos_a_procesar = [c for c in contactos if c.get('EMAIL_LIMPIO', '').strip() and not c.get('apollo_last_message_id', '').strip()]
    
    print(f"Contactos pendientes de enriquecer: {len(contactos_a_procesar)}")
    
    if not contactos_a_procesar:
        print("No hay contactos pendientes de procesar.")
        return

    procesados_exito = 0
    errores = 0
    rate_limit_hits = 0

    # 3. Procesar cada contacto
    for i, contacto in enumerate(contactos_a_procesar, 1):
        email = contacto.get('EMAIL_LIMPIO', '').strip()
        nombre = contacto.get('Contacto', 'Sin nombre')
        
        print(f"[{i}/{len(contactos_a_procesar)}] Procesando: {nombre} ({email})")
        
        mensajes = buscar_mensajes_apollo(email)
        
        if mensajes == "RATE_LIMIT":
            print("\n!!! RATE LIMIT ALCANZADO !!! Deteniendo el proceso para evitar bloqueo prolongado.")
            break
            
        if mensajes:
            # Ordenar por fecha de creación desc (el más reciente primero)
            # Aunque la API suele devolverlos ordenados, nos aseguramos
            mensajes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            ultimo_msg = mensajes[0]
            
            # Actualizar campos en el objeto contacto
            contacto['apollo_last_message_id'] = ultimo_msg.get('id', '')
            
            campaign = ultimo_msg.get('emailer_campaign', {})
            contacto['apollo_sequence_id'] = campaign.get('id', '')
            contacto['campaña'] = campaign.get('name', '')
            
            step = ultimo_msg.get('emailer_step', {})
            contacto['apollo_step_id'] = step.get('id', '')
            contacto['step_numero'] = ultimo_msg.get('step_number', '')
            contacto['apollo_step'] = ultimo_msg.get('step_number', '')
            
            contacto['apollo_status'] = ultimo_msg.get('status', '')
            contacto['estado_apollo'] = ultimo_msg.get('status', '')
            
            contacto['apollo_last_sent_at'] = ultimo_msg.get('sent_at', '')
            contacto['fecha_envio'] = ultimo_msg.get('sent_at', '')
            
            contacto['apollo_last_opened_at'] = ultimo_msg.get('opened_at', '')
            contacto['apollo_last_clicked_at'] = ultimo_msg.get('clicked_at', '')
            contacto['apollo_last_replied_at'] = ultimo_msg.get('replied_at', '')
            
            contacto['apollo_last_sync_at'] = datetime.now().isoformat()
            contacto['fecha de step'] = ultimo_msg.get('created_at', '')

            print(f"   ✓ Encontrado! Campaña: {contacto['campaña']} | Estado: {contacto['estado_apollo']}")
            procesados_exito += 1
        else:
            # No se encontraron mensajes, marcamos como sincronizado pero vacío
            contacto['apollo_last_sync_at'] = datetime.now().isoformat()
            print("   - No se encontraron mensajes en Apollo.")
            errores += 1

        # Pequeña pausa
        time.sleep(PAUSE_BETWEEN_REQUESTS)

        # Guardar progreso cada 20 contactos para no perder todo si falla
        if i % 20 == 0:
            guardar_tabla(contactos, fieldnames)
            print(f"\n--- PROGRESO GUARDADO ({i} procesados) ---\n")

    # 4. Guardar resultados finales
    guardar_tabla(contactos, fieldnames)
    
    print("\n" + "="*80)
    print("PROCESO FINALIZADO")
    print("="*80)
    print(f"Total exitosos: {procesados_exito}")
    print(f"Sin info: {errores}")
    print(f"Restantes: {len(contactos_a_procesar) - (procesados_exito + errores)}")
    print("="*80)

def guardar_tabla(contactos, fieldnames):
    """Guarda la lista de contactos de vuelta a TablaBase.csv"""
    with open('TablaBase.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contactos)

if __name__ == "__main__":
    sync_apollo()
