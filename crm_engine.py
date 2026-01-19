#!/usr/bin/env python3
"""
CRM Engine v2 - Intelligent KPI Processor
Mapea los KPIs específicos solicitados por el usuario.
"""

import csv
import json
from collections import defaultdict, Counter
from datetime import datetime

def generate_full_data():
    print("Generating Specialized CRM KPIs...")

    # 1. Leer Datos
    contactos_base = []
    with open('TablaBase.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contactos_base.append(row)

    historial_eventos = []
    try:
        with open('steps_apollo_resultado.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Eliminar duplicados exactos en el historial para KPIs limpios
            seen_signatures = set()
            for row in reader:
                signature = f"{row.get('To Email')}_{row.get('Type')}_{row.get('Step')}_{row.get('Subject')}"
                if signature not in seen_signatures:
                    historial_eventos.append(row)
                    seen_signatures.add(signature)
    except:
        print("Warning: steps_apollo_resultado.csv issue.")

    # 2. Calcular KPIs Específicos
    stats = {
        "email": {"sent": 0, "replied": 0, "total": 0},
        "calls": {"realized": 0, "answered": 0, "meetings": 0},
        "linkedin": {"sent": 0, "replied": 0},
        "other": {"sent": 0, "replied": 0}
    }

    # Procesar Historial (Apollo)
    for h in historial_eventos:
        m_type = h.get('Type', '').lower()
        status = h.get('Task Status', '').lower()

        # 1. Emails
        if 'email' in m_type:
            stats["email"]["total"] += 1
            # Incluir scheduled como emails enviados/programados
            if status in ['sent', 'completed', 'opened', 'clicked', 'replied', 'scheduled']:
                stats["email"]["sent"] += 1
            if 'replied' in status or 'respondido' in status:
                stats["email"]["replied"] += 1

        # 2. LinkedIn
        elif 'linkedin' in m_type:
            stats["linkedin"]["sent"] += 1
            if 'replied' in status:
                stats["linkedin"]["replied"] += 1

    # Procesar contactos de Apollo en TablaBase
    for c in contactos_base:
        apollo_status = c.get('apollo_status', '').lower()

        # Contar emails de Apollo
        if apollo_status == 'scheduled':
            # Evitar contar duplicados si ya están en historial_eventos
            email = c.get('EMAIL_LIMPIO', '').strip().lower()
            en_historial = any(h.get('To Email', '').lower() == email for h in historial_eventos)
            if not en_historial:
                stats["email"]["total"] += 1
                stats["email"]["sent"] += 1

    # Procesar Tabla Base (Manual Actions & States)
    for c in contactos_base:
        step = c.get('STEP', '').upper()
        estado = c.get('ESTADO', '').upper()
        
        # 2. Llamadas
        if 'LLAMADA' in step:
            stats["calls"]["realized"] += 1
            # Si el estado no es "NO CONTESTA" o "APAGADO", asumimos contestada
            if estado not in ['NO CONTESTA', 'APAGADO', 'REPICADOR', 'BUZON']:
                if estado != 'SIN GESTION' and estado != '':
                    stats["calls"]["answered"] += 1
        
        if 'AGENDADO' in estado or 'REUNION' in estado:
            stats["calls"]["meetings"] += 1

    # 3. Análisis de Steps y Conversiones
    steps_metrics = defaultdict(lambda: {
        'total': 0, 'interesado': 0, 'agendado': 0,
        'no_interesado': 0, 'no_contesta': 0, 'sin_respuesta': 0
    })

    observaciones_recientes = []

    for c in contactos_base:
        step = c.get('STEP', '')
        estado = c.get('ESTADO', '').upper()

        if step and step not in ['SIN GESTION', '']:
            steps_metrics[step]['total'] += 1

            if 'INTERESADO' in estado:
                steps_metrics[step]['interesado'] += 1
            elif 'AGENDADO' in estado:
                steps_metrics[step]['agendado'] += 1
            elif 'NO INTERESADO' in estado or 'NO PERFIL' in estado:
                steps_metrics[step]['no_interesado'] += 1
            elif 'NO CONTESTA' in estado or 'APAGADO' in estado:
                steps_metrics[step]['no_contesta'] += 1
            else:
                steps_metrics[step]['sin_respuesta'] += 1

        # Capturar observaciones con contenido real
        obs = c.get('observaciones', '').strip()
        if obs and len(obs) > 10:
            observaciones_recientes.append({
                'contacto': c.get('Contacto', 'Sin nombre'),
                'empresa': c.get('Empresa', ''),
                'observacion': obs,
                'estado': c.get('ESTADO', ''),
                'step': c.get('STEP', ''),
                'fecha': c.get('fecha gestion envio secuencia 2025- 2026', '')
            })

    # Ordenar observaciones por fecha (las más recientes primero)
    observaciones_recientes = sorted(
        observaciones_recientes,
        key=lambda x: x.get('fecha', ''),
        reverse=True
    )[:30]

    # 3. Pipeline Mapping
    pipeline = {
        'NUEVOS': [],
        'EN_SECUENCIA': [],
        'INTERESADOS': [],
        'AGENDADOS': [],
        'RECHAZADOS': []
    }

    status_counts = Counter()
    for c in contactos_base:
        estado = c.get('ESTADO', 'SIN GESTION').upper()
        category = 'NUEVOS'
        if 'INTERESADO' in estado: category = 'INTERESADOS'
        elif 'AGENDADO' in estado: category = 'AGENDADOS'
        elif 'NO_INTERESADO' in estado: category = 'RECHAZADOS'
        elif c.get('campaña'): category = 'EN_SECUENCIA'
        
        # Usar apollo_name si Contacto está vacío
        contact_name = c.get('Contacto') or c.get('apollo_name') or 'Sin Nombre'
        
        pipeline[category].append({
            'name': contact_name,
            'company': c.get('Empresa') or c.get('apollo_org') or '-',
            'email': c.get('EMAIL_LIMPIO'),
            'apollo_status': c.get('estado_apollo') or c.get('apollo_status') or c.get('ESTADO'),
            'current_campaign': c.get('campaña') or '',
            'current_step': c.get('step_numero') or c.get('STEP') or ''
        })
        status_counts[category] += 1

    # Recent Activity (para el feed)
    def get_date(x):
        d = x.get('Completed Date (PST)') or x.get('Due Date (PST)', '')
        try: return datetime.strptime(d, "%B %d, %Y %H:%M")
        except: return datetime.min

    historial_ordenado = sorted(historial_eventos, key=get_date, reverse=True)

    # 4. Final Data Structure
    final_data = {
        'timestamp': datetime.now().isoformat(),
        'kpis_v2': stats,
        'steps_metrics': dict(steps_metrics),
        'observaciones': observaciones_recientes,
        'pipeline': {k: v[:100] for k, v in pipeline.items()},
        'recent_activity': [{
            'contact': h.get('Contact Name'),
            'account': h.get('Account'),
            'type': h.get('Type'),
            'status': h.get('Task Status'),
            'sequence': h.get('Sequence') or 'Sin secuencia',
            'step': h.get('Step') or '-',
            'date': h.get('Completed Date (PST)') or h.get('Due Date (PST)')
        } for h in historial_ordenado[:30]],
        'counts': dict(status_counts)
    }

    with open('crm_dashboard_data_full.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print("Success: KPIs updated with user specific requirements.")

if __name__ == "__main__":
    generate_full_data()
