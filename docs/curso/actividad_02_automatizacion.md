# Actividad 2 — ¿Qué puede automatizarse y qué necesita inteligencia?
**Programa:** Antigravity + IA | **Módulo:** Clase 2 — Desglosando el Reto  
**Fecha de realización:** Abril 2026  
**Herramienta utilizada:** Agente IA Analista de Procesos

---

## 🏗️ Desglose de Tareas de la Solución (El "Gatekeeper" Emocional)

A partir del reto de diseño formulado en la Actividad 1 (controlar el impulso emocional mediante reglas estrictas), hemos desglosado el sistema de protección en 6 tareas concretas y las hemos clasificado según la tecnología necesaria.

### 🟢 Tareas Automatizables (Lógica Matemática / Make / n8n)
*Reglas "Si X entonces Y". Mover datos de un lado a otro.*

1. **Validar posiciones y calcular riesgo (0.5%)**
   * **Descripción:** Comprobar cuántos activos hay abiertos. Si hay < 2, calcular el tamaño del lote para que el Stop Loss equivalga exactamente al 0.5% del saldo de la cuenta.
   * **Por qué:** Es matemática pura y lectura de base de datos.
2. **Recopilación de noticias financieras**
   * **Descripción:** Extraer automáticamente los titulares de los principales portales financieros (ej. Investing, Bloomberg) mediante RSS o APIs.
   * **Por qué:** Es una acción repetitiva de recolección de datos ("copiar y pegar").
3. **Notificaciones y Registro (Diario de Trading)**
   * **Descripción:** Enviar alertas al móvil vía Telegram y registrar automáticamente todos los datos de la operación (fecha, activo, PnL, lotaje) en Google Sheets o en una base de datos.
   * **Por qué:** Ejecución directa, sin necesidad de interpretación.

### 🔵 Tareas que Necesitan IA (Antigravity / LLMs locales)
*Interpretación de contexto, comprensión lectora y toma de decisiones.*

4. **Análisis de Sentimiento de Mercado**
   * **Descripción:** Leer los titulares financieros extraídos en la Tarea 2 y determinar si el contexto macroeconómico es de "Risk-On" (euforia) o "Risk-Off" (miedo).
   * **Por qué:** Requiere entender el tono y las implicaciones financieras del texto.
5. **Filtro Emocional (La más importante)**
   * **Descripción:** Antes de abrir la operación, el trader debe escribir una justificación. La IA analiza el texto para detectar ansiedad, impulsividad, urgencia ("tengo que recuperar") o venganza contra el mercado.
   * **Por qué:** Identificar sesgos cognitivos o estados alterados en un texto requiere comprensión psicológica profunda.

### 🟡 Opcional / Para Después
6. **Histórico Emocional Cruzado**
   * **Descripción:** Cruzar los resultados de las operaciones a largo plazo con el estado de ánimo detectado, para encontrar patrones (ej. "Pierdes el 80% de los trades cuando operas enfadado").
   * **Por qué:** Es Business Intelligence avanzada; muy útil, pero no bloquea el funcionamiento del sistema inicial.

---

## 🎯 Conclusiones y Próximos Pasos

* **Total de tareas:** 3 Automatizables 🟢 | 2 Necesitan IA 🔵 | 1 Para después 🟡
* **Tarea Crítica:** El **Filtro Emocional (Tarea 5)**. Es el núcleo de la solución, el mecanismo de gobernanza que mitiga el riesgo cognitivo.
* **Primer Paso a Construir (Clase 3):** Conectar Telegram con el sistema para validar la regla matemática de riesgo (máximo 2 activos, 0.5% de riesgo) antes de permitir una entrada.

---

## 💡 Resolución a la Duda Principal: ¿Cómo hacer un "Gatekeeper" real?

*Duda: ¿Cómo puedo diseñar el flujo para que el veredicto de Antigravity bloquee técnicamente la operación (gatekeeper) y no sea solo un aviso?*

**La Solución en la Arquitectura Antigravity:**
El bloqueo no lo puede hacer Make por sí solo ni Telegram. El bloqueo se hace en el script de Python que ejecuta la orden en MetaTrader 5 (`mt5.order_send()`). 

El flujo será el siguiente:
1. Tú envías tu "Petición de Entrada" + "Justificación Escrita" por **Telegram**.
2. **Make** recibe el mensaje y se lo envía a nuestro laboratorio en Python.
3. El script de Python consulta a la **IA Local (Ollama)** sobre tu justificación (Tarea 5).
4. La IA devuelve un veredicto estructurado: `{"estado": "APROBADO"}` o `{"estado": "BLOQUEADO"}`.
5. **El Gatekeeper (Código Python):** Si el estado es "BLOQUEADO", el código de Python activa un `return` abortando el proceso inmediatamente, y le manda a Make un mensaje de vuelta diciendo *"Operación rechazada por estado emocional alterado"*. El código de MT5 que abre la operación jamás llega a ejecutarse.
