#!/usr/bin/env python3
"""
Genera KPIs y métricas de análisis del CRM
"""

import csv
import json
from collections import defaultdict, Counter
from datetime import datetime

def analizar_crm():
    """Analiza todos los datos y genera KPIs completos"""

    # Leer TablaBase.csv (fuente principal)
    with open('TablaBase.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        contactos = list(reader)

    print("="*80)
    print("ANÁLISIS COMPLETO DEL CRM - GENERANDO KPIS")
    print("="*80)
    print(f"Total de contactos en la base: {len(contactos)}")

    # ========== KPIs PRINCIPALES ==========
    kpis = {
        'total_contactos': len(contactos),
        'con_email': sum(1 for c in contactos if c.get('EMAIL_LIMPIO', '').strip()),
        'con_telefono': sum(1 for c in contactos if c.get('CELULAR1', '').strip()),
        'con_apollo_info': sum(1 for c in contactos if c.get('apollo_sequence_id', '').strip()),
    }

    # ========== ANÁLISIS POR ESTADO ==========
    estados = Counter(c.get('ESTADO', 'SIN ESTADO').strip().upper() for c in contactos if c.get('ESTADO'))

    # ========== ANÁLISIS POR RESPONSABLE ==========
    responsables = Counter(c.get('Responsable', 'SIN ASIGNAR').strip() for c in contactos)

    # ========== ANÁLISIS POR STEP ==========
    steps = Counter(c.get('STEP', 'SIN STEP').strip().upper() for c in contactos if c.get('STEP'))

    # ========== ANÁLISIS POR CAMPAÑA ==========
    campanas = Counter(c.get('campaña', 'SIN CAMPAÑA').strip() for c in contactos if c.get('campaña'))

    # ========== ANÁLISIS POR FUENTE ==========
    fuentes = Counter(c.get('Fuente', 'SIN FUENTE').strip() for c in contactos if c.get('Fuente'))

    # ========== CONTACTOS POR ESTADO DETALLADO ==========
    contactos_por_estado = defaultdict(list)
    for c in contactos:
        estado = c.get('ESTADO', 'SIN ESTADO').strip().upper()
        contactos_por_estado[estado].append({
            'nombre': c.get('Contacto', 'Sin nombre'),
            'empresa': c.get('Empresa', 'Sin empresa'),
            'email': c.get('EMAIL_LIMPIO', ''),
            'responsable': c.get('Responsable', ''),
            'step': c.get('STEP', ''),
            'fecha': c.get('fecha gestion envio secuencia 2025- 2026', '')
        })

    # ========== MÉTRICAS DE CONVERSIÓN ==========
    total_con_estado = sum(1 for c in contactos if c.get('ESTADO'))

    metricas_conversion = {
        'tasa_respuesta': (estados.get('INTERESADO', 0) + estados.get('AGENDADO', 0)) / total_con_estado * 100 if total_con_estado > 0 else 0,
        'tasa_no_contacto': (estados.get('NO CONTESTA', 0) + estados.get('APAGADO', 0)) / total_con_estado * 100 if total_con_estado > 0 else 0,
        'tasa_rechazo': estados.get('NO INTERESADO', 0) / total_con_estado * 100 if total_con_estado > 0 else 0,
        'tasa_linkedin': estados.get('LINKEDIN', 0) / total_con_estado * 100 if total_con_estado > 0 else 0,
    }

    # ========== ANÁLISIS TEMPORAL ==========
    contactos_con_fecha = [c for c in contactos if c.get('fecha gestion envio secuencia 2025- 2026')]
    fechas = Counter(c.get('fecha gestion envio secuencia 2025- 2026') for c in contactos_con_fecha)

    # ========== GENERAR DATOS PARA EL DASHBOARD ==========
    dashboard_data = {
        'timestamp': datetime.now().isoformat(),
        'kpis_principales': {
            'Total Contactos': kpis['total_contactos'],
            'Con Email': kpis['con_email'],
            'Con Teléfono': kpis['con_telefono'],
            'En Apollo': kpis['con_apollo_info'],
        },
        'estados': dict(estados.most_common(10)),
        'responsables': dict(responsables.most_common()),
        'steps': dict(steps.most_common(10)),
        'campanas': dict(campanas.most_common()),
        'fuentes': dict(fuentes.most_common()),
        'metricas_conversion': {
            'Tasa de Interés/Agendados': round(metricas_conversion['tasa_respuesta'], 2),
            'Tasa de No Contacto': round(metricas_conversion['tasa_no_contacto'], 2),
            'Tasa de Rechazo': round(metricas_conversion['tasa_rechazo'], 2),
            'Tasa LinkedIn': round(metricas_conversion['tasa_linkedin'], 2),
        },
        'contactos_por_estado': {
            estado: {
                'cantidad': len(lista),
                'top_5': lista[:5]
            }
            for estado, lista in sorted(contactos_por_estado.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        },
        'timeline': dict(sorted(fechas.items())[:30])
    }

    # Guardar JSON para el dashboard
    with open('crm_dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

    # ========== IMPRIMIR RESUMEN ==========
    print("\n" + "="*80)
    print("📊 KPIS PRINCIPALES")
    print("="*80)
    for key, value in dashboard_data['kpis_principales'].items():
        print(f"{key:20s}: {value:6d}")

    print("\n" + "="*80)
    print("📈 MÉTRICAS DE CONVERSIÓN")
    print("="*80)
    for key, value in dashboard_data['metricas_conversion'].items():
        print(f"{key:30s}: {value:6.2f}%")

    print("\n" + "="*80)
    print("👥 TOP 5 ESTADOS")
    print("="*80)
    for estado, cantidad in list(estados.most_common(5)):
        porcentaje = (cantidad / total_con_estado * 100) if total_con_estado > 0 else 0
        print(f"{estado:30s}: {cantidad:4d} ({porcentaje:5.1f}%)")

    print("\n" + "="*80)
    print("🎯 TOP RESPONSABLES")
    print("="*80)
    for responsable, cantidad in responsables.most_common(5):
        print(f"{responsable:30s}: {cantidad:4d} contactos")

    print("\n" + "="*80)
    print("📧 CAMPAÑAS ACTIVAS")
    print("="*80)
    for campana, cantidad in campanas.most_common():
        print(f"{campana:50s}: {cantidad:4d} contactos")

    print("\n✓ Datos guardados en: crm_dashboard_data.json")
    print("="*80)

    return dashboard_data

if __name__ == "__main__":
    analizar_crm()
