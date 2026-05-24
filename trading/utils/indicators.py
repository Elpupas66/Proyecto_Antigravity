from __future__ import annotations
import pandas as pd

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["High"] - df["Low"]
    high_prev_close = (df["High"] - df["Close"].shift(1)).abs()
    low_prev_close = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calculate_classic_vortex(df: pd.DataFrame, period: int = 14, scaler: float = 100.0) -> pd.DataFrame:
    out = df.copy()
    
    # True Range
    high_low = out["High"] - out["Low"]
    high_prev_close = (out["High"] - out["Close"].shift(1)).abs()
    low_prev_close = (out["Low"] - out["Close"].shift(1)).abs()
    tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
    
    # Vortex Movements
    vm_plus = (out['High'] - out['Low'].shift(1)).abs()
    vm_minus = (out['Low'] - out['High'].shift(1)).abs()
    
    # Sum over period
    tr_sum = tr.rolling(window=period).sum()
    vm_plus_sum = vm_plus.rolling(window=period).sum()
    vm_minus_sum = vm_minus.rolling(window=period).sum()
    
    # Vortex Indicators
    vi_plus = vm_plus_sum / tr_sum.replace(0, 1)
    vi_minus = vm_minus_sum / tr_sum.replace(0, 1)
    
    # Vortex histogram: (vi_plus - vi_minus) * scaler
    vortex_val = (vi_plus - vi_minus) * scaler
    out['BVortex'] = vortex_val.fillna(0)
    
    return out

def calculate_macd_vortex(df: pd.DataFrame, fast=6, slow=13, signal=5, atr_len=50, scaler=100) -> pd.DataFrame:
    """
    Implementación exacta del 'Vortex Patxi' (MACD normalizado por ATR).
    Genera el histograma que avisa de sobreventa en pullbacks.
    """
    out = df.copy()
    
    # EMAs
    fast_ma = out['Close'].ewm(span=fast, adjust=False).mean()
    slow_ma = out['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = fast_ma - slow_ma
    
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    raw_hist = macd_line - signal_line
    
    atr_val = calculate_atr(out, atr_len)
    
    # Vortex histogram: (raw_hist / atr) * 100
    # Lidiamos con división por cero
    vortex_val = (raw_hist / atr_val.replace(0, 1)) * scaler
    out['BVortex'] = vortex_val.fillna(0)
    
    return out