# 📊 Normas del Proyecto — Trading con IA (Blacksheep Vortex)
### Stack: Antigravity · MetaTrader 5 · TradingView · Python/Pine Script
### Proyecto: Laboratorio de Trading Automatizado
### Versión: 1.0

> **¿Para qué sirve este fichero?**
> Define las reglas de trabajo ESPECÍFICAS para el proyecto de trading. Complementa `reglas_base_antigravity.md` con normas adicionales críticas para el dominio financiero, donde un error de código puede tener consecuencias económicas directas. El objetivo es hacer el desarrollo **determinista**, **trazable** y **seguro para el capital**.

---

## ⚠️ PRINCIPIO FUNDAMENTAL — En trading, la IA sugiere, el trader decide

> *"El código no miente, pero puede estar mal escrito. Valida siempre contra el mercado real."*

**Ninguna señal generada por IA, ningún backtest, ningún script en producción** debe operar con capital real sin haber pasado por los tres niveles de validación descritos en estas normas. Esto no es opcional.

---

## 🧭 NORMA 1 — Planificación antes de cualquier cambio en la estrategia

Antes de modificar cualquier parámetro de la estrategia Blacksheep Vortex, abrir cualquier posición con el sistema, o alterar cualquier script en MT5 o TradingView:

**El plan debe responder:**
- ¿Qué hipótesis técnica justifica este cambio?
- ¿En qué activo y timeframe se va a probar?
- ¿Cuáles son los criterios de éxito del backtest?
- ¿Cuál es el riesgo máximo permitido durante la prueba?

**Orden obligatorio de construcción:**
```
1. Hipótesis documentada  → ¿Por qué debería funcionar este cambio?
2. Backtest histórico     → Mínimo 3 meses de datos, 3 activos distintos
3. Paper trading          → Mínimo 2 semanas en demo sin capital real
4. Validación estadística → Ratio Sharpe, Max Drawdown, Win Rate, Profit Factor
5. Producción controlada  → Capital mínimo, tamaño de posición reducido al 25%
6. Escala progresiva      → Solo si los resultados en producción validan el backtest
```

### ❌ Nunca hagas esto:
- Activar un script nuevo directamente en cuenta real sin backtest.
- Cambiar parámetros de una estrategia en producción porque "una operación salió mal".
- Escalar el tamaño de posición antes de tener al menos 30 operaciones de muestra.

---

## 📊 NORMA 2 — Estructura de datos y nomenclatura del laboratorio

Todo archivo, script, backtest o log del proyecto debe seguir esta convención:

```
[tipo]_[activo]_[timeframe]_[versión]_[fecha]

Ejemplos correctos:
  backtest_EURUSD_H1_v2.3_20260430.xlsx
  script_mt5_vortex_entrada_filtro_volumen_v1.py
  log_operaciones_BTCUSD_D1_mayo2026.csv
  reporte_rendimiento_SP500_H4_semana18.md

Ejemplos incorrectos:
  backtest_nuevo.xlsx
  script_final_v2.py
  mis_operaciones.csv
```

**Estructura de carpetas obligatoria:**
```
Proyecto_antigravity/
├── reglas_base_antigravity.md          ← Reglas genéricas
├── normas_proyecto_trading.md          ← Este fichero
├── estrategia/
│   ├── documentacion/                  ← Especificaciones de la estrategia
│   ├── scripts_mt5/                    ← Código MQL5 para MetaTrader 5
│   ├── scripts_tradingview/            ← Código Pine Script
│   └── versiones/                      ← Historial de versiones de la estrategia
├── backtests/
│   ├── raw_data/                       ← Datos históricos sin procesar
│   ├── resultados/                     ← Reportes de backtest por versión
│   └── comparativas/                   ← Comparación entre versiones
├── paper_trading/
│   ├── logs/                           ← Registro de operaciones en demo
│   └── reportes_semanales/             ← Análisis semanal de resultados
├── produccion/
│   ├── logs_operaciones/               ← Registro de operaciones reales
│   ├── reportes_rendimiento/           ← P&L, métricas, drawdown
│   └── alertas/                        ← Configuración de alertas y stops
└── analisis_mercado/
    ├── SP500/
    ├── DAX40/
    └── BTCUSD/
```

