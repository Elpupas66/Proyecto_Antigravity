# Proyecto Antigravity 🚀

## 🏫 Proyecto Académico de Trading Algorítmico

**Antigravity** es un sistema académico de trading algorítmico asistido por IA, desarrollado como proyecto de fin de curso. El proyecto demuestra habilidades en diseño de arquitecturas de software, integración de APIs, seguridad financiera y sistemas de evaluación de riesgo.

> ⚠️ **AVISO IMPORTANTE**: Este proyecto **NO ejecuta operaciones reales** en mercados financieros. Todos los mecanismos de seguridad están configurados para bloquear la ejecución real.

---

## 📚 Objetivo Académico

Este proyecto fue desarrollado para demostrar:

1. **Arquitectura de Software**: Diseño de sistemas distribuidos con FastAPI
2. **Seguridad Financiera**: Motor de evaluación de riesgo con reglas deterministas
3. **Integración de Sistemas**: API REST, bases de datos SQLite, validación de configuraciones
4. **Desarrollo Seguro**: Variables de entorno, gestión de secretos, .gitignore

## 🧱 Arquitectura: Bot + Agente IA + Ecosistema

El proyecto Antigravity se concibe como un ecosistema integral de trading algorítmico estructurado en tres componentes:

- **Bot Algorítmico**: Receptor y enrutador de señales técnicas basadas en indicadores (e.g., TradingView vía webhooks y orquestación con n8n). En esta fase académica, actúa como el emisor de los intentos de operación (`TradeIntent`).
- **Agente IA**: Componente en fase de diseño/roadmap que utilizará LLMs locales (como Ollama) para la validación contextual de operaciones, análisis cualitativo y generación de explicaciones.
- **Ecosistema**: El núcleo base desarrollado en FastAPI, el motor determinista **RiskEngine** que aplica 7 reglas de seguridad estrictas de forma local, y la base de datos **SQLite** para persistir de manera segura la bitácora de auditoría.

---

## 🎯 Estado Actual

| Componente | Estado |
|------------|--------|
| FastAPI Core | ✅ Funcional |
| RiskEngine | ✅ 7/7 tests pasando |
| SQLite Database | ✅ Funcional |
| /health endpoint | ✅ Verificado |
| Kill Switch | ❌ No implementado |
| MT5 Integration | ❌ No implementado |
| Telegram Bot | ❌ No implementado |
| Ejecución Real | ❌ Bloqueada |

---

## 🔧 Instalación

### 1. Requisitos Previos
- Python 3.10+
- Windows/macOS/Linux

### 2. Clonar el Repositorio
```bash
git clone <repo-url>
cd Proyecto_antigravity
```

### 3. Crear Entorno Virtual (Recomendado)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno
```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# NOTA: El archivo .env contiene las configuraciones de seguridad
# NO subir .env al repositorio (ya está en .gitignore)
```

---

## 🚀 Cómo Arrancar FastAPI

### Iniciar el Servidor

Por defecto, el servidor intentará arrancar en el puerto `8000`:
```bash
python -m uvicorn core.main:app --reload
```

> 💡 **Nota de resolución de problemas**: Si el puerto `8000` falla (por ejemplo, debido a conflictos de permisos o colisiones de sockets en Windows con `WinError 10013`), arranca el servidor en el puerto alternativo `8080` ejecutando:
> ```bash
> python -m uvicorn core.main:app --host 127.0.0.1 --port 8080
> ```

### Documentación Automática
- Swagger UI: `http://127.0.0.1:8000/docs` (o `http://127.0.0.1:8080/docs`)
- ReDoc: `http://127.0.0.1:8000/redoc` (o `http://127.0.0.1:8080/redoc`)

### Verificar Estado

Desde otra terminal, puedes comprobar la salud del servicio:
```bash
curl http://127.0.0.1:8000/health
```
*(O si usas el puerto alternativo `8080`):*
```bash
curl http://127.0.0.1:8080/health
```

Debería devolver:
```json
{
  "status": "ok",
  "service": "antigravity_core",
  "security_locks": {
    "environment": "development",
    "real_execution_allowed": false,
    "approval_required": true
  }
}
```

