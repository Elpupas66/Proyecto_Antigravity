"""
tests/test_monte_carlo.py
-------------------------
Batería de pruebas unitarias para el módulo MonteCarloEngine (Fase 4.2B).
Valida simulación estocástica, cálculo de Risk of Ruin, percentiles,
e integración con el validador (D4).
"""

import pytest
import math
from datetime import datetime, timezone, timedelta
from typing import List
from core.strategy_models import (
    TradeRecord,
    TradeDirection,
    BacktestReport,
    BacktestPeriod,
    StrategyMetadata,
    AssetClass,
    BiasChecklist,
    MarketRegimeChecklist,
    StrategyClassification,
    MonteCarloResult
)
from core.metrics.monte_carlo import MonteCarloEngine
from core.metrics.metrics_engine import InsufficientTradesError
from core.backtest_validator import BacktestValidator, MetricThresholds

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

def generate_n_trades(n: int, win_rate: float, win_amount: float, loss_amount: float) -> List[TradeRecord]:
    base_time = datetime(2026, 5, 31, 12, 0, 0, tzinfo=timezone.utc)
    trades = []
    # Seed local determinista para la distribución de wins/losses
    for i in range(n):
        # Determinar si es win o loss de forma alternada o determinista basada en el índice para coincidir con el win_rate
        is_win = ((i * 17) % 100) < (win_rate * 100)
        pnl = win_amount if is_win else -loss_amount
        trades.append(
            create_mock_trade(
                ticket=str(i + 1),
                profit_loss=pnl,
                open_time=base_time + timedelta(hours=i),
                close_time=base_time + timedelta(hours=i, minutes=30),
                commission=-1.0,
                swap=-0.5
            )
        )
    return trades

def test_insufficient_trades_monte_carlo():
    """Verifica que Monte Carlo lance error si hay menos de 10 trades."""
    trades = generate_n_trades(9, 0.50, 100.0, 50.0)
    with pytest.raises(InsufficientTradesError) as exc_info:
        MonteCarloEngine.simulate(trades, initial_equity=10000.0)
    assert "Monte Carlo requiere mínimo 10 trades" in str(exc_info.value)

def test_low_confidence_flag_active():
    """Verifica que entre 10 y 29 trades se active low_confidence=True."""
    trades = generate_n_trades(15, 0.50, 100.0, 50.0)
    result = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=100)
    assert result.low_confidence is True
    assert result.n_simulations == 100

def test_high_confidence_flag_active():
    """Verifica que con 30 o más trades se desactive low_confidence."""
    trades = generate_n_trades(35, 0.50, 100.0, 50.0)
    result = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=100)
    assert result.low_confidence is False

def test_reproducibility_with_seed():
    """Verifica que con una semilla fija el resultado sea idéntico."""
    trades = generate_n_trades(30, 0.50, 100.0, 50.0)
    res1 = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=500, seed=42)
    res2 = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=500, seed=42)
    
    assert res1.risk_of_ruin_pct == res2.risk_of_ruin_pct
    assert res1.worst_case_drawdown == res2.worst_case_drawdown
    assert res1.monte_carlo_max_drawdown_p95 == res2.monte_carlo_max_drawdown_p95
    assert res1.median_final_equity == res2.median_final_equity

def test_robust_strategy_low_ruin():
    """Estrategia robusta (alta tasa de aciertos y ganancias) tiene cero o muy bajo riesgo de ruina."""
    # 40 trades, 85% aciertos, ganancia=150, pérdida=50. Capital inicial=10000. Umbral ruina=30% (caer a 7000)
    trades = generate_n_trades(40, 0.85, 150.0, 50.0)
    res = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=1000, seed=42)
    
    # Prácticamente imposible arruinarse
    assert res.risk_of_ruin_pct < 0.01
    assert res.median_final_equity > 10000.0
    assert res.approved_for_real is False

def test_fragile_strategy_high_ruin():
    """Estrategia frágil (baja tasa de aciertos y pérdidas grandes) tiene muy alto riesgo de ruina."""
    # 40 trades, 15% aciertos, ganancia=50, pérdida=400. Capital inicial=10000. Umbral ruina=30%
    trades = generate_n_trades(40, 0.15, 50.0, 400.0)
    res = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=1000, seed=42, ruin_threshold_pct=0.30)
    
    # Elevadísima probabilidad de ruina
    assert res.risk_of_ruin_pct > 0.50
    assert res.approved_for_real is False

