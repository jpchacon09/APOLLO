#!/usr/bin/env python3
"""
Script para obtener los steps de Apollo de cada contacto en la base de datos
"""

import csv
import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime

# Configuración de Apollo API
APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"
APOLLO_API_ENDPOINT = "https://api.apollo.io/api/v1/emailer_messages/search"

def leer_base_datos(archivo_csv: str) -> List[Dict]:
    """Lee el archivo CSV con la base de datos de contactos"""
    contactos = []
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contactos.append(row)
    return contactos

def buscar_steps_apollo(email: str, contact_name: str, empresa: str) -> List[Dict]:
    """Busca los steps de un contacto en Apollo usando la API"""
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }

    # Intentar buscar por email
    payload = {
        'email_address': email
    }

    try:
        response = requests.post(APOLLO_API_ENDPOINT, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            messages = data.get('emailer_messages', [])
            print(f"✓ {contact_name} ({empresa}): {len(messages)} steps encontrados")
            return messages
        elif response.status_code == 429:
            print(f"⚠ Rate limit alcanzado, esperando 60 segundos...")
            time.sleep(60)
            return buscar_steps_apollo(email, contact_name, empresa)
        else:
            print(f"✗ Error {response.status_code} para {contact_name} ({email}): {response.text}")
            return []
    except Exception as e:
        print(f"✗ Excepción para {contact_name} ({email}): {str(e)}")
        return []

def formatear_fecha(fecha_str: Optional[str]) -> str:
    """Formatea una fecha de Apollo al formato deseado"""
    if not fecha_str:
        return ""
    try:
        # Apollo devuelve fechas en formato ISO
        dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        # Convertir al formato: "January 12, 2026 08:00"
        return dt.strftime("%B %d, %Y %H:%M")
    except:
        return fecha_str

def convertir_a_formato_deseado(messages: List[Dict], contacto: Dict) -> List[Dict]:
    """Convierte los mensajes de Apollo al formato deseado del CSV"""
    rows = []

    contact_name = contacto.get('Contacto', '')
    empresa = contacto.get('Empresa', '')

    for msg in messages:
        # Determinar el tipo de step
        step_type = msg.get('type', 'Email')
        if step_type == 'phone_call':
            step_type = 'Phone Call'
        elif step_type == 'email' or step_type == 'outreach_automatic_email':
            step_type = 'Email'

        # Obtener información de la campaña
        campaign = msg.get('emailer_campaign', {})
        campaign_name = campaign.get('name', '')

        # Obtener información del step
        emailer_step = msg.get('emailer_step', {})
        step_id = msg.get('id', '')
        step_number = msg.get('step_number', '')

        # Determinar el nombre del step basado en el tipo
        step_nombre = emailer_step.get('type', step_type)

        # Estado de Apollo
        estado_apollo = msg.get('status', '')
        if estado_apollo == 'scheduled':
            estado_apollo = 'Programado'
        elif estado_apollo == 'sent':
            estado_apollo = 'Enviado'
        elif estado_apollo == 'completed':
            estado_apollo = 'Completado'
        elif estado_apollo == 'bounced':
            estado_apollo = 'Rebotado'
        elif estado_apollo == 'opened':
            estado_apollo = 'Abierto'
        elif estado_apollo == 'clicked':
            estado_apollo = 'Clicado'
        elif estado_apollo == 'replied':
            estado_apollo = 'Respondido'

        # Acción humana (si requiere intervención manual)
        accion_humana = 'Manual' if step_type == 'Phone Call' else 'Automático'

        # Mapear los campos
        row = {
            'Type': step_type,
            'Task Assignee': msg.get('user', {}).get('name', 'Santiago Munoz'),
            'Task Status': msg.get('status', 'completed').lower(),
            'Contact Name': contact_name,
            'Priority': 'medium',
            'Due Date (PST)': formatear_fecha(msg.get('scheduled_at')),
            'Completed Date (PST)': formatear_fecha(msg.get('sent_at')),
            'Sequence': campaign_name,
            'Step': step_number,
            'Template': msg.get('template', {}).get('name', ''),
            'From Email': msg.get('from_address', ''),
            'To Email': msg.get('to_address', contacto.get('EMAIL_LIMPIO', '')),
            'Subject': msg.get('subject', ''),
            'Email Body': msg.get('body', ''),
            'Call Purpose': msg.get('call_purpose', ''),
            'Call Disposition': msg.get('call_disposition', ''),
            'Task Note': msg.get('note', ''),
            'Email Note': msg.get('email_note', ''),
            'Task Created From': 'Apollo API',
            'Contact Stage': contacto.get('ESTADO', ''),
            'Account': empresa,
            # Campos adicionales solicitados
            'apollo_step_id': step_id,
            'contacto': contact_name,
            'campaña': campaign_name,
            'step_numero': step_number,
            'step_nombre': step_nombre,
            'accion_humana': accion_humana,
            'estado_apollo': estado_apollo,
            'fecha_programada': formatear_fecha(msg.get('scheduled_at')),
            'fecha_envio': formatear_fecha(msg.get('sent_at'))
        }

        rows.append(row)

    return rows

def main():
    print("="*80)
    print("OBTENIENDO STEPS DE APOLLO PARA TODOS LOS CONTACTOS")
    print("="*80)

    # Leer la base de datos
    print("\n1. Leyendo base de datos...")
    contactos = leer_base_datos('TablaBase.csv')
    print(f"   Total de contactos: {len(contactos)}")

    # Filtrar contactos con email y limitar a 400 para la muestra
    contactos_con_email = [c for c in contactos if c.get('EMAIL_LIMPIO', '').strip()][:400]
    print(f"   Contactos con email (limitado a 400 para muestra): {len(contactos_con_email)}")

    # Obtener steps de Apollo
    print("\n2. Obteniendo steps de Apollo...")
    todas_las_filas = []

    for i, contacto in enumerate(contactos_con_email, 1):
        email = contacto.get('EMAIL_LIMPIO', '').strip()
        contact_name = contacto.get('Contacto', 'Sin nombre')
        empresa = contacto.get('Empresa', 'Sin empresa')

        print(f"\n   [{i}/{len(contactos_con_email)}] Procesando: {contact_name} - {empresa}")

        # Buscar steps en Apollo
        messages = buscar_steps_apollo(email, contact_name, empresa)

        # Convertir al formato deseado
        if messages:
            filas = convertir_a_formato_deseado(messages, contacto)
            todas_las_filas.extend(filas)
            print(f"       → {len(filas)} steps agregados")
        else:
            print(f"       → Sin steps encontrados")

        # Pequeña pausa para no saturar la API
        time.sleep(0.5)

    # Guardar el archivo CSV
    print(f"\n3. Generando archivo CSV...")
    print(f"   Total de steps encontrados: {len(todas_las_filas)}")

    if todas_las_filas:
        output_file = 'steps_apollo_resultado.csv'
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
    else:
        print("   ⚠ No se encontraron steps para generar el archivo")

    print("\n" + "="*80)
    print("PROCESO COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
