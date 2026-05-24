# Actividad 1 — Descubre tu Problema de Negocio con IA
**Programa:** Antigravity + IA | **Módulo:** Clase 1 — El punto de partida es el problema  
**Fecha de realización:** Abril 2026  
**Herramienta utilizada:** Agente IA Consultor (prompt estructurado en 7 fases)

---

## 🏢 Mi Negocio

**Operativa de trading multiactivo** (Forex, Índices y Commodities) gestionada de forma individual. El negocio consiste en analizar mercados financieros y ejecutar operaciones de compra y venta de activos como el DAX40 (GER40), S&P500 (US500), pares de divisas como EURGBP, y activos digitales como BTCUSD, con el objetivo de generar rendimiento financiero de forma consistente y sistemática.

Pese a contar con formación externa de calidad (academia Blacksheep/Vortex) y haber desarrollado herramientas de análisis cuantitativo propias (el Laboratorio de IA Antigravity), la operativa carece de un sistema propio consolidado que guíe la ejecución de forma disciplinada e independiente del estado emocional del operador.

---

## ⚙️ Proceso Problemático

**¿Cuál es el proceso?**  
La **ejecución de operaciones en tiempo real**: el momento en el que, tras analizar el mercado y detectar una señal válida, hay que tomar la decisión de entrar, gestionar y salir de una operación.

**¿Por qué lo elegí?**  
Porque es el eslabón donde todo el conocimiento técnico acumulado (formación, backtesting, indicadores desarrollados) se puede desmoronar en segundos. Un sistema de análisis impecable no sirve de nada si en el momento de pulsar el botón la emoción toma el control. Es el cuello de botella que convierte meses de trabajo técnico en resultados inconsistentes.

---

## 🔍 Causa Raíz — Los 5 Por Qués

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | ¿Por qué la ejecución es inconsistente? | Porque no siempre sigo las reglas del sistema. |
| 2 | ¿Por qué no las sigues? | Porque en determinados momentos la presión emocional es mayor que la convicción en el sistema. |
| 3 | ¿Por qué hay tanta presión emocional? | Porque hay pérdidas pasadas sin recuperar que generan ansiedad y urgencia. |
| 4 | ¿Por qué esa urgencia afecta a las decisiones? | Porque la necesidad de "recuperar" lleva a buscar resultados rápidos, saltándose el proceso y el control del riesgo. |
| 5 | ¿Por qué esa necesidad de recuperar tiene tanto peso? | Porque la inversión en formación (3.000€) y el capital perdido en CFDs generan una carga de validación personal y familiar que mezcla el trading con la autoestima. |

**Causa raíz identificada:**  
> La ansiedad por recuperar pérdidas pasadas y validar el éxito personal (y familiar) nubla el análisis objetivo y empuja hacia decisiones impulsivas que sabotean la ejecución del sistema, incluso cuando el análisis técnico es correcto.

---

## 🎯 Reto de Diseño — Enunciado HMW

**Formulación principal elegida:**

> **¿Cómo podríamos implementar un sistema de registro de operaciones y reglas de riesgo estrictas (máximo 2 activos sin proteger, riesgo del 0,5% por operación) para lograr consistencia estadística, sin que la necesidad emocional de recuperar capital sabotee la ejecución?**

**Formulaciones alternativas consideradas:**

- *¿Cómo podríamos crear un "filtro racional" automatizado que bloquee la entrada a operaciones cuando el estado emocional no sea el adecuado?*
- *¿Cómo podríamos transformar el diario de trading en una herramienta de feedback continuo que desacople los resultados económicos de la autoestima del operador?*

---

## 📊 Mis 3 Indicadores de Éxito

| # | Dimensión | Indicador | Forma de medirlo |
|---|---|---|---|
| 1 | **Disciplina (Proceso)** | % de operaciones ejecutadas siguiendo el 100% de las reglas del sistema | Diario de trading: ratio operaciones conformes / total de operaciones. **Objetivo: ≥ 90%** |
| 2 | **Riesgo (Control)** | Drawdown máximo mensual inferior al 3% de la cuenta | Revisión de equity curve mensual generada por el Laboratorio. **Objetivo: nunca superar -3%** |
| 3 | **Rentabilidad (Resultado)** | WinRate estadísticamente superior al 58% mantenido durante 3 meses consecutivos | Script `analyze_assets.py` del laboratorio. **Objetivo: ≥ 58% en TF operativo (H1/D1)** |

---

## 💭 Mi Reflexión sobre la Experiencia con IA (150 palabras)

Trabajar con un agente IA estructurado como consultor ha sido una experiencia sorprendentemente diferente a usar la IA para obtener respuestas directas. El mayor valor no estuvo en lo que el agente me dijo, sino en lo que me obligó a pensar.

El proceso de los 5 Por Qués fue el momento de mayor impacto. Cuando el agente me preguntó por tercera vez "¿y por qué ocurre eso?", tuve que admitir algo que sabía pero que evitaba nombrar: el problema real no es técnico, no es la estrategia ni el indicador. El problema es emocional y tiene nombre propio — la necesidad de recuperar pérdidas mezclada con la autoestima.

Esa conclusión la tenía en algún rincón de mi mente, pero el diálogo guiado la trajo a la superficie de forma ordenada y sin juzgarme. Un coach humano habría tardado varias sesiones en llegar a ese punto.

Lo que me llevo de esta actividad es que la IA es más útil como "espejo socrático" que como "oráculo". No me dio la respuesta; me hizo las preguntas correctas hasta que yo mismo llegué a ella. Eso, aplicado al trading, tiene un valor incalculable: un sistema que me haga las preguntas correctas antes de ejecutar una operación podría ser más valioso que cualquier indicador técnico que haya desarrollado.

La frase del programa "la IA propone, el humano dispone" cobró un significado muy concreto: la IA estructuró el proceso, pero la honestidad y las decisiones fueron completamente mías.

---

## 📁 Conexión con el Proyecto Antigravity

Esta actividad no es teórica; está directamente conectada con el trabajo práctico del laboratorio:

- El **Laboratorio de Trading** (`trading/`) es parte de la **solución técnica** al reto identificado.
- El script `analyze_assets.py` es la base del **Indicador de Éxito nº 3** (WinRate ≥ 58%).
- El futuro **Diario de Operaciones automatizado** (próximo agente a desarrollar) será el instrumento del **Indicador de Éxito nº 1** (disciplina de ejecución).

> *"Recuerda: la IA te ha ayudado a pensar, pero las decisiones son tuyas. Ese es el enfoque Antigravity."*