def test_percentiles_order():
    """Verifica que el orden lógico de los percentiles sea el correcto."""
    trades = generate_n_trades(35, 0.60, 100.0, 100.0)
    res = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=500, seed=123)
    
    # Drawdowns
    assert res.worst_case_drawdown_pct >= res.monte_carlo_max_drawdown_p99
    assert res.monte_carlo_max_drawdown_p99 >= res.monte_carlo_max_drawdown_p95
    assert res.monte_carlo_max_drawdown_p95 >= res.monte_carlo_max_drawdown_p50
    
    # Equities
    assert res.p95_final_equity >= res.median_final_equity
    assert res.median_final_equity >= res.p05_final_equity
    
    # Rachas
    assert res.max_losing_streak_p99 >= res.max_losing_streak_p95

def test_bootstrap_vs_shuffle():
    """Verifica que bootstrap (con reemplazo) y shuffle (sin reemplazo) den resultados diferentes."""
    trades = generate_n_trades(30, 0.55, 100.0, 90.0)
    res_boot = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=500, seed=42, method="bootstrap")
    res_shuf = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=500, seed=42, method="shuffle")
    
    # Deberían divergir ligeramente por el tipo de muestreo
    assert res_boot.monte_carlo_max_drawdown_p95 != res_shuf.monte_carlo_max_drawdown_p95

def test_monte_carlo_parameters_adjustment():
    """Verifica el correcto ajuste con cost_per_trade y slippage_pct."""
    trades = generate_n_trades(30, 0.70, 100.0, 50.0)
    
    # Sin costes ni slippage adicionales
    res_base = MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=500, seed=42)
    
    # Con costes adicionales severos de 20 por trade y slippage del 5%
    res_adj = MonteCarloEngine.simulate(
        trades,
        initial_equity=10000.0,
        n_simulations=500,
        seed=42,
        cost_per_trade=20.0,
        slippage_pct=0.05
    )
    
    # El equity final debería ser menor y los drawdowns mayores
    assert res_adj.mean_final_equity < res_base.mean_final_equity
    assert res_adj.worst_case_drawdown > res_base.worst_case_drawdown

def test_invalid_arguments_validation():
    """Verifica la validación de argumentos inválidos en simulate."""
    trades = generate_n_trades(12, 0.5, 10, 10)
    
    with pytest.raises(ValueError):
        MonteCarloEngine.simulate(trades, initial_equity=-1000.0)
        
    with pytest.raises(ValueError):
        MonteCarloEngine.simulate(trades, initial_equity=10000.0, n_simulations=0)
        
    with pytest.raises(ValueError):
        MonteCarloEngine.simulate(trades, initial_equity=10000.0, ruin_threshold_pct=1.5)
        
    with pytest.raises(ValueError):
        MonteCarloEngine.simulate(trades, initial_equity=10000.0, method="invalid_method")

def test_backtest_validator_integration_low_confidence():
    """D4: BacktestValidator bloquea PAPER_TRADING_READY si low_confidence es True."""
    # Configurar mock de BacktestReport
    base_time = datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc)
    report = BacktestReport(
        strategy_id="ST_01",
        version="1.0.0",
        data_source="MetaTrader 5",
        in_sample_period=BacktestPeriod(start_date=base_time, end_date=base_time + timedelta(days=30), label="IS"),
        out_of_sample_period=BacktestPeriod(start_date=base_time + timedelta(days=31), end_date=base_time + timedelta(days=60), label="OOS"),
        total_trades=20,  # Pocos trades, cumple requisitos mínimos del validador genérico pero activa low_confidence en Monte Carlo
        profit_factor_is=1.8,
        profit_factor_oos=1.5,
        max_drawdown_pct=5.0,
        recovery_factor=4.0,
        sharpe_ratio=1.5,
        sortino_ratio=1.8,
        expectancy=20.0,
        average_win=50.0,
        average_loss=30.0,
        win_rate=0.60,
        max_losing_streak=3,
        max_daily_loss_pct=2.0,
        simultaneous_exposure_pct=1.0,
        risk_of_ruin_pct=0.01,
        average_slippage=0.0,
        average_trade_cost=-1.5,
    )
    
    # Crear un MonteCarloResult ficticio con low_confidence=True
    report.monte_carlo_result = MonteCarloResult(
        risk_of_ruin_pct=0.01,
        worst_case_drawdown=500.0,
        worst_case_drawdown_pct=5.0,
        monte_carlo_max_drawdown_p50=4.0,
        monte_carlo_max_drawdown_p95=6.0,
        monte_carlo_max_drawdown_p99=8.0,
        median_final_equity=11000.0,
        p05_final_equity=10200.0,
        p95_final_equity=11800.0,
        mean_final_equity=11000.0,
        max_losing_streak_p95=4,
        max_losing_streak_p99=6,
        n_simulations=1000,
        method="bootstrap",
        seed=42,
        n_trades_input=20,
        low_confidence=True, # Activa bloqueo D4
        initial_equity=10000.0,
        ruin_threshold_pct=0.30,
        computed_at=datetime.now(timezone.utc),
        approved_for_real=False
    )
    
    # Completar bias y market regime checklists con valores aceptables
    bias_checklist = BiasChecklist(
        look_ahead_bias_checked=True,
        survivorship_bias_checked=True,
        data_snooping_checked=True,
        overfitting_checked=True,
        curve_fitting_checked=True,
        selection_bias_checked=True,
        period_bias_checked=True,
        realistic_costs_checked=True,
        realistic_execution_checked=True,
        spread_slippage_checked=True
    )
    
    market_regime_checklist = MarketRegimeChecklist(
        trend_tested=True,
        range_tested=True,
        high_volatility_tested=True,
        low_volatility_tested=True,
        session_variability_tested=True
    )
    
    metadata = StrategyMetadata(
        strategy_id="ST_01",
        name="Test low confidence",
        version="1.0.0",
        config_hash="abc123hash",
        author_or_source="Developer",
        asset="EURUSD",
        asset_class=AssetClass.FOREX,
        timeframe="H1",
        created_at=datetime.now(timezone.utc)
    )
    
    # Configurar umbrales que permitan pasar a PAPER_TRADING_READY (min_trades = 20 para pasar esta regla)
    thresholds = MetricThresholds.get_default_thresholds(AssetClass.FOREX)
    thresholds.min_trades = 20  # Forzar a 20 para que no sea rechazado por cantidad total de trades
    
    validator = BacktestValidator()
    evaluation = validator.validate(
        metadata=metadata,
        report=report,
        bias_checklist=bias_checklist,
        market_regime_checklist=market_regime_checklist,
        thresholds=thresholds
    )
    
    # El validador debe clasificar como OBSERVATION, no como PAPER_TRADING_READY debido a low_confidence
    assert evaluation.classification == StrategyClassification.OBSERVATION
    assert "Baja confianza en la simulacion Monte Carlo" in evaluation.decision_reason

