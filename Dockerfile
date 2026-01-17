# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY crm_backend.py .
COPY crm_pro.html .
COPY crm_engine.py .
COPY TablaBase.csv .
COPY crm_dashboard_data_full.json .
COPY apollo_sync_v3.py .
COPY steps_apollo_resultado.csv .

# Expose port
EXPOSE 8080

# Set environment variable
ENV PORT=8080

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "crm_backend:app"]
