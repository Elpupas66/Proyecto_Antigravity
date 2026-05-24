import sys
import os
import pandas as pd
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.data.fetcher.mt5_fetcher import MT5Fetcher
from trading.utils.storage import DataStorage
from trading.strategies.bvortex_final import BlacksheepVortexStrategy

# NOTA: Los nombres exactos deben coincidir con tu Bróker de MT5. 
# Si tu bróker lo llama DAX40, DE40, o GER40, deberás escribir el string exacto.
SYMBOLS = [
    "EURUSD",
    "GBPUSD", 
    "GBPJPY", 
    "DE40",   # DAX40 suele ser DE40 o GER40 en muchos brokers
    "XTIUSD", # WTI Oil
]

# Timeframes menores sí funcionan para el Vortex si hay volatilidad
TIMEFRAMES = ["M15", "H1", "H4", "D1"]

def run_matrix_scanner():
    print("==============================================")
    print(">> ESCANER MULTIDIMENSIONAL DE ESTRATEGIA")
    print("==============================================\n")
    
    try:
        mt5 = MT5Fetcher()
    except Exception as e:
        print(f"Error grave conectando a MT5: {e}")
        return
        
    storage = DataStorage("trading/data/raw")
    
    # Parámetros Base que usamos siempre para no alterar el entorno
    strategy = BlacksheepVortexStrategy(vortex_period=14, extreme=-17.0, pullback_len=10, reward_ratio=0.8)
    
    results = []

    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            print(f"[{symbol} | {tf}] Procesando...")
            try:
                # 1. Intentar descargar si no existen los datos (10,000 velas para mayor muestra estadística)
                df_raw = mt5.fetch_historical_data(symbol, tf, n_bars=5000)
                storage.save_parquet(df_raw, symbol, tf)
                df = df_raw.copy()
            except Exception as e:
                print(f"   [FALLO] Descarga de {symbol} {tf}: {e}")
                continue
                
            # 2. Simulador
            try:
                _, df_trades = strategy.simulate(df)
            except Exception as e:
                print(f"   [FALLO] Simulacion: {e}")
                continue
                
            if df_trades.empty:
                 results.append({
                     "Symbol": symbol, "Timeframe": tf, "Trades": 0, "WinRate (%)": 0, "PNL": 0
                 })
                 continue
                 
            # 3. Métricas
            total = len(df_trades)
            wins = len(df_trades[df_trades['pnl'] > 0])
            wr = (wins / total) * 100
            pnl_total = df_trades['pnl'].sum()
            
            results.append({
                 "Symbol": symbol, 
                 "Timeframe": tf, 
                 "Trades": total, 
                 "WinRate (%)": round(wr, 2), 
                 "PNL": pnl_total
            })

    # Imprimir Tabla final
    df_results = pd.DataFrame(results)
    print("\n\n-- RESULTADOS MATRIZ:")
    print("====================================")
    
    # Ordenamos por Profit Total para ver los mejores ecosistemas
    df_results = df_results.sort_values(by="PNL", ascending=False)
    print(df_results.to_string(index=False))
    
    output_path = Path("trading/results/matrix_scan.csv")
    output_path.parent.mkdir(exist_ok=True)
    df_results.to_csv(output_path, index=False)
    print(f"\nArchivo guardado en: {output_path}")

if __name__ == "__main__":
    run_matrix_scanner()
