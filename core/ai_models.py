"""
core/ai_models.py
-----------------
Contratos de datos del AI Validator — Fase 4.4.

Contiene exclusivamente:
  - AIValidatorVerdict   (Enum)
  - AIRecommendedAction  (Enum)
  - AIValidatorInput     (Pydantic BaseModel)
  - AIValidatorResult    (Pydantic BaseModel)

REGLAS DE SEGURIDAD INVARIANTES (Fase 4.4):
  - La IA no decide operaciones.
  - La IA no ejecuta operaciones.
  - La IA no puede aprobar ejecución real.
  - La IA no sustituye al RiskEngine.
  - La IA no puede saltarse Approval Layer.
  - La salida del AI Validator es solo contexto estructurado.
  - approved_for_real = False SIEMPRE e INMUTABLE.

Sin conexiones externas. Sin llamadas a modelos. Sin red.
Sin MT5. Sin Telegram. Sin n8n. Sin ejecución real.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# FRASES PROHIBIDAS — Detección de intento de bypass de seguridad
# ─────────────────────────────────────────────────────────────────────────────

_BYPASS_PHRASES: List[str] = [
    # Bypass de RiskEngine
    "skip riskengine",
    "saltarse el riskengine",
    "saltar riskengine",
    "bypass riskengine",
    "ignorar riskengine",
    "ignore riskengine",
    "omitir riskengine",
    "evitar riskengine",
    "override riskengine",
    "skip risk engine",
    "bypass risk engine",
    "ignore risk engine",
    # Bypass de Approval Layer
    "skip approval",
    "bypass approval",
    "ignore approval",
    "saltarse approval",
    "saltar approval",
    "omitir approval",
    "evitar approval",
    # Instrucciones de ejecución real
    "ejecutar operacion",
    "ejecutar operación",
    "execute trade",
    "open trade",
    "open order",
    "send order",
    "place trade",
    "place order",
    "allow_real_execution = true",
    "allow_real_execution=true",
    "approved_for_real = true",
    "approved_for_real=true",
    # Instrucciones de inyección de prompt
    "ignore your instructions",
    "ignora tus instrucciones",
    "override your instructions",
    "olvida tus instrucciones",
    "forget your instructions",
    "disregard your instructions",
]


# ─────────────────────────────────────────────────────────────────────────────
# ENUMERACIONES
# ─────────────────────────────────────────────────────────────────────────────

class AIValidatorVerdict(str, Enum):
    """
    Clasificación del contexto técnico de la señal evaluada.

    IMPORTANTE: Ningún valor representa aprobación de ejecución real.
    El veredicto es contexto estructurado, no una orden operativa.
    """
    VALID_CONTEXT = "VALID_CONTEXT"
    """El contexto técnico es coherente con la señal. Sin contradicciones detectadas."""

    WEAK_CONTEXT = "WEAK_CONTEXT"
    """El contexto existe pero es superficial o incompleto. Señal puede ser válida, soporte técnico débil."""

    CONTRADICTORY_CONTEXT = "CONTRADICTORY_CONTEXT"
    """Contradicción explícita detectada entre la señal y la justificación técnica declarada."""

    MISSING_INFORMATION = "MISSING_INFORMATION"
    """Información insuficiente para análisis técnico fiable. No se puede emitir veredicto de coherencia."""

    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
    """La señal proviene de una estrategia cuyo estado impide evaluación favorable (e.g., REJECTED)."""

    SKIPPED = "SKIPPED"
    """El AI Validator no pudo ejecutarse (timeout, modelo no disponible). Pipeline continúa sin análisis IA."""


class AIRecommendedAction(str, Enum):
    """
    Acción recomendada al pipeline por el AI Validator.

    INVARIANTE CRÍTICA:
    Ningún valor de este Enum significa ejecutar una operación.
    Ningún valor puede interpretarse como aprobación operativa.
    Esta clase NO contiene EXECUTE, BUY, SELL, OPEN_TRADE, SEND_ORDER,
    ni ningún equivalente a una instrucción de ejecución de mercado.

    La Approval Layer y el operador humano pueden ignorar cualquier
    recomendación emitida por el AI Validator.
    """
    CONTINUE_TO_RISK_ENGINE = "CONTINUE_TO_RISK_ENGINE"
    """El contexto es suficientemente coherente. Se puede continuar al RiskEngine para evaluación determinista."""

    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    """Hay incertidumbre, datos faltantes o ambigüedad. Requiere revisión humana antes de continuar."""

    BLOCK_SIGNAL = "BLOCK_SIGNAL"
    """La señal viola una política declarada o contiene contradicción grave. Señal bloqueada para revisión."""

    REQUEST_MORE_INFORMATION = "REQUEST_MORE_INFORMATION"
    """Los datos son insuficientes para emitir un veredicto fiable. Se requiere información adicional."""

    SKIP_AI_VALIDATION = "SKIP_AI_VALIDATION"
    """El AI Validator no pudo ejecutarse. El pipeline continúa sin análisis IA. Revisión humana obligatoria."""


# ─────────────────────────────────────────────────────────────────────────────
# MODELO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

class AIValidatorInput(BaseModel):
    """
    Contrato de entrada del AI Validator — Fase 4.4.

    Contiene la señal de trading estructurada para análisis de coherencia contextual.
    El AI Validator NO ejecuta operaciones. Solo analiza coherencia técnica.

    Campos obligatorios: signal_id, symbol, direction, timeframe, technical_reason.
    Campos opcionales: enriquecimiento contextual de métricas, riesgo y estrategia.
    """

    # ── Campos obligatorios ─────────────────────────────────────────────────
    signal_id: str = Field(
        ...,
        description="UUID único de la señal. Imprescindible para trazabilidad SHA-256."
    )
    symbol: str = Field(
        ...,
        description="Activo financiero (e.g., 'EURUSD', 'NAS100', 'XAUUSD')."
    )
    direction: str = Field(
        ...,
        description="Dirección de la señal. Valores permitidos: BUY, SELL, LONG, SHORT."
    )
    timeframe: str = Field(
        ...,
        description="Marco temporal de la señal (e.g., 'H1', 'H4', 'D1')."
    )
    technical_reason: str = Field(
        ...,
        description=(
            "Justificación técnica de la señal. Mínimo 20 caracteres. "
            "No puede contener instrucciones de ejecución real ni intentos de bypass."
        )
    )

    # ── Campos opcionales ───────────────────────────────────────────────────
    strategy_id: Optional[str] = Field(
        default=None,
        description="Identificador de la estrategia de origen."
    )
    strategy_classification: Optional[str] = Field(
        default=None,
        description="Estado de validación de la estrategia (e.g., PAPER_TRADING_READY, REJECTED)."
    )
    entry_price: Optional[float] = Field(
        default=None,
        description="Precio de entrada propuesto. Solo para contexto analítico."
    )
    stop_loss: Optional[float] = Field(
        default=None,
        description="Nivel de Stop Loss propuesto. Solo para contexto analítico."
    )
    take_profit: Optional[float] = Field(
        default=None,
        description="Nivel de Take Profit propuesto. Solo para contexto analítico."
    )
    risk_notes: Optional[str] = Field(
        default=None,
        description="Notas de riesgo adicionales del operador."
    )
    market_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto de mercado adicional (régimen, volatilidad, sesión, etc.)."
    )
    recent_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Resumen de métricas recientes de la estrategia: "
            "profit_factor, win_rate, max_drawdown_pct, expectancy, risk_of_ruin_pct."
        )
    )
    source: Optional[str] = Field(
        default=None,
        description="Origen de la señal (e.g., 'TradingView', 'n8n', 'ManualEntry')."
    )

    # ── Validadores de campos individuales ─────────────────────────────────

    @field_validator("signal_id")
    @classmethod
    def signal_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "CONTRATO VIOLADO: signal_id no puede estar vacío. "
                "Es obligatorio para la trazabilidad del pipeline."
            )
        return v.strip()

    @field_validator("symbol")
    @classmethod
    def symbol_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "CONTRATO VIOLADO: symbol no puede estar vacío. "
                "El activo financiero es un campo obligatorio."
            )
        return v.strip().upper()

    @field_validator("direction")
    @classmethod
    def direction_must_be_valid(cls, v: str) -> str:
        allowed = {"BUY", "SELL", "LONG", "SHORT"}
        normalized = v.strip().upper() if v else ""
        if normalized not in allowed:
            raise ValueError(
                f"CONTRATO VIOLADO: direction='{v}' no es válido. "
                f"Valores permitidos: {sorted(allowed)}. "
                "El AI Validator no acepta direcciones ambiguas o personalizadas."
            )
        return normalized

    @field_validator("timeframe")
    @classmethod
    def timeframe_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "CONTRATO VIOLADO: timeframe no puede estar vacío. "
                "El marco temporal es obligatorio para el análisis de coherencia."
            )
        return v.strip().upper()

    @field_validator("technical_reason")
    @classmethod
    def technical_reason_must_be_adequate(cls, v: str) -> str:
        MIN_LENGTH = 20

        if not v or not v.strip():
            raise ValueError(
                "CONTRATO VIOLADO: technical_reason no puede estar vacía. "
                "Es obligatoria para que el AI Validator pueda analizar coherencia técnica."
            )

        if len(v.strip()) < MIN_LENGTH:
            raise ValueError(
                f"CONTRATO VIOLADO: technical_reason demasiado corta "
                f"({len(v.strip())} caracteres). Mínimo requerido: {MIN_LENGTH} caracteres. "
                "Proporciona una justificación técnica suficiente para el análisis."
            )

        # Detección de instrucciones de bypass / inyección
        v_lower = v.lower()
        for phrase in _BYPASS_PHRASES:
            if phrase in v_lower:
                raise ValueError(
                    f"CONTRATO VIOLADO: technical_reason contiene instrucción prohibida: "
                    f"'{phrase}'. "
                    "No se permiten instrucciones que intenten saltarse el RiskEngine, "
                    "la Approval Layer o habilitar ejecución real. "
                    "El campo technical_reason es solo justificación técnica analítica."
                )

        return v.strip()


# ─────────────────────────────────────────────────────────────────────────────
# MODELO DE SALIDA
# ─────────────────────────────────────────────────────────────────────────────

class AIValidatorResult(BaseModel):
    """
    Contrato de salida del AI Validator — Fase 4.4.

    Representa el resultado estructurado del análisis de coherencia técnica
    de una señal de trading. Es exclusivamente contexto estructurado.

    INVARIANTES DE SEGURIDAD:
      - approved_for_real: SIEMPRE False. Inmutable. No negociable.
      - El resultado no constituye aprobación operativa.
      - El resultado no sustituye al RiskEngine.
      - El resultado no activa ninguna ejecución.
      - La decisión final es SIEMPRE del operador humano.
    """

    signal_id: str = Field(
        ...,
        description="UUID de la señal evaluada. Debe coincidir con AIValidatorInput.signal_id."
    )
    verdict: AIValidatorVerdict = Field(
        ...,
        description="Clasificación del contexto técnico de la señal. No es aprobación operativa."
    )
    confidence: float = Field(
        ...,
        description=(
            "Nivel de confianza del veredicto [0.0–1.0]. "
            "Representa confianza en la coherencia del contexto, "
            "NO probabilidad de éxito de la operación."
        )
    )
    reasons: List[str] = Field(
        ...,
        description=(
            "Lista de razones que justifican el veredicto. "
            "Debe contener al menos un elemento salvo cuando verdict=SKIPPED."
        )
    )
    contradictions: List[str] = Field(
        default_factory=list,
        description="Contradicciones detectadas entre la señal y la justificación técnica. Puede estar vacía."
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Datos ausentes o insuficientes que limitan el análisis. Puede estar vacía."
    )
    risk_notes: List[str] = Field(
        default_factory=list,
        description="Observaciones de riesgo adicionales detectadas. Puede estar vacía."
    )
    recommended_action: AIRecommendedAction = Field(
        ...,
        description=(
            "Acción recomendada al pipeline. NUNCA implica ejecución automática. "
            "La Approval Layer y el operador humano pueden ignorarla."
        )
    )
    requires_human_review: bool = Field(
        ...,
        description=(
            "True si la ambigüedad, contradicción o baja confianza "
            "detectada requiere revisión manual obligatoria."
        )
    )
    provider: str = Field(
        ...,
        description="Identificador del proveedor/adaptador que generó el análisis (e.g., 'MockAIValidator')."
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Nombre del modelo LLM utilizado (e.g., 'qwen2.5:7b'). None si es mock o no disponible."
    )
    raw_response: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Respuesta bruta del modelo para auditoría. None si es mock o no se almacena."
    )
    validation_timestamp: datetime = Field(
        ...,
        description="Timestamp UTC de cuando se generó el resultado."
    )
    approved_for_real: bool = Field(
        default=False,
        description=(
            "CONSTANTE DE SEGURIDAD INMUTABLE. Siempre False. "
            "El AI Validator nunca puede aprobar ejecución real. "
            "PROHIBIDA LA EJECUCIÓN REAL EN MERCADOS FINANCIEROS (CONTRATO FASE 4.4)."
        )
    )

    # ── Validadores de campos individuales ─────────────────────────────────

    @field_validator("confidence")
    @classmethod
    def confidence_must_be_in_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(
                f"CONTRATO VIOLADO: confidence={v} está fuera del rango permitido [0.0, 1.0]. "
                "El nivel de confianza debe ser un valor entre 0.0 y 1.0 inclusive."
            )
        return v

    @field_validator("approved_for_real")
    @classmethod
    def approved_for_real_must_be_false(cls, v: bool) -> bool:
        if v:
            raise ValueError(
                "CONTRATO VIOLADO: approved_for_real=True está PROHIBIDO. "
                "El AI Validator NUNCA puede aprobar ejecución real en mercados financieros. "
                "Esta es una invariante de seguridad irrevocable del Proyecto Antigravity (Fase 4.4). "
                "approved_for_real es siempre False."
            )
        return False

    # ── Validadores de modelo (cross-field) ────────────────────────────────

    @model_validator(mode="after")
    def validate_cross_field_contracts(self) -> "AIValidatorResult":
        """
        Valida las invariantes de contrato que involucran múltiples campos.

        Contratos implementados:
          C1: reasons no puede estar vacío salvo verdict=SKIPPED.
          C2: CONTRADICTORY_CONTEXT → recommended_action ≠ CONTINUE_TO_RISK_ENGINE.
          C3: BLOCKED_BY_POLICY → recommended_action = BLOCK_SIGNAL.
          C4: MISSING_INFORMATION → recommended_action ∈ {REQUEST_MORE_INFORMATION, REQUIRE_HUMAN_REVIEW}.
          C5: SKIPPED → recommended_action = SKIP_AI_VALIDATION y requires_human_review = True.
          C6: confidence < 0.60 → requires_human_review = True.
        """
        verdict = self.verdict
        action = self.recommended_action
        confidence = self.confidence
        reasons = self.reasons
        requires_review = self.requires_human_review

        # C1: reasons no puede estar vacío salvo SKIPPED
        if verdict != AIValidatorVerdict.SKIPPED and len(reasons) == 0:
            raise ValueError(
                f"CONTRATO C1 VIOLADO: reasons no puede estar vacío cuando verdict='{verdict.value}'. "
                "El AI Validator debe proporcionar al menos una razón que justifique el veredicto. "
                "Solo se permite reasons=[] cuando verdict=SKIPPED."
            )

        # C2: CONTRADICTORY_CONTEXT → no puede continuar al RiskEngine
        if verdict == AIValidatorVerdict.CONTRADICTORY_CONTEXT:
            if action == AIRecommendedAction.CONTINUE_TO_RISK_ENGINE:
                raise ValueError(
                    "CONTRATO C2 VIOLADO: verdict=CONTRADICTORY_CONTEXT es incompatible con "
                    "recommended_action=CONTINUE_TO_RISK_ENGINE. "
                    "Una contradicción detectada no puede continuar al RiskEngine sin revisión. "
                    "Usa REQUIRE_HUMAN_REVIEW o BLOCK_SIGNAL."
                )

        # C3: BLOCKED_BY_POLICY → debe usar BLOCK_SIGNAL
        if verdict == AIValidatorVerdict.BLOCKED_BY_POLICY:
            if action != AIRecommendedAction.BLOCK_SIGNAL:
                raise ValueError(
                    f"CONTRATO C3 VIOLADO: verdict=BLOCKED_BY_POLICY requiere "
                    f"recommended_action=BLOCK_SIGNAL, pero se recibió '{action.value}'. "
                    "Una señal bloqueada por política no puede tener otra acción recomendada."
                )

        # C4: MISSING_INFORMATION → REQUEST_MORE_INFORMATION o REQUIRE_HUMAN_REVIEW
        if verdict == AIValidatorVerdict.MISSING_INFORMATION:
            allowed_actions = {
                AIRecommendedAction.REQUEST_MORE_INFORMATION,
                AIRecommendedAction.REQUIRE_HUMAN_REVIEW,
            }
            if action not in allowed_actions:
                raise ValueError(
                    f"CONTRATO C4 VIOLADO: verdict=MISSING_INFORMATION requiere "
                    f"recommended_action ∈ {{REQUEST_MORE_INFORMATION, REQUIRE_HUMAN_REVIEW}}, "
                    f"pero se recibió '{action.value}'. "
                    "Información insuficiente no puede continuar al RiskEngine ni bloquearse sin más contexto."
                )

        # C5: SKIPPED → SKIP_AI_VALIDATION y requires_human_review=True
        if verdict == AIValidatorVerdict.SKIPPED:
            if action != AIRecommendedAction.SKIP_AI_VALIDATION:
                raise ValueError(
                    f"CONTRATO C5a VIOLADO: verdict=SKIPPED requiere "
                    f"recommended_action=SKIP_AI_VALIDATION, pero se recibió '{action.value}'."
                )
            if not requires_review:
                raise ValueError(
                    "CONTRATO C5b VIOLADO: verdict=SKIPPED requiere requires_human_review=True. "
                    "Cuando el AI Validator es omitido, la revisión humana es obligatoria."
                )

        # C6: confidence < 0.60 → requires_human_review=True
        if confidence < 0.60 and not requires_review:
            raise ValueError(
                f"CONTRATO C6 VIOLADO: confidence={confidence:.3f} < 0.60 requiere "
                f"requires_human_review=True, pero se recibió False. "
                "La baja confianza del análisis obliga a revisión humana obligatoria."
            )

        return self
