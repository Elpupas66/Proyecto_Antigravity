# ANTIGRAVITY_SPACE_BUNDLE: Contexto Consolidado del Proyecto

Este documento constituye la fuente única de verdad y contexto para **Perplexity Space** sobre el **Proyecto Antigravity**. Contiene la identidad, el estado actual de implementación, decisiones arquitectónicas fundamentales, la estructura de seguridad activa y las directrices de asistencia técnica para la interacción con la inteligencia artificial.

---

## 1. Identidad del Proyecto

* **Nombre:** Proyecto Antigravity.
* **Propósito:** Desarrollo de un framework académico e infraestructura de trading cuantitativo automatizado de bajo riesgo. El sistema se encarga de ingerir informes de backtesting de terminales de trading, recalcular métricas de forma matemática independiente, evaluar la solidez estadística de las estrategias mediante simulaciones de Monte Carlo, filtrar las señales resultantes mediante un motor de riesgos determinista y presentar la información enriquecida para aprobación final de un operador humano.
* **Rol del Perplexity Space:** Actuar como repositorio de contexto para el copiloto técnico (IA). Su función es proveer a Perplexity del entendimiento exacto del estado del repositorio, su arquitectura lineal y las restricciones inquebrantables, de modo que las respuestas sean seguras, precisas y alineadas con la fase de desarrollo real.
* **Líneas Rojas Irrevocables (Invariantes de Seguridad):**
  * **La IA no decide:** Las salidas del AI Validator son estrictamente consultivas y de explicación técnica. No son vinculantes ni deciden sobre la viabilidad operativa de una señal.
  * **La IA no ejecuta:** Ningún agente de inteligencia artificial tiene capacidad de enviar o procesar órdenes directas a terminales de trading.
  * **La IA no sustituye al RiskEngine:** El `RiskEngine` determinista está jerárquicamente por encima de la IA y es el único con autoridad técnica para vetar o bloquear señales de forma automática.
  * **La IA no aprueba operaciones reales:** La constante `approved_for_real = False` y el cierre `ALLOW_REAL_EXECUTION = False` son absolutos e inalterables por el análisis de la IA.

---

## 2. Estado Actual del Proyecto

* **Versión Core Documentada:** `1.3.0` (registrada en `docs/management/PROJECT_STATUS.md`, ampliada con el cierre de las fases 4.2B y 4.3).
* **Fases Completadas:**
  * **Fase 4.2B — Monte Carlo & Risk of Ruin (Completada):** Implementación del motor matemático de remuestreo (Bootstrap y Shuffle) para evaluar la probabilidad de ruina y la solidez estadística del drawdown ante variaciones de racha. Integrada la Regla D4 que degrada clasificaciones a `OBSERVATION` si el análisis arroja `low_confidence = True`.
  * **Fase 4.3 — AI Validator Design (Completada):** Diseño conceptual completo de la capa de inteligencia artificial auxiliar detallada en una arquitectura por adaptadores.
* **Fase Actual y Próxima Recomendada:**
  * **Fase 4.4 — AI Validator Contracts:** Implementación de contratos de datos Pydantic para el AI Validator y el adaptador inicial `MockAIValidator` para pruebas locales sin red.

---

## 3. Componentes Implementados

