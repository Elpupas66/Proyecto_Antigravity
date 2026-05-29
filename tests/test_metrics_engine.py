"""
tests/test_metrics_engine.py
----------------------------
Batería de pruebas unitarias para el módulo MetricsEngine (Fase 4.2A).
Valida todos los cálculos matemáticos deterministas de forma rigurosa.
"""

import pytest
import math
from datetime import datetime, timedelta
from core.strategy_models import TradeRecord, TradeDirection
from core.metrics.metrics_engine import MetricsEngine, InsufficientTradesError

def create_mock_trade(
    ticket: str,
    profit_loss: float,
    open_time: datetime,
    close_time: datetime,
    commission: float = 0.0,
    swap: float = 0.0,
    direction: TradeDirection = TradeDirection.BUY
) -> TradeRecord:
    return TradeRecord(
        ticket=ticket,
        symbol="EURUSD",
        open_time=open_time,
        close_time=close_time,
        direction=direction,
        volume=0.1,
        open_price=1.1000,
        close_price=1.1100 if profit_loss >= 0 else 1.0900,
        commission=commission,
        swap=swap,
        profit_loss=profit_loss
    )

def test_insufficient_trades():
    """Verifica que el motor falle con gracia ante datos nulos o insuficientes (< 2 trades)."""
    # Lista vacía
    with pytest.raises(InsufficientTradesError):
        MetricsEngine.calculate([])

    # Un solo trade
    base_time = datetime(2026, 5, 29, 10, 0, 0)
    single_trade = create_mock_trade("1", 50.0, base_time, base_time + timedelta(hours=1))
    with pytest.raises(InsufficientTradesError):
        MetricsEngine.calculate([single_trade])

def test_expectancy_and_fees():
    """Valida los cálculos de esperanza matemática, coste medio y factor de beneficio."""
    base_time = datetime(2026, 5, 29, 10, 0, 0)
    
    # 3 trades:
    # T1: Profit = 100, Comm = -2, Swap = -1. Net profit = 97 (Win)
    # T2: Profit = -50, Comm = -2, Swap = 0. Net profit = -52 (Loss)
    # T3: Profit = 80, Comm = -2, Swap = -2. Net profit = 76 (Win)
    trades = [
        create_mock_trade("1", 100.0, base_time, base_time + timedelta(minutes=30), commission=-2.0, swap=-1.0),
        create_mock_trade("2", -50.0, base_time + timedelta(hours=1), base_time + timedelta(hours=1, minutes=30), commission=-2.0, swap=0.0),
        create_mock_trade("3", 80.0, base_time + timedelta(hours=2), base_time + timedelta(hours=2, minutes=30), commission=-2.0, swap=-2.0)
    ]
    
    metrics = MetricsEngine.calculate(trades, initial_balance=10000.0)
    
    # total_trades = 3
    assert metrics.total_trades == 3
    
    # expectancy = (97 - 52 + 76) / 3 = 121 / 3 = 40.3333
    assert math.isclose(metrics.expectancy, 40.3333, abs_tol=1e-4)
    
    # cost_per_trade = ((-2 + -1) + (-2 + 0) + (-2 + -2)) / 3 = (-3 - 2 - 4) / 3 = -9 / 3 = -3.00
    assert metrics.cost_per_trade == -3.0
    
    # profit_factor = (97 + 76) / 52 = 173 / 52 = 3.3269
    assert math.isclose(metrics.profit_factor, 3.3269, abs_tol=1e-4)
    
    # win_rate = 2 / 3 = 0.6667
    assert math.isclose(metrics.win_rate, 0.6667, abs_tol=1e-4)
    
    # average_win = (97 + 76) / 2 = 86.5
    assert metrics.average_win == 86.5
    
    # average_loss = |-52| = 52.0
    assert metrics.average_loss == 52.0

