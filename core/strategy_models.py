"""
core/strategy_models.py
-----------------------
Modelos Pydantic del Ecosistema de Evaluación de Estrategias.
Fase 3: Contratos de datos cuantitativos puros e instrumentación.

Sin integraciones, sin base de datos, sin ejecución real.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator

class StrategyClassification(str, Enum):
    REJECTED = "REJECTED"
    OBSERVATION = "OBSERVATION"
    PAPER_TRADING_READY = "PAPER_TRADING_READY"
    APPROVED_FOR_DEMO = "APPROVED_FOR_DEMO"
    BLOCKED_FOR_REAL = "BLOCKED_FOR_REAL"

class AssetClass(str, Enum):
    FOREX = "FOREX"
    INDICES = "INDICES"
    GOLD = "GOLD"
    CRYPTO = "CRYPTO"
    OTHER = "OTHER"

class StrategyMetadata(BaseModel):
    strategy_id: str
    name: str
    version: str
    config_hash: str
    author_or_source: str
    asset: str
    asset_class: AssetClass
    timeframe: str
    created_at: datetime
    notes: Optional[str] = None

class BacktestPeriod(BaseModel):
    start_date: datetime
    end_date: datetime
    label: str  # e.g., IS, OOS, PAPER

class TradeDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradeRecord(BaseModel):
    ticket: str = Field(..., description="ID de transacción único")
    symbol: str = Field(..., description="Activo financiero")
    open_time: datetime = Field(..., description="Fecha de apertura")
    close_time: datetime = Field(..., description="Fecha de cierre")
    direction: TradeDirection = Field(..., description="Dirección BUY/SELL")
    volume: float = Field(..., gt=0.0, description="Volumen en lotes")
    open_price: float = Field(..., gt=0.0, description="Precio de apertura")
    close_price: float = Field(..., gt=0.0, description="Precio de cierre")
    commission: float = Field(default=0.0, description="Comisión del broker")
    swap: float = Field(default=0.0, description="Swap cargado")
    profit_loss: float = Field(..., description="Resultado neto o bruto del trade")
    slippage: Optional[float] = Field(default=None, description="Slippage experimentado")

class CalculatedMetrics(BaseModel):
    total_trades: int = Field(..., description="Número total de trades analizados")
    profit_factor: float = Field(..., description="Factor de beneficio neto recalculado")
    expectancy: float = Field(..., description="Esperanza matemática de beneficio por trade")
    average_win: float = Field(..., description="Ganancia promedio")
    average_loss: float = Field(..., description="Pérdida promedio")
    win_rate: float = Field(..., description="Porcentaje de operaciones ganadoras")
    max_winning_streak: int = Field(..., description="Racha máxima de ganancias consecutivas")
    max_losing_streak: int = Field(..., description="Racha máxima de pérdidas consecutivas")
    max_daily_loss: float = Field(..., description="Pérdida máxima acumulada en un único día natural")
    max_daily_loss_pct: float = Field(..., description="Pérdida diaria máxima relativa al balance inicial")
    max_simultaneous_trades: int = Field(..., description="Exposición simultánea máxima de trades")
    sortino_ratio: float = Field(..., description="Sortino Ratio aproximado trade-based")
    cost_per_trade: float = Field(..., description="Cargos medios (comisión + swap) por trade")

class MonteCarloResult(BaseModel):
    risk_of_ruin_pct: float = Field(..., description="Fracción de simulaciones que alcanzaron la ruina")
    worst_case_drawdown: float = Field(..., description="Drawdown máximo absoluto observado")
    worst_case_drawdown_pct: float = Field(..., description="Drawdown máximo en porcentaje sobre equity inicial")
    monte_carlo_max_drawdown_p50: float = Field(..., description="Mediana del drawdown máximo")
    monte_carlo_max_drawdown_p95: float = Field(..., description="Percentil 95 del drawdown máximo")
    monte_carlo_max_drawdown_p99: float = Field(..., description="Percentil 99 del drawdown máximo")
    median_final_equity: float = Field(..., description="Mediana del equity final")
    p05_final_equity: float = Field(..., description="Percentil 5 del equity final")
    p95_final_equity: float = Field(..., description="Percentil 95 del equity final")
    mean_final_equity: float = Field(..., description="Media del equity final")
    max_losing_streak_p95: int = Field(..., description="Percentil 95 de la racha máxima de pérdidas")
    max_losing_streak_p99: int = Field(..., description="Percentil 99 de la racha máxima de pérdidas")
    n_simulations: int = Field(..., description="Número de simulaciones ejecutadas")
    method: str = Field(..., description="Método de remuestreo (bootstrap/shuffle)")
    seed: Optional[int] = Field(default=None, description="Semilla utilizada")
    n_trades_input: int = Field(..., description="Número de trades de entrada")
    low_confidence: bool = Field(..., description="Flag de baja confianza (< 30 trades)")
    initial_equity: float = Field(..., description="Equity inicial de simulación")
    ruin_threshold_pct: float = Field(..., description="Umbral de ruina configurado")
    computed_at: datetime = Field(..., description="Timestamp UTC del cálculo")
    approved_for_real: bool = Field(default=False, description="Flag de seguridad inmutable")

    @field_validator("approved_for_real")
    @classmethod
    def force_false_always(cls, v: bool) -> bool:
        if v:
            raise ValueError("PROHIBIDA LA EJECUCIÓN REAL EN MERCADOS FINANCIEROS (CONTRATO DE SEGURIDAD FASE 4.2B)")
        return False

class BacktestReport(BaseModel):
    strategy_id: str
    version: str
    data_source: str
    in_sample_period: BacktestPeriod
    out_of_sample_period: BacktestPeriod
    total_trades: int
    profit_factor_is: float
    profit_factor_oos: float
    max_drawdown_pct: float
    recovery_factor: float
    sharpe_ratio: float
    sortino_ratio: float
    expectancy: float
    average_win: float
    average_loss: float
    win_rate: float
    max_losing_streak: int
    max_daily_loss_pct: float
    simultaneous_exposure_pct: float
    risk_of_ruin_pct: float
    average_slippage: float
    average_trade_cost: float
    raw_metrics: Optional[Dict[str, Any]] = None
    calculated_metrics: Optional[CalculatedMetrics] = None
    monte_carlo_result: Optional[MonteCarloResult] = None

class BiasChecklist(BaseModel):
    look_ahead_bias_checked: bool
    survivorship_bias_checked: bool
    data_snooping_checked: bool
    overfitting_checked: bool
    curve_fitting_checked: bool
    selection_bias_checked: bool
    period_bias_checked: bool
    realistic_costs_checked: bool
    realistic_execution_checked: bool
    spread_slippage_checked: bool
    comments: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        """
        Devuelve True solo si todos los checks obligatorios están en True.
        """
        return all([
            self.look_ahead_bias_checked,
            self.survivorship_bias_checked,
            self.data_snooping_checked,
            self.overfitting_checked,
            self.curve_fitting_checked,
            self.selection_bias_checked,
            self.period_bias_checked,
            self.realistic_costs_checked,
            self.realistic_execution_checked,
            self.spread_slippage_checked
        ])

class MarketRegimeChecklist(BaseModel):
    trend_tested: bool
    range_tested: bool
    high_volatility_tested: bool
    low_volatility_tested: bool
    session_variability_tested: bool
    multi_asset_tested: Optional[bool] = None
    comments: Optional[str] = None

    @property
    def is_sufficient(self) -> bool:
        """
        Devuelve True si al menos tendencia, rango, alta y baja volatilidad están testeados.
        """
        return all([
            self.trend_tested,
            self.range_tested,
            self.high_volatility_tested,
            self.low_volatility_tested
        ])

class StrategyEvaluation(BaseModel):
    metadata: StrategyMetadata
    backtest_report: BacktestReport
    bias_checklist: BiasChecklist
    market_regime_checklist: MarketRegimeChecklist
    classification: StrategyClassification
    decision_reason: str
    approved_for_real: bool = Field(default=False)
    evaluated_at: datetime
    evaluator: str
    notes: Optional[str] = None

    @field_validator("approved_for_real")
    @classmethod
    def force_false_always(cls, v: bool) -> bool:
        if v:
            raise ValueError("PROHIBIDA LA EJECUCIÓN REAL EN MERCADOS FINANCIEROS (CONTRATO DE SEGURIDAD FASE 3)")
        return False
