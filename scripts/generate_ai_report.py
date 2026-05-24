import sys
import os
import requests
import json
import pandas as pd
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# OLLAMA CONFIGURATION
OLLAMA_URL = "http://localhost:11434/api/generate"
# Usa el modelo de Ollama que tengas descargado para "análisis profundo"
MODEL = "gemma4:e4b" 

def generate_report():
    print("========================================")
    print(">> INICIANDO AGENTE ANALISTA DE RIESGOS >>")
    print("========================================\n")
    
    csv_file = Path("trading/results/matrix_scan.csv")
    
    if not csv_file.exists():
        print("Error: No se ha encontrado el archivo de resultados del Scanner. Ejecuta matrix_scanner.py primero.")
        return
        
    # Leemos la tabla
    df = pd.read_csv(csv_file)
    tabla_texto = df.to_markdown(index=False)
    
    print(f"-> Analizando resultados matemáticos de {len(df)} escenarios...")
    
    # Construimos el Prompt
    system_prompt = """
    Eres el "Analista de Riesgos Cuantitativo Jefe" de un fondo de inversión que utiliza una estrategia algorítmica llamada "Blacksheep Vortex" (un seguidor de tendencia puro basado en retrocesos que compra debilidad).
    Tu labor no es programar, tu labor es mirar tablas de resultados y escribir un informe ejecutivo claro, formal y directo al grano, que avise a los inversores sobre de qué mercados deben alejarse y dónde deben apostar su dinero con nuestra estrategia, según un balance entre WinRate elevado y buenas ganancias PNL.
    Formato deseado:
    1. Resumen Ejecutivo (Qué ha pasado al pasar nuestro escáner).
    2. El Mejor Entorno (Dónde invertir).
    3. Zonas de Peligro (De qué activos o temporalidades huir y por qué el modelo falla allí).
    """

    user_prompt = f"Por favor, redacta el informe evaluando esta matriz de resultados que acaba de arrojar nuestro laboratorio:\n\n{tabla_texto}"

    payload = {
        "model": MODEL,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False
    }
    
    print(f"-> Conectando con IA Local por Ollama ({MODEL})... Esto puede tardar según tu PC.\n")
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            reporte_texto = data.get("response", "No se generó respuesta.")
            
            output_path = Path("docs/reporte_ia_blacksheep.md")
            output_path.parent.mkdir(exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(reporte_texto)
                
            print(f"[EXITO] Tu Inteligencia Artificial ha redactado y guardado el informe en: {output_path}")
            
        else:
             print(f"Error HTTP del servidor Ollama. Código {response.status_code}")
             print(response.text)
             
    except requests.exceptions.ConnectionError:
        print("[ERROR] DE CONEXION CON OLLAMA.")
        print("1. Verifica que la aplicación local de Ollama está abierta y corriendo.")
        print('2. Abre tu símbolo de sistema (CMD) normal en Windows y escribe "ollama run gemma4:e4b" para asegurarte de que tienes el modelo.')
        

if __name__ == "__main__":
    generate_report()
