import MetaTrader5 as mt5
import pandas as pd
import sys
import os
from pathlib import Path

# Fix relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.data.fetcher.mt5_fetcher import MT5Fetcher
from trading.utils.storage import DataStorage
from trading.strategies.bvortex_final import BlacksheepVortexStrategy

def analyze_trend(df):
    """Analiza la tendencia principal basada en el gráfico diario (D1) usando cruce MAs y posición del precio"""
    if df.empty or len(df) < 200:
        return "Insuficientes datos para calcular SMA 200"
    
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    
    last_close = df['Close'].iloc[-1]
    last_sma50 = df['SMA50'].iloc[-1]
    last_sma200 = df['SMA200'].iloc[-1]
    
    if last_sma50 > last_sma200 and last_close > last_sma50:
        return "Alcista (Bullish)"
    elif last_sma50 < last_sma200 and last_close < last_sma50:
        return "Bajista (Bearish)"
    elif last_close > last_sma200:
        return "Consolidación a corto plazo, pero tendencia general Alcista"
    elif last_close < last_sma200:
        return "Consolidación a corto plazo, pero tendencia general Bajista"
    else:
        return "Lateral / Indefinida"

def run_asset_analysis():
    mt5.initialize()
    fetcher = MT5Fetcher()
    storage = DataStorage(str(Path("trading/data/raw").absolute()))
    
    assets = ['GER40', 'US500', 'EURGBP']
    timeframes = ['M5', 'M15', 'H1', 'H4', 'D1']
    results = []
    
    strategy = BlacksheepVortexStrategy(vortex_period=14, extreme=-17.0, pullback_len=10)
    
    for symbol in assets:
        print(f"\n--- Analizando: {symbol} ---")
        
        # Intentar con variantes comunes si no encuentra el simbolo
        check_symbol = symbol
        if not mt5.symbol_select(symbol, True):
            alt_symbols = {'GER40': 'GER40.', 'US500': 'US500.'}
            if symbol in alt_symbols and mt5.symbol_select(alt_symbols[symbol], True):
                check_symbol = alt_symbols[symbol]
                print(f"[{symbol} no encontrado. Usando {check_symbol}]")
            else:
                print(f"[{symbol} no encontrado en MT5]")
                continue
                
        # 1. Analizar D1
        try:
            # 5 años aprox en barras diarias = 1250 
            df_d1 = fetcher.fetch_historical_data(check_symbol, 'D1', 1500)
            storage.save_parquet(df_d1, check_symbol, 'D1')
            trend = analyze_trend(df_d1)
            print(f"Tendencia Principal ({check_symbol} D1): {trend}")
        except Exception as e:
            print(f"Error obteniendo D1 para {check_symbol}: {e}")
            continue
            
        # 2. Backtesting
        for tf in timeframes:
            try:
                n_bars_dict = {'M5': 30000, 'M15': 20000, 'H1': 10000, 'H4': 5000, 'D1': 2000}
                n_bars = n_bars_dict.get(tf, 5000) 
                df_tf = fetcher.fetch_historical_data(check_symbol, tf, n_bars)
                storage.save_parquet(df_tf, check_symbol, tf)
                
                df_processed, df_trades = strategy.simulate(df_tf)
                
                if not df_trades.empty:
                    wins = len(df_trades[df_trades['pnl'] > 0])
                    total = len(df_trades)
                    winrate = wins / total * 100
                    pnl_sum = df_trades['pnl'].sum()
                    
                    print(f"Backtest {tf}: {total} operaciones, WinRate {winrate:.1f}%, PnL Total: {pnl_sum:.2f}")
                    results.append({'Asset': check_symbol, 'TF': tf, 'Trades': total, 'WinRate': winrate, 'PnL': pnl_sum})
                else:
                    print(f"Backtest {tf}: 0 operaciones")
                    results.append({'Asset': check_symbol, 'TF': tf, 'Trades': 0, 'WinRate': 0.0, 'PnL': 0.0})
                    
            except Exception as e:
                print(f"Error en backtest {check_symbol} {tf}: {e}")

    mt5.shutdown()
    
    print("\n--- RESUMEN MEJORES TEMPORALIDADES ---")
    df_res = pd.DataFrame(results)
    if not df_res.empty:
        print(df_res.sort_values(by='WinRate', ascending=False))

if __name__ == '__main__':
    run_asset_analysis()
