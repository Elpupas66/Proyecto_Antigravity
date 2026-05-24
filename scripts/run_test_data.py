import sys
import os

# Añade la ruta del proyecto actual para importar los módulos correctamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.data.fetcher.mt5_fetcher import MT5Fetcher
from trading.data.fetcher.yfinance_fetcher import YFinanceFetcher
from trading.utils.storage import DataStorage

def test_mt5():
    print("Iniciando prueba con MetaTrader 5...")
    try:
        mt5_fetcher = MT5Fetcher()
        # Puedes cambiar 'EURUSD' por un símbolo que estés seguro que tienes en tu MT5
        symbol = 'EURUSD'
        timeframe = 'H1'
        print(f"Descargando {symbol} en {timeframe}...")
        df = mt5_fetcher.fetch_historical_data(symbol, timeframe, 1000)
        print(df.head())
        print(df.tail())
        
        # Guardamos a formato Parquet
        storage = DataStorage("trading/data/raw")
        storage.save_parquet(df, symbol, timeframe)
    except Exception as e:
        print(f"Error con MT5: {e}")

def test_yfinance():
    print("\nIniciando prueba con Yahoo Finance...")
    try:
        yf_fetcher = YFinanceFetcher()
        symbol = 'AAPL' # Apple
        timeframe = 'D1'
        print(f"Descargando {symbol} en {timeframe}...")
        df = yf_fetcher.fetch_historical_data(symbol, timeframe, 500)
        print(df.head())
        print(df.tail())
        
        # Guardamos a formato Parquet
        storage = DataStorage("trading/data/raw")
        storage.save_parquet(df, symbol, timeframe)
    except Exception as e:
        print(f"Error con Yahoo Finance: {e}")

if __name__ == "__main__":
    print("--- INICIANDO DIAGNÓSTICO DE INGESTIÓN DE DATOS ---")
    test_mt5()
    test_yfinance()
    print("--- DIAGNÓSTICO FINALIZADO ---")