El ecosistema cuenta con los siguientes módulos completamente funcionales y validados:
1. **FastAPI Core:** Servidor web ASGI para endpoints de control, estado (`/health`) y auditoría.
2. **SQLite Database:** Base de datos para persistir el historial de auditoría de señales y estados.
3. **Settings & Safety Locks:** Cierres de seguridad basados en variables de entorno inmutables (`ALLOW_REAL_EXECUTION = False`).
4. **RiskEngine determinista:** Motor que aplica de forma estricta las reglas operativas R1 a R6.
5. **Strategy Validation Framework:** Conjunto de umbrales académicos (Profit Factor, OOS, Drawdowns) para calificar la robustez de las estrategias.
6. **Metrics Standard:** Estandarización de las métricas clave del sistema para evitar ambigüedades técnicas.
7. **Strategy Models Pydantic:** Modelos estrictamente tipados para representar informes de backtests, periodos y resultados de evaluación.
8. **BacktestValidator:** Validador lógico que consume métricas y determina el estado final de la estrategia, aplicando degradaciones por baja confianza (Regla D4).
9. **MT5 HTML Backtest Import Layer:** Capa de ingesta que permite importar informes estructurados.
10. **MT5HtmlParser:** Parser de informes en formato HTML en inglés generados por MetaTrader 5.
11. **SHA-256 Traceability:** Firma criptográfica del reporte crudo HTML para asegurar trazabilidad e inmutabilidad de la auditoría.
12. **Metrics Engine determinista:** Recálculo offline e independiente de métricas básicas y avanzadas (Sortino Ratio, Expectancy, Max Daily Loss, rachas consecutivas).
13. **Monte Carlo & Risk of Ruin:** Motor de simulaciones estadísticas de remuestreo y cálculo de la probabilidad de ruina en base a rachas.
14. **AI Validator Design:** Especificación de la arquitectura por adaptadores del AI Validator.
15. **GitHub y control de versiones:** Repositorio limpio estructurado por módulos aislados.
16. **pytest:** Suite de pruebas unitarias y de integración automatizadas.

---

## 4. Última Batería de Tests Conocida

* **Resultado:** `67 tests pasados / 0 fallados` de manera exitosa ejecutando `.venv\Scripts\pytest tests/`.
* **Advertencias (Warnings):** 14 warnings no bloqueantes por la depreciación de `datetime.utcnow()` en validaciones internas de paquetes de dependencias de Pydantic.
* **Clasificación:** Catalogado como deuda técnica menor; pendiente de resolución al migrar a objetos datetime conscientes del huso horario (`datetime.now(datetime.UTC)`) en la próxima actualización de dependencias de Pydantic.

---

## 5. Pipeline Oficial del Ecosistema

El pipeline de ingesta, cálculo, validación y control de señales sigue un flujo unidireccional estricto que no puede ser alterado o saltado bajo ninguna circunstancia:

```
[ Signal Parser ]
       │  (Carga datos brutos e inmutabilidad criptográfica)
       ▼
[ Metrics Engine ]
       │  (Recálculo determinista de métricas del backtest)
       ▼
[ Monte Carlo & Risk of Ruin ]
       │  (Simulación estocástica y cálculo de confianza operativa)
       ▼
[ BacktestValidator ]
       │  (Clasificación de la estrategia y aplicación de D4)
       ▼
[ RiskEngine ]
       │  (Validación determinista de reglas operativas R1-R6)
       ▼
[ Approval Layer ]
       │  (Decisión y control humano explicativo)
       ▼
[ Operador Humano / Cuenta Demo (Paper) ]
```

---

## 6. Componentes Pendientes (Roadmap)

1. **AI Validator Contracts (Fase 4.4):** Implementación de los modelos Pydantic `AIValidatorInput` y `AIValidatorResult`.
2. **MockAIValidator:** Adaptador local offline para testing y desarrollo.
3. **RemoteAPIValidator:** Conectores de APIs en la nube (OpenRouter, OpenAI, Gemini, Claude, etc.) para producción inicial ágil.
4. **OllamaRemoteValidator:** Adaptador concebido únicamente en caso de contar con un VPS adecuado en el futuro.
5. **Telegram Approval Layer:** Bot o canal de comunicación integrado para interacción en vivo y alertas con el operador humano.
6. **Kill Switch:** Módulo de seguridad para detención instantánea del flujo de señales.
7. **Paper Trading Sandbox:** Entorno controlado de pruebas en tiempo real con datos de mercado simulados.
8. **Gatekeeper MT5:** Componente para el control estricto de envío de órdenes y volumen exclusivamente en cuentas demo MetaTrader 5.
9. **TradingView Integration:** Endpoint receptor de webhooks autenticados de señales.
10. **n8n auxiliary workflows:** Procesos auxiliares de comunicación fuera de la lógica crítica del backend.
11. **Demo execution:** Ejecución de operaciones simuladas bajo control.

---

## 7. Áreas y Estados Bloqueados por Diseño