def test_backtest_validator_rejection_prevails():
    """Si hay una regla de rechazo activa, REJECTED prevalece sobre OBSERVATION debido a low_confidence."""
    base_time = datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc)
    report = BacktestReport(
        strategy_id="ST_01",
        version="1.0.0",
        data_source="MetaTrader 5",
        in_sample_period=BacktestPeriod(start_date=base_time, end_date=base_time + timedelta(days=30), label="IS"),
        out_of_sample_period=BacktestPeriod(start_date=base_time + timedelta(days=31), end_date=base_time + timedelta(days=60), label="OOS"),
        total_trades=20,
        profit_factor_is=1.8,
        profit_factor_oos=1.0,  # PF OOS muy bajo, causa REJECTED
        max_drawdown_pct=5.0,
        recovery_factor=4.0,
        sharpe_ratio=1.5,
        sortino_ratio=1.8,
        expectancy=20.0,
        average_win=50.0,
        average_loss=30.0,
        win_rate=0.60,
        max_losing_streak=3,
        max_daily_loss_pct=2.0,
        simultaneous_exposure_pct=1.0,
        risk_of_ruin_pct=0.01,
        average_slippage=0.0,
        average_trade_cost=-1.5,
    )
    
    report.monte_carlo_result = MonteCarloResult(
        risk_of_ruin_pct=0.01,
        worst_case_drawdown=500.0,
        worst_case_drawdown_pct=5.0,
        monte_carlo_max_drawdown_p50=4.0,
        monte_carlo_max_drawdown_p95=6.0,
        monte_carlo_max_drawdown_p99=8.0,
        median_final_equity=11000.0,
        p05_final_equity=10200.0,
        p95_final_equity=11800.0,
        mean_final_equity=11000.0,
        max_losing_streak_p95=4,
        max_losing_streak_p99=6,
        n_simulations=1000,
        method="bootstrap",
        seed=42,
        n_trades_input=20,
        low_confidence=True, # Activa observación por baja confianza
        initial_equity=10000.0,
        ruin_threshold_pct=0.30,
        computed_at=datetime.now(timezone.utc),
        approved_for_real=False
    )
    
    bias_checklist = BiasChecklist(
        look_ahead_bias_checked=True,
        survivorship_bias_checked=True,
        data_snooping_checked=True,
        overfitting_checked=True,
        curve_fitting_checked=True,
        selection_bias_checked=True,
        period_bias_checked=True,
        realistic_costs_checked=True,
        realistic_execution_checked=True,
        spread_slippage_checked=True
    )
    
    market_regime_checklist = MarketRegimeChecklist(
        trend_tested=True,
        range_tested=True,
        high_volatility_tested=True,
        low_volatility_tested=True,
        session_variability_tested=True
    )
    
    metadata = StrategyMetadata(
        strategy_id="ST_01",
        name="Test prevails rejected",
        version="1.0.0",
        config_hash="abc123hash",
        author_or_source="Developer",
        asset="EURUSD",
        asset_class=AssetClass.FOREX,
        timeframe="H1",
        created_at=datetime.now(timezone.utc)
    )
    
    thresholds = MetricThresholds.get_default_thresholds(AssetClass.FOREX)
    thresholds.min_trades = 20
    
    validator = BacktestValidator()
    evaluation = validator.validate(
        metadata=metadata,
        report=report,
        bias_checklist=bias_checklist,
        market_regime_checklist=market_regime_checklist,
        thresholds=thresholds
    )
    
    # Debe seguir siendo REJECTED por el Profit Factor OOS insuficiente
    assert evaluation.classification == StrategyClassification.REJECTED
    assert "RECHAZO: Profit Factor OOS por debajo del minimo" in evaluation.decision_reason
    assert "Baja confianza en la simulacion Monte Carlo" in evaluation.decision_reason