def test_streaks_calculation():
    """Verifica que el motor detecte de forma determinista las rachas de victorias y derrotas."""
    base_time = datetime(2026, 5, 29, 10, 0, 0)
    
    # Resultados netos esperados: Win (50), Loss (-10), Loss (-20), Win (10), Win (15), Win (5), Loss (-30), Flat (0.0)
    trades = [
        create_mock_trade("1", 50.0, base_time, base_time + timedelta(minutes=10)), # W (1)
        create_mock_trade("2", -10.0, base_time + timedelta(minutes=20), base_time + timedelta(minutes=30)), # L (1)
        create_mock_trade("3", -20.0, base_time + timedelta(minutes=40), base_time + timedelta(minutes=50)), # L (2)
        create_mock_trade("4", 10.0, base_time + timedelta(hours=1), base_time + timedelta(hours=1, minutes=10)), # W (1)
        create_mock_trade("5", 15.0, base_time + timedelta(hours=1, minutes=20), base_time + timedelta(hours=1, minutes=30)), # W (2)
        create_mock_trade("6", 5.0, base_time + timedelta(hours=1, minutes=40), base_time + timedelta(hours=1, minutes=50)), # W (3)
        create_mock_trade("7", -30.0, base_time + timedelta(hours=2), base_time + timedelta(hours=2, minutes=10)), # L (1)
        create_mock_trade("8", 0.0, base_time + timedelta(hours=3), base_time + timedelta(hours=3, minutes=10)), # Flat (Resetea)
    ]
    
    metrics = MetricsEngine.calculate(trades)
    
    assert metrics.max_winning_streak == 3
    assert metrics.max_losing_streak == 2

def test_max_daily_loss():
    """Valida la agregación por día natural y el cálculo de la pérdida diaria máxima."""
    base_time_day1 = datetime(2026, 5, 29, 10, 0, 0)
    base_time_day2 = datetime(2026, 5, 30, 10, 0, 0)
    
    # Balance inicial: 10000
    # Día 1 (29 de Mayo):
    # T1: -100 USD
    # T2: -250 USD
    # T3: +150 USD
    # Neto Día 1 = -200 USD (Pérdida de 2.0%)
    #
    # Día 2 (30 de Mayo):
    # T4: -400 USD
    # T5: +50 USD
    # Neto Día 2 = -350 USD (Pérdida de 3.5%)
    trades = [
        # Día 1
        create_mock_trade("1", -100.0, base_time_day1, base_time_day1 + timedelta(minutes=30)),
        create_mock_trade("2", -250.0, base_time_day1 + timedelta(hours=1), base_time_day1 + timedelta(hours=1, minutes=30)),
        create_mock_trade("3", 150.0, base_time_day1 + timedelta(hours=2), base_time_day1 + timedelta(hours=2, minutes=30)),
        # Día 2
        create_mock_trade("4", -400.0, base_time_day2, base_time_day2 + timedelta(minutes=30)),
        create_mock_trade("5", 50.0, base_time_day2 + timedelta(hours=1), base_time_day2 + timedelta(hours=1, minutes=30))
    ]
    
    metrics = MetricsEngine.calculate(trades, initial_balance=10000.0)
    
    # Peor pérdida diaria es en el Día 2 (-350)
    assert metrics.max_daily_loss == 350.0
    assert metrics.max_daily_loss_pct == 3.5

def test_max_simultaneous_trades():
    """Evalúa la detección de concurrencia temporal y solapamiento de operaciones."""
    base_time = datetime(2026, 5, 29, 10, 0, 0)
    
    # Escenario de solapamientos:
    # T1: [10:00, 10:30]
    # T2: [10:15, 10:45]  (Solapa con T1, concurrencia = 2)
    # T3: [10:20, 10:25]  (Solapa con T1 y T2, concurrencia = 3)
    # T4: [10:50, 11:30]  (No solapa con anteriores)
    trades = [
        create_mock_trade("1", 10.0, base_time, base_time + timedelta(minutes=30)),
        create_mock_trade("2", 20.0, base_time + timedelta(minutes=15), base_time + timedelta(minutes=45)),
        create_mock_trade("3", -5.0, base_time + timedelta(minutes=20), base_time + timedelta(minutes=25)),
        create_mock_trade("4", 15.0, base_time + timedelta(minutes=50), base_time + timedelta(minutes=90))
    ]
    
    metrics = MetricsEngine.calculate(trades)
    assert metrics.max_simultaneous_trades == 3

