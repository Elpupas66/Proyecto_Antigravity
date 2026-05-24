# 🗺️ Roadmap y Bitácora General del Proyecto
### Laboratorio de Trading Automatizado

> **Propósito:** Este documento mantiene un registro determinista de todas las acciones, decisiones y progresos realizados por el usuario y Antigravity. Garantiza la trazabilidad total del proyecto.

---

## 📍 Estado Actual (17/05/2026)
**✅ Infraestructura E2E completamente validada.**
- El pipeline completo TradingView → n8n → Gatekeeper API → MetaTrader 5 está operativo y probado en producción.
- La primera estrategia implementada (Blacksheep Vortex) ha sido descartada tras backtesting exhaustivo. Ver [`bitacora_vortex.md`](./bitacora_vortex.md) para el detalle completo.
- **Siguiente acción pendiente:** Seleccionar e implementar una nueva estrategia de trading en el laboratorio.

---

## 📝 Bitácora de Actividades

### Sesión 1 - 02/05/2026
- **Acción:** Inicialización del marco de trabajo determinista.
- **Artefactos creados:** 
  - `reglas_base_antigravity.md` (Reglas generales heredadas del curso).
  - `normas_proyecto_trading.md` (Restricciones de riesgo, flujos de validación).
- **Decisión estratégica:** Descartar archivos de texto/Word intermedios no oficiales para basar la codificación exclusivamente en las fuentes originales de la academia para cada estrategia.
- **Estructura creada:** Se han generado todas las carpetas necesarias (`estrategia/`, `backtests/`, `produccion/`, etc.) para organizar el ciclo de vida del desarrollo.

---

### Sesión 2 - 15/05/2026
- **Acción:** Consolidación de la Arquitectura de Documentación y Seguridad.
- **Detalle de las acciones (Los 4 puntos clave):**
  1. **Reestructuración de `/docs`:** Creación de subcarpetas temáticas (`/architecture`, `/environment`, `/management`, `/trading_rules`) y reubicación semántica de los documentos (ej. `PRD_AI_DEV_ENV.md` en `/architecture`).
  2. **Punto de Entrada (`README.md`):** Creación del README principal en la raíz con el índice del proyecto, contexto y comandos de inicio rápido.
  3. **Seguridad y Limpieza (`.gitignore`):** Creación del archivo para evitar la exposición accidental de credenciales (`.env`), entornos virtuales (`.venv`) y configuraciones pesadas de IA local.
  4. **Trazabilidad (`CHANGELOG.md`):** Inicialización del archivo de log de versiones en `/docs/CHANGELOG.md` para mantener el registro evolutivo de las automatizaciones y configuración de IA.

---

### Sesión 3 - 17/05/2026
- **Acción:** Validación E2E del pipeline de automatización y cierre del ciclo de la estrategia Blacksheep Vortex.
- **Logros principales:**
  1. **Pipeline E2E funcional:** Se confirmó el flujo completo TradingView → Webhook n8n → DeepSeek AI → Gatekeeper API → MetaTrader 5. Se abrieron 2 órdenes reales en cuenta demo de MT5 de forma completamente automática.
  2. **Backtesting Bvortex cerrado:** Tras probar la estrategia en múltiples activos (Forex, Oro, Plata, Petróleo, Bitcoin), temporalidades (1H, 4H, 1D) y parámetros (nivel extremo ±15/±17/±20, R:R 1:1 a 1:3), **la estrategia no alcanzó rentabilidad en ninguna combinación**. Descartada oficialmente.
  3. **Guía de errores documentada:** Se identificaron y documentaron en `bitacora_vortex.md` los 5 errores típicos de conexión del pipeline (404 webhook, 502 Bad Gateway, URL incorrecta de Cloudflare, alertas que no disparan, módulo de Python no encontrado) con sus causas y soluciones para evitar repetición en futuras estrategias.
- **Para el detalle completo de esta sesión, ver:** [`bitacora_vortex.md`](./bitacora_vortex.md) — Sección "Sesión 3".

---

