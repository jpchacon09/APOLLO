# Platam CRM - Deployment Guide

## 🚀 Arquitectura Profesional

### Stack Tecnológico:
- **Backend**: FastAPI (Python)
- **Frontend**: HTML5 + Vanilla JS + Chart.js
- **Data Engine**: Python scripts con pandas
- **API Integration**: Apollo.io REST API

---

## 📦 Estructura del Proyecto

```
/Users/jpchacon/Prospeccion/
├── api_server.py              # FastAPI backend server
├── crm_dashboard_pro.html     # Dashboard frontend (conectado a API)
├── crm_engine.py              # Motor de generación de KPIs
├── apollo_super_sync.py       # Sincronización con Apollo
├── TablaBase.csv              # Base de datos principal
├── crm_dashboard_data_full.json  # Datos procesados
└── requirements.txt           # Dependencias Python
```

---

## 🏃 Ejecutar en Local

### 1. Iniciar el servidor API:
```bash
cd /Users/jpchacon/Prospeccion
/Users/jpchacon/anaconda3/bin/python3 api_server.py
```

El servidor estará disponible en: **http://localhost:8000**

### 2. Abrir el dashboard:
Navega a: **http://localhost:8000**

### 3. Endpoints disponibles:
- `GET /` - Dashboard HTML
- `GET /api/health` - Health check
- `GET /api/dashboard/data` - Obtener datos del CRM
- `POST /api/data/regenerate` - Regenerar KPIs
- `POST /api/sync/apollo` - Sincronizar con Apollo
- `GET /api/sync/status` - Estado de sincronización

---

## ☁️ Deployment a Google Cloud

### Opción 1: Cloud Run (Recomendada - Serverless)

#### Paso 1: Crear Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar archivos
COPY requirements.txt .
COPY api_server.py .
COPY crm_engine.py .
COPY apollo_super_sync.py .
COPY crm_dashboard_pro.html .
COPY TablaBase.csv .
COPY informacion.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto
EXPOSE 8080

# Comando de inicio
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Paso 2: Crear requirements.txt
```txt
fastapi==0.119.0
uvicorn==0.37.0
pandas==2.0.3
requests==2.31.0
```

#### Paso 3: Deploy a Cloud Run
```bash
# Autenticar
gcloud auth login

# Configurar proyecto
gcloud config set project YOUR_PROJECT_ID

# Build y deploy
gcloud run deploy platam-crm \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

### Opción 2: App Engine (Más simple)

#### Crear app.yaml:
```yaml
runtime: python311
entrypoint: uvicorn api_server:app --host 0.0.0.0 --port $PORT

instance_class: F1

automatic_scaling:
  min_instances: 0
  max_instances: 2
```

#### Deploy:
```bash
gcloud app deploy
```

---

## 🔄 Sincronización Automática

### Configurar Cloud Scheduler (para sync periódico):

```bash
# Crear job que sincroniza cada hora
gcloud scheduler jobs create http apollo-sync \
  --schedule="0 * * * *" \
  --uri="https://YOUR_APP_URL/api/sync/apollo" \
  --http-method=POST \
  --location=us-central1
```

---

## 🔐 Seguridad

### Variables de Entorno (para producción):
```bash
export APOLLO_API_KEY="your_key_here"
export ENVIRONMENT="production"
```

Modificar `api_server.py` para leer desde env:
```python
import os
APOLLO_API_KEY = os.getenv('APOLLO_API_KEY', '_KzNd14cLtj4Mpjj7RsJJw')
```

---

## 📊 Monitoreo

### Cloud Logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Health Check Endpoint:
Ya incluido en `/api/health`

---

## 💰 Estimación de Costos (Google Cloud)

### Cloud Run:
- **Requests**: Primeros 2M gratis/mes
- **Compute**: $0.00002400/vCPU-second
- **Memory**: $0.00000250/GiB-second
- **Estimado mensual**: $5-15 USD (uso moderado)

### App Engine:
- **F1 Instance**: ~$0.05/hora
- **Estimado mensual**: $36 USD (24/7)

---

## 🎯 Próximos Pasos

1. ✅ Probar localmente
2. ⬜ Crear Dockerfile
3. ⬜ Deploy a Cloud Run
4. ⬜ Configurar dominio personalizado
5. ⬜ Agregar autenticación (opcional)
6. ⬜ Configurar Cloud Scheduler para sync automático

---

## 📞 Soporte

Para dudas sobre deployment, consultar:
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
