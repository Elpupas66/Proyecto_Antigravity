import sys
import os
import pandas as pd
import optuna
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.utils.storage import DataStorage
from trading.strategies.bvortex_final import BlacksheepVortexStrategy

# Variables Globales (Para no recargar el CSV en cada iteración)
GLOBAL_DF = None

def objective(trial):
    """
    La función que Optuna intentará maximizar. Busca la configuración más rentable.
    """
    # 1. Parámetros que la Inteligencia de Enjambre va a probar:
    # ¿De verdad el extremo institucional es -17 o es un mito y funciona mejor si exigimos -25?
    extreme_val = trial.suggest_float("extreme", -30.0, -10.0, step=0.5)
    
    # ¿Qué periodo de Vortex Clásico funciona mejor? Probamos de 7 a 28.
    vortex_period = trial.suggest_int("vortex_period", 7, 28, step=1)
    
    # ¿El pullback debe ser el mínimo de 10 velas obligatoriamente o vale con 5?
    pullback_window = trial.suggest_int("pullback_len", 5, 20, step=1)
    
    # ¿El ratio 1:0.8 es óptimo o puede ser mejor 1:0.6 o 1:1.0?
    reward_ratio = trial.suggest_float("reward_ratio", 0.5, 1.2, step=0.1)
    
    # Init robot
    strategy = BlacksheepVortexStrategy(
        vortex_period=vortex_period,
        extreme=extreme_val,
        pullback_len=pullback_window,
        reward_ratio=reward_ratio
    )
    
    # Simulamos
    _, df_trades = strategy.simulate(GLOBAL_DF.copy())
    
    # 2. MÉTRICA DE CASTIGO (Función de pérdida)
    # Queremos que busque rentabilidad bruta, pero no un sistema que solo abre 1 operación y la gana
    if df_trades.empty or len(df_trades) < 10:
        return -100.0 # Castigamos severamente si no da suficientes señales
        
    wins = len(df_trades[df_trades['pnl'] > 0])
    total = len(df_trades)
    win_rate = wins / total
    
    # Recompensa a nuestro algoritmo si sube del 50%
    # Penalty combinado por PNL total y un WinRate sólido.
    profit_factor = df_trades['pnl'].sum()
    
    # La salida final es lo que dictamina la supervivencia del "gen" algorítmico 
    return profit_factor

def optimize(symbol: str, timeframe: str, n_trials: int = 50):
    global GLOBAL_DF
    print(f"--- Iniciando Búsqueda Genética: {symbol} - {timeframe} ---")
    
    storage = DataStorage(str(Path("trading/data/raw").absolute()))
    try:
        GLOBAL_DF = storage.load_parquet(symbol, timeframe)
    except FileNotFoundError:
        print("Datos no encontrados. Descarga datos antes de optimizar.")
        return
        
    # Inicializamos Optuna
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)
    
    # Resultados
    print("\n===============================")
    print("[TROFEO] LA MEJOR CONFIGURACION ENCONTRADA")
    print("===============================")
    print(f"Rendimiento Brutal (Score PNL): {study.best_value}")
    print("Mueve tu TradingView a estos valores:")
    for key, value in study.best_trial.params.items():
        print(f"  - {key}: {value}")
        
if __name__ == "__main__":
    optimize("EURUSD", "H1", n_trials=50)