def test_paper_trading_only_with_high_confidence():
    """PAPER_TRADING_READY solo se permite si low_confidence es False."""
    base_time = datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc)
    report = BacktestReport(
        strategy_id="ST_01",
        version="1.0.0",
        data_source="MetaTrader 5",
        in_sample_period=BacktestPeriod(start_date=base_time, end_date=base_time + timedelta(days=30), label="IS"),
        out_of_sample_period=BacktestPeriod(start_date=base_time + timedelta(days=31), end_date=base_time + timedelta(days=60), label="OOS"),
        total_trades=180,  # Suficientes trades, cumple thresholds
        profit_factor_is=1.8,
        profit_factor_oos=1.5,
        max_drawdown_pct=5.0,
        recovery_factor=4.0,
        sharpe_ratio=1.5,
        sortino_ratio=1.8,
        expectancy=20.0,
        average_win=50.0,
        average_loss=30.0,
        win_rate=0.60,
        max_losing_streak=3,
        max_daily_loss_pct=2.0,
        simultaneous_exposure_pct=1.0,
        risk_of_ruin_pct=0.01,
        average_slippage=0.0,
        average_trade_cost=-1.5,
    )
    
    report.monte_carlo_result = MonteCarloResult(
        risk_of_ruin_pct=0.01,
        worst_case_drawdown=500.0,
        worst_case_drawdown_pct=5.0,
        monte_carlo_max_drawdown_p50=4.0,
        monte_carlo_max_drawdown_p95=6.0,
        monte_carlo_max_drawdown_p99=8.0,
        median_final_equity=11000.0,
        p05_final_equity=10200.0,
        p95_final_equity=11800.0,
        mean_final_equity=11000.0,
        max_losing_streak_p95=4,
        max_losing_streak_p99=6,
        n_simulations=1000,
        method="bootstrap",
        seed=42,
        n_trades_input=180,
        low_confidence=False, # Alta confianza
        initial_equity=10000.0,
        ruin_threshold_pct=0.30,
        computed_at=datetime.now(timezone.utc),
        approved_for_real=False
    )
    
    bias_checklist = BiasChecklist(
        look_ahead_bias_checked=True,
        survivorship_bias_checked=True,
        data_snooping_checked=True,
        overfitting_checked=True,
        curve_fitting_checked=True,
        selection_bias_checked=True,
        period_bias_checked=True,
        realistic_costs_checked=True,
        realistic_execution_checked=True,
        spread_slippage_checked=True
    )
    
    market_regime_checklist = MarketRegimeChecklist(
        trend_tested=True,
        range_tested=True,
        high_volatility_tested=True,
        low_volatility_tested=True,
        session_variability_tested=True
    )
    
    metadata = StrategyMetadata(
        strategy_id="ST_01",
        name="Test high confidence success",
        version="1.0.0",
        config_hash="abc123hash",
        author_or_source="Developer",
        asset="EURUSD",
        asset_class=AssetClass.FOREX,
        timeframe="H1",
        created_at=datetime.now(timezone.utc)
    )
    
    thresholds = MetricThresholds.get_default_thresholds(AssetClass.FOREX)
    
    validator = BacktestValidator()
    evaluation = validator.validate(
        metadata=metadata,
        report=report,
        bias_checklist=bias_checklist,
        market_regime_checklist=market_regime_checklist,
        thresholds=thresholds
    )
    
    # Cumple todos los requisitos y tiene alta confianza, pasa a PAPER_TRADING_READY
    assert evaluation.classification == StrategyClassification.PAPER_TRADING_READY
