#!/usr/bin/env python3
"""
Analizar qué información de Apollo tenemos en TablaBase.csv
"""

import csv

with open('TablaBase.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print("="*80)
print(f"ANÁLISIS DE TABLA BASE - Total de filas: {len(rows)}")
print("="*80)

# Campos de Apollo que tenemos
apollo_fields = [
    'apollo_last_message_id', 'apollo_sequence_id', 'apollo_step',
    'apollo_last_sent_at', 'apollo_status', 'apollo_last_opened_at',
    'apollo_last_clicked_at', 'apollo_last_replied_at',
    'apollo_last_activity_at', 'apollo_last_sync_at', 'apollo_step_id',
    'estado_apollo', 'campaña', 'step_numero', 'step_nombre',
    'accion_humana', 'fecha_programada', 'fecha_envio', 'fecha de step'
]

print("\nPrimeras 5 filas con información de Apollo:")
print("="*80)

for i, row in enumerate(rows[:5], 1):
    print(f"\n{i}. {row.get('Contacto', 'Sin nombre')} - {row.get('Empresa', 'Sin empresa')}")
    print(f"   STEP: {row.get('STEP', 'N/A')}")
    print(f"   Email: {row.get('EMAIL_LIMPIO', 'N/A')}")

    # Mostrar campos de Apollo que no estén vacíos
    print(f"   Campos de Apollo:")
    for field in apollo_fields:
        value = row.get(field, '')
        if value and value.strip():
            print(f"      • {field}: {value[:100]}")

# Estadísticas
print("\n" + "="*80)
print("ESTADÍSTICAS DE CAMPOS DE APOLLO:")
print("="*80)

for field in apollo_fields:
    if field in rows[0]:
        no_vacios = sum(1 for r in rows if r.get(field, '').strip())
        print(f"{field:30s}: {no_vacios:4d} filas con datos ({no_vacios/len(rows)*100:.1f}%)")
