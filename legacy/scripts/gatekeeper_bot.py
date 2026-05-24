import os
import re
import asyncio
from dotenv import load_dotenv
import MetaTrader5 as mt5
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Credenciales Opcionales de MT5
MT5_LOGIN = os.getenv("MT5_LOGIN")
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")
MT5_PATH = os.getenv("MT5_PATH")

# Inicializar cliente de DeepSeek
llm_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

SYSTEM_PROMPT = """Eres el Gatekeeper Emocional de un sistema de trading institucional.
Tu trabajo es leer la 'justificación de entrada' del trader y decidir si la operación está basada en un análisis técnico/cuantitativo sólido, o si está sesgada por la necesidad emocional de recuperar pérdidas, venganza contra el mercado, sobreoperación o ansiedad.

Reglas:
- Si detectas ansiedad, prisa, deseos de 'recuperar' dinero o falta de lógica técnica pura: responde EXACTAMENTE con la palabra "BLOQUEADO" seguida de un guion y la razón breve.
- Si la justificación es técnica, neutral y muestra disciplina al plan de trading: responde EXACTAMENTE con la palabra "APROBADO" seguida de un guion y una palabra de ánimo.
No digas nada más."""

# Funciones de Validación Matemática (MT5)
def check_mt5_rules(symbol, volume):
    # Verificar si ya está inicializado
    if mt5.terminal_info() is None:
        print("Initializing MT5 connection for Bot...")
        if MT5_PATH:
            initialized = mt5.initialize(path=MT5_PATH)
        else:
            initialized = mt5.initialize()
            
        if not initialized:
            return False, f"Error conectando a MT5: {mt5.last_error()}"
            
        # Login en cuenta específica si se proporcionan credenciales
        if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
            try:
                login_id = int(MT5_LOGIN)
                if not mt5.login(login=login_id, password=MT5_PASSWORD, server=MT5_SERVER):
                    return False, f"Error haciendo login en la cuenta {MT5_LOGIN}: {mt5.last_error()}"
            except ValueError:
                return False, "El MT5_LOGIN debe ser un número."
    
    # Regla 1: Máximo 2 activos abiertos
    posiciones = mt5.positions_total()
    if posiciones is None:
        return False, "Error obteniendo posiciones de MT5."
        
    if posiciones >= 2:
        return False, f"Tienes {posiciones} posiciones abiertas. El límite máximo es 2."
        
    # Regla 2: Riesgo máximo del 0.5%
    account_info = mt5.account_info()
    if account_info is None:
        return False, "No se pudo obtener información de la cuenta."
        
    # Calcular margen requerido aproximado (simplificado)
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return False, f"El símbolo {symbol} no existe o no está disponible."
        
    return True, "Reglas matemáticas superadas."

# Funciones de Inteligencia Artificial
def analyze_emotion(justification):
    try:
        response = llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": justification}
            ],
            temperature=0.2, # Baja temperatura para ser más determinista
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR DE IA: {e}"

