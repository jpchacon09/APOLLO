#!/usr/bin/env python3
"""
Platam CRM API Server
FastAPI backend para servir datos del CRM y sincronizar con Apollo
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import json
import subprocess
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Platam CRM API", version="1.0.0")

# CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de archivos
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "crm_dashboard_data_full.json"
ENGINE_SCRIPT = BASE_DIR / "crm_engine.py"
SYNC_SCRIPT = BASE_DIR / "apollo_super_sync.py"

# Estado de sincronización
sync_status = {
    "is_syncing": False,
    "last_sync": None,
    "last_error": None
}

@app.get("/")
async def root():
    """Servir el dashboard HTML"""
    return FileResponse(BASE_DIR / "crm_dashboard_pro.html")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_file_exists": DATA_FILE.exists()
    }

@app.get("/api/dashboard/data")
async def get_dashboard_data():
    """Obtener datos del dashboard"""
    try:
        if not DATA_FILE.exists():
            # Generar datos si no existen
            import sys
            result = subprocess.run([
                sys.executable,  # Usar el Python actual en lugar de ruta hardcodeada
                str(ENGINE_SCRIPT)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"Error generando datos: {result.stderr}")
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Archivo no encontrado: {str(e)}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout generando datos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.post("/api/sync/apollo")
async def trigger_apollo_sync(background_tasks: BackgroundTasks, limit: int = 20):
    """Iniciar sincronización con Apollo en background"""
    if sync_status["is_syncing"]:
        return {
            "status": "already_syncing",
            "message": "Ya hay una sincronización en progreso"
        }
    
    background_tasks.add_task(run_apollo_sync, limit)
    
    return {
        "status": "started",
        "message": f"Sincronización iniciada para {limit} contactos",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sync/status")
async def get_sync_status():
    """Obtener estado de la sincronización"""
    return sync_status

@app.post("/api/data/regenerate")
async def regenerate_data():
    """Regenerar datos del dashboard"""
    try:
        import sys
        result = subprocess.run([
            sys.executable,
            str(ENGINE_SCRIPT)
        ], capture_output=True, text=True, check=True, timeout=30)
        
        return {
            "status": "success",
            "message": "Datos regenerados correctamente",
            "timestamp": datetime.now().isoformat(),
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error regenerando datos: {e.stderr}"
        )

async def run_apollo_sync(limit: int):
    """Ejecutar sincronización de Apollo en background"""
    sync_status["is_syncing"] = True
    sync_status["last_error"] = None
    
    try:
        import sys
        # Ejecutar script de sincronización
        result = subprocess.run([
            sys.executable,
            str(SYNC_SCRIPT)
        ], capture_output=True, text=True, timeout=300)
        
        # Regenerar datos del dashboard
        subprocess.run([
            sys.executable,
            str(ENGINE_SCRIPT)
        ], check=True, timeout=30)
        
        sync_status["last_sync"] = datetime.now().isoformat()
        
    except Exception as e:
        sync_status["last_error"] = str(e)
    finally:
        sync_status["is_syncing"] = False

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
