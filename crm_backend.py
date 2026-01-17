#!/usr/bin/env python3
"""
CRM Backend - API para actualización y servicio del dashboard
"""

from flask import Flask, jsonify, send_file
from flask_cors import CORS
import subprocess
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Servir el dashboard"""
    return send_file('crm_pro.html')

@app.route('/api/data')
def get_data():
    """Obtener datos del dashboard"""
    try:
        with open('crm_dashboard_data_full.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Actualizar datos del CRM"""
    try:
        # 1. Regenerar KPIs
        result = subprocess.run(
            ['python3', 'crm_engine.py'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': 'Error al regenerar KPIs',
                'details': result.stderr
            }), 500

        # 2. Leer datos actualizados
        with open('crm_dashboard_data_full.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        return jsonify({
            'success': True,
            'message': 'Datos actualizados correctamente',
            'timestamp': datetime.now().isoformat(),
            'data': data
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout al actualizar datos'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sync-apollo', methods=['POST'])
def sync_apollo():
    """Iniciar sincronización con Apollo (background)"""
    try:
        # Ejecutar en background
        subprocess.Popen(
            ['python3', 'apollo_sync_v3.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return jsonify({
            'success': True,
            'message': 'Sincronización con Apollo iniciada en background'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Estadísticas rápidas del sistema"""
    try:
        import csv

        with open('TablaBase.csv', 'r', encoding='utf-8') as f:
            contactos = list(csv.DictReader(f))

        total = len(contactos)
        sincronizados = sum(1 for c in contactos if c.get('apollo_last_sync_at', '').strip())

        return jsonify({
            'total_contactos': total,
            'sincronizados_apollo': sincronizados,
            'pendientes': total - sincronizados,
            'porcentaje_sync': round((sincronizados / total * 100), 2) if total > 0 else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
