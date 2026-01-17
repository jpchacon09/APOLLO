#!/bin/bash
# Script de deployment a Google Cloud Run

set -e

PROJECT_ID=${1:-"platam-crm"}
REGION=${2:-"us-central1"}
SERVICE_NAME="platam-crm-dashboard"

echo "═══════════════════════════════════════════════════════════"
echo "  Deploying Platam CRM to Google Cloud Run"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# 1. Verificar gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI no está instalado"
    echo "   Instala desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# 2. Configurar proyecto
echo "📋 Configurando proyecto..."
gcloud config set project $PROJECT_ID

# 3. Habilitar APIs necesarias
echo "🔧 Habilitando APIs de Google Cloud..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 4. Build y deploy con Cloud Build
echo "🏗️  Construyendo imagen Docker..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 5. Deploy a Cloud Run
echo "🚀 Desplegando a Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 3 \
    --port 8080

# 6. Obtener URL
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Deployment completado!"
echo "═══════════════════════════════════════════════════════════"
echo ""
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "🌐 Tu CRM está disponible en:"
echo "   $SERVICE_URL"
echo ""
echo "📊 Dashboard: $SERVICE_URL"
echo "🔄 API Refresh: $SERVICE_URL/api/refresh"
echo "📈 Stats: $SERVICE_URL/api/stats"
echo ""