### Sesión 4 - 24/05/2026
- **Acción:** Auditoría Arquitectónica Completa (Transición a Infraestructura Profesional).
- **Logros principales:**
  1. **Análisis de Estado:** Diagnóstico de la arquitectura actual, identificando acoplamiento prematuro, falta de control de riesgos y estado inconsistente.
  2. **Diseño de Nueva Arquitectura (6 Capas):** Se define un modelo basado en Signal Engine, AI Validator, Risk Engine, Approval Layer, Execution Layer y Ecosistema (Logs/Kill Switch).
  3. **Nuevo Roadmap Definido:** Se paraliza la creación de algoritmos nuevos para priorizar el desarrollo del Central Core en Python, el Risk Engine y los sistemas de auditoría inmutables.
- **Artefactos creados:**
  - Documento maestro de arquitectura: [`bitacora_auditoria_arquitectura.md`](./bitacora_auditoria_arquitectura.md) (Contiene los 10 puntos auditados).

---

## 📊 Nota Metodológica: Fuentes de Datos Históricos para Backtesting

> Registrado el 17/05/2026 tras consulta con la academia.

El rigor del backtesting depende directamente de la calidad del histórico utilizado. El laboratorio distingue tres fuentes:

| Fuente | Ecosistema | Calidad | Uso recomendado |
|---|---|---|---|
| **TradingView (interno)** | Pine Script / `strategy()` | Buena (OHLC por vela) | Backtesting de indicadores en Pine Script |
| **MT5 Demo (VT Markets)** | MetaTrader 5 EAs | Media (histórico sintético del bróker) | Solo para pruebas rápidas, no para validación final |
| **Dukascopy** ([enlace](https://www.dukascopy.com/europe/spanish/home/)) | MetaTrader 5 EAs | **Excelente** (tick a tick, gratuito) | Validación rigurosa de EAs en MQL5 |
| **StrategyQuant** ([enlace](https://strategyquant.com/es/quantdatamanager/)) | MT5/MT4 EAs | Profesional | Optimización avanzada (versión gratuita con límites) |

### Reglas de uso para este laboratorio

1. **Si la estrategia se implementa en Pine Script (TradingView):** El histórico de TradingView es el único disponible y es suficiente. No es posible inyectar datos externos de Dukascopy en TradingView. La limitación conocida es que el probador trabaja con velas OHLC (no tick a tick), lo que puede inflar ligeramente los resultados en estrategias con stops muy ajustados.

2. **Si la estrategia se implementa como EA en MQL5 (MetaTrader 5):** Obligatorio importar ticks de **Dukascopy** para el backtesting final. Flujo:
   - Descargar datos tick desde dukascopy.com (formato `.csv` o `.hst`).
   - Importar en MT5: `Herramientas → Historial de Cotizaciones`.
   - Ejecutar el Probador de Estrategias de MT5 en modo **"Cada tick"**.

3. **Nunca usar el histórico del bróker demo como validación final:** Los brókers demo sintetizan el histórico, lo que genera ejecuciones de órdenes en precios imposibles en mercado real e infla el Profit Factor artificialmente.

---

## 🚀 Ciclo de Vida Estándar de las Estrategias (Plantilla)

*Cada estrategia añadida al laboratorio deberá contar con su propia bitácora (ej. `bitacora_vortex.md`) que seguirá las siguientes fases comunes:*

### Fase 1: Documentación de la Estrategia
- [ ] Ejecutar extracción de texto sobre los materiales de origen de la academia.
- [ ] Redactar el documento maestro: `estrategia/documentacion/especificacion_[nombre_estrategia].md`.
- [ ] Validación manual por parte del usuario de las reglas extraídas.

### Fase 2: Desarrollo del Algoritmo
- [ ] Traducir las especificaciones de Markdown a código (MQL5 para MetaTrader o Pine Script para TradingView).
- [ ] Implementar la función obligatoria `validar_riesgo()`.
- [ ] Compilación y corrección de errores sintácticos.

### Fase 3: Backtesting y Validación
- [ ] Definir el marco de pruebas (Activos, timeframe, periodo histórico).
- [ ] Ejecutar backtest y exportar resultados.
- [ ] Validar métricas contra las `normas_proyecto_trading.md` (Sharpe > 1.0, Profit Factor > 1.3, etc.).

### Fase 4: Paper Trading
- [ ] Desplegar algoritmo en entorno de demostración (dinero virtual).
- [ ] Monitorización durante mínimo 2 semanas.
- [ ] Revisión de logs y concordancia con el backtest.
