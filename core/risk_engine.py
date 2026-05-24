"""
core/risk_engine.py
-------------------
Motor de Riesgo Determinista (T2.1)

Responsabilidad exclusiva: evaluar si un TradeIntent cumple todas las
reglas de seguridad. NO llama a la red, NO se comunica con MT5,
NO invoca IA, NO tiene efectos externos. Solo lógica pura y retorno
de un RiskResult.

Reglas implementadas (ID → descripción):
  R1  - Bloqueo de ejecución real en entorno no autorizado.
  R2  - Aprobación de usuario obligatoria si REQUIRE_APPROVAL=True.
  R3  - Límite de pérdida diaria.
  R4  - Límite de operaciones concurrentes.
  R5  - UUID obligatorio.
  R6  - Campos mínimos: símbolo, dirección, volumen, precio de entrada.
"""

from core.models import TradeIntent, AccountState, RiskResult


# Peso de cada regla para el cálculo del risk_score (0.0 = sin riesgo, 1.0 = máximo)
_RULE_WEIGHTS: dict[str, float] = {
    "R1_REAL_EXECUTION_BLOCKED": 1.0,   # Crítico: siempre bloquea
    "R2_APPROVAL_REQUIRED":      1.0,   # Crítico: siempre bloquea
    "R3_DAILY_LOSS_EXCEEDED":    0.9,
    "R4_MAX_TRADES_EXCEEDED":    0.7,
    "R5_MISSING_UUID":           1.0,   # Crítico: trazabilidad rota
    "R6_MISSING_FIELDS":         0.8,
}


class RiskEngine:
    """
    Evaluador determinista de riesgo para un TradeIntent.

    Uso:
        engine = RiskEngine()
        result = engine.evaluate(intent, account)
        if result.approved:
            ...
    """

    def evaluate(self, intent: TradeIntent, account: AccountState) -> RiskResult:
        """
        Evalúa el intent contra el estado de cuenta.

        Retorna un RiskResult con:
          - approved     : bool
          - reason       : str  (resumen legible)
          - failed_rules : list[str]  (IDs de reglas fallidas)
          - risk_score   : float (0.0 aprobado sin riesgos, 1.0 riesgo máximo)
        """
        failed_rules: list[str] = []

        # ── R5: UUID obligatorio ──────────────────────────────────────────────
        if not intent.id or intent.id.strip() == "":
            failed_rules.append("R5_MISSING_UUID")

        # ── R6: Campos mínimos ────────────────────────────────────────────────
        missing_fields = []
        if not intent.symbol:
            missing_fields.append("symbol")
        if not intent.action:
            missing_fields.append("action")
        if intent.lot_size is None or intent.lot_size <= 0:
            missing_fields.append("lot_size")
        if intent.entry_price is None or intent.entry_price <= 0:
            missing_fields.append("entry_price")
        if missing_fields:
            failed_rules.append(f"R6_MISSING_FIELDS:{','.join(missing_fields)}")

        # ── R1: Ejecución real bloqueada ──────────────────────────────────────
        if intent.is_real_execution_intent and not account.allow_real_execution:
            failed_rules.append("R1_REAL_EXECUTION_BLOCKED")

        # ── R2: Aprobación de usuario obligatoria ─────────────────────────────
        if account.require_approval and not intent.is_user_approved:
            failed_rules.append("R2_APPROVAL_REQUIRED")

        # ── R3: Límite de pérdida diaria ──────────────────────────────────────
        if account.daily_loss_pct >= account.max_daily_loss_pct:
            failed_rules.append("R3_DAILY_LOSS_EXCEEDED")

        # ── R4: Máximo de operaciones concurrentes ────────────────────────────
        if account.open_trades >= account.max_concurrent_trades:
            failed_rules.append("R4_MAX_TRADES_EXCEEDED")

        # ── Cálculo de risk_score ─────────────────────────────────────────────
        if failed_rules:
            # El score es el máximo peso de las reglas fallidas
            score = max(
                _RULE_WEIGHTS.get(r.split(":")[0], 0.5)
                for r in failed_rules
            )
        else:
            score = 0.0

        # ── Resultado final ───────────────────────────────────────────────────
        approved = len(failed_rules) == 0

        if approved:
            reason = "Todas las reglas de riesgo superadas. Intent autorizado para proceder."
        else:
            readable = [r.split(":")[0] for r in failed_rules]
            reason = f"Intent rechazado. Reglas fallidas: {', '.join(readable)}."

        return RiskResult(
            approved=approved,
            reason=reason,
            failed_rules=failed_rules,
            risk_score=round(score, 2),
        )
