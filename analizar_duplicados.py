#!/usr/bin/env python3
"""
Script para analizar los datos crudos y entender la duplicación
"""

import csv
import json
from collections import defaultdict

def analizar_csv():
    # Leer el CSV generado
    with open('steps_apollo_resultado.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print("="*80)
    print(f"ANÁLISIS DE DUPLICADOS - Total de registros: {len(rows)}")
    print("="*80)

    # Agrupar por contacto
    por_contacto = defaultdict(list)
    for row in rows:
        contacto = row.get('Contact Name', 'Sin nombre')
        por_contacto[contacto].append(row)

    print(f"\nTotal de contactos únicos: {len(por_contacto)}")

    # Analizar los primeros 3 contactos en detalle
    print("\n" + "="*80)
    print("ANÁLISIS DETALLADO DE LOS PRIMEROS 3 CONTACTOS:")
    print("="*80)

    for i, (contacto, steps) in enumerate(list(por_contacto.items())[:3], 1):
        print(f"\n{i}. CONTACTO: {contacto}")
        print(f"   Total de steps: {len(steps)}")
        print(f"   Empresa: {steps[0].get('Account', 'N/A')}")

        # Verificar si son duplicados exactos
        unique_steps = []
        for step in steps:
            # Crear una firma del step basada en campos clave
            firma = f"{step.get('Type')}|{step.get('Sequence')}|{step.get('Step')}|{step.get('Subject')}|{step.get('Due Date (PST)')}"
            if firma not in [f"{s.get('Type')}|{s.get('Sequence')}|{s.get('Step')}|{s.get('Subject')}|{s.get('Due Date (PST)')}" for s in unique_steps]:
                unique_steps.append(step)

        print(f"   Steps únicos (sin duplicados): {len(unique_steps)}")

        # Mostrar los primeros 5 steps
        print(f"\n   Primeros 5 steps:")
        for j, step in enumerate(steps[:5], 1):
            print(f"\n   Step {j}:")
            print(f"      Type: {step.get('Type', 'N/A')}")
            print(f"      Status: {step.get('Task Status', 'N/A')}")
            print(f"      Sequence: {step.get('Sequence', 'VACÍO')}")
            print(f"      Step #: {step.get('Step', 'VACÍO')}")
            print(f"      Subject: {step.get('Subject', 'VACÍO')[:50]}")
            print(f"      Due Date: {step.get('Due Date (PST)', 'VACÍO')}")
            print(f"      Sent Date: {step.get('Completed Date (PST)', 'VACÍO')}")

    # Estadísticas generales
    print("\n" + "="*80)
    print("ESTADÍSTICAS GENERALES:")
    print("="*80)

    # Contar registros con campos vacíos
    vacios_sequence = sum(1 for r in rows if not r.get('Sequence'))
    vacios_step = sum(1 for r in rows if not r.get('Step'))
    vacios_subject = sum(1 for r in rows if not r.get('Subject'))
    vacios_fecha = sum(1 for r in rows if not r.get('Due Date (PST)'))

    print(f"Registros con Sequence vacío: {vacios_sequence} ({vacios_sequence/len(rows)*100:.1f}%)")
    print(f"Registros con Step # vacío: {vacios_step} ({vacios_step/len(rows)*100:.1f}%)")
    print(f"Registros con Subject vacío: {vacios_subject} ({vacios_subject/len(rows)*100:.1f}%)")
    print(f"Registros con Fecha vacía: {vacios_fecha} ({vacios_fecha/len(rows)*100:.1f}%)")

if __name__ == "__main__":
    analizar_csv()
