"""
core/metrics/monte_carlo.py
---------------------------
Módulo estocástico para la simulación Monte Carlo y cálculo de Risk of Ruin (Fase 4.2B).
Realiza remuestreos (bootstrap/shuffle) offline a partir de una lista de transacciones.

Sin dependencias externas complejas de red o IA, 100% aislado.
"""

import numpy as np
from datetime import datetime, timezone
from typing import List, Optional
from core.strategy_models import TradeRecord, MonteCarloResult
from core.metrics.metrics_engine import InsufficientTradesError

class MonteCarloEngine:
    @staticmethod
    def simulate(
        trades: List[TradeRecord],
        initial_equity: float,
        n_simulations: int = 1000,
        seed: Optional[int] = 42,
        method: str = "bootstrap",
        ruin_threshold_pct: float = 0.30,
        cost_per_trade: Optional[float] = None,
        slippage_pct: Optional[float] = None
    ) -> MonteCarloResult:
        """
        Ejecuta la simulación Monte Carlo para evaluar el riesgo de ruina y drawdowns.

        Args:
            trades: Lista de TradeRecord con el historial de operaciones.
            initial_equity: Capital inicial del backtest.
            n_simulations: Número de trayectorias a simular.
            seed: Semilla para garantizar reproducibilidad.
            method: Método de remuestreo ("bootstrap" con reemplazo, "shuffle" sin reemplazo).
            ruin_threshold_pct: Porcentaje de pérdida sobre el capital inicial que define la ruina.
            cost_per_trade: Coste fijo adicional por trade (reemplaza comisiones y swap si no es None).
            slippage_pct: Porcentaje de penalización por slippage aplicado a cada trade.

        Returns:
            MonteCarloResult: Modelo Pydantic con los resultados y estadísticas.

        Raises:
            InsufficientTradesError: Si la cantidad de trades es inferior a 10.
            ValueError: Si los parámetros de configuración son inválidos.
        """
        if not trades or len(trades) < 10:
            raise InsufficientTradesError(
                f"Monte Carlo requiere mínimo 10 trades. Se recibieron: {len(trades) if trades else 0}"
            )

        if n_simulations <= 0:
            raise ValueError("El número de simulaciones debe ser mayor que 0.")

        if initial_equity <= 0:
            raise ValueError("El capital inicial (initial_equity) debe ser mayor que 0.")

        if not (0.0 < ruin_threshold_pct <= 1.0):
            raise ValueError("El umbral de ruina (ruin_threshold_pct) debe estar entre 0.0 (excluyente) y 1.0.")

        if method not in ("bootstrap", "shuffle"):
            raise ValueError("El método de simulación debe ser 'bootstrap' o 'shuffle'.")

        n_trades_input = len(trades)
        low_confidence = n_trades_input < 30

        # 1. Preparar resultados netos ajustados de cada trade
        trade_outcomes = []
        for t in trades:
            # Resultado bruto
            gross = t.profit_loss
            # Costes
            if cost_per_trade is not None:
                # Se aplica el coste fijo penalizando la equidad (cost_per_trade negativo o positivo se resta)
                net_p = gross - abs(cost_per_trade)
            else:
                net_p = gross + t.commission + t.swap
            
            # Slippage
            if slippage_pct is not None:
                # Penalización: reduce ganancias y amplifica pérdidas
                net_p = net_p - abs(net_p) * slippage_pct
                
            trade_outcomes.append(net_p)

        trade_outcomes = np.array(trade_outcomes, dtype=float)

        # 2. Inicializar generador de números aleatorios
        rng = np.random.default_rng(seed)

        # 3. Generar índices de remuestreo
        N = n_trades_input
        if method == "bootstrap":
            # Con reemplazo
            indices = rng.choice(N, size=(n_simulations, N), replace=True)
        else:
            # Shuffle (sin reemplazo) para cada simulación
            indices = np.empty((n_simulations, N), dtype=int)
            for i in range(n_simulations):
                indices[i] = rng.permutation(N)

        # Mapear a los resultados simulados
        sim_outcomes = trade_outcomes[indices]

        # 4. Generar curvas de equidad
        # Cada fila representa una simulación. Columna 0 es initial_equity
        initial_column = np.full((n_simulations, 1), initial_equity)
        equity_curves = initial_column + np.cumsum(sim_outcomes, axis=1)
        equity_curves = np.hstack([initial_column, equity_curves]) # Shape: (n_simulations, N + 1)

        # 5. Calcular Drawdowns
        peaks = np.maximum.accumulate(equity_curves, axis=1)
        drawdowns = peaks - equity_curves
        
        # Evitar división por cero en peaks
        peaks_safe = np.where(peaks <= 0.0, 1e-9, peaks)
        drawdowns_pct = (drawdowns / peaks_safe) * 100.0

        max_drawdowns = np.max(drawdowns, axis=1)
        max_drawdowns_pct = np.max(drawdowns_pct, axis=1)
        final_equities = equity_curves[:, -1]

        # 6. Evaluar Risk of Ruin
        ruin_limit = initial_equity * (1.0 - ruin_threshold_pct)
        ruined = np.any(equity_curves < ruin_limit, axis=1)
        risk_of_ruin_pct = np.mean(ruined)

        # 7. Calcular distribución de rachas de pérdidas consecutivas
        max_losing_streaks = np.zeros(n_simulations, dtype=int)
        for i in range(n_simulations):
            outcomes_sim = sim_outcomes[i]
            max_streak = 0
            current_streak = 0
            for val in outcomes_sim:
                if val < 0.0:
                    current_streak += 1
                    if current_streak > max_streak:
                        max_streak = current_streak
                else:
                    current_streak = 0
            max_losing_streaks[i] = max_streak

        # 8. Obtener percentiles
        worst_case_drawdown = np.max(max_drawdowns)
        worst_case_drawdown_pct = np.max(max_drawdowns_pct)
        
        monte_carlo_max_drawdown_p50 = np.percentile(max_drawdowns_pct, 50)
        monte_carlo_max_drawdown_p95 = np.percentile(max_drawdowns_pct, 95)
        monte_carlo_max_drawdown_p99 = np.percentile(max_drawdowns_pct, 99)

        median_final_equity = np.percentile(final_equities, 50)
        p05_final_equity = np.percentile(final_equities, 5)
        p95_final_equity = np.percentile(final_equities, 95)
        mean_final_equity = np.mean(final_equities)

        max_losing_streak_p95 = int(np.percentile(max_losing_streaks, 95))
        max_losing_streak_p99 = int(np.percentile(max_losing_streaks, 99))

        return MonteCarloResult(
            risk_of_ruin_pct=round(float(risk_of_ruin_pct), 4),
            worst_case_drawdown=round(float(worst_case_drawdown), 4),
            worst_case_drawdown_pct=round(float(worst_case_drawdown_pct), 4),
            monte_carlo_max_drawdown_p50=round(float(monte_carlo_max_drawdown_p50), 4),
            monte_carlo_max_drawdown_p95=round(float(monte_carlo_max_drawdown_p95), 4),
            monte_carlo_max_drawdown_p99=round(float(monte_carlo_max_drawdown_p99), 4),
            median_final_equity=round(float(median_final_equity), 4),
            p05_final_equity=round(float(p05_final_equity), 4),
            p95_final_equity=round(float(p95_final_equity), 4),
            mean_final_equity=round(float(mean_final_equity), 4),
            max_losing_streak_p95=max_losing_streak_p95,
            max_losing_streak_p99=max_losing_streak_p99,
            n_simulations=n_simulations,
            method=method,
            seed=seed,
            n_trades_input=n_trades_input,
            low_confidence=low_confidence,
            initial_equity=initial_equity,
            ruin_threshold_pct=ruin_threshold_pct,
            computed_at=datetime.now(timezone.utc),
            approved_for_real=False
        )
