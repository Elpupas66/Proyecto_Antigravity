"""
core/backtest_validator.py
--------------------------
Validador de Backtests determinista para el Proyecto Antigravity.
Fase 3.2: Evalúa los reportes cuantitativos frente a los estándares
de STRATEGY_VALIDATION_FRAMEWORK.md y METRICS_STANDARD.md.

Sin red, sin base de datos, sin ejecución real.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from core.strategy_models import (
    AssetClass,
    StrategyClassification,
    StrategyMetadata,
    BacktestReport,
    BiasChecklist,
    MarketRegimeChecklist,
    StrategyEvaluation
)

class MetricThresholds(BaseModel):
    min_trades: int = 150
    min_pf_is: float = 1.40
    min_pf_oos: float = 1.25
    max_drawdown_pct: float = 12.0
    min_recovery_factor: float = 3.0
    min_sharpe: float = 1.20
    min_sortino: float = 1.50
    max_risk_of_ruin_pct: float = 0.10  # 0.1% (0.001) o 10% (0.10). En Monte Carlo es 0.1% = 0.001
    min_expectancy: float = 0.0

    @classmethod
    def get_default_thresholds(cls, asset_class: AssetClass) -> "MetricThresholds":
        """
        Retorna los umbrales conservadores oficiales según METRICS_STANDARD.md (Sección 6).
        """
        if asset_class == AssetClass.FOREX:
            return cls(
                min_trades=180,
                min_pf_is=1.40,
                min_pf_oos=1.25,
                max_drawdown_pct=10.0,
                min_recovery_factor=3.0,
                min_sharpe=1.20,
                min_sortino=1.50,
                max_risk_of_ruin_pct=0.10
            )
        elif asset_class == AssetClass.INDICES:
            return cls(
                min_trades=150,
                min_pf_is=1.45,
                min_pf_oos=1.30,
                max_drawdown_pct=8.0,
                min_recovery_factor=4.0,
                min_sharpe=1.30,
                min_sortino=1.60,
                max_risk_of_ruin_pct=0.10
            )
        elif asset_class == AssetClass.GOLD:
            return cls(
                min_trades=200,
                min_pf_is=1.50,
                min_pf_oos=1.35,
                max_drawdown_pct=12.0,
                min_recovery_factor=3.0,
                min_sharpe=1.10,
                min_sortino=1.40,
                max_risk_of_ruin_pct=0.10
            )
        elif asset_class == AssetClass.CRYPTO:
            return cls(
                min_trades=250,
                min_pf_is=1.60,
                min_pf_oos=1.40,
                max_drawdown_pct=15.0,
                min_recovery_factor=3.0,
                min_sharpe=1.00,
                min_sortino=1.30,
                max_risk_of_ruin_pct=0.10
            )
        else:
            # AssetClass.OTHER
            return cls()

class BacktestValidator:
    """
    Motor determinista para evaluar reportes de backtest e instrumentar clasificaciones.
    """

    def validate(
        self,
        metadata: StrategyMetadata,
        report: BacktestReport,
        bias_checklist: BiasChecklist,
        market_regime_checklist: MarketRegimeChecklist,
        thresholds: Optional[MetricThresholds] = None
    ) -> StrategyEvaluation:
        """
        Evalúa secuencialmente las 10 reglas del ecosistema de validación.
        Retorna un objeto StrategyEvaluation.
        """
        # Cargar umbrales adecuados (usar por defecto de la clase de activo si no se proveen)
        if thresholds is None:
            thresholds = MetricThresholds.get_default_thresholds(metadata.asset_class)

        classification = StrategyClassification.REJECTED
        decision_reasons = []
        is_rejected = False
        is_observation = False

        # ─── REGLA 1: AUDITORÍA DE SESGOS ───
        if not bias_checklist.is_complete:
            is_rejected = True
            decision_reasons.append("RECHAZO: Auditoria de sesgos incompleta o fallida (BiasChecklist.is_complete es False).")

        # ─── REGLA 2: COBERTURA DE REGÍMENES DE MERCADO ───
        if not market_regime_checklist.is_sufficient:
            # Según gravedad: Si no se probó ni tendencia ni rango (regímenes core), es REJECTED
            if not market_regime_checklist.trend_tested or not market_regime_checklist.range_tested:
                is_rejected = True
                decision_reasons.append("RECHAZO: Regimenes core (tendencia o rango) no probados.")
            else:
                is_observation = True
                decision_reasons.append("OBSERVACION: Cobertura de regimenes incompleta (is_sufficient es False, faltan pruebas de volatilidad).")

        # ─── REGLA 3: VOLUMEN DE TRADES MÍNIMO ───
        if report.total_trades < thresholds.min_trades:
            is_rejected = True
            decision_reasons.append(f"RECHAZO: Volumen transaccional insuficiente ({report.total_trades} < {thresholds.min_trades}).")

        # ─── REGLA 4: PROFIT FACTOR OUT-OF-SAMPLE (OOS) ───
        if report.profit_factor_oos < thresholds.min_pf_oos:
            is_rejected = True
            decision_reasons.append(f"RECHAZO: Profit Factor OOS por debajo del minimo ({report.profit_factor_oos:.2f} < {thresholds.min_pf_oos:.2f}).")

        # ─── REGLA 5: MAX DRAWDOWN MÁXIMO PERMITIDO ───
        if report.max_drawdown_pct > thresholds.max_drawdown_pct:
            is_rejected = True
            decision_reasons.append(f"RECHAZO: Drawdown maximo de equidad superado ({report.max_drawdown_pct:.1f}% > {thresholds.max_drawdown_pct:.1f}%).")

        # ─── REGLA EVITACIÓN DE ESPERANZA NEGATIVA ───
        if report.expectancy <= thresholds.min_expectancy:
            is_rejected = True
            decision_reasons.append(f"RECHAZO: Esperanza matematica negativa o nula ({report.expectancy:.2f} <= {thresholds.min_expectancy:.2f}).")

        # ─── REGLA 6: PROFIT FACTOR OOS ACEPTABLE PERO DÉBIL ───
        # Si no ha sido rechazada, pero el PF OOS es débil (e.g. inferior a min_pf_oos + 0.05)
        weak_pf_limit = thresholds.min_pf_oos + 0.05
        if not is_rejected and report.profit_factor_oos < weak_pf_limit:
            is_observation = True
            decision_reasons.append(f"OBSERVACION: Profit Factor OOS aceptable pero debil ({report.profit_factor_oos:.2f} < {weak_pf_limit:.2f}).")

        # ─── REGLA 7: RECOVERY FACTOR MÍNIMO ───
        if report.recovery_factor < thresholds.min_recovery_factor:
            is_observation = True
            decision_reasons.append(f"OBSERVACION: Recovery Factor por debajo de lo requerido ({report.recovery_factor:.2f} < {thresholds.min_recovery_factor:.2f}).")

        # ─── REGLA 8: RATIOS SHARPE / SORTINO ───
        if report.sharpe_ratio < thresholds.min_sharpe:
            is_observation = True
            decision_reasons.append(f"OBSERVACION: Sharpe Ratio debil ({report.sharpe_ratio:.2f} < {thresholds.min_sharpe:.2f}).")
        if report.sortino_ratio < thresholds.min_sortino:
            is_observation = True
            decision_reasons.append(f"OBSERVACION: Sortino Ratio debil ({report.sortino_ratio:.2f} < {thresholds.min_sortino:.2f}).")

        # ─── REGLA ADICIONAL: RIESGO DE RUINA MONTE CARLO ───
        if report.risk_of_ruin_pct > thresholds.max_risk_of_ruin_pct:
            is_observation = True
            decision_reasons.append(f"OBSERVACION: Riesgo de ruina elevado ({report.risk_of_ruin_pct:.2f}% > {thresholds.max_risk_of_ruin_pct:.2f}%).")

        # ─── RESOLUCIÓN DE CLASIFICACIÓN ───
        # D4: low_confidence de Monte Carlo bloquea PAPER_TRADING_READY y degrada a OBSERVATION
        is_low_confidence = False
        if report.monte_carlo_result and report.monte_carlo_result.low_confidence:
            is_low_confidence = True
            decision_reasons.append("OBSERVACION: Baja confianza en la simulacion Monte Carlo (< 30 trades).")

        if is_rejected:
            classification = StrategyClassification.REJECTED
        elif is_observation or is_low_confidence:
            classification = StrategyClassification.OBSERVATION
        else:
            classification = StrategyClassification.PAPER_TRADING_READY

        reason_text = " | ".join(decision_reasons) if decision_reasons else "Aprobado sin observaciones cuantitativas."

        return StrategyEvaluation(
            metadata=metadata,
            backtest_report=report,
            bias_checklist=bias_checklist,
            market_regime_checklist=market_regime_checklist,
            classification=classification,
            decision_reason=reason_text,
            approved_for_real=False,  # Enclavamiento estricto
            evaluated_at=datetime.now(timezone.utc),
            evaluator="BacktestValidator-Determinista"
        )