* **Ejecución en Real:** Totalmente bloqueada.
* **Variables de control inmutables:** `ALLOW_REAL_EXECUTION = False` y `approved_for_real = False`. Cualquier intento del sistema de modificar estas variables a `True` arroja error de validación inmediato y descarta el proceso.
* **Autonomía de la IA:** El AI Validator no tiene poder de autorización ni ejecución. Actúa exclusivamente como un enriquecedor de texto explicativo en la *Approval Layer*.
* **Bypass de Componentes:** Ningún flujo puede saltarse la validación del `RiskEngine` determinista ni la aprobación humana del *Approval Layer*.

---

## 8. Decisiones Arquitectónicas Fundamentales

* **Parser Aislado:** El parser (`MT5HtmlParser`) no calcula métricas de rendimiento avanzadas. Solo extrae la información en crudo del informe y la valida.
* **Cómputo en Metrics Engine:** El cálculo de métricas complejas (Sortino, max daily loss, expectancy recalculado) se realiza de forma centralizada en el `Metrics Engine`.
* **Cálculo de Confianza Aislado:** Monte Carlo solo genera el estado probabilístico (`low_confidence`), dejando la clasificación de la estrategia al `BacktestValidator`.
* **Seguridad determinista en RiskEngine:** Las decisiones de riesgo se rigen por un enfoque determinista de caja negra estricto que no admite razonamientos ambiguos o probabilisticos.
* **IA basada en Adaptadores:** Se adopta el patrón *Adapter* para desacoplar el AI Validator de los proveedores LLM, permitiendo alternar de forma transparente entre simulaciones locales (`Mock`), APIs en la nube (`RemoteAPI`) y servidores privados dedicados (`OllamaRemote`).
* **Instalación y Alojamiento de Ollama:** 
  * **No local:** No se requiere la instalación de Ollama en el ordenador de desarrollo para optimizar recursos del hardware de los desarrolladores.
  * **No en AWS Gratuito:** No se desplegará Ollama en el servidor actual n8n de AWS gratuito por insuficiencia de memoria y CPU.
  * **VPS Futuro:** La utilización de Ollama remoto queda relegada a un servidor VPS de pago dedicado.
* **Notificaciones y orquestación:** n8n y Telegram operan fuera de la lógica de procesamiento central. El backend FastAPI debe ser autónomo y resiliente ante fallos de estos servicios externos.
* **Gatekeeper MT5:** Toda conexión futura con MetaTrader 5 se centralizará a través del componente Gatekeeper para aislar los scripts de ejecución de los modelos de riesgo.

---

## 9. Documentos y Rutas Importantes en el Repositorio