---

## 🛡️ NORMA 3 — Gestión de riesgo no negociable

> *"El primer objetivo de un sistema de trading es sobrevivir. El segundo es ganar."*

Estas restricciones son absolutas y deben estar codificadas en **todo script en producción**:

| Parámetro | Límite | Acción si se supera |
|-----------|--------|---------------------|
| Riesgo por operación | Máx. 1% del capital | Script NO abre la posición |
| Drawdown diario máximo | 3% del capital | Script se desactiva automáticamente |
| Drawdown semanal máximo | 5% del capital | Revisión obligatoria antes de reactivar |
| Drawdown total máximo | 10% del capital | Parada completa del sistema, revisión estratégica |
| Posiciones simultáneas | Máx. 3 posiciones | Script NO abre más hasta que cierre alguna |
| Ratio Riesgo/Beneficio mínimo | 1:1.5 | Si el setup no cumple, no hay operación |

**En el código de cada script de producción, debe existir una función `validar_riesgo()` que compruebe estas restricciones ANTES de ejecutar cualquier orden.**

---

## 📈 NORMA 4 — Métricas mínimas de validación del sistema

Un backtest o periodo de paper trading NO es válido si no incluye estas métricas:

```
Métricas obligatorias de rendimiento:
  ├── Win Rate (%)                → % de operaciones ganadoras
  ├── Profit Factor               → Beneficio bruto / Pérdida bruta (mínimo aceptable: 1.3)
  ├── Ratio de Sharpe             → Rentabilidad ajustada al riesgo (mínimo aceptable: 1.0)
  ├── Máximo Drawdown (%)         → Caída máxima desde el pico (máximo aceptable: 15%)
  ├── Nº de operaciones           → Mínimo 30 para ser estadísticamente relevante
  ├── Duración media de trade     → Para detectar sobreoptimización
  ├── Rendimiento por activo      → EURUSD, SP500, DAX40, BTCUSD por separado
  └── Rendimiento por timeframe   → H1, H4, D1 por separado

Métricas de robustez (anti-overfitting):
  ├── Walk-forward analysis       → El sistema debe funcionar en datos "no vistos"
  ├── Monte Carlo simulation      → Distribución de resultados posibles
  └── Correlación con benchmarks  → Comparar con buy & hold del activo
```

---

## 🔍 NORMA 5 — Análisis técnico: protocolo de entrada al mercado

Para cada operación potencial, el análisis debe seguir este protocolo top-down:

```
NIVEL 1 — Contexto macro (Timeframe: Semanal/Diario)
  ├── Tendencia principal: ¿alcista / bajista / lateral?
  ├── Niveles clave: soportes, resistencias, zonas de volumen
  └── Contexto fundamental relevante (si existe)

NIVEL 2 — Setup técnico (Timeframe operativo: H4/H1)
  ├── Confirmación de señal Vortex
  ├── Filtro de volumen / volatilidad
  ├── Confluencia con niveles de Nivel 1
  └── Patrón de precio de confirmación

NIVEL 3 — Entrada y gestión (Timeframe de entrada: H1/M15)
  ├── Precio de entrada exacto
  ├── Stop Loss: técnico + validado contra Norma 3
  ├── Take Profit: niveles R/R ≥ 1:1.5
  └── Plan de trailing stop o gestión dinámica
```

**Si alguno de los 3 niveles no está claro, NO hay operación.**

---

## 🤖 NORMA 6 — Uso de IA en el proyecto de trading

Define cómo usar Antigravity (y cualquier LLM) de forma determinista:

