#!/usr/bin/env python3
"""
Merge Steps to Base v2 - Fix mapping for steps_apollo_resultado.csv
"""

import csv

def merge():
    print("="*80)
    print("MERGING STEPS TO TABLA BASE")
    print("="*80)

    # 1. Leer steps_apollo_resultado.csv
    steps_por_email = {}
    try:
        with open('steps_apollo_resultado.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('To Email', '').strip().lower()
                if not email:
                    continue
                
                try:
                    current_step = int(row.get('Step', 0))
                except:
                    current_step = 0
                
                if email not in steps_por_email:
                    steps_por_email[email] = row
                else:
                    try:
                        existing_step = int(steps_por_email[email].get('Step', 0))
                    except:
                        existing_step = 0
                    if current_step >= existing_step:
                        steps_por_email[email] = row
        print(f"Info de Apollo en steps_apollo_resultado.csv: {len(steps_por_email)} emails")
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Leer TablaBase.csv
    try:
        with open('TablaBase.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contactos = list(reader)
            fieldnames = reader.fieldnames
    except Exception as e:
        print(f"Error: {e}")
        return

    # 3. Actualizar contactos
    actualizados = 0
    for contacto in contactos:
        email = contacto.get('EMAIL_LIMPIO', '').strip().lower()
        if email in steps_por_email:
            info = steps_por_email[email]
            
            # Map correctly based on existing columns in steps_apollo_resultado.csv
            contacto['campaña'] = info.get('Sequence', '')
            contacto['step_numero'] = info.get('Step', '')
            contacto['apollo_status'] = info.get('Task Status', '')
            contacto['estado_apollo'] = info.get('Task Status', '')
            contacto['fecha_envio'] = info.get('Completed Date (PST)', '')
            contacto['fecha_programada'] = info.get('Due Date (PST)', '')
            
            # Use Subject as a proxy for message ID if not present
            # contacto['apollo_last_message_id'] = info.get('Subject', '') 
            
            actualizados += 1

    # 4. Guardar
    with open('TablaBase.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contactos)

    print(f"Se actualizaron {actualizados} contactos.")
    print("="*80)

if __name__ == "__main__":
    merge()
