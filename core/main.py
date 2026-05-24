from fastapi import FastAPI, Depends, HTTPException
from core.database import SessionLocal, engine
from core.models import TradeState
from core.settings import settings, validate_execution_safety
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

app = FastAPI(
    title="Antigravity Core API",
    description="Orquestador central para trading asistido por IA",
    version="1.1.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint básico para verificar que el Core arranca y funciona,
    incluyendo el estado de la base de datos y los candados de seguridad.
    """
    # Verificar conexión a base de datos
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "ok",
        "service": "antigravity_core",
        "message": "Sistema operativo.",
        "security_locks": {
            "environment": settings.environment,
            "real_execution_allowed": settings.allow_real_execution,
            "approval_required": settings.require_approval
        },
        "database_status": db_status
    }

if __name__ == "__main__":
    import uvicorn
    # Validamos al arrancar
    try:
        validate_execution_safety()
    except Exception as e:
        logging.warning(f"Advertencia de inicio: {str(e)}")
        
    uvicorn.run("core.main:app", host="127.0.0.1", port=8000, reload=True)