* [README.md](file:///c:/Users/34628/Downloads/Proyecto_antigravity/README.md) - Guía general del proyecto.
* [docs/architecture/ARCHITECTURE_OVERVIEW.md](file:///c:/Users/34628/Downloads/Proyecto_antigravity/docs/architecture/ARCHITECTURE_OVERVIEW.md) - Visión global de la arquitectura.
* [docs/architecture/monte_carlo_risk_design.md](file:///c:/Users/34628/Downloads/Proyecto_antigravity/docs/architecture/monte_carlo_risk_design.md) - Diseño técnico del análisis estocástico.
* [docs/architecture/ai_validator_design.md](file:///c:/Users/34628/Downloads/Proyecto_antigravity/docs/architecture/ai_validator_design.md) - Diseño de adaptadores del AI Validator (Fase 4.3 corregido).
* [docs/management/PROJECT_STATUS.md](file:///c:/Users/34628/Downloads/Proyecto_antigravity/docs/management/PROJECT_STATUS.md) - Estado de las fases y métricas de completitud.
* [docs/management/ROADMAP_NEXT_STEPS.md](file:///c:/Users/34628/Downloads/Proyecto_antigravity/docs/management/ROADMAP_NEXT_STEPS.md) - Planificación del desarrollo futuro.
* [docs/trading_rules/STRATEGY_VALIDATION_FRAMEWORK.md](file:///c:/Users/34628/Downloads/Proyecto_antigravity/docs/trading_rules/STRATEGY_VALIDATION_FRAMEWORK.md) - Límites y umbrales de validación.
* [docs/trading_rules/METRICS_STANDARD.md](file:///c:/Users/34628/Downloads/Proyecto_antigravity/docs/trading_rules/METRICS_STANDARD.md) - Definición normalizada de términos y ecuaciones financieras.
* [core/risk_engine.py](file:///c:/Users/34628/Downloads/Proyecto_antigravity/core/risk_engine.py) - Código del motor determinista de reglas operativas R1-R6.
* [core/backtest_validator.py](file:///c:/Users/34628/Downloads/Proyecto_antigravity/core/backtest_validator.py) - Implementación del evaluador lógico de estrategias (incluye D4).
* [core/strategy_models.py](file:///c:/Users/34628/Downloads/Proyecto_antigravity/core/strategy_models.py) - Modelos Pydantic de backtests y simulación de Monte Carlo.
* [core/parsers/mt5_html_parser.py](file:///c:/Users/34628/Downloads/Proyecto_antigravity/core/parsers/mt5_html_parser.py) - Código del parser de MetaTrader 5.
* [core/metrics/metrics_engine.py](file:///c:/Users/34628/Downloads/Proyecto_antigravity/core/metrics/metrics_engine.py) - Implementación del recálculo matemático de métricas.
* [core/metrics/monte_carlo.py](file:///c:/Users/34628/Downloads/Proyecto_antigravity/core/metrics/monte_carlo.py) - Simulación de remuestreo (Bootstrap/Shuffle).
* [tests/](file:///c:/Users/34628/Downloads/Proyecto_antigravity/tests/) - Carpeta de pruebas globales (67 tests passing).

---

## 10. Glosario Técnico del Proyecto

* **Parser:** Módulo encargado de la lectura y procesamiento de archivos HTML crudos de MetaTrader 5 en inglés. Convierte tablas y textos no estructurados en diccionarios y objetos Python, validando tipos y asegurando la firma criptográfica (SHA-256).
* **BacktestReport:** Modelo Pydantic central que representa los datos de un backtest. Contiene metadatos de la estrategia, el periodo del backtest, métricas del parser, métricas recalculadas de forma independiente, firmas de auditoría y resultados de simulaciones.
* **Metrics Engine:** Componente determinista aislado que procesa la lista de transacciones del parser para verificar, corregir y calcular métricas cuantitativas clave de la estrategia sin intervención humana o dependencias de APIs.
* **Monte Carlo:** Proceso de simulación estocástica que realiza miles de iteraciones reordenando (Shuffle) o remuestreando con reemplazo (Bootstrap) la lista de operaciones históricas para evaluar la robustez estadística de los Drawdowns y rachas.
* **Risk of Ruin:** Medida de probabilidad estadística derivada de la simulación de Monte Carlo que calcula el riesgo de que la cuenta caiga por debajo de un nivel catastrófico definido de capital antes de alcanzar la rentabilidad esperada.
* **BacktestValidator:** Evaluador lógico encargado de comparar el informe enriquecido (`BacktestReport`) contra las reglas de aceptación y umbrales académicos. Asigna clasificaciones como `PAPER_TRADING_READY`, `OBSERVATION` o `REJECTED`.
* **RiskEngine:** Módulo crítico y determinista de seguridad en tiempo real. Actúa en el pipeline final evaluando señales en base a parámetros del entorno (seguridad real bloqueada, autorización manual activa, pérdidas acumuladas diarias y exposición de margen).
* **Approval Layer:** Capa de interacción y visualización final para el operador. En ella se unifican las decisiones del `RiskEngine`, del `BacktestValidator` y los comentarios del `AI Validator`. Presenta un resumen para la aprobación manual definitiva del humano.
* **AI Validator:** Capa de análisis y razonamiento auxiliar construida con modelos LLM mediante arquitectura de adaptadores. Su función es evaluar la coherencia técnica del contexto de la señal y generar informes explicativos legibles.
* **Gatekeeper MT5:** Conector ultra-seguro encargado del paso final de transmisión de órdenes a la terminal MetaTrader 5. Restringido por código a cuentas virtuales demo y con bloqueos de volumen.
* **Kill Switch:** Mecanismo de parada rápida manual o automático a nivel de API para desconectar la ingesta de webhooks e invalidar ejecuciones en caso de condiciones del mercado anómalas.
* **Paper Trading:** Modo de operación en cuenta de demostración virtual utilizando datos de mercado en tiempo real para verificar la robustez de las señales antes de cualquier planteamiento de producción.
* **BLOCKED_FOR_REAL:** Estado lógico absoluto e irreversible impuesto por los safety locks en settings que impide la conexión de sockets o envío de órdenes a servidores reales.

---

## 11. Directrices de Respuesta para Perplexity

Para asistir de manera efectiva en el desarrollo, Perplexity debe clasificar la procedencia de la información y estructurar sus análisis de la siguiente manera:

### Clasificación de Fuentes
1. **Bundle Contextual:** Información de este archivo (`ANTIGRAVITY_SPACE_BUNDLE.md`). Debe tratarse como la realidad actual e indiscutible del repositorio.
2. **Contexto de Rutas:** Información de archivos de código o documentación enlazados en la Sección 9. Deben consultarse antes de proponer cambios sintácticos o imports.
3. **Outputs Reales:** Evidencias provistas directamente por el usuario (mensajes de error de consola, trazas de pytest, logs de API). Tienen prioridad para resolución de bugs.
4. **Inferencia Técnica:** Sugerencias basadas en el conocimiento técnico general de la IA. Debe indicarse explícitamente cuando una propuesta es una inferencia y no está en la base de datos del repositorio.

### Formato Obligatorio de Respuesta Explicativa
Cualquier diagnóstico o sugerencia técnica relevante generada por Perplexity debe estructurarse obligatoriamente bajo los siguientes cuatro apartados:
1. **Diagnóstico:** Explicación técnica clara del estado observado del código o del diseño propuesto.
2. **Riesgo Detectado:** Identificación de impactos negativos en las invariantes de seguridad del ecosistema, dependencias o cuellos de botella de rendimiento.
3. **Recomendación:** Diseño de solución de código limpio, modular y desacoplado acorde a las directrices de Antigravity.
4. **Próximo Paso:** Tarea inmediata, concreta e incremental que debe realizar el programador.

---

## 12. Matriz de Tareas Permitidas y Prohibidas en el Space

| Acciones Permitidas | Acciones Prohibidas |
|:---|:---|
| ✅ **Auditar coherencia:** Validar código de cálculo de métricas o de riesgo contra las fórmulas y reglas descritas en la documentación del bundle. | ❌ **Recomendar inversiones:** Sugerir entrar en activos, temporalidades o dar consejos financieros o de trading real. |
| ✅ **Refactorización de código:** Generar código limpio de Python (Pydantic, FastAPI, algoritmos de cálculo, etc.) compatible con la arquitectura del repositorio. | ❌ **Eludir safety locks:** Proponer configuraciones o métodos para saltarse el `RiskEngine` determinista, desactivar la confirmación humana o cambiar `ALLOW_REAL_EXECUTION=True`. |
| ✅ **Planificar pruebas:** Diseñar escenarios de tests para `pytest` (mocks, valores límite, etc.) basados en los tests existentes. | ❌ **Inventar métricas:** Introducir conceptos de trading cuantitativo no contemplados en el *Metrics Standard* o el *Strategy Validation Framework*. |
| ✅ **Explicar flujos:** Ayudar a nuevos desarrolladores o sistemas a entender el pipeline unidireccional y las dependencias de los módulos del proyecto. | ❌ **Simular ejecución de código real:** Afirmar que el sistema está operando o ejecutándose en vivo sin contar con salidas de consola provistas por el usuario. |
| ✅ **Detectar deuda técnica:** Identificar código obsoleto o ineficiente, sugiriendo mejoras incrementales para las próximas fases. | ❌ **Alterar prioridades de fases:** Diseñar componentes de fases posteriores sin terminar la implementación de los contratos del AI Validator (Fase 4.4). |
