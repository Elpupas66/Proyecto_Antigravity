import pandas as pd
import yfinance as yf
from .base_fetcher import BaseFetcher

class YFinanceFetcher(BaseFetcher):
    """
    Conector gratuito usando la API pública de Yahoo Finance.
    Ideal para D1 y H1 en mercado de acciones tradicionales, ETFs y algunos índices.
    """
    
    # Mapeo limitado a los periodos interdiarios y diarios
    TIMEFRAMES = {
        'M5': '5m',
        'M15': '15m',
        'H1': '1h',
        'H4': '1h', # Yahoo no tiene H4 nativo, usamos H1 o D1 por lo general
        'D1': '1d'
    }

    def fetch_historical_data(self, symbol: str, timeframe: str, n_bars: int) -> pd.DataFrame:
        if timeframe not in self.TIMEFRAMES:
            raise ValueError(f"Timeframe {timeframe} no soportado por YFinance. Usa: {list(self.TIMEFRAMES.keys())}")
            
        tf = self.TIMEFRAMES[timeframe]
        ticker = yf.Ticker(symbol)
        
        # yfinance restringe el máximo histórico según el timeframe:
        # 1m = 7d, interdiario (5m, 1h) = 60d a 730d.
        period = "730d" if timeframe == 'D1' else "60d"
        
        # Descargamos los datos
        df = ticker.history(period=period, interval=tf)
        
        if df.empty:
             raise ValueError(f"No se obtuvieron datos de Yahoo Finance para el símbolo {symbol}")
             
        # yfinance devuelve el índice como la fecha
        df.reset_index(inplace=True)
        
        # Dependiendo del timeframe, devuelve 'Date' o 'Datetime'
        date_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
        
        df.rename(columns={
            date_col: 'Date',
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        }, inplace=True)
        
        # Estandarizamos limpiando las zonas horarias
        df['Date'] = pd.to_datetime(df['Date'])
        if df['Date'].dt.tz is not None:
            df['Date'] = df['Date'].dt.tz_localize(None)
            
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Devolvemos solo la cantidad solicitada (n_bars) contando desde el más reciente
        return df.tail(n_bars).reset_index(drop=True)