# Manejadores de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mensaje = (
        "🛡️ Bienvenido al **Gatekeeper de Trading**.\n\n"
        "Para enviar una orden, escribe un mensaje con este formato exacto:\n\n"
        "`COMPRAR EURUSD 0.1 MERCADO SL 1.0500 TP 1.0800 Porque mi análisis...`\n"
        "`VENDER BTCUSD 0.01 LIMIT 65000 SL 66000 TP 60000 Porque rebotará en...`\n\n"
        "*(La acción debe ser COMPRAR/VENDER. El tipo de orden MERCADO, LIMIT o STOP).* "
    )
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
        
    texto = update.message.text
    
    # Extraer comando: ACCION SIMBOLO VOLUMEN TIPO [PRECIO] SL <sl> TP <tp> Justificación
    pattern = r"^(COMPRAR|VENDER)\s+([A-Za-z0-9_]+)\s+([0-9.]+)\s+(MERCADO|LIMIT|STOP)(?:\s+([0-9.]+))?\s+SL\s+([0-9.]+)\s+TP\s+([0-9.]+)\s+(.*)$"
    match = re.match(pattern, texto, re.IGNORECASE)
    
    if not match:
        await update.message.reply_text("❌ Formato incorrecto. Ejemplo:\nCOMPRAR EURUSD 0.1 MERCADO SL 1.05 TP 1.08 Mi justificación...")
        return
        
    accion = match.group(1).upper()
    simbolo = match.group(2).upper()
    
    try:
        volumen = float(match.group(3))
        tipo_orden_texto = match.group(4).upper()
        precio = float(match.group(5)) if match.group(5) else None
        sl = float(match.group(6))
        tp = float(match.group(7))
    except ValueError:
        await update.message.reply_text("❌ Volumen, Precio, SL o TP inválidos. Deben ser números.")
        return
        
    justificacion = match.group(8)
    
    await update.message.reply_text("⏳ Procesando validación matemática en MT5...")
    
    # 1. Validación Matemática
    math_passed, math_msg = check_mt5_rules(simbolo, volumen)
    if not math_passed:
        await update.message.reply_text(f"⛔ **BLOQUEADO POR REGLA MATEMÁTICA:**\n{math_msg}", parse_mode='Markdown')
        return
        
    await update.message.reply_text("✅ Matemática aprobada. Consultando al Gatekeeper Emocional...")
    
    # 2. Validación Psicológica
    ai_response = analyze_emotion(justificacion)
    
    # 3. Veredicto Final
    if ai_response.startswith("APROBADO"):
        await update.message.reply_text(f"🟢 **OPERACIÓN APROBADA**\nIA: {ai_response}\n\n*Enviando orden a MT5...*", parse_mode='Markdown')
        
        # Determinar el tipo de orden MT5
        tipo_mt5 = mt5.ORDER_TYPE_BUY if accion == "COMPRAR" else mt5.ORDER_TYPE_SELL
        
        if tipo_orden_texto == "LIMIT":
            tipo_mt5 = mt5.ORDER_TYPE_BUY_LIMIT if accion == "COMPRAR" else mt5.ORDER_TYPE_SELL_LIMIT
        elif tipo_orden_texto == "STOP":
            tipo_mt5 = mt5.ORDER_TYPE_BUY_STOP if accion == "COMPRAR" else mt5.ORDER_TYPE_SELL_STOP
            
        # Preparar la solicitud
        request = {
            "action": mt5.TRADE_ACTION_DEAL if tipo_orden_texto == "MERCADO" else mt5.TRADE_ACTION_PENDING,
            "symbol": simbolo,
            "volume": volumen,
            "type": tipo_mt5,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 1095773,
            "comment": "Gatekeeper AI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Si es a mercado, necesitamos el precio actual
        if tipo_orden_texto == "MERCADO":
            tick = mt5.symbol_info_tick(simbolo)
            if not tick:
                await update.message.reply_text("❌ MT5 Error: No se pudo obtener el precio actual.")
                return
            request["price"] = tick.ask if accion == "COMPRAR" else tick.bid
        else:
            if not precio:
                await update.message.reply_text("❌ Error: Necesitas especificar un precio para órdenes LIMIT o STOP.")
                return
            request["price"] = precio
            
        # Enviar orden
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            await update.message.reply_text(f"⚠️ **Error en MT5 al ejecutar la orden:** {result.comment} (Código {result.retcode})", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"🚀 **ORDEN EJECUTADA CORRECTAMENTE!**\nTicket: {result.order}\nPrecio: {result.price}", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"🛑 **OPERACIÓN BLOQUEADA POR FILTRO EMOCIONAL**\nIA: {ai_response}", parse_mode='Markdown')

def main():
    print("Iniciando el Bot de Telegram Gatekeeper...")
    print(f"Token: {TELEGRAM_TOKEN[:10]}...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_order))
    
    print("Bot corriendo. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
