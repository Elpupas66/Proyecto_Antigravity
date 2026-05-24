# Product Requirements Document (PRD)

## Gatekeeper de Trading — Filtro Racional y Emocional con IA

---

## 1. Visión General / Resumen Ejecutivo

Este documento define los requisitos para el desarrollo del "Gatekeeper", un sistema automatizado de intercepción de órdenes de trading. Su objetivo es actuar como barrera de seguridad entre la decisión del trader y el envío de la orden a MetaTrader 5, validando tanto reglas matemáticas estrictas como el estado emocional del operador a través de Inteligencia Artificial. Esto mitigará el sabotaje emocional provocado por la necesidad de recuperar pérdidas pasadas, asegurando la consistencia del sistema de trading.

---

## 2. Objetivos del Producto

- **Implementar control matemático de riesgo:** Forzar de manera inquebrantable el límite de 0,5% de riesgo por operación y un máximo de 2 activos abiertos simultáneamente.
- **Implementar filtro emocional:** Analizar la justificación de entrada del trader usando un LLM en la nube (ej. ChatGPT, Claude, DeepSeek) para detectar ansiedad, impulsividad o deseo de venganza contra el mercado.
- **Bloqueo técnico duro:** Impedir la ejecución de la orden a nivel de código (script Python - MT5) si las validaciones no son superadas, pasando de un simple "aviso" a un bloqueo real.
- **Trazabilidad total:** Registrar todas las interacciones, tanto aprobadas como rechazadas, para alimentar un Diario de Trading objetivo.

---

## 3. Alcance (MVP - Minimum Viable Product)

**Incluye:**
- Interfaz de entrada mediante un bot de Telegram.
- Flujo de comunicación gestionado vía Make/n8n hacia el entorno local.
- Evaluación emocional de la "justificación de entrada" usando la API de un LLM en la nube.
- Validación de condiciones (activos abiertos y lotaje) en Python mediante integración con MetaTrader 5.
- Respuesta estructurada de APROBADO o BLOQUEADO enviada de vuelta a Telegram.
- Registro automático en archivo CSV o Google Sheets.

**No incluye (Futuras versiones):**
- Análisis avanzado cruzado del histórico emocional con el PnL a largo plazo.
- Conexiones a múltiples plataformas de trading adicionales a MT5.
- Interfaz web gráfica (Dashboard).

---

## 4. Usuarios y Roles

### 4.1 Usuarios
- Trader individual (Operador principal).

### 4.2 Permisos
- El trader es el único usuario del sistema.
- El sistema actúa de manera autónoma con permisos de ejecución sobre la API de MT5, con autoridad absoluta para vetar operaciones del usuario.

---

## 5. Flujo de Usuario y Lógica Operativa

1. **Intención de Entrada:** El trader identifica una oportunidad (ej. Setup en DAX40 tras análisis técnico, fundamental o cuantitativo).
2. **Solicitud de Ejecución:** A través de Telegram, el trader envía los parámetros de la orden y un párrafo justificando técnicamente la entrada.
3. **Recepción y Enrutamiento:** Make/n8n captura el mensaje y lanza un webhook al script local de Python.
4. **Validación Dual:**
   - *Fase 1 (Matemática):* Python revisa MT5. Si hay ≥ 2 activos abiertos o el cálculo del lotaje supera el 0,5% de riesgo, devuelve `BLOQUEADO`.
   - *Fase 2 (Psicológica):* Python envía el texto de justificación a la API del LLM en la nube. El LLM analiza si hay sesgos cognitivos o impulsividad.
5. **Veredicto Final:** 
   - Si la IA devuelve `APROBADO`, Python ejecuta `mt5.order_send()` y notifica éxito por Telegram.
   - Si la IA devuelve `BLOQUEADO`, Python descarta la orden, notifica el motivo del bloqueo por Telegram y anota el evento en el registro.

---

## 6. Arquitectura Técnica

### 6.1 Interfaz y Orquestación
- **Mensajería:** API de Telegram (Bot).
- **Automatización Web:** Make o n8n.

### 6.2 Lógica Core y Procesamiento (Entorno Local o Servidor VPS)
- **Lenguaje:** Python 3.10+.
- **Integración Broker:** Librería oficial `MetaTrader5` de Python.
- **Inteligencia Artificial:** LLM en la nube conectado mediante API (ej. OpenAI, Anthropic, Gemini, DeepSeek, Grok, Qwen) o alojado en un VPS externo para no ralentizar la máquina local.

### 6.3 Base de Datos / Registro
- **MVP:** Archivo local CSV para logging rápido.
- **Fase 2:** Integración con Google Sheets para el "Diario de Trading".

---

## 7. Métricas de Éxito (KPIs)

El éxito del Gatekeeper se medirá con los indicadores definidos en la etapa de análisis del problema:

1. **Disciplina (Proceso):** ≥ 90% de las operaciones ejecutadas cumplen con el 100% de las reglas del sistema (medido por el ratio de operaciones aprobadas que resultan conformes al plan de trading).
2. **Riesgo (Control):** Drawdown máximo mensual de la cuenta ≤ 3%. El sistema debe prevenir las caídas abruptas por sobreoperación.
3. **Rentabilidad (Resultado):** WinRate sostenido ≥ 58% en el timeframe operativo (H1/D1) durante 3 meses consecutivos, gracias a la filtración de operaciones impulsivas.

---

## 8. Riesgos y Mitigaciones

- **Latencia:** El tiempo de respuesta de la API del LLM o la red podría tardar y hacer que se pierda el precio de entrada óptimo. 
  *Mitigación:* Usar endpoints de modelos rápidos (ej. versiones Flash o Haiku) para garantizar respuestas en < 5 segundos.
- **Falsos Positivos de la IA:** La IA podría bloquear una operación válida confundiendo convicción técnica con impulsividad.
  *Mitigación:* Refinar iterativamente el system prompt del LLM proporcionando ejemplos claros de justificaciones válidas vs impulsivas.
- **Caída de la API de MT5:** Errores de conexión local.
  *Mitigación:* Implementar un sistema de retries y alertas de error claras en Telegram.

---

## 9. Cronograma Tentativo

- **Semana 1:** Setup del entorno Python y conexión con la API de MT5 para validación de lotaje y lectura de posiciones.
- **Semana 2:** Configuración del webhook en n8n/Make y el bot de Telegram.
- **Semana 3:** Implementación y ajuste del prompt de análisis de sentimiento con el LLM seleccionado vía API.
- **Semana 4:** Pruebas integradas en cuenta Demo (Paper Trading).
- **Semana 5:** Despliegue en producción con capital controlado.

---

## 10. Conclusión y Filosofía de Mejora Continua

En el desarrollo de software (y aún más en el trading sistemático), la primera versión rara vez es la definitiva. Lo importante de este documento es establecer unos cimientos sólidos, definir el "qué" y el "por qué", y delimitar de forma clara el Producto Mínimo Viable (MVP).

Una vez que el sistema se ponga en marcha, comenzará un proceso iterativo de mejora continua: refinaremos el análisis del LLM, mediremos los tiempos de latencia reales en condiciones de mercado, ajustaremos las métricas e iremos escalando la arquitectura conforme lo pida el proyecto.
