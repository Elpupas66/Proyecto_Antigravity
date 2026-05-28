"""
tests/test_backtest_validator.py
---------------------------------
Pruebas unitarias de BacktestValidator para el Proyecto Antigravity.
Fase 3.2: Evalúa los 10 escenarios cuantitativos obligatorios.

Ejecutar con: python tests/test_backtest_validator.py
"""

import sys
import os
from datetime import datetime, timezone
from pydantic import ValidationError

# Insertar el path del proyecto al inicio para resolver imports correctamente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.strategy_models import (
    StrategyClassification,
    AssetClass,
    StrategyMetadata,
    BacktestPeriod,
    BacktestReport,
    BiasChecklist,
    MarketRegimeChecklist,
    StrategyEvaluation
)
from core.backtest_validator import BacktestValidator, MetricThresholds

passed = 0
failed = 0

def run_test(name: str, test_func):
    global passed, failed
    try:
        test_func()
        print(f"PASS | {name}")
        passed += 1
    except Exception as e:
        print(f"FAIL | {name}")
        print(f"       Error: {e}")
        failed += 1

# ─────────────────────────────────────────────────────────────────────────────
# MOCKS Y HELPERS DE DATOS SÓLIDOS (APROBABLES)
# ─────────────────────────────────────────────────────────────────────────────

def get_base_metadata(asset_class: AssetClass = AssetClass.FOREX) -> StrategyMetadata:
    return StrategyMetadata(
        strategy_id="ST-VALID-888",
        name="Arbitrage Momentum",
        version="1.0.0",
        config_hash="7f8e9d0c1b2a",
        author_or_source="QuantEngine",
        asset="EURUSD" if asset_class == AssetClass.FOREX else "SP500",
        asset_class=asset_class,
        timeframe="H1",
        created_at=datetime.now(timezone.utc),
        notes="Ficha base aprobable"
    )

def get_base_period(label: str) -> BacktestPeriod:
    return BacktestPeriod(
        start_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2023, 12, 31, tzinfo=timezone.utc),
        label=label
    )

def get_robust_report() -> BacktestReport:
    # Métrica excelente para Forex (min_trades=180, PF_OOS=1.25, DD<=10.0%, RF>=3.0, Sharpe>=1.2, Sortino>=1.5)
    return BacktestReport(
        strategy_id="ST-VALID-888",
        version="1.0.0",
        data_source="Darwinex ticks",
        in_sample_period=get_base_period("IS"),
        out_of_sample_period=get_base_period("OOS"),
        total_trades=200,
        profit_factor_is=1.65,
        profit_factor_oos=1.35,  # Muy robusto (> 1.25 + 0.05 = 1.30)
        max_drawdown_pct=5.5,    # Muy controlado (< 10.0%)
        recovery_factor=4.5,     # (> 3.0)
        sharpe_ratio=1.45,       # (> 1.20)
        sortino_ratio=1.85,      # (> 1.50)
        expectancy=22.5,         # Positiva
        average_win=60.0,
        average_loss=-35.0,
        win_rate=0.48,
        max_losing_streak=4,
        max_daily_loss_pct=1.0,
        simultaneous_exposure_pct=1.5,
        risk_of_ruin_pct=0.01,   # Muy bajo (< 0.10)
        average_slippage=1.1,
        average_trade_cost=0.08
    )

def get_complete_bias_checklist() -> BiasChecklist:
    return BiasChecklist(
        look_ahead_bias_checked=True,
        survivorship_bias_checked=True,
        data_snooping_checked=True,
        overfitting_checked=True,
        curve_fitting_checked=True,
        selection_bias_checked=True,
        period_bias_checked=True,
        realistic_costs_checked=True,
        realistic_execution_checked=True,
        spread_slippage_checked=True,
        comments="Completo"
    )

def get_sufficient_market_regime_checklist() -> MarketRegimeChecklist:
    return MarketRegimeChecklist(
        trend_tested=True,
        range_tested=True,
        high_volatility_tested=True,
        low_volatility_tested=True,
        session_variability_tested=True,
        comments="Suficiente"
    )

