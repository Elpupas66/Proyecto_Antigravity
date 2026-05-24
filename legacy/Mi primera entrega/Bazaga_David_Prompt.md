# Documento 1: Prompt Optimizado

**Título del proyecto:** Gatekeeper de Trading — Filtro Racional y Emocional con IA
**Modelo utilizado:** CREA (Contexto, Rol, Especificaciones, Acción)

### Prompt Completo:

**Contexto:** 
Soy un trader que opera de forma individual en mercados multiactivo (Forex, Índices, Commodities). Opero basándome en una combinación de Análisis Técnico (estructura del mercado, manipulación institucional, desequilibrios, lectura de gráficos, patrones de precios e indicadores), Análisis Fundamental (evaluación de factores económicos, financieros, resultados de empresas y tendencias macroeconómicas para determinar valor intrínseco) y Trading Cuantitativo (utilización de modelos matemáticos y algoritmos para identificar oportunidades y operar a gran escala). Sin embargo, tengo un cuello de botella crítico en la ejecución: la ansiedad por recuperar pérdidas pasadas y la presión de validación personal me empujan a tomar decisiones impulsivas, ignorando mis propias reglas de gestión de riesgo (máximo 0,5% por operación y máximo 2 activos abiertos).

**Rol:** 
Actúa como un Product Manager senior especializado en sistemas algorítmicos de trading, automatización de procesos e inteligencia artificial aplicada al control de riesgos (fintech).

**Especificaciones:** 
Quiero diseñar un sistema "Gatekeeper" (guarda barreras) automatizado que intervenga justo antes de lanzar una orden al mercado (MetaTrader 5). El sistema debe recibir una "justificación de entrada" escrita por mí vía Telegram. A partir de ahí, debe utilizar automatizaciones (Make/n8n) y un LLM en la nube (API de OpenAI, Anthropic, Gemini, DeepSeek, etc.) para: 
1. Validar matemáticamente que se cumple la regla del 0,5% de riesgo y máximo 2 activos. 
2. Realizar un análisis psicológico del texto para detectar urgencia, impulsividad, venganza contra el mercado o exceso de euforia. 
Si el sistema detecta vulnerabilidad emocional o incumplimiento matemático, debe devolver un estado de "BLOQUEADO", impidiendo que el script de Python envíe la orden al mercado. Todo debe quedar documentado en un registro de operaciones.

**Acción:** 
Genera un Product Requirements Document (PRD) exhaustivo para este sistema Gatekeeper. El documento debe seguir la estructura estándar de desarrollo de producto e incluir: Resumen Ejecutivo, Objetivos del Producto, Alcance del MVP, Arquitectura Técnica (Python, MT5, Make, Telegram, APIs de LLM Cloud), Flujo de Usuario, y Métricas de Éxito concretas (Disciplina ≥ 90%, Drawdown ≤ 3%, WinRate ≥ 58%).
