import os
import MetaTrader5 as mt5
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from pydantic import BaseModel
from typing import Optional, Union, List
from dotenv import load_dotenv
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GatekeeperAPI")

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad básica
API_KEY_LOCAL = os.getenv("GATEKEEPER_API_KEY", "antigravity-secure-key-2024")

# Credenciales de MT5
MT5_LOGIN = os.getenv("MT5_LOGIN")
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")
MT5_PATH = os.getenv("MT5_PATH")

app = FastAPI(title="Gatekeeper MT5 Bridge API")

# Modelos de datos
class OrderRequest(BaseModel):
    action: str  # COMPRAR / VENDER
    symbol: str
    volume: float
    order_type: str # MERCADO / LIMIT / STOP
    price: Optional[float] = None
    sl: float
    tp: float
    justification: Optional[str] = None  # Añadido para que no se pierda en n8n
    chat_id: Optional[int] = None        # Añadido para trazabilidad

# Dependencia para verificar API Key
async def verify_api_key(x_api_key: str = Header(...)):
    # Normalización ultra-robusta
    received = x_api_key.strip().replace(" ", "-").lower()
    local = API_KEY_LOCAL.strip().replace(" ", "-").lower()
    
    logger.info(f"API Key check: received='{received}', local='{local}'")
    
    if received != local:
        logger.warning(f"Invalid API Key attempt. Received: {received}")
        raise HTTPException(status_code=403, detail="Invalid API Key")

def init_mt5():
    """Inicializa la conexión a MT5 de forma persistente"""
    try:
        if mt5.terminal_info() is not None:
            return True, "MT5 already connected"
    except Exception:
        pass
        
    logger.info("Initializing MT5 connection...")
    if MT5_PATH:
        initialized = mt5.initialize(path=MT5_PATH)
    else:
        initialized = mt5.initialize()
        
    if not initialized:
        return False, f"Error conectando a MT5: {mt5.last_error()}"
        
    if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
        login_id = int(MT5_LOGIN)
        if not mt5.login(login=login_id, password=MT5_PASSWORD, server=MT5_SERVER):
            return False, f"Error login MT5: {mt5.last_error()}"
            
    logger.info("MT5 Ready and Logged in")
    return True, "MT5 Ready"

@app.on_event("startup")
async def startup_event():
    success, msg = init_mt5()
    if not success:
        logger.error(f"Startup MT5 Error: {msg}")
    else:
        logger.info("Application started with MT5 connection active")

@app.on_event("shutdown")
async def shutdown_event():
    mt5.shutdown()
    logger.info("MT5 connection closed")

@app.get("/health")
def health():
    success, msg = init_mt5()
    connected = False
    try:
        connected = mt5.terminal_info() is not None
    except:
        pass
    return {"status": "ok" if success else "error", "message": msg, "mt5_connected": connected}

@app.post("/validate", dependencies=[Depends(verify_api_key)])
async def validate_rules(request: Request):
    # Soporte para n8n: Extraer el primer elemento si es una lista o el campo 'body' si existe
    try:
        body = await request.json()
        logger.info(f"Received payload: {body}")
        
        # Desenvolver lista
        if isinstance(body, list) and len(body) > 0:
            data = body[0]
        else:
            data = body
            
        # Desenvolver objeto 'body' de n8n si existe
        if isinstance(data, dict) and "body" in data and isinstance(data["body"], dict):
            data = data["body"]
            
        order = OrderRequest(**data)
    except Exception as e:
        logger.error(f"Payload Error: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid payload format: {e}")

    logger.info(f"Validating rules for {order.symbol}...")
    success, msg = init_mt5()
    if not success:
        raise HTTPException(status_code=500, detail=msg)
        
    # Regla 1: Máximo 2 activos abiertos
    posiciones = mt5.positions_total()
    if posiciones is None:
        raise HTTPException(status_code=500, detail="Error obteniendo posiciones de MT5")
        
    if posiciones >= 2:
        return {"passed": False, "reason": f"Límite excedido: {posiciones} posiciones abiertas."}
        
    # Regla 2: Stop Loss obligatorio
    if order.sl == 0:
        return {"passed": False, "reason": "El Stop Loss es obligatorio."}

    logger.info("Validation PASSED")
    return {
        "passed": True, 
        "message": "Validación matemática superada.",
        "order": order  # Devolvemos la orden para que n8n la use en el siguiente paso
    }

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_order(request: Request):
    try:
        body = await request.json()
        
        # Desenvolver lista
        if isinstance(body, list) and len(body) > 0:
            data = body[0]
        else:
            data = body
            
        # Desenvolver objeto 'body' de n8n si existe
        if isinstance(data, dict) and "body" in data and isinstance(data["body"], dict):
            data = data["body"]
            
        order = OrderRequest(**data)
    except Exception as e:
        logger.error(f"Payload Error: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid payload format: {e}")

    logger.info(f"EXECUTING ORDER for {order.symbol}...")
    success, msg = init_mt5()
    if not success:
        raise HTTPException(status_code=500, detail=msg)
        
    # Determinar tipo MT5
    tipo_mt5 = mt5.ORDER_TYPE_BUY if order.action == "COMPRAR" else mt5.ORDER_TYPE_SELL
    
    if order.order_type == "LIMIT":
        tipo_mt5 = mt5.ORDER_TYPE_BUY_LIMIT if order.action == "COMPRAR" else mt5.ORDER_TYPE_SELL_LIMIT
    elif order.order_type == "STOP":
        tipo_mt5 = mt5.ORDER_TYPE_BUY_STOP if order.action == "COMPRAR" else mt5.ORDER_TYPE_SELL_STOP
        
    # Preparar solicitud
    trade_request = {
        "action": mt5.TRADE_ACTION_DEAL if order.order_type == "MERCADO" else mt5.TRADE_ACTION_PENDING,
        "symbol": order.symbol,
        "volume": order.volume,
        "type": tipo_mt5,
        "sl": order.sl,
        "tp": order.tp,
        "deviation": 20,
        "magic": 1095773,
        "comment": "Gatekeeper n8n",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    if order.order_type == "MERCADO":
        tick = mt5.symbol_info_tick(order.symbol)
        if not tick:
            return {"success": False, "error": f"Símbolo {order.symbol} no encontrado."}
        trade_request["price"] = tick.ask if order.action == "COMPRAR" else tick.bid
    else:
        if not order.price:
            return {"success": False, "error": "Precio requerido para orden pendiente."}
        trade_request["price"] = order.price
        
    logger.info(f"DEBUG: Trade Request to MT5: {trade_request}")
    
    result = mt5.order_send(trade_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"MT5 Order Failed: {result.comment}")
        return {"success": False, "error": f"{result.comment} ({result.retcode})"}
    
    logger.info(f"Order executed: {result.order}")
    return {
        "success": True, 
        "ticket": result.order, 
        "price": result.price,
        "message": "Orden ejecutada con éxito"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
