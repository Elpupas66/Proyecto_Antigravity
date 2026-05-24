"""
tests/test_risk_engine.py
--------------------------
Pruebas unitarias del RiskEngine determinista (T2.1).

Sin red, sin MT5, sin IA. Solo datos mockeados y lógica pura.
Ejecutar con: python tests/test_risk_engine.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.risk_engine import RiskEngine
from core.models import TradeIntent, AccountState

# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────

engine = RiskEngine()
passed = 0
failed = 0

def run_test(name: str, result, expect_approved: bool):
    global passed, failed
    ok = result.approved == expect_approved
    status = "✅ PASS" if ok else "❌ FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"{status} | {name}")
    print(f"       approved={result.approved} | score={result.risk_score}")
    print(f"       reason={result.reason}")
    if result.failed_rules:
        print(f"       failed_rules={result.failed_rules}")
    print()

# ─────────────────────────────────────────────────────────────────────────────
# ACCOUNT BASE: demo, sin pérdidas, con slots libres
# ─────────────────────────────────────────────────────────────────────────────
account_demo = AccountState(
    balance=10000.0,
    equity=10000.0,
    daily_loss_pct=0.5,
    open_trades=1,
    max_daily_loss_pct=2.0,
    max_concurrent_trades=3,
    allow_real_execution=False,
    require_approval=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Trade válido en modo demo, usuario ha aprobado → APPROVED
# R2 exige aprobación → ponemos is_user_approved=True
# ─────────────────────────────────────────────────────────────────────────────
intent_valid = TradeIntent(
    signal_id="signal-001",
    symbol="EURUSD",
    action="BUY",
    lot_size=0.01,
    entry_price=1.0850,
    sl=1.0800,
    tp=1.0950,
    is_real_execution_intent=False,
    is_user_approved=True,
)
result = engine.evaluate(intent_valid, account_demo)
run_test("T1 | Trade válido (demo, aprobado por usuario) → APPROVED", result, expect_approved=True)

# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Trade sin UUID → REJECTED (R5)
# ─────────────────────────────────────────────────────────────────────────────
intent_no_uuid = TradeIntent(
    signal_id="signal-002",
    symbol="GBPUSD",
    action="SELL",
    lot_size=0.01,
    entry_price=1.2700,
    is_user_approved=True,
)
intent_no_uuid.id = ""   # Forzar UUID vacío
result = engine.evaluate(intent_no_uuid, account_demo)
run_test("T2 | Trade sin UUID → REJECTED (R5)", result, expect_approved=False)

# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Pérdida diaria excedida → REJECTED (R3)
# ─────────────────────────────────────────────────────────────────────────────
account_loss_exceeded = AccountState(
    balance=10000.0,
    equity=9700.0,
    daily_loss_pct=3.0,      # Supera el max de 2.0
    open_trades=1,
    max_daily_loss_pct=2.0,
    max_concurrent_trades=3,
    allow_real_execution=False,
    require_approval=True,
)
intent_loss = TradeIntent(
    signal_id="signal-003",
    symbol="EURUSD",
    action="BUY",
    lot_size=0.01,
    entry_price=1.0850,
    is_user_approved=True,
)
result = engine.evaluate(intent_loss, account_loss_exceeded)
run_test("T3 | Pérdida diaria excedida (3% > 2%) → REJECTED (R3)", result, expect_approved=False)

# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Demasiadas operaciones abiertas → REJECTED (R4)
# ─────────────────────────────────────────────────────────────────────────────
account_full = AccountState(
    balance=10000.0,
    equity=10000.0,
    daily_loss_pct=0.5,
    open_trades=3,           # Igual al max → bloqueado
    max_daily_loss_pct=2.0,
    max_concurrent_trades=3,
    allow_real_execution=False,
    require_approval=True,
)
intent_full = TradeIntent(
    signal_id="signal-004",
    symbol="USDJPY",
    action="BUY",
    lot_size=0.01,
    entry_price=155.00,
    is_user_approved=True,
)
result = engine.evaluate(intent_full, account_full)
run_test("T4 | Máximo de trades concurrentes alcanzado (3/3) → REJECTED (R4)", result, expect_approved=False)

# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Intento de ejecución real con ALLOW_REAL_EXECUTION=False → REJECTED (R1)
# ─────────────────────────────────────────────────────────────────────────────
intent_real = TradeIntent(
    signal_id="signal-005",
    symbol="XAUUSD",
    action="BUY",
    lot_size=0.01,
    entry_price=2350.0,
    is_real_execution_intent=True,   # Pretende ejecución real
    is_user_approved=True,
)
result = engine.evaluate(intent_real, account_demo)  # account_demo tiene allow_real_execution=False
run_test("T5 | Ejecución real con ALLOW_REAL_EXECUTION=False → REJECTED (R1)", result, expect_approved=False)

# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: Trade sin campos mínimos (sin entry_price, sin symbol) → REJECTED (R6)
# ─────────────────────────────────────────────────────────────────────────────
intent_missing = TradeIntent(
    signal_id="signal-006",
    symbol="",           # Vacío
    action="BUY",
    lot_size=0.01,
    entry_price=None,    # Falta precio
    is_user_approved=True,
)
result = engine.evaluate(intent_missing, account_demo)
run_test("T6 | Campos mínimos ausentes (symbol, entry_price) → REJECTED (R6)", result, expect_approved=False)

# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Trade sin aprobación de usuario con REQUIRE_APPROVAL=True → REJECTED (R2)
# ─────────────────────────────────────────────────────────────────────────────
intent_no_approval = TradeIntent(
    signal_id="signal-007",
    symbol="EURUSD",
    action="SELL",
    lot_size=0.01,
    entry_price=1.0850,
    is_real_execution_intent=False,
    is_user_approved=False,   # Sin aprobación
)
result = engine.evaluate(intent_no_approval, account_demo)
run_test("T7 | Sin aprobación de usuario (REQUIRE_APPROVAL=True) → REJECTED (R2)", result, expect_approved=False)

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────────────────
total = passed + failed
print("=" * 60)
print(f"RESULTADO FINAL: {passed}/{total} tests pasados | {failed} fallados")
if failed == 0:
    print("✅ RiskEngine determinista VALIDADO completamente.")
else:
    print("❌ Hay tests fallando. Revisar la lógica del RiskEngine.")
print("=" * 60)