---

## 🧪 Ejecutar Tests

### Tests del RiskEngine
```bash
python tests/test_risk_engine.py
```

**Resultado esperado**: 7/7 tests pasando

```
✅ PASS | T1 | Trade válido (demo, aprobado por usuario) → APPROVED
✅ PASS | T2 | Trade sin UUID → REJECTED (R5)
✅ PASS | T3 | Pérdida diaria excedida → REJECTED (R3)
✅ PASS | T4 | Máximo de trades concurrentes alcanzado → REJECTED (R4)
✅ PASS | T5 | Ejecución real bloqueada → REJECTED (R1)
✅ PASS | T6 | Campos mínimos ausentes → REJECTED (R6)
✅ PASS | T7 | Sin aprobación de usuario → REJECTED (R2)

RESULTADO FINAL: 7/7 tests pasados | 0 fallados
```

---

## 📁 Estructura del Proyecto

```
Proyecto_antigravity/
├── .env                    # ⚠️ NO subir a Git (secretos)
├── .env.example           # ✅ Plantilla segura
├── .gitignore             # ✅ Configurado
├── core/                  # ✅ Núcleo del sistema
│   ├── main.py           # FastAPI app
│   ├── risk_engine.py    # Motor de riesgo
│   ├── database.py       # SQLite
│   ├── models.py        # Modelos Pydantic
│   └── settings.py      # Configuración segura
├── tests/                 # ✅ Tests unitarios
│   └── test_risk_engine.py
├── docs/                  # ✅ Documentación
│   ├── architecture/
│   ├── management/
│   └── trading_rules/
└── README.md
```

---

## 🔒 Seguridad

### Variables de Seguridad Activas

El sistema está configurado con múltiples capas de seguridad:

```bash
# En .env (NUNCA subir a Git)
ENVIRONMENT=development
ALLOW_REAL_EXECUTION=False
REQUIRE_APPROVAL=True
```

### Reglas de Riesgo Implementadas

| ID | Regla | Descripción |
|----|-------|-------------|
| R1 | REAL_EXECUTION_BLOCKED | Bloquea ejecución real |
| R2 | APPROVAL_REQUIRED | Requiere aprobación humana |
| R3 | DAILY_LOSS_EXCEEDED | Límite de pérdida diaria (2%) |
| R4 | MAX_TRADES_EXCEEDED | Máximo 3 trades concurrentes |
| R5 | MISSING_UUID | Requiere identificador único |
| R6 | MISSING_FIELDS | Requiere campos mínimos |

---

## 📖 Documentación

### Para Empezar
1. **[Arquitectura](./docs/architecture/ARCHITECTURE_OVERVIEW.md)**: Visión general del sistema
2. **[Estado del Proyecto](./docs/management/PROJECT_STATUS.md)**: Qué está implementado
3. **[Roadmap](./docs/management/ROADMAP_NEXT_STEPS.md)**: Próximos pasos

### Documentación Técnica
- `docs/architecture/PRD_AI_DEV_ENV.md`
- `docs/trading_rules/normas_proyecto_trading.md`
- `docs/management/bitacora_proyecto.md`

---

## ❌ Limitaciones Actuales

Este proyecto **NO** incluye (por diseño):

- ❌ Conexión con MetaTrader 5
- ❌ Ejecución de operaciones reales
- ❌ Telegram Bot funcional
- ❌ Paper Trading completo
- ❌ Integración con n8n
- ❌ AI Validator

Estas funcionalidades están planned para fases futuras, pero **la ejecución real permanecerá bloqueada** por razones de seguridad.

---

## 📝 Commits Recientes

```bash
66eb410 - Validate T2.1 deterministic RiskEngine
a52556e - Backup: Estado base legacy
```

---

## 📬 Contacto

Este es un proyecto académico. Para preguntas sobre la arquitectura o el código, revisar la documentación en `docs/`.

---

## ⚠️ Disclaimer

**Este proyecto es con fines educativos y académicos.**

- NO utilizar para trading con dinero real
- NO conectar a cuentas reales de brokers
- El autor no se hace responsable de pérdidas financieras
- Siempre usar cuenta demo para cualquier prueba
