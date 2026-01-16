#!/usr/bin/env python3
"""
Script MEJORADO para obtener los steps de Apollo
Usa el método GET correcto y hace llamadas más específicas
"""

import csv
import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime

# Configuración de Apollo API
APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"

def leer_base_datos(archivo_csv: str) -> List[Dict]:
    """Lee el archivo CSV con la base de datos de contactos"""
    contactos = []
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contactos.append(row)
    return contactos

def obtener_steps_por_contact_id(contact_email: str) -> Optional[Dict]:
    """
    Obtiene steps usando el endpoint GET correcto
    Primero necesitamos buscar el contact_id
    """
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }

    # Endpoint 1: Buscar el contacto por email para obtener su ID
    people_url = "https://api.apollo.io/api/v1/people/match"
    people_payload = {
        "email": contact_email
    }

    try:
        print(f"   Buscando contact ID para {contact_email}...")
        response = requests.post(people_url, headers=headers, json=people_payload, timeout=30)

        if response.status_code == 200:
            contact_data = response.json()
            person = contact_data.get('person', {})
            contact_id = person.get('id')

            if contact_id:
                print(f"   ✓ Contact ID encontrado: {contact_id}")

                # Endpoint 2: Ahora obtener sus emailer_messages usando GET
                messages_url = f"https://api.apollo.io/api/v1/contacts/{contact_id}/emailer_touches"

                response2 = requests.get(messages_url, headers=headers, timeout=30)

                if response2.status_code == 200:
                    touches_data = response2.json()
                    return touches_data
                elif response2.status_code == 404:
                    # Probar endpoint alternativo
                    print(f"   Probando endpoint alternativo...")
                    alt_url = "https://api.apollo.io/api/v1/emailer_messages/search"
                    params = {
                        "contact_ids[]": contact_id,
                        "per_page": 100
                    }
                    response3 = requests.get(alt_url, headers=headers, params=params, timeout=30)

                    if response3.status_code == 200:
                        return response3.json()
                    else:
                        print(f"   ✗ Error en endpoint alternativo: {response3.status_code}")
                        return None
                else:
                    print(f"   ✗ Error obteniendo touches: {response2.status_code}")
                    return None
            else:
                print(f"   ✗ No se encontró contact ID")
                return None

        elif response.status_code == 429:
            print(f"   ⚠ Rate limit alcanzado. Esperando...")
            return "RATE_LIMIT"
        else:
            print(f"   ✗ Error buscando contacto: {response.status_code}")
            return None

    except Exception as e:
        print(f"   ✗ Excepción: {str(e)}")
        return None

