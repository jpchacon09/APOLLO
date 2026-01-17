#!/bin/bash
# Script para actualizar el dashboard CRM
set -e

echo "🔄 Actualizando Dashboard CRM..."
echo ""

# 1. Regenerar KPIs
echo "📊 Generando KPIs..."
python3 crm_engine.py

# 2. Crear dashboard profesional con datos embebidos
echo "🎨 Embebiendo datos en dashboard profesional..."
python3 << 'PYTHON'
import json

with open('crm_dashboard_data_full.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Leer template profesional
with open('crm_pro.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Buscar y reemplazar loadData
import re
pattern = r'function loadData\(\) \{[^}]+\}'
replacement = f'''function loadData() {{
            dashboardData = {json.dumps(data, ensure_ascii=False)};
            renderDashboard();
        }}'''

html_nuevo = re.sub(pattern, replacement, html, flags=re.DOTALL)

# Guardar
with open('crm_pro.html', 'w', encoding='utf-8') as f:
    f.write(html_nuevo)

print('✓ Dashboard profesional actualizado')
PYTHON

echo ""
echo "✅ Dashboard actualizado exitosamente!"
echo "📂 Abre: crm_pro.html"
echo ""

# Mostrar estadísticas
python3 << 'STATS'
import csv, json
with open('TablaBase.csv', 'r', encoding='utf-8') as f:
    contactos = list(csv.DictReader(f))
with open('crm_dashboard_data_full.json', 'r') as f:
    data = json.load(f)

sincronizados = sum(1 for c in contactos if c.get('apollo_last_sync_at', '').strip())
print(f"📈 Estadísticas:")
print(f"   Contactos totales: {len(contactos)}")
print(f"   Sincronizados con Apollo: {sincronizados} ({sincronizados*100//len(contactos)}%)")
print(f"   Emails enviados: {data['kpis_v2']['email']['sent']}")
print(f"   Llamadas realizadas: {data['kpis_v2']['calls']['realized']}")
print(f"   Reuniones agendadas: {data['kpis_v2']['calls']['meetings']}")
STATS
