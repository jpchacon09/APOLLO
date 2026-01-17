# Platam CRM - Dashboard Profesional

## 📊 Características

### Dashboard Profesional
- ✅ Diseño único y profesional (dark slate + teal)
- ✅ KPIs principales en tiempo real
- ✅ Análisis de conversión por steps
- ✅ Timeline de observaciones
- ✅ Gráficas interactivas (Chart.js)
- ✅ Botón de actualización funcional

### Métricas Implementadas
1. **Funnel de Conversión** - Progresión por cada step
2. **Distribución del Pipeline** - Categorización de contactos
3. **Tendencias de KPIs** - Evolución de métricas principales
4. **Análisis por Steps** - Barras de progreso visuales
5. **Observaciones** - Timeline de últimas 30 interacciones

### Backend API
- `/` - Dashboard principal
- `/api/data` - Obtener datos completos
- `/api/refresh` - Actualizar KPIs (POST)
- `/api/sync-apollo` - Sincronizar con Apollo (POST)
- `/api/stats` - Estadísticas rápidas

---

## 🚀 Uso Local

### 1. Instalar dependencias

```bash
pip3 install -r requirements.txt
```

### 2. Iniciar servidor

```bash
# Opción A: Con Flask (desarrollo)
python3 crm_backend.py

# Opción B: Con Gunicorn (producción)
gunicorn --bind 0.0.0.0:8080 --workers 2 crm_backend:app
```

### 3. Abrir dashboard

```
http://localhost:8080
```

### 4. Actualizar datos

**Desde el dashboard:**
- Click en botón "Actualizar Datos"

**Desde terminal:**
```bash
./actualizar_dashboard.sh
```

**Manualmente:**
```bash
python3 crm_engine.py
```

---

## ☁️ Deployment a Google Cloud

### Prerequisitos

1. **Instalar Google Cloud SDK**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk

   # Otros: https://cloud.google.com/sdk/docs/install
   ```

2. **Autenticarse**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. **Crear proyecto** (si no existe)
   ```bash
   gcloud projects create platam-crm --name="Platam CRM"
   gcloud config set project platam-crm
   ```

### Opción 1: Deployment Automático (Recomendado)

```bash
./deploy_gcloud.sh [PROJECT_ID] [REGION]

# Ejemplo:
./deploy_gcloud.sh platam-crm us-central1
```

### Opción 2: Deployment Manual

#### Cloud Run (Recomendado)

```bash
# 1. Configurar proyecto
gcloud config set project platam-crm

# 2. Habilitar APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# 3. Build imagen
gcloud builds submit --tag gcr.io/platam-crm/platam-crm-dashboard

# 4. Deploy
gcloud run deploy platam-crm-dashboard \
    --image gcr.io/platam-crm/platam-crm-dashboard \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --port 8080
```

#### App Engine (Alternativa)

```bash
# 1. Deploy
gcloud app deploy app.yaml

# 2. Ver logs
gcloud app logs tail -s default

# 3. Abrir app
gcloud app browse
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Puerto del servidor
export PORT=8080

# API Key de Apollo (ya incluida en código)
export APOLLO_API_KEY="tu_key_aqui"
```

### Personalizar Región

Edita `deploy_gcloud.sh`:
```bash
REGION="us-central1"  # Cambia a tu región preferida
```

Regiones disponibles:
- `us-central1` (Iowa)
- `us-east1` (South Carolina)
- `europe-west1` (Belgium)
- `asia-northeast1` (Tokyo)

### Escalamiento

Edita `app.yaml`:
```yaml
automatic_scaling:
  min_instances: 1      # Mínimo de instancias
  max_instances: 5      # Máximo de instancias
  target_cpu_utilization: 0.65
```

---

## 📦 Estructura del Proyecto

```
APOLLO/
├── crm_backend.py              # Backend Flask
├── crm_pro.html                # Dashboard profesional
├── crm_engine.py               # Generador de KPIs
├── apollo_sync_v3.py           # Sincronización Apollo
├── TablaBase.csv               # Base de datos
├── crm_dashboard_data_full.json # Datos para dashboard
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Para containerización
├── app.yaml                    # Config App Engine
├── deploy_gcloud.sh            # Script de deployment
└── README_DEPLOYMENT.md        # Esta guía
```

---

## 🔄 Actualización de Datos

### Automática (desde dashboard)

1. Abre el dashboard
2. Click en **"Actualizar Datos"**
3. Espera la confirmación

### Manual (vía API)

```bash
curl -X POST http://localhost:8080/api/refresh
```

### Programada (cron)

**Local:**
```bash
# Agregar a crontab
0 */6 * * * cd /path/to/APOLLO && python3 crm_engine.py
```

**Google Cloud:**
1. Crear Cloud Scheduler job
2. Configurar URL: `https://tu-app.run.app/api/refresh`
3. Método: POST
4. Frecuencia: `0 */6 * * *` (cada 6 horas)

---

## 🐛 Troubleshooting

### Error: "Port already in use"

```bash
# Matar proceso en puerto 8080
lsof -ti:8080 | xargs kill -9

# O usar otro puerto
PORT=8081 python3 crm_backend.py
```

### Error: "Module not found"

```bash
pip3 install -r requirements.txt
```

### Dashboard no carga datos

```bash
# Verificar que existe el archivo de datos
ls -lh crm_dashboard_data_full.json

# Regenerar si es necesario
python3 crm_engine.py
```

### Error de autenticación en Google Cloud

```bash
gcloud auth login
gcloud auth application-default login
```

---

## 💰 Costos Estimados (Google Cloud)

### Cloud Run (Recomendado)
- **Tier gratuito**: 2 millones de requests/mes
- **Después**: ~$0.40 por millón de requests
- **Memoria**: ~$2.40/mes (1GB siempre activo)
- **Estimado**: **$5-10/mes** para uso moderado

### App Engine
- **Tier gratuito**: 28 horas/día de instancia F1
- **Después**: ~$0.05/hora
- **Estimado**: **$10-20/mes**

### Recomendación
Usar **Cloud Run** para costos más bajos y mejor escalamiento automático.

---

## 🔐 Seguridad

### Producción

1. **Autenticación**: Agregar Cloud IAP o OAuth
2. **HTTPS**: Automático en Cloud Run
3. **Secrets**: Usar Secret Manager para API keys
4. **CORS**: Configurar dominios permitidos

### Implementar autenticación básica

Edita `crm_backend.py`:
```python
from functools import wraps
from flask import request

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth != 'Bearer tu_token_secreto':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/refresh', methods=['POST'])
@require_auth
def refresh_data():
    # ...
```

---

## 📞 Soporte

- **Issues**: Reportar en el repositorio
- **Documentación**: Este archivo
- **Logs**: `gcloud run logs read --service platam-crm-dashboard`

---

## 📝 Changelog

### v1.0.0 (2026-01-16)
- ✅ Dashboard profesional con diseño único
- ✅ 3 gráficas interactivas
- ✅ Botón de actualización funcional
- ✅ Backend Flask con API REST
- ✅ Deployment automático a Google Cloud
- ✅ Métricas de steps con conversión
- ✅ Timeline de observaciones
- ✅ Sincronización con Apollo API