def obtener_steps_por_sequence_id(sequence_id: str, contact_email: str) -> Optional[List[Dict]]:
    """
    Obtiene los steps de una secuencia específica para un contacto
    """
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }

    # Endpoint para obtener estadísticas de una secuencia específica
    url = f"https://api.apollo.io/api/v1/emailer_campaigns/{sequence_id}/contact_export"

    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            return "RATE_LIMIT"
        else:
            print(f"   ✗ Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"   ✗ Excepción: {str(e)}")
        return None

def formatear_fecha(fecha_str: Optional[str]) -> str:
    """Formatea una fecha al formato deseado"""
    if not fecha_str:
        return ""
    try:
        dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y %H:%M")
    except:
        return fecha_str

def procesar_contacto_con_info_existente(contacto: Dict) -> List[Dict]:
    """
    Procesa un contacto usando la información que YA tenemos en TablaBase.csv
    Sin hacer llamadas a la API
    """
    rows = []

    contact_name = contacto.get('Contacto', '')
    empresa = contacto.get('Empresa', '')
    email = contacto.get('EMAIL_LIMPIO', '')

    # Si tiene información de Apollo en la tabla base, úsala
    if contacto.get('campaña') or contacto.get('apollo_sequence_id'):
        row = {
            'Type': 'Email',  # o Phone Call según el step
            'Task Assignee': 'Santiago Munoz',
            'Task Status': contacto.get('apollo_status', contacto.get('estado_apollo', '')).lower(),
            'Contact Name': contact_name,
            'Priority': 'medium',
            'Due Date (PST)': contacto.get('fecha_programada', ''),
            'Completed Date (PST)': contacto.get('fecha_envio', ''),
            'Sequence': contacto.get('campaña', ''),
            'Step': contacto.get('step_numero', ''),
            'Template': '',
            'From Email': '',
            'To Email': email,
            'Subject': '',
            'Email Body': '',
            'Call Purpose': '',
            'Call Disposition': '',
            'Task Note': '',
            'Email Note': '',
            'Task Created From': 'TablaBase.csv',
            'Contact Stage': contacto.get('ESTADO', ''),
            'Account': empresa,
            # Campos adicionales
            'apollo_step_id': contacto.get('apollo_step_id', ''),
            'contacto': contact_name,
            'campaña': contacto.get('campaña', ''),
            'step_numero': contacto.get('step_numero', ''),
            'step_nombre': contacto.get('step_nombre', contacto.get('STEP', '')),
            'accion_humana': contacto.get('accion_humana', ''),
            'estado_apollo': contacto.get('estado_apollo', ''),
            'fecha_programada': contacto.get('fecha_programada', ''),
            'fecha_envio': contacto.get('fecha_envio', contacto.get('fecha de step', ''))
        }
        rows.append(row)

    return rows

def main():
    print("="*80)
    print("OBTENIENDO STEPS DE APOLLO - VERSIÓN MEJORADA")
    print("="*80)

    # Leer la base de datos
    print("\n1. Leyendo base de datos...")
    contactos = leer_base_datos('TablaBase.csv')
    print(f"   Total de contactos: {len(contactos)}")

    # Primero, usar la información que YA tenemos
    print("\n2. Procesando información existente de Apollo en TablaBase.csv...")
    todas_las_filas = []
    contactos_sin_info = []

    for i, contacto in enumerate(contactos, 1):
        email = contacto.get('EMAIL_LIMPIO', '').strip()
        if not email:
            continue

        # Verificar si ya tiene información de Apollo
        if contacto.get('campaña') or contacto.get('apollo_sequence_id'):
            filas = procesar_contacto_con_info_existente(contacto)
            todas_las_filas.extend(filas)
            if i % 100 == 0:
                print(f"   Procesados: {i}/{len(contactos)}")
        else:
            contactos_sin_info.append(contacto)

    print(f"   ✓ {len(todas_las_filas)} steps encontrados en TablaBase.csv")
    print(f"   ⚠ {len(contactos_sin_info)} contactos sin información de Apollo")

    # Guardar el archivo CSV
    print(f"\n3. Generando archivo CSV...")

    if todas_las_filas:
        output_file = 'steps_apollo_resultado_MEJORADO.csv'
        fieldnames = [
            'Type', 'Task Assignee', 'Task Status', 'Contact Name', 'Priority',
            'Due Date (PST)', 'Completed Date (PST)', 'Sequence', 'Step', 'Template',
            'From Email', 'To Email', 'Subject', 'Email Body', 'Call Purpose',
            'Call Disposition', 'Task Note', 'Email Note', 'Task Created From',
            'Contact Stage', 'Account',
            # Campos adicionales
            'apollo_step_id', 'contacto', 'campaña', 'step_numero', 'step_nombre',
            'accion_humana', 'estado_apollo', 'fecha_programada', 'fecha_envio'
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(todas_las_filas)

        print(f"   ✓ Archivo guardado: {output_file}")
        print(f"   Total de steps: {len(todas_las_filas)}")
    else:
        print("   ⚠ No se encontraron steps para generar el archivo")

    # Guardar lista de contactos sin información
    if contactos_sin_info:
        with open('contactos_sin_info_apollo.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=contactos[0].keys())
            writer.writeheader()
            writer.writerows(contactos_sin_info)
        print(f"\n   ℹ Lista de contactos sin info guardada en: contactos_sin_info_apollo.csv")

    print("\n" + "="*80)
    print("PROCESO COMPLETADO")
    print(f"RESUMEN:")
    print(f"  - Contactos con información: {len(contactos) - len(contactos_sin_info)}")
    print(f"  - Contactos sin información: {len(contactos_sin_info)}")
    print(f"  - Steps totales exportados: {len(todas_las_filas)}")
    print("="*80)

if __name__ == "__main__":
    main()
