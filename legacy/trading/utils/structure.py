import pandas as pd
import numpy as np

def identify_market_structure(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Escanea la Estructura de Mercado basándose en Pivotes (Máximos y Mínimos locales).
    Retorna 1 si tenemos Altos Crecientes (AC) y Bajos Crecientes (BC) (Tendencia Alcista).
    Retorna -1 si tenemos Altos Decrecientes (AD) y Bajos Decrecientes (BD) (Tendencia Bajista).
    """
    out = df.copy()
    
    highs = out['High'].values
    lows = out['Low'].values
    length = len(out)
    
    pivot_h = np.full(length, np.nan)
    pivot_l = np.full(length, np.nan)
    
    # Identificación local
    for i in range(window, length - window):
        chunk_high = highs[i - window : i + window + 1]
        chunk_low = lows[i - window : i + window + 1]
        if highs[i] == max(chunk_high):
            pivot_h[i] = highs[i]
        if lows[i] == min(chunk_low):
            pivot_l[i] = lows[i]
            
    out['pivot_high'] = pivot_h
    out['pivot_low'] = pivot_l
    
    # Rellenar con los últimos pivotes conocidos
    out['last_h'] = out['pivot_high'].ffill()
    out['last_l'] = out['pivot_low'].ffill()
    
    # Detectar el último AC o AD
    h_series = out['last_h'].dropna().drop_duplicates()
    h_trend = h_series.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    out['h_trend'] = h_trend
    out['h_trend'] = out['h_trend'].ffill()
    
    # Detectar el último BC o BD
    l_series = out['last_l'].dropna().drop_duplicates()
    l_trend = l_series.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    out['l_trend'] = l_trend
    out['l_trend'] = out['l_trend'].ffill()
    
    out['market_structure'] = 0
    # Alcista = AC y BC
    out.loc[(out['h_trend'] == 1) & (out['l_trend'] == 1), 'market_structure'] = 1
    # Bajista = AD y BD
    out.loc[(out['h_trend'] == -1) & (out['l_trend'] == -1), 'market_structure'] = -1
    
    out['market_structure'] = out['market_structure'].ffill().fillna(0)
    
    return out