def test_sortino_ratio_trade_based():
    """Valida el cálculo matemático de Sortino en su versión trade-based."""
    base_time = datetime(2026, 5, 29, 10, 0, 0)
    
    # Serie de operaciones:
    # 4 trades con resultados netos: [100, -20, 50, -30]
    # Expectancy = (100 - 20 + 50 - 30) / 4 = 100 / 4 = 25.0
    # downside diffs para R_f = 0:
    # T1 (100 >= 0) -> 0
    # T2 (-20 < 0)  -> -20 (al cuadrado = 400)
    # T3 (50 >= 0)  -> 0
    # T4 (-30 < 0)  -> -30 (al cuadrado = 900)
    #
    # Downside variance = (400 + 900) / 4 = 1300 / 4 = 325.0
    # Downside deviation = sqrt(325.0) = 18.027756
    # Sortino = (25.0 - 0.0) / 18.027756 = 1.38675
    trades = [
        create_mock_trade("1", 100.0, base_time, base_time + timedelta(hours=1)),
        create_mock_trade("2", -20.0, base_time + timedelta(hours=2), base_time + timedelta(hours=3)),
        create_mock_trade("3", 50.0, base_time + timedelta(hours=4), base_time + timedelta(hours=5)),
        create_mock_trade("4", -30.0, base_time + timedelta(hours=6), base_time + timedelta(hours=7))
    ]
    
    metrics = MetricsEngine.calculate(trades, risk_free_rate=0.0)
    
    assert math.isclose(metrics.sortino_ratio, 1.3868, abs_tol=1e-4)

def test_sortino_ratio_no_losses():
    """Verifica que el Sortino Ratio maneje correctamente casos sin pérdidas (downside deviation cero)."""
    base_time = datetime(2026, 5, 29, 10, 0, 0)
    
    # Todos ganadores: [50, 100, 150] -> downside deviation = 0
    # Expectancy = 100 > R_f(0.0) -> Debería devolver 99.0
    trades = [
        create_mock_trade("1", 50.0, base_time, base_time + timedelta(hours=1)),
        create_mock_trade("2", 100.0, base_time + timedelta(hours=2), base_time + timedelta(hours=3)),
        create_mock_trade("3", 150.0, base_time + timedelta(hours=4), base_time + timedelta(hours=5))
    ]
    
    metrics = MetricsEngine.calculate(trades)
    assert metrics.sortino_ratio == 99.0

    # Todos planos (0.0) -> downside deviation = 0.0, Expectancy = 0.0 <= R_f(0.0) -> Debería devolver 0.0
    trades_flat = [
        create_mock_trade("1", 0.0, base_time, base_time + timedelta(hours=1)),
        create_mock_trade("2", 0.0, base_time + timedelta(hours=2), base_time + timedelta(hours=3))
    ]
    metrics_flat = MetricsEngine.calculate(trades_flat, risk_free_rate=0.0)
    assert metrics_flat.sortino_ratio == 0.0

    # Si hay pérdidas y la media es negativa, el Sortino calculado es negativo
    trades_negative = [
        create_mock_trade("1", -50.0, base_time, base_time + timedelta(hours=1)),
        create_mock_trade("2", -100.0, base_time + timedelta(hours=2), base_time + timedelta(hours=3))
    ]
    metrics_neg = MetricsEngine.calculate(trades_negative, risk_free_rate=0.0)
    assert metrics_neg.sortino_ratio < 0.0
    assert math.isclose(metrics_neg.sortino_ratio, -0.9487, abs_tol=1e-4)