# ─────────────────────────────────────────────────────────────────────────────
# PRUEBAS UNITARIAS DE REGLAS DE NEGOCIO
# ─────────────────────────────────────────────────────────────────────────────

def test_1_robust_strategy():
    # T1: Estrategia robusta → PAPER_TRADING_READY
    validator = BacktestValidator()
    eval_result = validator.validate(
        metadata=get_base_metadata(AssetClass.FOREX),
        report=get_robust_report(),
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result.classification == StrategyClassification.PAPER_TRADING_READY
    assert eval_result.approved_for_real is False

def test_2_incomplete_biases():
    # T2: Sesgos incompletos → REJECTED
    validator = BacktestValidator()
    bias = get_complete_bias_checklist()
    bias.realistic_costs_checked = False  # Saltarse un check crítico

    eval_result = validator.validate(
        metadata=get_base_metadata(),
        report=get_robust_report(),
        bias_checklist=bias,
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result.classification == StrategyClassification.REJECTED
    assert "RECHAZO: Auditoria de sesgos" in eval_result.decision_reason

def test_3_low_trades_count():
    # T3: Pocas operaciones → REJECTED
    validator = BacktestValidator()
    report = get_robust_report()
    report.total_trades = 100  # Menos de 180 (Forex)

    eval_result = validator.validate(
        metadata=get_base_metadata(AssetClass.FOREX),
        report=report,
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result.classification == StrategyClassification.REJECTED
    assert "relevancia estadistica" in eval_result.decision_reason.lower() or "insuficiente" in eval_result.decision_reason.lower()

def test_4_low_pf_oos():
    # T4: PF OOS bajo → REJECTED
    validator = BacktestValidator()
    report = get_robust_report()
    report.profit_factor_oos = 1.15  # Menor que 1.25

    eval_result = validator.validate(
        metadata=get_base_metadata(),
        report=report,
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result.classification == StrategyClassification.REJECTED
    assert "Profit Factor OOS por debajo" in eval_result.decision_reason

def test_5_excessive_drawdown():
    # T5: Drawdown excesivo → REJECTED
    validator = BacktestValidator()
    report = get_robust_report()
    report.max_drawdown_pct = 15.0  # Límite Forex es 10.0%

    eval_result = validator.validate(
        metadata=get_base_metadata(AssetClass.FOREX),
        report=report,
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result.classification == StrategyClassification.REJECTED
    assert "Drawdown maximo de equidad superado" in eval_result.decision_reason

def test_6_insufficient_market_regimes():
    validator = BacktestValidator()
    
    # 6a. Falla crítica: No probó Tendencia (regimen core) → REJECTED
    regime_reject = get_sufficient_market_regime_checklist()
    regime_reject.trend_tested = False

    eval_result_reject = validator.validate(
        metadata=get_base_metadata(),
        report=get_robust_report(),
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=regime_reject
    )
    assert eval_result_reject.classification == StrategyClassification.REJECTED
    assert "Regimenes core" in eval_result_reject.decision_reason

    # 6b. Falla moderada: Tendencia y rango OK, pero falló volatilidad → OBSERVATION
    regime_obs = get_sufficient_market_regime_checklist()
    regime_obs.high_volatility_tested = False

    eval_result_obs = validator.validate(
        metadata=get_base_metadata(),
        report=get_robust_report(),
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=regime_obs
    )
    assert eval_result_obs.classification == StrategyClassification.OBSERVATION
    assert "OBSERVACION: Cobertura de regimenes incompleta" in eval_result_obs.decision_reason

def test_7_low_recovery_factor():
    # T7: Recovery Factor bajo → OBSERVATION
    validator = BacktestValidator()
    report = get_robust_report()
    report.recovery_factor = 2.5  # Límite es 3.0

    eval_result = validator.validate(
        metadata=get_base_metadata(),
        report=report,
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result.classification == StrategyClassification.OBSERVATION
    assert "Recovery Factor por debajo" in eval_result.decision_reason

def test_8_low_sharpe_or_sortino():
    # T8: Sharpe/Sortino bajos → OBSERVATION
    validator = BacktestValidator()
    
    # Sharpe bajo (1.0 < 1.20)
    report_sharpe = get_robust_report()
    report_sharpe.sharpe_ratio = 1.0

    eval_result_sharpe = validator.validate(
        metadata=get_base_metadata(),
        report=report_sharpe,
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result_sharpe.classification == StrategyClassification.OBSERVATION
    assert "Sharpe Ratio debil" in eval_result_sharpe.decision_reason

    # Sortino bajo (1.3 < 1.50)
    report_sortino = get_robust_report()
    report_sortino.sortino_ratio = 1.3

    eval_result_sortino = validator.validate(
        metadata=get_base_metadata(),
        report=report_sortino,
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result_sortino.classification == StrategyClassification.OBSERVATION
    assert "Sortino Ratio debil" in eval_result_sortino.decision_reason

def test_9_negative_expectancy():
    # T9: Esperanza matemática negativa → REJECTED
    validator = BacktestValidator()
    report = get_robust_report()
    report.expectancy = -0.5  # Negativo

    eval_result = validator.validate(
        metadata=get_base_metadata(),
        report=report,
        bias_checklist=get_complete_bias_checklist(),
        market_regime_checklist=get_sufficient_market_regime_checklist()
    )
    assert eval_result.classification == StrategyClassification.REJECTED
    assert "Esperanza matematica negativa" in eval_result.decision_reason

def test_10_approved_for_real_override_blocked():
    # T10: Intentar obtener approved_for_real=True es imposible
    # Intentamos comprobar que la estructura rechaza cualquier intento de inicializarse en True
    try:
        StrategyEvaluation(
            metadata=get_base_metadata(),
            backtest_report=get_robust_report(),
            bias_checklist=get_complete_bias_checklist(),
            market_regime_checklist=get_sufficient_market_regime_checklist(),
            classification=StrategyClassification.PAPER_TRADING_READY,
            decision_reason="Intento malicioso",
            approved_for_real=True,  # ESTO DEBE ARROJAR ERROR
            evaluated_at=datetime.now(timezone.utc),
            evaluator="Hacker"
        )
        raise AssertionError("Se permitio approved_for_real=True maliciosamente")
    except ValidationError:
        pass  # Bloqueado correctamente a nivel de Pydantic

# ─────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("EJECUTANDO PRUEBAS UNITARIAS DE BACKTEST_VALIDATOR (FASE 3.2)")
    print("=" * 60)
    
    run_test("T1 | Estrategia robusta -> PAPER_TRADING_READY", test_1_robust_strategy)
    run_test("T2 | Sesgos incompletos -> REJECTED", test_2_incomplete_biases)
    run_test("T3 | Pocas operaciones -> REJECTED", test_3_low_trades_count)
    run_test("T4 | PF OOS bajo -> REJECTED", test_4_low_pf_oos)
    run_test("T5 | Drawdown excesivo -> REJECTED", test_5_excessive_drawdown)
    run_test("T6 | Regimen de mercado insuficiente -> REJECTED o OBSERVATION", test_6_insufficient_market_regimes)
    run_test("T7 | Recovery Factor bajo -> OBSERVATION", test_7_low_recovery_factor)
    run_test("T8 | Sharpe/Sortino bajos -> OBSERVATION", test_8_low_sharpe_or_sortino)
    run_test("T9 | Esperanza matematica negativa -> REJECTED", test_9_negative_expectancy)
    run_test("T10 | approved_for_real=True es imposible", test_10_approved_for_real_override_blocked)
    
    print("=" * 60)
    total = passed + failed
    print(f"RESULTADO DE LAS PRUEBAS: {passed}/{total} PASADOS | {failed} FALLADOS")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)
