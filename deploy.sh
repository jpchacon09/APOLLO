#!/bin/bash

# Script de deployment a Google Cloud Run
# Proyecto: platam-analytics

echo "🚀 Iniciando deployment a Google Cloud Run..."
echo ""

# Configurar proyecto
PROJECT_ID="platam-analytics"
SERVICE_NAME="platam-crm"
REGION="us-central1"

echo "📋 Configuración:"
echo "   Proyecto: $PROJECT_ID"
echo "   Servicio: $SERVICE_NAME"
echo "   Región: $REGION"
echo ""

# Autenticar (si es necesario)
echo "🔐 Verificando autenticación..."
gcloud auth list

echo ""
read -p "¿Continuar con el deployment? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Deployment cancelado"
    exit 1
fi

# Configurar proyecto
echo "⚙️  Configurando proyecto..."
gcloud config set project $PROJECT_ID

# Build y deploy
echo "🏗️  Building y deploying..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --platform managed

echo ""
echo "✅ Deployment completado!"
echo ""
echo "🌐 Tu CRM está disponible en:"
gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)'
