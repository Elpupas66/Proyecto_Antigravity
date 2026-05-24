from __future__ import annotations

import pandas as pd
import sys
import os
from pathlib import Path

# Añadimos el PATH para que module imports funcionen bien
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.utils.storage import DataStorage
from trading.strategies.bvortex_final import BlacksheepVortexStrategy

def run_backtest(symbol: str, timeframe: str) -> None:
    print(f"=== INICIANDO BACKTEST PARA {symbol} EN {timeframe} ===")
    
    # 1. Cargar datos locales de nuestro motor de extracción
    base_path = Path(__file__).parent.parent
    storage = DataStorage(str((base_path / "trading" / "data" / "raw").absolute()))
    try:
        df = storage.load_parquet(symbol, timeframe)
    except FileNotFoundError:
        print(f"Error: No se encontraron datos para {symbol}_{timeframe}. ¡Extrae los datos primero usando run_test_data.py!")
        return
        
    print(f"Datos cargados exitosamente: {len(df)} velas.")

    # 2. Inicializar Estrategia
    strategy = BlacksheepVortexStrategy(vortex_period=14, extreme=-17.0, pullback_len=10, reward_ratio=0.8)
    
    print("Simulando estrategia Blacksheep...")
    df_processed, df_trades = strategy.simulate(df)
    
    # 3. Mostrar Resultados Financieros y Estadísticos
    if df_trades.empty:
        print("El backtest no arrojó ninguna operación. El mercado no cumplió una estructura tan estricta en este periodo.")
    else:
        print("\n=== RENDIMIENTO DE ESTRATEGIA: BVORTEX ===")
        total_trades = len(df_trades)
        wins = len(df_trades[df_trades['pnl'] > 0])
        losses = len(df_trades[df_trades['pnl'] < 0])
        winrate = (wins / total_trades) * 100 if total_trades > 0 else 0
        
        print(f"Total Operaciones Cerradas: {total_trades}")
        print(f"Ganadoras (TP 1:1): {wins}")
        print(f"Perdedoras (SL): {losses}")
        print(f"WinRate Global: {winrate:.2f}%")
        
        output_trades = (base_path / "trading" / "results" / "bvortex_historical_trades.csv").absolute()
        output_trades.parent.mkdir(parents=True, exist_ok=True)
        df_trades.to_csv(output_trades, index=False)
        print(f"\nLista detallada de operaciones exportada a: {output_trades}")

if __name__ == "__main__":
    # Testearemos con EURUSD H1 que es lo que descargamos antes 
    run_backtest("EURUSD", "H1")