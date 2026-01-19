# Usar imagen oficial de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos de la aplicación
COPY api_server.py .
COPY crm_engine.py .
COPY apollo_enrichment_v2.py .
COPY crm_dashboard_pro.html .
COPY TablaBase.csv .
COPY steps_apollo_resultado.csv .
COPY informacion.txt .

# Generar datos iniciales
RUN python crm_engine.py

# Crear directorio para datos
RUN mkdir -p /app/data

# Exponer puerto (Cloud Run usa PORT env variable)
ENV PORT=8080
EXPOSE 8080

# Comando de inicio
CMD uvicorn api_server:app --host 0.0.0.0 --port ${PORT}
