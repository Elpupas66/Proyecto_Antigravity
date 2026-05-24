# 📘 PRD: Entorno de Desarrollo Asistido por IA & Roadmap de Automatización

## 1. Objetivo del Módulo
Definir la arquitectura de desarrollo local para la fase de codificación, backtesting y automatización de estrategias de trading. Se integra **Visual Studio Code** con la extensión **Cline** y el proveedor **OpenRouter** para actuar como agente de desarrollo autónomo, complementando la infraestructura central de **Antigravity** sin sustituirla.

## 2. Justificación Técnica: Migración de Continue a Cline

| Criterio | Continue.dev | Cline (Claude Dev) | Decisión |
|----------|--------------|-------------------|----------|
| **Naturaleza** | Asistente conversacional con contexto | Agente autónomo con ejecución real | ✅ Cline |
| **Gestión de archivos** | Muestra código en chat (copia/pega manual) | Crea, edita y refactoriza archivos directamente en el FS | ✅ Cline |
| **Iteración de errores** | Usuario debe copiar logs y reconsultar | Lee terminal, detecta errores de compilación y auto-corrige | ✅ Cline |
| **Contexto de proyecto** | `@codebase` consulta fragmentos bajo demanda | Explora activamente la estructura, respeta dependencias y rutas | ✅ Cline |
| **Adecuación a MQL5/Pine/Python** | Útil para dudas rápidas | Ideal para ciclos de desarrollo completos (escribir → compilar → probar) | ✅ Cline |

**Conclusión:** Cline se selecciona como motor de desarrollo principal porque reduce la fricción humana en tareas repetitivas de codificación, mantiene la coherencia con la arquitectura de Antigravity y acelera el ciclo de prueba-error en lenguajes estrictos (MQL5, Pine Script v5).

## 3. Integración con la Arquitectura Antigravity
- **Antigravity** actúa como núcleo arquitectónico: gestión de datos, lógica de negocio, endpoints FastAPI, túneles Cloudflare y orquestación de servicios.
- **Cline + OpenRouter** actúa como capa de desarrollo asistido:
  - Indexación local (`@codebase`) para que el agente comprenda la estructura de carpetas, convenciones de nombres y dependencias existentes.
  - Generación y refactorización de scripts de estrategias, indicadores y conectores sin romper la integración con el puente API.
  - Sincronización de cambios mediante aprobación explícita (`Plan → Act`), garantizando control humano sobre modificaciones críticas.

## 4. Estrategia de Modelos y Routing (OpenRouter)
Se ha configurado un routing híbrido **FREE/Pago** para garantizar continuidad de desarrollo con coste cercano a cero, priorizando estabilidad y rendimiento en coding y análisis financiero.

| Rol | Modelo (OpenRouter ID) | Coste | Uso Principal |
|-----|------------------------|-------|---------------|
| **Principal (Coding)** | `minimax/minimax-m2.5:free` | $0 | Generación MQL5/Pine/Python, autocompletado |
| **Alternativa Coding** | `qwen/qwen-2.5-coder-32b-instruct:free` | $0 | Fallback cuando MiniMax satura rate limits |
| **Estrategia/Análisis** | `meta-llama/llama-3.1-70b-instruct:free` / `qwen/qwen-2.5-72b-instruct:free` | $0 | Diseño de lógica, backtesting conceptual, revisiones |
| **Backup de Pago** | `minimax/minimax-m2.5` / `deepseek/deepseek-chat` | ~$0.14-0.15/M tokens | Alta disponibilidad cuando capas free están congestionadas |
| **Autocompletado** | `minimax/minimax-m2.5:free` | $0 | Sugerencias en tiempo real mientras se escribe |

**Mecanismos de resiliencia:**
- `providerRouting: default` para balanceo automático entre proveedores upstream.
- Selector manual en UI para cambio rápido ante errores `429 Rate Limited`.
- Temperatura diferenciada: `0.3` para código (determinista), `0.7` para estrategia (creativo/analítico).

## 5. Roadmap de Fases Posteriores
El proyecto se encuentra en fase de desarrollo activo. Las próximas iteraciones siguen el siguiente cronograma técnico:

### 🔹 Fase 2: Implementación y Backtesting de Estrategias
- Codificación completa de todas las estrategias actualmente en uso.
- Ejecución de backtests históricos (2 a 5 años) en múltiples temporalidades (M1, M5, M15, H1, H4, D1).
- **Criterios de filtrado obligatorios:**
  - Win Rate ≥ 70%
  - Risk/Reward mínimo 1:1
  - Drawdown controlado y consistencia en distintos regímenes de mercado
  - Validación out-of-sample y walk-forward analysis

### 🔹 Fase 3: Automatización & Bot Algorítmico MT5
- Selección de la estrategia más sostenible y rentable según métricas de Fase 2.
- Desarrollo de Expert Advisor (EA) en MQL5 con gestión de riesgo dinámica, trailing stops y filtros de volatilidad.
- Integración con el puente FastAPI existente para ejecución paper trading → live trading.
- Monitorización de logs, métricas en tiempo real y sistema de alertas.

### 🔹 Fase 4: Evaluación de Plataforma Propia de Trading (EN ESTUDIO.-POSIBLEMENTE NO VIABLE)
- Estudio de viabilidad técnica, regulatoria y de costes para desplegar una plataforma de trading propietaria.
- Alternativas analizadas: White-label de brokers, infraestructura cloud con APIs FIX/REST, desarrollo modular en microservicios.
- Decisión final basada en escalabilidad, compliance y coste de mantenimiento.

## 6. Gestión de Riesgos y Mitigación

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Rate limits en modelos FREE | Bloqueo temporal de desarrollo | Fallback automático a backup de pago ultra-económico (~$0.14/M) |
| Deriva de contexto en estrategias | Código inconsistente con Antigravity | Uso obligatorio de `@codebase` + revisión de diffs antes de aceptar cambios |
| Overfitting en backtests | Estrategia no válida en live | Validación cruzada, out-of-sample testing y límites de drawdown predefinidos |
| Dependencia de proveedor externo | Interrupción de servicio | Configuración multi-modelo + posibilidad de despliegue local (Ollama) como contingencia |