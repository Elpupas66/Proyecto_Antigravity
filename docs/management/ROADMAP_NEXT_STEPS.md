# Roadmap: Próximos Pasos

## 📋 Resumen del Roadmap

El proyecto Antigravity sigue una hoja de ruta modular. La Fase 2.1 (RiskEngine Determinista) está completada. Las siguientes fases se enfocan en seguridad, validación y ejecución controlada.

---

## 🗺️ Fases del Proyecto

```
Fase 1: Fundamentos           ✅ COMPLETADO
Fase 2.1: RiskEngine         ✅ COMPLETADO
─────────────────────────────────────────────
Fase 2.2: Kill Switch        🔜 PRÓXIMO
Fase 2.3: Approval Layer     📅 PLANIFICADO
Fase 2.4: AI Validator       📅 PLANIFICADO
Fase 3.1: Gatekeeper         📅 PLANIFICADO
Fase 3.2: Paper Trading      📅 PLANIFICADO
Fase 4: Ejecución Real       🔒 BLOQUEADO
```

---

## 🔜 Fase 2.2: Kill Switch

### Descripción
Sistema de parada de emergencia que permite detener inmediatamente cualquier operación del sistema.

### Objetivos
- [ ] Implementar endpoint `/emergency/stop`
- [ ] Crear flag global `EMERGENCY_STOP`
- [ ] Integrar con RiskEngine para rechazar todas las operaciones cuando esté activo
- [ ] Añadir logging de eventos de emergencia

### Criterios de Éxito
- El Kill Switch debe poder activarse via API
- Una vez activado, ninguna operación puede ejecutarse
- Debe persistir el estado hasta que se desactive manualmente

---

## 📅 Fase 2.3: Approval Layer

### Descripción
Capa de aprobación que requiere confirmación humana antes de ejecutar cualquier operación.

### Objetivos
- [ ] Implementar sistema de tokens de aprobación
- [ ] Crear endpoint `/approve/{token}`
- [ ] Integrar con Telegram para notificaciones (futuro)
- [ ] Timeout automático si no hay aprobación en X minutos

### Criterios de Éxito
- Todo trade debe ser aprobado explícitamente
- El sistema rechaza operaciones no aprobadas
- Registro completo de approvals/rejections

---

## 📅 Fase 2.4: AI Validator

### Descripción
Módulo de validación que usa agentes IA para analizar y validar operaciones antes de su ejecución.

### Objetivos
- [ ] Integrar con LLM local (Ollama)
- [ ] Crear prompt de validación de trades
- [ ] Implementar endpoint `/ai/validate`
- [ ] Logging de análisis IA

### Criterios de Éxito
- El sistema puede analizar un trade con IA
- Devuelve rationale de aprobación/rechazo
- No bloquea la ejecución (es informativo)

---

## 📅 Fase 3.1: Gatekeeper

### Descripción
Orquestador central que gestiona el flujo completo de señales desde TradingView hasta MT5.

### Objetivos
- [ ] Receptor de webhooks de TradingView
- [ ] Integración con n8n para orquestación
- [ ] Buffer de señales
- [ ] Retry logic

### Criterios de Éxito
- Recibe señales de TradingView
- Las enruta a través del pipeline completo
- Maneja errores gracefully

---

## 📅 Fase 3.2: Paper Trading

### Descripción
Simulación completa de trading sin usar dinero real.

### Objetivos
- [ ] Motor de simulación de cuentas
- [ ] Cálculo de P&L virtual
- [ ] Tracking de estadísticas
- [ ] Reporting semanal

### Criterios de Éxito
- Simula operaciones correctamente
- Calcula balance/equity virtual
- Genera reportes de rendimiento

---

## 🔒 Fase 4: Ejecución Real

### ⚠️ IMPORTANTE: Esta fase está BLOQUEADA

La ejecución con dinero real **NUNCA** será parte de este proyecto académico por razones de seguridad y cumplimiento.

### Razones del Bloqueo
1. **Riesgo financiero**: Operaciones reales requieren licencias y regulación
2. **Seguridad**: El proyecto es académico y educativo
3. **Responsabilidad**: No nos hacemos responsables de pérdidas financieras

### Alternativas
- Usar cuenta demo de MT5 exclusivamente
- Paper trading para simulaciones
- Learning lab para desarrollo de estrategias

---

## 🎯 Prioridades de Desarrollo

| Prioridad | Fase | Descripción |
|-----------|------|-------------|
| **ALTA** | 2.2 | Kill Switch - Seguridad de emergencia |
| **ALTA** | 2.3 | Approval Layer - Control humano |
| **MEDIA** | 2.4 | AI Validator - Asistencia IA |
| **MEDIA** | 3.1 | Gatekeeper - Orquestación |
| **MEDIA** | 3.2 | Paper Trading - Simulación |
| **BAJA** | 4 | Ejecución Real - ❌ BLOQUEADO |

---

## 🔧 Cómo Continuar el Desarrollo

### Setup del Entorno
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
python tests/test_risk_engine.py

# Arrancar servidor
python -m uvicorn core.main:app --reload
```

### Commits Sugeridos
```bash
# Fase 2.2 - Kill Switch
git commit -m "feat: implement T2.2 Kill Switch emergency endpoint"

# Fase 2.3 - Approval Layer  
git commit -m "feat: implement T2.3 Approval Layer with tokens"

# Fase 2.4 - AI Validator
git commit -m "feat: implement T2.4 AI Validator with Ollama"
```

---

## 📚 Referencias

- Documento de Arquitectura: `docs/architecture/ARCHITECTURE_OVERVIEW.md`
- Estado del Proyecto: `docs/management/PROJECT_STATUS.md`
- Reglas de Riesgo: `core/risk_engine.py`

---

## ⚠️ Disclaimer

Este roadmap es para fines educativos y académicos. El proyecto **NO** está diseñado para uso en producción financiera real.
