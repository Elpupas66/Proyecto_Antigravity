# 🏛️ Auditoría Arquitectónica: Infraestructura de Trading Asistido por IA

**Fecha:** 24/05/2026
**Rol:** Director Técnico y Arquitecto Principal (Antigravity)
**Objetivo:** Transición de scripts experimentales hacia una infraestructura profesional de trading asistido por IA (AI-Assisted Trading Infrastructure).

---

## 1. Diagnóstico Actual
El proyecto ha demostrado capacidad técnica validando el pipeline básico (`TradingView → n8n → Gatekeeper API → MetaTrader 5`). Existen módulos bases validados (`ConfigLoader`, `SessionManager`, `SignalGenerator`).
Sin embargo, la estructura actual es un conjunto de herramientas acopladas orientadas al "happy path" (flujo ideal) y no a la resiliencia financiera. La IA se está utilizando como un intermediario o filtro simple, pero sin un ecosistema robusto de validación, contención y auditoría que soporte la toma de decisiones.

## 2. Problemas Detectados
- **Fragmentación del Repositorio:** Múltiples carpetas raíz (`orb_system`, `automatizaciones`, `scripts`, `experimentos`, `trading`) con propósitos superpuestos.
- **Acoplamiento Prematuro y Enrutamiento Inseguro:** El flujo directo hacia n8n y de ahí al Gatekeeper genera una dependencia riesgosa en herramientas de automatización no diseñadas para baja latencia o alta criticidad.
- **Ausencia de Estado (Stateless):** El sistema actual no tiene memoria centralizada de las operaciones en curso, su estado o los balances.
- **Falta de Capas de Seguridad Transversales:** Ausencia de `Approval Layer`, registro estructurado unificado y un `Kill Switch` real.

## 3. Riesgos Arquitectónicos
1. **Ejecución Descontrolada (Runaway Execution):** Si el SignalGenerator enloquece o TradingView emite falsos positivos, el sistema actual pasaría las órdenes a MT5 sin resistencia.
2. **Dependencia de la Caja Negra (AI Hallucination Risk):** Delegar el filtrado de señales directamente a la IA sin un motor de riesgo determinista previo o posterior.
3. **Falta de Trazabilidad (Auditability):** No hay logs inmutables para cada Trade ID desde que nace hasta que muere, dificultando el debugging cuando ocurren pérdidas.
4. **Pérdida de Control Humano:** No hay un mecanismo establecido para pausar el sistema inmediatamente ante condiciones adversas (Flash Crashes).

## 4. Arquitectura Recomendada
Se propone un patrón de **Arquitectura Orientada a Eventos y Tuberías (Pipeline)** con validaciones estrictas, dividida en 6 capas:

1. **Signal Engine (Capa Determinista):** Generación de señales (vía TV, Python o MT5). Solo emite intenciones de operación (`Trade Intents`).
2. **AI Validator (Capa Analítica):** Recibe el `Trade Intent` + Contexto (Noticias, Volatilidad). Emite un veredicto justificado (Approve/Reject). **No tiene poder de ejecución**.
3. **Risk Engine (Capa de Contención):** Motor determinista. Evalúa DD, márgenes, máxima pérdida diaria, exposición correlacionada. La palabra del Risk Engine está por encima de la IA.
4. **Approval Layer (Capa de Gobernanza):** Dependiendo del riesgo o configuración, pausa el flujo y requiere aprobación explícita humana (Telegram/Web).
5. **Execution Layer (Capa de Interfaz con el Mercado):** `Gatekeeper` y `MT5 EA`. Ejecutan la orden final y manejan el ciclo de vida del trade (SL, TP, Trailing).
6. **Ecosistema Transversal:** 
   - **Audit Logger:** Trazabilidad absoluta.
   - **Kill Switch:** Proceso demonio que monitorea la salud financiera del sistema.

## 5. Componentes que Sobran (o deben congelarse)
- **Automatizaciones n8n complejas para Trading:** n8n debe limitarse a enviar/recibir notificaciones (Telegram) o mover datos lentos. NO debe orquestar el flujo de ejecución rápida.
- **Complejidad en el EA de MetaTrader:** El EA en MQL5 debe ser "tonto" (Dumb Execution Node), limitándose a ejecutar comandos HTTP (Buy, Sell, Close, Modify SL/TP). La inteligencia debe vivir en Python.
- **Implementación prematura de Agentes Autónomos (AutoGPT/Skills/MCP):** El uso de memoria semántica o MCPs para trading es peligroso en esta fase. Se debe posponer hasta tener el Risk Engine al 100%.

## 6. Componentes que Faltan
- **Central Core (Python):** Un orquestador central (API REST / Event Loop) que reciba todas las señales y controle el paso a través de las capas.
- **RiskManager Module:** Clase determinista que bloquea operaciones riesgosas antes y después de la IA.
- **Kill Switch Daemon:** Un hilo separado que vigile el MT5 (Balance/Equidad). Si detecta caída del X%, cierra todas las operaciones y apaga el Central Core.
- **Audit System (JSON/SQLite):** Almacenamiento local para cada evento del sistema (Signal Received -> AI Approved -> Risk Validated -> Executed).

