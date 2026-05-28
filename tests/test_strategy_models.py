"""
tests/test_strategy_models.py
------------------------------
Pruebas unitarias de los modelos Pydantic de evaluación de estrategias.
Fase 3: Contratos de datos cuantitativos puros e instrumentación.

Ejecutar con: python tests/test_strategy_models.py
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
# MOCKS Y HELPERS DE DATOS
# ─────────────────────────────────────────────────────────────────────────────

def get_valid_metadata():
    return StrategyMetadata(
        strategy_id="ST-TREND-001",
        name="Trend Follower SP500",
        version="1.0.0",
        config_hash="a1b2c3d4e5f6",
        author_or_source="QuantTeam",
        asset="SPY",
        asset_class=AssetClass.INDICES,
        timeframe="H4",
        created_at=datetime.now(timezone.utc),
        notes="Estrategia tendencial de prueba académica"
    )

def get_valid_period(label: str):
    return BacktestPeriod(
        start_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2023, 12, 31, tzinfo=timezone.utc),
        label=label
    )

def get_valid_report():
    return BacktestReport(
        strategy_id="ST-TREND-001",
        version="1.0.0",
        data_source="MetaTrader 5",
        in_sample_period=get_valid_period("IS"),
        out_of_sample_period=get_valid_period("OOS"),
        total_trades=150,
        profit_factor_is=1.45,
        profit_factor_oos=1.28,
        max_drawdown_pct=8.5,
        recovery_factor=4.2,
        sharpe_ratio=1.35,
        sortino_ratio=1.65,
        expectancy=15.2,
        average_win=45.0,
        average_loss=-30.0,
        win_rate=0.42,
        max_losing_streak=6,
        max_daily_loss_pct=1.5,
        simultaneous_exposure_pct=2.0,
        risk_of_ruin_pct=0.02,
        average_slippage=1.2,
        average_trade_cost=0.06
    )

def get_valid_bias_checklist(all_true: bool = True):
    return BiasChecklist(
        look_ahead_bias_checked=all_true,
        survivorship_bias_checked=all_true,
        data_snooping_checked=all_true,
        overfitting_checked=all_true,
        curve_fitting_checked=all_true,
        selection_bias_checked=all_true,
        period_bias_checked=all_true,
        realistic_costs_checked=all_true,
        realistic_execution_checked=all_true,
        spread_slippage_checked=all_true,
        comments="Auditoría de sesgos completada satisfactoriamente" if all_true else "Incompleto"
    )

def get_valid_market_regime_checklist(trend=True, range_val=True, high_vol=True, low_vol=True):
    return MarketRegimeChecklist(
        trend_tested=trend,
        range_tested=range_val,
        high_volatility_tested=high_vol,
        low_volatility_tested=low_vol,
        session_variability_tested=True,
        multi_asset_tested=False,
        comments="Regímenes de mercado clave analizados"
    )

# ─────────────────────────────────────────────────────────────────────────────
# TESTS OBLIGATORIOS
# ─────────────────────────────────────────────────────────────────────────────

def test_1_valid_evaluation():
    eval_obj = StrategyEvaluation(
        metadata=get_valid_metadata(),
        backtest_report=get_valid_report(),
        bias_checklist=get_valid_bias_checklist(True),
        market_regime_checklist=get_valid_market_regime_checklist(),
        classification=StrategyClassification.PAPER_TRADING_READY,
        decision_reason="Cumple ampliamente con todos los criterios del Metrics Standard",
        evaluated_at=datetime.now(timezone.utc),
        evaluator="Architect-Core"
    )
    assert eval_obj.metadata.strategy_id == "ST-TREND-001"
    assert eval_obj.classification == StrategyClassification.PAPER_TRADING_READY

def test_2_missing_strategy_id():
    try:
        StrategyMetadata(
            strategy_id=None,
            name="Fail Strategy",
            version="1.0.0",
            config_hash="abc",
            author_or_source="Test",
            asset="EURUSD",
            asset_class=AssetClass.FOREX,
            timeframe="M15",
            created_at=datetime.now(timezone.utc)
        )
        raise AssertionError("Se esperaba una ValidationError debido a strategy_id=None")
    except ValidationError:
        pass

def test_3_invalid_classification():
    try:
        StrategyEvaluation(
            metadata=get_valid_metadata(),
            backtest_report=get_valid_report(),
            bias_checklist=get_valid_bias_checklist(True),
            market_regime_checklist=get_valid_market_regime_checklist(),
            classification="SUPER_LIVE_REAL_EXECUTION",
            decision_reason="Test inválido",
            evaluated_at=datetime.now(timezone.utc),
            evaluator="Tester"
        )
        raise AssertionError("Se esperaba una ValidationError por clasificación incorrecta")
    except ValidationError:
        pass

def test_4_bias_checklist_complete():
    checklist = get_valid_bias_checklist(True)
    assert checklist.is_complete is True

def test_5_bias_checklist_incomplete():
    checklist = get_valid_bias_checklist(True)
    checklist.overfitting_checked = False
    assert checklist.is_complete is False

def test_6_market_regime_checklist_sufficient():
    checklist_ok = get_valid_market_regime_checklist(True, True, True, True)
    assert checklist_ok.is_sufficient is True

    checklist_fail = get_valid_market_regime_checklist(True, True, False, True)
    assert checklist_fail.is_sufficient is False

def test_7_approved_for_real_default_and_restriction():
    eval_obj = StrategyEvaluation(
        metadata=get_valid_metadata(),
        backtest_report=get_valid_report(),
        bias_checklist=get_valid_bias_checklist(True),
        market_regime_checklist=get_valid_market_regime_checklist(),
        classification=StrategyClassification.PAPER_TRADING_READY,
        decision_reason="Cumple criterios",
        evaluated_at=datetime.now(timezone.utc),
        evaluator="Tester"
    )
    assert eval_obj.approved_for_real is False

    try:
        StrategyEvaluation(
            metadata=get_valid_metadata(),
            backtest_report=get_valid_report(),
            bias_checklist=get_valid_bias_checklist(True),
            market_regime_checklist=get_valid_market_regime_checklist(),
            classification=StrategyClassification.PAPER_TRADING_READY,
            decision_reason="Intento malicioso",
            approved_for_real=True,
            evaluated_at=datetime.now(timezone.utc),
            evaluator="MaliciousUser"
        )
        raise AssertionError("Se esperaba una ValidationError al intentar setear approved_for_real=True")
    except ValidationError:
        pass

def test_8_complete_paper_trading_ready_example():
    eval_obj = StrategyEvaluation(
        metadata=get_valid_metadata(),
        backtest_report=get_valid_report(),
        bias_checklist=get_valid_bias_checklist(True),
        market_regime_checklist=get_valid_market_regime_checklist(),
        classification=StrategyClassification.PAPER_TRADING_READY,
        decision_reason="Todos los tests cuantitativos de sesgos superados. Backtest reporta un profit factor IS de 1.45 y OOS de 1.28 con 150 operaciones.",
        evaluated_at=datetime.now(timezone.utc),
        evaluator="Director Tecnico Antigravity"
    )
    assert eval_obj.classification == StrategyClassification.PAPER_TRADING_READY
    assert eval_obj.approved_for_real is False

# ─────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("EJECUTANDO PRUEBAS UNITARIAS DE MODELOS PYDANTIC (FASE 3 - ASCII)")
    print("=" * 60)
    
    run_test("T1 | Creacion de StrategyEvaluation valida", test_1_valid_evaluation)
    run_test("T2 | Falta de strategy_id produce error de validacion", test_2_missing_strategy_id)
    run_test("T3 | StrategyClassification invalida produce error", test_3_invalid_classification)
    run_test("T4 | BiasChecklist.is_complete es True si todo esta verificado", test_4_bias_checklist_complete)
    run_test("T5 | BiasChecklist.is_complete es False si falta algun check", test_5_bias_checklist_incomplete)
    run_test("T6 | MarketRegimeChecklist.is_sufficient funciona correctamente", test_6_market_regime_checklist_sufficient)
    run_test("T7 | approved_for_real es False por defecto y bloquea intentos de True", test_7_approved_for_real_default_and_restriction)
    run_test("T8 | Ejemplo completo en PAPER_TRADING_READY", test_8_complete_paper_trading_ready_example)
    
    print("=" * 60)
    total = passed + failed
    print(f"RESULTADO DE LAS PRUEBAS: {passed}/{total} PASADOS | {failed} FALLADOS")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

