# Entregable Fase 1: MVP del Gatekeeper de Trading

## 1. El Problema de Negocio (Actividad 1)
**El Problema:** La ejecución operativa inconsistente debido a la interferencia emocional y el sabotaje al sistema (exceso de operaciones y apalancamiento) para "recuperar" pérdidas.
**La Solución:** Un "Gatekeeper" (Guardabarrera) que actúa como intermediario obligatorio. El trader pierde la capacidad de ejecutar órdenes directamente en su broker, delegando la ejecución a un sistema que valida estrictamente las matemáticas y las emociones.

## 2. Distribución de Arquitectura (Actividad 2)
Aplicando la premisa fundamental ("¿Qué se puede automatizar y qué necesita IA?"), hemos construido una solución local que orquesta ambas vertientes:
- **Automatizable (Módulo Python + MT5):** Se encarga de la matemática pura. El sistema conecta directamente con la API de MetaTrader 5 para validar de forma binaria si el trader está incumpliendo su límite de activos simultáneos o su riesgo por operación. También lanza las órdenes a mercado (SL, TP).
- **Inteligencia Artificial (Módulo DeepSeek):** Se encarga del análisis de comportamiento. La orden del trader, que incluye una "justificación escrita", se envía mediante un prompt sistémico a un modelo LLM. Éste detecta sesgos de venganza, ansiedad o falta de soporte técnico, bloqueando la orden si es necesario.

## 3. Demostración Técnica Conseguida
Se ha programado e implementado el script `gatekeeper_bot.py`, que actúa como Bot de Telegram. El flujo de éxito validado en cuenta Demo es el siguiente:

1. **Entrada de Usuario:** El trader envía un mensaje parametrizado por Telegram (Ej: `COMPRAR BTCUSD 0.01 MERCADO SL 60000 TP 66000 Porque el análisis técnico...`).
2. **Orquestación:** El Bot recibe la orden e inicia la validación.
3. **Control MT5:** Python verifica en MetaTrader 5 el número de posiciones abiertas. Si supera las reglas, devuelve *BLOQUEADO*.
4. **Control IA:** Si MT5 da luz verde, la justificación viaja a la API de DeepSeek. El sistema cognitivo evalúa el texto y devuelve *APROBADO* o *BLOQUEADO*.
5. **Ejecución:** Si la IA otorga el *APROBADO*, el script Python construye la petición y ejecuta la función `mt5.order_send()`, abriendo la posición real en el mercado y devolviendo el ticket al usuario en Telegram.

## 4. Archivos Entregables
- El código fuente central reside en: `scripts/gatekeeper_bot.py`
- Las variables de entorno de seguridad (claves API) en: `.env`
