#!/usr/bin/env python3
"""
Script automático que espera el reset del rate limit y completa TODOS los datos de Apollo
Se ejecuta automáticamente cuando la API esté disponible
"""

import csv
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Configuración
APOLLO_API_KEY = "_KzNd14cLtj4Mpjj7RsJJw"
WAIT_TIME_HOURS = 1  # Tiempo de espera para el rate limit
MAX_RETRIES = 3

def verificar_rate_limit():
    """Verifica si el rate limit se ha reseteado haciendo una llamada de prueba"""
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }

    # Hacer una llamada pequeña de prueba
    url = "https://api.apollo.io/api/v1/people/match"
    payload = {"email": "test@example.com"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 429:
            return False, "Rate limit activo"
        elif response.status_code in [200, 404]:
            return True, "API disponible"
        else:
            return True, f"API respondió con código {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def obtener_contact_id_y_sequences(email: str) -> Dict:
    """Obtiene el ID del contacto y sus secuencias activas"""
    headers = {
        'X-Api-Key': APOLLO_API_KEY,
        'Content-Type': 'application/json'
    }

    url = "https://api.apollo.io/api/v1/people/match"
    payload = {"email": email}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            person = data.get('person', {})

            return {
                'success': True,
                'contact_id': person.get('id'),
                'name': person.get('name'),
                'email': email,
                'sequences': person.get('active_sequences', []),
                'data': person
            }
        elif response.status_code == 429:
            return {'success': False, 'error': 'rate_limit'}
        else:
            return {'success': False, 'error': f'status_{response.status_code}'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

def procesar_contactos_pendientes(archivo_pendientes: str):
    """Procesa todos los contactos que no tienen información de Apollo"""
    print("\n" + "="*80)
    print("PROCESANDO CONTACTOS PENDIENTES")
    print("="*80)

    # Leer contactos sin información
    with open(archivo_pendientes, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        contactos = list(reader)

    print(f"Total de contactos a procesar: {len(contactos)}")

    resultados = []
    errores = []

    for i, contacto in enumerate(contactos, 1):
        email = contacto.get('EMAIL_LIMPIO', '').strip()
        if not email:
            continue

        nombre = contacto.get('Contacto', 'Sin nombre')
        empresa = contacto.get('Empresa', 'Sin empresa')

        print(f"\n[{i}/{len(contactos)}] Procesando: {nombre} - {empresa}")
        print(f"   Email: {email}")

        # Obtener información de Apollo
        info = obtener_contact_id_y_sequences(email)

        if info.get('success'):
            print(f"   ✓ Contact ID: {info.get('contact_id')}")
            print(f"   ✓ Secuencias activas: {len(info.get('sequences', []))}")

            # Guardar resultado
            resultado = {
                'contacto_original': contacto,
                'apollo_info': info
            }
            resultados.append(resultado)

        elif info.get('error') == 'rate_limit':
            print(f"   ⚠ Rate limit alcanzado nuevamente. Deteniendo...")
            break
        else:
            print(f"   ✗ Error: {info.get('error')}")
            errores.append({'contacto': nombre, 'email': email, 'error': info.get('error')})

        # Pequeña pausa para no saturar la API
        time.sleep(0.5)

        # Guardar progreso cada 50 contactos
        if i % 50 == 0:
            guardar_progreso(resultados, errores)

    # Guardar resultados finales
    guardar_resultados_finales(resultados, errores)

    return resultados, errores

def guardar_progreso(resultados, errores):
    """Guarda el progreso parcial"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(f'apollo_progreso_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump({
            'resultados': resultados,
            'errores': errores,
            'timestamp': timestamp
        }, f, indent=2, ensure_ascii=False)

    print(f"\n   💾 Progreso guardado: apollo_progreso_{timestamp}.json")

def guardar_resultados_finales(resultados, errores):
    """Guarda los resultados finales en CSV"""
    print("\n" + "="*80)
    print("GUARDANDO RESULTADOS FINALES")
    print("="*80)

    # Crear CSV con información completa
    output_file = 'apollo_datos_completos.csv'

    filas = []
    for resultado in resultados:
        contacto = resultado['contacto_original']
        apollo = resultado['apollo_info']

        # Crear fila con toda la información
        fila = {
            'Contacto': contacto.get('Contacto', ''),
            'Empresa': contacto.get('Empresa', ''),
            'Email': contacto.get('EMAIL_LIMPIO', ''),
            'Apollo_Contact_ID': apollo.get('contact_id', ''),
            'Secuencias_Activas': len(apollo.get('sequences', [])),
            'Estado_Original': contacto.get('ESTADO', ''),
            'Responsable': contacto.get('Responsable', ''),
            'STEP': contacto.get('STEP', ''),
        }

        # Agregar información de secuencias si existe
        sequences = apollo.get('sequences', [])
        if sequences:
            for idx, seq in enumerate(sequences[:3]):  # Primeras 3 secuencias
                fila[f'Secuencia_{idx+1}_ID'] = seq.get('id', '')
                fila[f'Secuencia_{idx+1}_Nombre'] = seq.get('name', '')
                fila[f'Secuencia_{idx+1}_Step'] = seq.get('current_step_number', '')

        filas.append(fila)

    if filas:
        fieldnames = filas[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filas)

        print(f"✓ Datos completos guardados en: {output_file}")
        print(f"  Total de contactos procesados: {len(filas)}")

    # Guardar errores
    if errores:
        with open('apollo_errores.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['contacto', 'email', 'error'])
            writer.writeheader()
            writer.writerows(errores)

        print(f"⚠ Errores guardados en: apollo_errores.csv ({len(errores)} errores)")

def main():
    print("="*80)
    print("APOLLO AUTO-COMPLETER - Script Automático")
    print("="*80)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Verificar si existe el archivo de contactos pendientes
    archivo_pendientes = 'contactos_sin_info_apollo.csv'

    try:
        with open(archivo_pendientes, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"\n✗ Error: No se encontró el archivo {archivo_pendientes}")
        print("   Ejecuta primero: obtener_steps_apollo_MEJORADO.py")
        return

    # Verificar estado del rate limit
    print("\n1. Verificando estado de la API...")
    disponible, mensaje = verificar_rate_limit()

    if not disponible:
        print(f"   ⏳ {mensaje}")
        print(f"   Esperando {WAIT_TIME_HOURS} hora(s) para el reset del rate limit...")

        tiempo_espera = WAIT_TIME_HOURS * 3600  # Convertir a segundos
        hora_reinicio = datetime.now() + timedelta(seconds=tiempo_espera)
        print(f"   Reinicio programado para: {hora_reinicio.strftime('%Y-%m-%d %H:%M:%S')}")

        # Esperar con actualizaciones cada 5 minutos
        for i in range(0, tiempo_espera, 300):
            tiempo_restante = tiempo_espera - i
            minutos = tiempo_restante // 60
            print(f"   ⏰ Tiempo restante: {minutos} minutos... ", end='', flush=True)
            time.sleep(300)  # Esperar 5 minutos
            print("✓")

        print("\n   ✓ Tiempo de espera completado. Verificando nuevamente...")
        disponible, mensaje = verificar_rate_limit()

    if disponible:
        print(f"   ✓ {mensaje}")
        print("\n2. Iniciando procesamiento de contactos...")

        resultados, errores = procesar_contactos_pendientes(archivo_pendientes)

        print("\n" + "="*80)
        print("PROCESO COMPLETADO")
        print("="*80)
        print(f"✓ Contactos procesados exitosamente: {len(resultados)}")
        print(f"✗ Errores encontrados: {len(errores)}")
        print(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    else:
        print(f"   ✗ API aún no disponible: {mensaje}")
        print("   Por favor, intenta nuevamente más tarde.")

if __name__ == "__main__":
    main()
