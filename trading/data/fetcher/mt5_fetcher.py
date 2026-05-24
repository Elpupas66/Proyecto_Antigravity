import pandas as pd
import MetaTrader5 as mt5
from .base_fetcher import BaseFetcher

class MT5Fetcher(BaseFetcher):
    """
    Conector local a la terminal de MetaTrader 5.
    (La terminal debe estar abierta y logeada a una cuenta en Windows).
    """

    TIMEFRAMES = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1
    }

    def __init__(self):
        # Intentamos iniciar conexión con el terminal en segundo plano
        if not mt5.initialize():
            raise ConnectionError(f"Error al conectar con la terminal de MT5. Error code: {mt5.last_error()}")

    def fetch_historical_data(self, symbol: str, timeframe: str, n_bars: int) -> pd.DataFrame:
        if timeframe not in self.TIMEFRAMES:
            raise ValueError(f"Timeframe {timeframe} no reconocido en MT5.")
            
        # Comprobar que el símbolo está en el Market Watch
        if not mt5.symbol_select(symbol, True):
            raise ValueError(f"Símbolo {symbol} no encontrado o no autorizado en tu bróker de MT5.")

        tf_code = self.TIMEFRAMES[timeframe]
        
        # Función ultra rápida en C++ nativo de MT5 para extraer M velas hacia atrás
        rates = mt5.copy_rates_from_pos(symbol, tf_code, 0, n_bars)
        
        if rates is None or len(rates) == 0:
            raise ValueError(f"Devolvió 0 datos para {symbol}. Revisa si el símbolo tiene histórico.")
            
        # Parseo a DataFrame de Pandas
        df = pd.DataFrame(rates)
        
        # MT5 entrega el tiempo Unix en segundos
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        df.rename(columns={
            'time': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume'
        }, inplace=True)
        
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        return df

    def __del__(self):
        # Desconectar memoria al finalizar
        mt5.shutdown()