## 7. Responsabilidades por Capa
| Entidad | Responsabilidad | Lo que NO hace |
| :--- | :--- | :--- |
| **MT5 EA** | Ejecutar órdenes, modificar niveles, informar estado (Balance, Equidad, Posiciones). | NO toma decisiones. NO analiza el mercado. |
| **Python Core** | Orquestar el flujo, aplicar reglas deterministas (Risk Engine), gestionar el Kill Switch. | NO delega la ejecución sin validación. |
| **AI Agent** | Leer contexto, entender sentimiento, justificar si la señal técnica tiene sentido fundamental. | NO ejecuta operaciones. NO altera límites de riesgo. |
| **n8n / Telegram**| Interfaz de notificaciones y Approval Layer (botones In-line de Telegram). | NO alberga lógica de trading. |
| **Usuario** | Configurar límites, aprobar trades excepcionales, analizar las justificaciones de la IA. | NO necesita programar día a día. |

## 8. Flujo Operativo Ideal (Trade Lifecycle)
1. **[SIGNAL]** TradingView envía webhook POST `/signal` al Python Core.
2. **[LOG]** Python Core asigna un UUID y guarda en la base de datos (Status: `PENDING_AI`).
3. **[AI VALIDATION]** Python Core solicita a la IA que evalúe la señal basándose en el historial y contexto.
4. **[RISK CHECK]** Python Core pasa la señal (y el veredicto de la IA) al Risk Engine para verificar que se cumplen los parámetros de seguridad.
5. **[APPROVAL]** Si la estrategia lo requiere (o si la confianza es baja), el Core envía a Telegram un mensaje interactivo: *"Señal EURUSD evaluada. ¿Aprobar? [SI] / [NO]"*. El flujo queda en pausa (`PENDING_APPROVAL`).
6. **[EXECUTION]** Al aprobar, Python Core envía a MT5 (vía Gatekeeper). Status cambia a `EXECUTED`.
7. **[MONITORING]** MT5 maneja el Trade. Kill Switch vigila el margen global 24/7.

## 9. Modelo Formal de Permisos
- **Autónomo Permitido:** Rechazar operaciones si la señal es mala. Cerrar operaciones si se alcanza SL/TP dinámico o el Kill Switch se activa.
- **Requiere Aprobación (Humano):** Abrir nuevas operaciones (hasta que se pase a modo Autónomo total), aumentar riesgo o sobrepasar número máximo de trades simultáneos.
- **Prohibido:** Modificar el Risk Engine, desactivar el Kill Switch, operar sin Stop Loss, ejecutar operaciones que la IA aprobó pero el Risk Engine rechazó.

## 10. Roadmap Priorizado y Profesional
*Este roadmap suspende la ejecución real y la creación de nuevos algoritmos hasta consolidar la infraestructura.*

- **Fase 1: Refactorización y Arquitectura Base (Semanas 1-2)**
  - Unificar repositorios y limpiar carpetas redundantes.
  - Crear el **Python Core** central (FastAPI o similar) para orquestar.
- **Fase 2: Modelado de Datos y Estándares (Semana 3)**
  - Definir las clases/estructuras para `Signal`, `Trade`, `RiskProfile`, `LogEvent`.
- **Fase 3: Desarrollo del Risk Engine & Kill Switch (Semanas 4-5)**
  - Lógica determinista pura. Test unitarios exhaustivos (sin IA).
- **Fase 4: Audit & Logging Layer (Semana 6)**
  - Trazabilidad UUID en base de datos local (SQLite o JSON logs estructurados).
- **Fase 5: Approval Layer & Notificaciones (Semana 7)**
  - Integración segura con Telegram vía webhooks al Python Core (n8n opcional solo como pasarela).
- **Fase 6: AI Validator Integration (Semana 8)**
  - Conectar los LLMs (DeepSeek/Ollama) al Core, con prompts estructurados para devolver JSON estricto.
- **Fase 7: Paper Trading (Semanas 9-11)**
  - Operativa completa en Demo. Monitoreo pasivo para afinar la IA y el Risk Engine.
- **Fase 8: Ejecución Real Controlada (Semana 12+)**

---

### Recomendaciones Estratégicas Finales
El error más común en trading algorítmico es la "deuda técnica letal". Construir bots sobre bases frágiles funciona en backtest pero quiebra cuentas en producción. 
A partir de hoy, la mentalidad cambia: **Trataremos este proyecto como un sistema de alta criticidad (Mission-Critical).** Todo componente asume que los demás van a fallar (Zero Trust). El Kill Switch es nuestro seguro de vida, y el Risk Engine nuestro CEO. La IA es solo un analista inteligente, pero subordinado.
