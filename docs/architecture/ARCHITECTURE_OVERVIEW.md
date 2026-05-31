# Arquitectura del Proyecto Antigravity

## 1. Objetivo del Proyecto

**Antigravity** es un ecosistema de trading algorítmico asistido por inteligencia artificial, diseñado para automatizar el flujo completo de señales de trading: desde la recepción de señales hasta la validación de riesgo y la posible ejecución en cuenta demo.

### Propósito Académico

El proyecto tiene un doble propósito:
1. **Académico**: Demostrar habilidades en diseño de sistemas distribuidos, arquitectura de software, seguridad financiera y integración de IA.
2. **Práctico**: Proporcionar una base sólida para el desarrollo de un sistema de trading automatizado con múltiples capas de seguridad.

---

## 2. Diferencia entre Bot Algorítmico, Agente IA y Ecosistema

| Concepto | Descripción | Rol en Antigravity |
|----------|-------------|-------------------|
| **Bot Algorítmico** | Programa que ejecuta reglas predefinidas de trading basadas en indicadores técnicos | No implementado directamente; se integra vía webhooks de TradingView |
| **Agente IA** | Sistema basado en inteligencia artificial que toma decisiones, aprende y se adapta | En desarrollo (Fase 2.x); uso de LLMs locales para análisis y documentación |
| **Ecosistema** | Conjunto integrado de componentes que trabajan juntos (API, Base de Datos, Reglas de Riesgo, UI) | **Implementado**: FastAPI + RiskEngine + SQLite + Documentación |

---

## 3. Arquitectura Actual

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ANTIGRAVITY CORE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │   FastAPI    │───▶│ RiskEngine   │───▶│  SQLite DB   │         │
│  │  (Puerto 8000)│    │  (Evaluación │    │ (TradeState │         │
│  │  /health     │    │   de riesgo) │    │  + Logs)    │         │
│  └──────────────┘    └──────────────┘    └──────────────┘         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                    CAPAS DE SEGURIDAD                    │      │
│  │  ┌────────────────┐  ┌────────────────┐                 │      │
│  │  │ ALLOW_REAL_   │  │ REQUIRE_       │                 │      │
│  │  │ EXECUTION=False│  │ APPROVAL=True  │                 │      │
│  │  └────────────────┘  └────────────────┘                 │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Componentes Principales

1. **FastAPI Core** (`core/main.py`)
   - Servidor REST API en puerto 8000
   - Endpoint `/health` para verificación de estado
   - Endpoints de trading (preparados para integración)

2. **RiskEngine** (`core/risk_engine.py`)
   - Motor de evaluación de riesgo determinista
   - 6 reglas de seguridad implementadas (R1-R6)
   - Evaluación sin red, sin MT5, sin IA externa

3. **Base de Datos** (`core/database.py`)
   - SQLite para almacenamiento local
   - Modelos: TradeDB, LogEventDB

4. **Modelos Pydantic** (`core/models.py`)
   - TradeIntent, AccountState, RiskResult
   - Enums: TradeState

---

## 4. Flujo Previsto (Pipeline Completo)

```
TradingView Signal ──▶ n8n (orquestación) ──▶ Gatekeeper API ──▶ RiskEngine
                                                                         │
                                                                         ▼
                                                             ┌───────────────┐
                                                             │ EVALUACIÓN    │
                                                             │ DE RIESGO     │
                                                             └───────────────┘
                                                                         │
                                              ┌──────────────────────────┘
                                              ▼
                                      ┌───────────────┐
                                      │ APROBADO?     │
                                      └───────────────┘
                                         │          │
                                        SÍ          NO
                                         │          │
                                         ▼          ▼
                                  ┌───────────┐  ┌─────────┐
                                  │  MT5      │  │ BLOQUEADO│
                                  │ (Demo)    │  │ (Log)    │
                                  └───────────┘  └─────────┘
```

**Nota**: El flujo completo (MT5, Gatekeeper, Telegram, n8n) NO está implementado en esta entrega académica. Solo está implementado el núcleo (FastAPI + RiskEngine).

---

## 5. Módulos Implementados (Fase 2.1 - Completada)

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| FastAPI Core | ✅ | Servidor REST con /health |
| RiskEngine | ✅ | 7 reglas de riesgo deterministas |
| SQLite Database | ✅ | Almacenamiento de trades y logs |
| Settings/Config | ✅ | Validación de seguridad al inicio |
| Tests Unitarios | ✅ | 7/7 tests pasando |

---

## 6. Módulos Pendientes (Fase 2.2+)

| Módulo | Estado | Prioridad |
|--------|--------|-----------|
| T2.2 Kill Switch | ❌ No implementado | Alta |
| Approval Layer (Telegram) | ❌ No implementado | Alta |
| AI Validator | ❌ No implementado | Media |
| Gatekeeper Bot | ❌ No implementado | Media |
| Paper Trading | ❌ No implementado | Media |
| Integración MT5 | ❌ No implementado | Media |
| Webhook /signal | ❌ No implementado | Baja |
| Ejecución Real | ❌ Bloqueado permanentemente | - |

---

## 7. Restricciones de Seguridad Activas

El sistema está configurado con bloqueos estrictos:

```python
ALLOW_REAL_EXECUTION = False  # Bloquea cualquier ejecución real
REQUIRE_APPROVAL = True       # Requiere aprobación manual
ENVIRONMENT = development     # Modo desarrollo
```

### Reglas de Riesgo Implementadas (RiskEngine)

| ID | Regla | Descripción |
|----|-------|-------------|
| R1 | REAL_EXECUTION_BLOCKED | Bloquea intentos de ejecución real |
| R2 | APPROVAL_REQUIRED | Requiere aprobación explícita del usuario |
| R3 | DAILY_LOSS_EXCEEDED | Bloquea si pérdida diaria > 2% |
| R4 | MAX_TRADES_EXCEEDED | Limita trades concurrentes (máx 3) |
| R5 | MISSING_UUID | Requiere identificador único |
| R6 | MISSING_FIELDS | Requiere campos mínimos (symbol, entry_price) |
| R7 | *(reservada)* | *Regla futura, no activa ni validada actualmente* |

---

## 8. Prohibición de Ejecución Real

⚠️ **IMPORTANTE**: Este proyecto **NO EJECUTA OPERACIONES REALES** en mercados financieros.

- `ALLOW_REAL_EXECUTION` está configurado como `False`
- Cualquier intento de ejecución real será bloqueado por el RiskEngine
- El proyecto está diseñado exclusivamente para:
  - Aprendizaje académico
  - Paper trading (simulación)
  - Desarrollo y validación de estrategias

---

## 9. Estructura de Archivos Clave

```
Proyecto_antigravity/
├── .env                    # Variables reales (NO subir a Git)
├── .env.example            # Plantilla segura para GitHub
├── .gitignore              # Excluye .env, .venv, datos pesados
├── core/
│   ├── main.py             # FastAPI app
│   ├── risk_engine.py      # Evaluador de riesgo
│   ├── database.py          # SQLite setup
│   ├── models.py           # Modelos Pydantic
│   └── settings.py         # Configuración segura
├── tests/
│   └── test_risk_engine.py # 7 tests unitarios
├── docs/
│   ├── architecture/       # Este archivo
│   ├── management/         # Estado y roadmap
│   └── ...
└── README.md              # Guía principal
```

---

## 10. Referencias

- Documento de arquitectura: `docs/architecture/PRD_AI_DEV_ENV.md`
- Bitácora del proyecto: `docs/management/bitacora_proyecto.md`
- Reglas de trading: `docs/trading_rules/normas_proyecto_trading.md`