### Usos VÁLIDOS de la IA:
- ✅ Generar y depurar código MQL5 / Pine Script
- ✅ Automatizar generación de reportes de backtests
- ✅ Análisis de datos históricos y estadísticas
- ✅ Estructurar y documentar la estrategia
- ✅ Optimizar parámetros mediante algoritmos (Bayesiano, Genético)
- ✅ Generar alertas y resúmenes de sesión de mercado

### Usos PROHIBIDOS de la IA:
- ❌ Tomar decisiones de entrada/salida en tiempo real sin validación humana
- ❌ Interpretar datos fundamentales sin fuente verificable
- ❌ Modificar parámetros de estrategia en producción basándose solo en una sugerencia de IA
- ❌ Ejecutar órdenes en cuenta real de forma autónoma sin aprobación explícita

### Protocolo de consulta a Antigravity:
```
ANTES de pedir código o análisis:
  1. Especifica el ACTIVO y TIMEFRAME exactos
  2. Proporciona el contexto completo de la estrategia
  3. Define los criterios de éxito/fracaso del entregable

AL RECIBIR código generado por IA:
  1. Revísalo línea por línea antes de compilar
  2. Pruébalo primero en entorno de test/demo
  3. Valida que incluye la función validar_riesgo()
```

---

## 💬 NORMA 7 — Registro y documentación de operaciones

Todo log de operaciones (paper o producción) debe registrar:

```
Campos obligatorios por operación:
  ├── ID único de operación
  ├── Fecha y hora de apertura (UTC)
  ├── Activo y timeframe de análisis
  ├── Dirección (LONG / SHORT)
  ├── Precio de entrada, SL y TP
  ├── Tamaño de posición y % de riesgo real
  ├── Señal que generó la entrada (criterios Vortex cumplidos)
  ├── Fecha y hora de cierre
  ├── Precio de cierre y resultado (pips / €)
  ├── Razón del cierre (TP / SL / Manual / Trailing)
  └── Notas del trader (aprendizajes, desviaciones del plan)
```

**Revisión semanal obligatoria:** Cada viernes, generar un reporte que incluya las métricas de la Norma 4 para las operaciones de la semana.

---

## 🔒 NORMA 8 — Seguridad de credenciales y APIs

- Las claves de API (brokers, datos de mercado, herramientas externas) se almacenan **únicamente en variables de entorno**, nunca en el código.
- Los scripts con acceso a cuenta real deben tener una variable `MODO_PRODUCCION = True/False` que controle si ejecutan órdenes reales o las simula.
- Antes de desplegar cualquier script nuevo en producción, ejecutar con `MODO_PRODUCCION = False` durante al menos una sesión completa de mercado.

---

## 📋 Checklist de validación — Por etapa del ciclo de vida de la estrategia

### Antes del Backtest ✅
- [ ] Hipótesis de la estrategia documentada
- [ ] Parámetros iniciales definidos y justificados
- [ ] Datos históricos verificados (sin gaps, sin datos erróneos)
- [ ] Métricas de éxito definidas ANTES de ejecutar el backtest

### Después del Backtest ✅
- [ ] Todas las métricas de Norma 4 calculadas y documentadas
- [ ] Walk-forward analysis completado
- [ ] Profit Factor ≥ 1.3 y Sharpe ≥ 1.0
- [ ] Max Drawdown ≤ 15%
- [ ] Nº de operaciones ≥ 30

### Antes de Paper Trading ✅
- [ ] Backtest aprobado según criterios anteriores
- [ ] Script compilado y probado en entorno demo
- [ ] `validar_riesgo()` implementada y probada
- [ ] Duración mínima de paper trading acordada (mínimo 2 semanas)

### Antes de Producción ✅
- [ ] Paper trading completado con resultados consistentes con el backtest
- [ ] Posición inicial al 25% del tamaño objetivo
- [ ] Alertas y stops automáticos configurados
- [ ] Plan de escalada definido (cuándo y cómo subir el tamaño)

---

*Proyecto: Blacksheep Vortex · IA Práctica para Crear Soluciones de Negocio con Antigravity · v1.0*
