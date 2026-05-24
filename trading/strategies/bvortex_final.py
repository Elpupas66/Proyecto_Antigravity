from __future__ import annotations
import pandas as pd

from trading.utils.structure import identify_market_structure
from trading.utils.indicators import calculate_macd_vortex

class BlacksheepVortexStrategy:
    """
    Simulador que reproduce las lógicas institucionales marcadas por la academia:
    Estructura MD + Vortex(oscilador) Extremo + Patrón Color/V + Stop Orders + Anulación.
    """
    def __init__(self, vortex_period=14, extreme=-17.0, pullback_len=10, reward_ratio=0.8):
        self.vortex_period = vortex_period
        self.extreme = extreme
        self.pullback_len = pullback_len
        self.reward_ratio = reward_ratio

    def simulate(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        # 1. Calcular indicadores y estructura base
        # Nota: Usamos window=15 para imitar detección de pivotes grandes y evitar operar en ruido
        df = identify_market_structure(df, window=15)
        df = calculate_macd_vortex(df, fast=6, slow=13, signal=5, atr_len=50, scaler=100)
        
        # 2. Calcular los históricos del histograma para detectar si tocó el extremo
        df['hist'] = df['BVortex']
        df['lowest_hist'] = df['hist'].rolling(self.pullback_len).min()
        df['highest_hist'] = df['hist'].rolling(self.pullback_len).max()
        
        historical_trades = []
        active_trades = []
        pending_order = None
        
        for i in range(max(self.pullback_len, 20), len(df)):
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            idx_date = curr['Date'] if 'Date' in curr else df.index[i]
            
            # --- EVALUACIÓN DE ORDEN PENDIENTE EXISTENTE ---
            if pending_order is not None:
                if pending_order['type'] == 'BUY_STOP':
                    # Ver si cruzó el máximo para abrir
                    if curr['High'] >= pending_order['entry_price']:
                        pending_order['entry_date'] = idx_date
                        active_trades.append(pending_order)
                        pending_order = None
                        
                    # Regla Blacksheep: vela cerró roja (en contra de la tendencia), anular!
                    elif curr['Close'] < curr['Open']:
                        pending_order = None
                        
                elif pending_order['type'] == 'SELL_STOP':
                    if curr['Low'] <= pending_order['entry_price']:
                        pending_order['entry_date'] = idx_date
                        active_trades.append(pending_order)
                        pending_order = None
                        
                    # Regla Blacksheep: Cierra contraria (verde), anular orden!
                    elif curr['Close'] > curr['Open']:
                        pending_order = None

            # --- GESTIÓN DE COMPRAS Y VENTAS ABIERTAS ---
            to_remove = []
            for t in active_trades:
                if t['type'] == 'BUY_STOP':
                    if curr['Low'] <= t['sl']:
                        t['exit_date'] = idx_date
                        t['exit_price'] = t['sl']
                        t['pnl'] = -100 # SL tocó (Pérdida 1R)
                        historical_trades.append(t)
                        to_remove.append(t)
                    elif curr['High'] >= t['tp']:
                        t['exit_date'] = idx_date
                        t['exit_price'] = t['tp']
                        t['pnl'] = 100 * self.reward_ratio # TP tocó
                        historical_trades.append(t)
                        to_remove.append(t)
                else:
                    if curr['High'] >= t['sl']:
                        t['exit_date'] = idx_date
                        t['exit_price'] = t['sl']
                        t['pnl'] = -100
                        historical_trades.append(t)
                        to_remove.append(t)
                    elif curr['Low'] <= t['tp']:
                        t['exit_date'] = idx_date
                        t['exit_price'] = t['tp']
                        t['pnl'] = 100 * self.reward_ratio
                        historical_trades.append(t)
                        to_remove.append(t)
            
            for t in to_remove:
                active_trades.remove(t)

            # --- EVALUACIÓN DEL ESTADO DE ARMADO (Para Gatillos) ---
            if curr['hist'] <= self.extreme:
                armed_buy = True
                armed_sell = False
            elif curr['hist'] >= abs(self.extreme):
                armed_sell = True
                armed_buy = False

            # --- BUSCAR SEÑAL GATILLO PARA PONER ORDEN PENDIENTE ---
            if pending_order is None and len(active_trades) == 0:
                
                # --- COMPRA (Largo) ---
                # Condiciones: Tendencia a favor, Armado, cruza a positivo (barra azul), cierra verde
                if curr['market_structure'] == 1 and armed_buy and curr['hist'] > 0 and curr['Close'] > curr['Open']:
                    entry_price = curr['High']
                    sl_price = df['Low'].iloc[i - self.pullback_len : i + 1].min()
                    
                    risk = entry_price - sl_price
                    if risk > 0:
                        tp_price = entry_price + (risk * self.reward_ratio)
                        
                        pending_order = {
                            'type': 'BUY_STOP',
                            'entry_price': entry_price,
                            'sl': sl_price,
                            'tp': tp_price
                        }
                    armed_buy = False # Se desactiva tras disparar el gatillo
                            
                # --- VENTA (Corto) ---
                # Condiciones: Tendencia a favor, Armado, cruza a negativo (barra gris), cierra rojo
                elif curr['market_structure'] == -1 and armed_sell and curr['hist'] < 0 and curr['Close'] < curr['Open']:
                    entry_price = curr['Low']
                    sl_price = df['High'].iloc[i - self.pullback_len : i + 1].max()
                    
                    risk = sl_price - entry_price
                    if risk > 0:
                        tp_price = entry_price - (risk * self.reward_ratio)
                        
                        pending_order = {
                            'type': 'SELL_STOP',
                            'entry_price': entry_price,
                            'sl': sl_price,
                            'tp': tp_price
                        }
                    armed_sell = False # Se desactiva tras disparar el gatillo

        df_trades = pd.DataFrame(historical_trades)
        return df, df_trades
