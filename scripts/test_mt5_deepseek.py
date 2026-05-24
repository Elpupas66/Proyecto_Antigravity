import os
import MetaTrader5 as mt5
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def test_deepseek_connection():
    print("--- Probando conexión a DeepSeek ---")
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "sk-tu-clave-api-aqui":
        print("❌ Error: No se ha configurado DEEPSEEK_API_KEY en el archivo .env")
        return False
        
    try:
        # DeepSeek usa una API compatible con OpenAI
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
        
        print("⏳ Enviando mensaje de prueba al LLM...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Eres un asistente de pruebas."},
                {"role": "user", "content": "Responde únicamente con la palabra: CONECTADO."}
            ],
            max_tokens=10
        )
        respuesta_llm = response.choices[0].message.content.strip()
        print(f"✅ Respuesta recibida: {respuesta_llm}")
        return True
    except Exception as e:
        print(f"❌ Error al conectar con DeepSeek: {e}")
        return False

def test_mt5_connection():
    print("\n--- Probando conexión a MetaTrader 5 ---")
    # Intentar inicializar MT5
    if not mt5.initialize():
        print("❌ Error: No se pudo inicializar MetaTrader 5.")
        print(f"Código de error: {mt5.last_error()}")
        return False
        
    # Obtener información de la terminal
    terminal_info = mt5.terminal_info()
    if terminal_info != None:
        print("✅ Conectado a MetaTrader 5 con éxito.")
        print(f"Broker: {mt5.account_info().company}")
        print(f"Servidor: {mt5.account_info().server}")
        print(f"Saldo de la cuenta: {mt5.account_info().balance} {mt5.account_info().currency}")
        
        # Consultar posiciones abiertas
        posiciones = mt5.positions_total()
        print(f"Activos abiertos actualmente: {posiciones}")
    else:
        print("❌ No se pudo obtener información de la terminal.")
        
    # Cerrar conexión al terminar
    mt5.shutdown()
    return True

if __name__ == "__main__":
    print("Iniciando pruebas de las herramientas de apoyo para el Gatekeeper...\n")
    test_deepseek_connection()
    test_mt5_connection()
    print("\nFin de las pruebas.")
