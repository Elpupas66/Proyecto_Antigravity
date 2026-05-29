"""
core/metrics/metrics_engine.py
------------------------------
Motor matemático determinista para el cálculo de métricas de trading (Fase 4.2A).
Calcula métricas avanzadas a partir de una lista de transacciones tipadas (TradeRecord).

Sin dependencias externas complejas, sin simulaciones estocásticas ni llamadas de red.
"""

import math
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from core.strategy_models import TradeRecord, CalculatedMetrics, TradeDirection

class InsufficientTradesError(Exception):
    """Excepción lanzada cuando la lista de operaciones no es suficiente para calcular métricas."""
    pass

class MetricsEngine:
    @staticmethod
    def calculate(
        trades: List[TradeRecord],
        initial_balance: float = 10000.0,
        risk_free_rate: float = 0.0
    ) -> CalculatedMetrics:
        """
        Calcula las métricas cuantitativas deterministas a partir de la lista de trades.

        Args:
            trades: Lista de objetos TradeRecord estructurados.
            initial_balance: Balance inicial del backtest (usado para calcular porcentajes de drawdown/pérdida).
            risk_free_rate: Tasa libre de riesgo por trade utilizada para el Sortino Ratio (por defecto 0.0).

        Returns:
            CalculatedMetrics: Objeto Pydantic con todas las métricas calculadas.

        Raises:
            InsufficientTradesError: Si la lista de trades contiene menos de 2 elementos.
        """
        if not trades or len(trades) < 2:
            raise InsufficientTradesError(
                f"El Metrics Engine requiere al menos 2 operaciones para realizar el cálculo. "
                f"Recibidos: {len(trades) if trades else 0}"
            )

        total_trades = len(trades)

        # 1. Calcular los resultados netos individuales de cada trade
        # net_profit = profit_loss + commission + swap
        net_profits: List[float] = []
        commissions_sum = 0.0
        swaps_sum = 0.0

        for t in trades:
            net_p = t.profit_loss + t.commission + t.swap
            net_profits.append(net_p)
            commissions_sum += t.commission
            swaps_sum += t.swap

        # 2. Esperanza matemática (Expectancy)
        # expectancy = Sum(net_profits) / total_trades
        expectancy = sum(net_profits) / total_trades

        # 3. Costes medios por trade
        # cost_per_trade = (commissions + swaps) / total_trades
        cost_per_trade = (commissions_sum + swaps_sum) / total_trades

        # 4. Profit Factor neto recalculado
        # profit_factor = sum(ganancias netas) / sum(|pérdidas netas|)
        gross_profit = sum(p for p in net_profits if p > 0.0)
        gross_loss = sum(abs(p) for p in net_profits if p < 0.0)

        if gross_loss > 0.0:
            profit_factor = gross_profit / gross_loss
        else:
            # Si no hay pérdidas, el profit factor es teóricamente infinito. Devolvemos un límite controlado.
            profit_factor = 99.0 if gross_profit > 0.0 else 0.0

        # 5. Ratio de aciertos (Win Rate) y promedios individuales
        wins = [p for p in net_profits if p > 0.0]
        losses = [p for p in net_profits if p < 0.0]

        win_rate = len(wins) / total_trades
        average_win = sum(wins) / len(wins) if wins else 0.0
        average_loss = abs(sum(losses) / len(losses)) if losses else 0.0

        # 6. Rachas consecutivas (Streaks)
        max_winning_streak = 0
        max_losing_streak = 0
        current_win_streak = 0
        current_loss_streak = 0

        for p in net_profits:
            if p > 0.0:
                current_win_streak += 1
                current_loss_streak = 0
                if current_win_streak > max_winning_streak:
                    max_winning_streak = current_win_streak
            elif p < 0.0:
                current_loss_streak += 1
                current_win_streak = 0
                if current_loss_streak > max_losing_streak:
                    max_losing_streak = current_loss_streak
            else:
                # Un trade plano (0.0) resetea ambas rachas
                current_win_streak = 0
                current_loss_streak = 0

        # 7. Pérdida Diaria Máxima (Max Daily Loss) determinista
        # Agrupamos por fecha de cierre del trade (close_time.date())
        daily_results: Dict[date, float] = {}
        for t in trades:
            day = t.close_time.date()
            net_p = t.profit_loss + t.commission + t.swap
            daily_results[day] = daily_results.get(day, 0.0) + net_p

        # Buscamos la pérdida más severa (el valor diario más negativo)
        worst_day_val = min(daily_results.values()) if daily_results else 0.0

        if worst_day_val < 0.0:
            max_daily_loss = abs(worst_day_val)
            max_daily_loss_pct = (max_daily_loss / initial_balance) * 100.0
        else:
            max_daily_loss = 0.0
            max_daily_loss_pct = 0.0

        # 8. Exposición Simultánea Máxima (max_simultaneous_trades)
        # Detección de solapamiento de intervalos temporales [open_time, close_time]
        events: List[tuple] = []
        for t in trades:
            # +1 para apertura, -1 para cierre
            events.append((t.open_time, 1))
            events.append((t.close_time, -1))

        # Ordenar cronológicamente. Si dos eventos coinciden, el -1 (cierre) se procesará
        # antes que el +1 (apertura) para evitar picos artificiales transitorios.
        events.sort(key=lambda x: (x[0], x[1]))

        max_simultaneous_trades = 0
        current_active = 0
        for _, change in events:
            current_active += change
            if current_active > max_simultaneous_trades:
                max_simultaneous_trades = current_active

        # 9. Sortino Ratio (Trade-based)
        # downside_deviation = sqrt( sum(min(0, R_i - R_f)^2) / total_trades )
        downside_returns_sq = []
        for r in net_profits:
            diff = r - risk_free_rate
            if diff < 0.0:
                downside_returns_sq.append(diff ** 2)
            else:
                downside_returns_sq.append(0.0)

        downside_variance = sum(downside_returns_sq) / total_trades
        downside_deviation = math.sqrt(downside_variance)

        if downside_deviation > 0.0:
            sortino_ratio = (expectancy - risk_free_rate) / downside_deviation
        else:
            # Si no hay volatilidad negativa (downside deviation es cero)
            sortino_ratio = 99.0 if expectancy > risk_free_rate else 0.0

        return CalculatedMetrics(
            total_trades=total_trades,
            profit_factor=round(profit_factor, 4),
            expectancy=round(expectancy, 4),
            average_win=round(average_win, 4),
            average_loss=round(average_loss, 4),
            win_rate=round(win_rate, 4),
            max_winning_streak=max_winning_streak,
            max_losing_streak=max_losing_streak,
            max_daily_loss=round(max_daily_loss, 4),
            max_daily_loss_pct=round(max_daily_loss_pct, 4),
            max_simultaneous_trades=max_simultaneous_trades,
            sortino_ratio=round(sortino_ratio, 4),
            cost_per_trade=round(cost_per_trade, 4)
        )
