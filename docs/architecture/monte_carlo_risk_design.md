# Diseño Técnico: Monte Carlo & Risk of Ruin (Fase 4.2B)

**Estado:** PENDIENTE DE APROBACIÓN
**Autor:** Director Técnico y Arquitecto Principal del Proyecto Antigravity
**Fase Predecesora:** 4.2A — Metrics Engine Determinista (COMPLETADA, 54/54 tests)
**Fecha de Creación:** 2026-05-31
**Última Modificación:** 2026-05-31

---

## 1. Propósito del Módulo

El **Metrics Engine de la Fase 4.2A** proporciona métricas deterministas: calculan exactamente el comportamiento histórico registrado. Sin embargo, el historial es una única trayectoria temporal de trades ejecutados en un orden determinado y bajo condiciones de mercado irrepetibles.

La **simulación Monte Carlo** nace de la necesidad de responder a una pregunta que la Fase 4.2A es incapaz de formular: *¿Qué habría pasado si los trades hubiesen ocurrido en otro orden, bajo otra secuencia aleatoria de resultados?*

Esto es crítico porque:

- **El orden de los trades importa.** Una racha de pérdidas al inicio de la operativa puede destruir una cuenta incluso si la estrategia es globalmente rentable. La secuencia histórica observada puede ser favorable por azar.
- **El drawdown histórico subestima el riesgo real.** El peor drawdown registrado no es necesariamente el peor posible. Monte Carlo fuerza al sistema a explorar distribuciones de drawdowns no observados.
- **La robustez estadística no se mide con una sola pasada.** Una estrategia con 20 trades y resultado positivo puede ser pura suerte. La simulación evalúa cuántas de las trayectorias posibles siguen siendo rentables.
- **La supervivencia del capital es la condición primaria.** El Risk of Ruin cuantifica la probabilidad de que la estrategia destruya la cuenta antes de que las ventajas estadísticas se manifiesten.

El objetivo del módulo de la **Fase 4.2B** es calcular, de forma determinista y reproducible mediante seeds, estas métricas de robustez y supervivencia como complemento cuantitativo avanzado al `MetricsEngine` existente, sin alterar los contratos de datos establecidos ni modificar los módulos validados anteriores.

---

## 2. Separación de Responsabilidades

Este módulo sigue estrictamente el **Principio de Responsabilidad Única (SRP)**. La cadena de responsabilidades es:

```
MT5 HTML Report
     │
     ▼
┌─────────────────────────────┐
│ Parser (MT5HtmlParser)      │  Solo lee e interpreta el informe HTML.
│                             │  No calcula nada. No decide nada.
└─────────────────────────────┘
     │ List[TradeRecord]
     ▼
┌─────────────────────────────┐
│ Metrics Engine (4.2A)       │  Calcula métricas deterministas históricas.
│                             │  No simula. No decide. No lee archivos.
└─────────────────────────────┘
     │ List[TradeRecord] + CalculatedMetrics
     ▼
┌─────────────────────────────┐
│ Monte Carlo Engine (4.2B)   │  Simula escenarios alternativos mediante
│                             │  remuestreo. Calcula Risk of Ruin y
│                             │  distribuciones de drawdown.
│                             │  No lee archivos. No calcula métricas base.
│                             │  No decide clasificación.
└─────────────────────────────┘
     │ MonteCarloResult
     ▼
┌─────────────────────────────┐
│ BacktestValidator           │  Clasifica la estrategia:
│                             │  REJECTED / OBSERVATION / PAPER_TRADING_READY
│                             │  No calcula. No simula. No lee archivos.
└─────────────────────────────┘
     │ StrategyEvaluation
     ▼
┌─────────────────────────────┐
│ RiskEngine                  │  Evalúa seguridad operativa de cada trade.
│                             │  Aplica reglas R1–R6. No evalúa estrategias.
│                             │  No calcula métricas. No simula.
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│ Approval Layer (Futuro)     │  Requiere confirmación humana explícita.
│                             │  ALLOW_REAL_EXECUTION = False siempre.
└─────────────────────────────┘
```

**Regla invariante:** Ninguna capa ejecuta, ordena, ni sugiere operaciones reales. El pipeline es secuencial y no saltable.

---

## 3. Entrada del Módulo

El módulo `MonteCarloEngine` recibirá los siguientes parámetros de entrada:

### 3.1 Datos de Operaciones
| Parámetro | Tipo | Obligatorio | Descripción |
|:---|:---|:---|:---|
| `trades` | `List[TradeRecord]` | ✅ | Lista cronológica de operaciones cerradas del backtest. Mínimo recomendado: 30 trades. |
| `initial_equity` | `float` | ✅ | Capital inicial con el que se realizó el backtest (e.g., `10000.0`). |

### 3.2 Parámetros de Simulación
| Parámetro | Tipo | Obligatorio | Default | Descripción |
|:---|:---|:---|:---|:---|
| `n_simulations` | `int` | ❌ | `1000` | Número de trayectorias aleatorias a generar. |
| `seed` | `Optional[int]` | ❌ | `42` | Semilla para el generador aleatorio. Fija para tests reproducibles; `None` para simulaciones estadísticas reales. |
| `method` | `str` | ❌ | `"bootstrap"` | Método de remuestreo: `"bootstrap"` (con reemplazo) o `"shuffle"` (sin reemplazo). |
| `ruin_threshold_pct` | `float` | ❌ | `0.30` | Fracción de pérdida del equity inicial que define la ruina (e.g., `0.30` = 30% de pérdida). |
| `cost_per_trade` | `Optional[float]` | ❌ | `None` | Coste fijo adicional por operación (comisión+spread adicional). Si `None`, se toma directamente del `profit_loss` neto del `TradeRecord`. |
| `slippage_pct` | `Optional[float]` | ❌ | `None` | Porcentaje de slippage adicional aplicado sobre el resultado de cada trade simulado. |

### 3.3 Mínimo de Muestra
Se establecerá un umbral mínimo de **20 trades** para ejecutar la simulación. Si la lista de trades es inferior, el módulo emitirá una advertencia técnica (`InsufficientSampleWarning`) y ejecutará igualmente la simulación marcando el resultado como `low_confidence=True`. Por debajo de **10 trades**, la simulación se rechazará con excepción `InsufficientTradesError`.

---

## 4. Salida del Módulo

El módulo devolverá un modelo Pydantic estructurado `MonteCarloResult` con los siguientes campos:

### 4.1 Métricas de Risk of Ruin
| Campo | Tipo | Descripción |
|:---|:---|:---|
| `risk_of_ruin_pct` | `float` | Fracción de simulaciones `[0.0, 1.0]` en las que el equity cayó por debajo del umbral de ruina definido. |
| `worst_case_drawdown` | `float` | Drawdown máximo absoluto observado en cualquier trayectoria simulada (valor absoluto en unidades monetarias). |
| `worst_case_drawdown_pct` | `float` | Drawdown máximo en porcentaje sobre el equity inicial. |

### 4.2 Distribución de Drawdown Máximo
| Campo | Tipo | Descripción |
|:---|:---|:---|
| `monte_carlo_max_drawdown_p50` | `float` | Percentil 50 (mediana) del drawdown máximo de las `n` simulaciones. |
| `monte_carlo_max_drawdown_p95` | `float` | Percentil 95 del drawdown máximo. El 95% de las simulaciones tuvo un drawdown inferior a este valor. |
| `monte_carlo_max_drawdown_p99` | `float` | Percentil 99 del drawdown máximo. Escenario de cola extrema. |

### 4.3 Distribución de Equity Final
| Campo | Tipo | Descripción |
|:---|:---|:---|
| `median_final_equity` | `float` | Mediana del equity final tras `n` simulaciones. |
| `p05_final_equity` | `float` | Percentil 5 del equity final. El 5% de las simulaciones terminó con menos de este valor. |
| `p95_final_equity` | `float` | Percentil 95 del equity final. El 95% de las simulaciones terminó por debajo de este valor. |
| `mean_final_equity` | `float` | Media aritmética del equity final. |

### 4.4 Análisis de Rachas
| Campo | Tipo | Descripción |
|:---|:---|:---|
| `max_losing_streak_p95` | `int` | Percentil 95 de la racha de pérdidas consecutivas máxima a lo largo de todas las simulaciones. |
| `max_losing_streak_p99` | `int` | Percentil 99 de la racha de pérdidas consecutivas máxima. |

### 4.5 Metadata de Simulación
| Campo | Tipo | Descripción |
|:---|:---|:---|
| `n_simulations` | `int` | Número de simulaciones efectivamente ejecutadas. |
| `method` | `str` | Método utilizado: `"bootstrap"` o `"shuffle"`. |
| `seed` | `Optional[int]` | Semilla utilizada. `None` si la simulación fue aleatoria. |
| `n_trades_input` | `int` | Número de trades recibidos como input. |
| `low_confidence` | `bool` | `True` si el número de trades era inferior al mínimo recomendado (< 30). |
| `initial_equity` | `float` | Equity inicial utilizado. |
| `ruin_threshold_pct` | `float` | Umbral de ruina configurado. |
| `computed_at` | `datetime` | Timestamp UTC del cálculo. |
| `approved_for_real` | `bool` | Siempre `False`. Constante de seguridad. |

---

## 5. Tipo de Simulación Inicial

### 5.1 Bootstrap con Reemplazo (`method="bootstrap"`)
El método por defecto de la Fase 4.2B. Consiste en:
1. Tomar la lista de `n` trades como universo de muestra.
2. Extraer aleatoriamente `n` trades **con reemplazo** para construir una secuencia sintética de la misma longitud.
3. Aplicar secuencialmente los resultados de los trades extraídos sobre el equity inicial para construir una curva de equity simulada.
4. Registrar el drawdown máximo de la trayectoria, el equity final y la racha máxima de pérdidas.
5. Repetir `n_simulations` veces.

**Ventaja:** Permite que eventos extremos se repitan o que secuencias favorables no ocurran, revelando robustez real.
**Limitación documentada:** El bootstrap asume independencia entre trades (i.i.d.). Si los trades están correlacionados (e.g., misma sesión de mercado), el bootstrap puede ser excesivamente optimista.

### 5.2 Shuffle sin Reemplazo (`method="shuffle"`)
1. Tomar la lista de `n` trades y barajarlos aleatoriamente manteniendo los `n` trades originales.
2. Aplicar la secuencia aleatoria sobre el equity inicial.
3. Registrar métricas de trayectoria.
4. Repetir `n_simulations` veces.

**Ventaja:** Conserva exactamente la distribución empírica de resultados (no genera trades nuevos).
**Limitación documentada:** No puede generar escenarios de rachas más largas que las observadas en los datos originales.

### 5.3 Reproducibilidad con Seed Fija
Para garantizar la testabilidad determinista:
- Si `seed` es un entero, se inicializa `random.seed(seed)` y/o `numpy.random.seed(seed)` antes de cada simulación.
- Dos invocaciones con la misma `seed`, mismo `n_simulations` y mismos `trades` producirán exactamente el mismo `MonteCarloResult`.
- Los tests unitarios usarán siempre `seed=42` por convención del proyecto.

### 5.4 Principio de Aislamiento
- Sin conexión a internet.
- Sin acceso a MT5 ni a ningún broker.
- Sin llamadas a modelos de IA ni LLMs.
- Sin lectura de archivos del sistema de ficheros.
- 100% offline, calculado exclusivamente sobre la lista `List[TradeRecord]` recibida.

---

## 6. Definición Oficial de Risk of Ruin en Antigravity

**Definición formal aprobada:**

> Se considera que una trayectoria simulada ha alcanzado **la ruina** cuando el equity de la cuenta simulada cae por debajo del `(1 - ruin_threshold_pct)` del equity inicial en cualquier punto de la trayectoria.

Con el umbral por defecto de `ruin_threshold_pct = 0.30`:

> Una trayectoria ha alcanzado la ruina si el equity cae en algún momento por debajo del **70% del equity inicial**.

**Ejemplos numéricos:**
- `initial_equity = 10,000 €` → Ruina si `equity < 7,000 €` en cualquier momento.
- `initial_equity = 10,000 €` con `ruin_threshold_pct = 0.50` → Ruina si `equity < 5,000 €`.

**Interpretación del `risk_of_ruin_pct`:**
- `0.00` → Ninguna trayectoria simulada alcanzó la ruina. Estrategia altamente robusta.
- `0.05` → El 5% de las trayectorias alcanzó la ruina. Riesgo bajo pero no despreciable.
- `0.20` → El 20% de las trayectorias alcanzó la ruina. Riesgo elevado. Clasificación esperada: `OBSERVATION`.
- `> 0.30` → Más del 30% de las trayectorias alcanzaron la ruina. Riesgo crítico. Clasificación esperada: `REJECTED`.

**Nota sobre umbrales de ruina alternativos:**
El módulo acepta cualquier `ruin_threshold_pct` entre `0.05` y `1.00`. Los umbrales de `0.30` y `0.50` se proponen como referencia académica estándar de la industria de gestión de riesgos de fondos. El Director Técnico puede redefinirlos en la configuración de cada evaluación.

---

## 7. Parámetros Iniciales Recomendados

| Parámetro | Valor por Defecto | Justificación |
|:---|:---|:---|
| `n_simulations` | `1000` | Balance entre precisión estadística y coste computacional. Con 1000 simulaciones, el error estándar del `risk_of_ruin_pct` es ≤ 1.6%. Aumentar a `10000` para análisis de publicación. |
| `seed` | `42` | Convención estándar del proyecto para reproducibilidad. Tests siempre con `seed=42`. |
| `method` | `"bootstrap"` | El bootstrap es más conservador y penalizante que el shuffle, priorizando la seguridad del capital. |
| `ruin_threshold_pct` | `0.30` | Pérdida del 30% del capital. Umbral estándar de parada en gestión activa. |
| `min_trades_recommended` | `30` | Mínimo estadístico para distribuciones de bootstrap representativas. |
| `min_trades_hard` | `10` | Por debajo de este límite, la simulación lanza `InsufficientTradesError`. |

**Advertencias obligatorias en metadata:**
- Si `n_trades < 30` → `low_confidence = True` y se loguea `WARNING: Muestra insuficiente para simulación representativa. Resultados orientativos únicamente.`
- Si `n_trades < 10` → `InsufficientTradesError` con mensaje: `"Monte Carlo requiere mínimo 10 trades. Se recibieron {n}. Amplíe el periodo de backtest."`

---

## 8. Relación con el Metrics Engine

### 8.1 Localización del Módulo
El `MonteCarloEngine` se implementará como un **archivo independiente dentro del paquete `core/metrics/`**:

```
core/
└── metrics/
    ├── __init__.py
    ├── metrics_engine.py       # Fase 4.2A (EXISTENTE, NO MODIFICAR)
    └── monte_carlo.py          # Fase 4.2B (NUEVO)
```

**Razón de diseño:** Mantener el mismo paquete `core/metrics/` garantiza cohesión por dominio (todo el análisis cuantitativo en el mismo espacio), pero la separación en archivo independiente evita tocar código validado y rompre tests existentes.

### 8.2 Integración en los Modelos de Datos
Se añadirá un nuevo campo **opcional** en `BacktestReport`:

```python
# Propuesta para core/strategy_models.py
class BacktestReport(BaseModel):
    # ... campos existentes intactos (NO MODIFICAR) ...
    calculated_metrics: Optional[CalculatedMetrics] = None     # Fase 4.2A (existente)
    monte_carlo_result: Optional[MonteCarloResult] = None      # Fase 4.2B (nuevo)
```

**Invariante contractual:** El campo `monte_carlo_result` es siempre `Optional`. Un `BacktestReport` sin `MonteCarloResult` es perfectamente válido. Ningún test de la Fase 4.1 o 4.2A puede fallar por la adición de este campo.

### 8.3 Flujo de Datos Propuesto (Fase 4.2B)

```
List[TradeRecord]
       │
       ├──► MetricsEngine (4.2A) ──► CalculatedMetrics
       │
       └──► MonteCarloEngine (4.2B)
               │ initial_equity, n_simulations, seed, method, ruin_threshold_pct
               ▼
            MonteCarloResult
                   │
                   └──► BacktestReport.monte_carlo_result (opcional)
                                │
                                ▼
                      BacktestValidator (futura integración)
```

---

## 9. Relación con el BacktestValidator

### 9.1 Principio para la Fase 4.2B
El `BacktestValidator` **no se modificará en la Fase 4.2B**. La integración de los umbrales de Monte Carlo en las reglas de clasificación se reserva para una fase posterior específica de refactoring de validación.

### 9.2 Criterios de Integración Propuestos (Futura)
Cuando se autorice la integración, los umbrales orientativos propuestos son:

| Condición Monte Carlo | Impacto en clasificación |
|:---|:---|
| `risk_of_ruin_pct > 0.30` | Fuerza `REJECTED` independientemente de las demás métricas. |
| `0.10 < risk_of_ruin_pct ≤ 0.30` | Degrada a `OBSERVATION` si la clasificación previa era `PAPER_TRADING_READY`. |
| `monte_carlo_max_drawdown_p95 > max_drawdown_threshold` | Añade nota de `OBSERVATION`. |
| `risk_of_ruin_pct ≤ 0.10` y `monte_carlo_max_drawdown_p95 ≤ threshold` | No modifica la clasificación positiva. |
| `low_confidence = True` (muestra insuficiente) | Bloquea `PAPER_TRADING_READY`, fuerza mínimo `OBSERVATION`. |

**Nota de diseño:** Estos umbrales son orientativos y requieren aprobación del Director Técnico antes de cualquier implementación en el `BacktestValidator`.

---

## 10. Tests Propuestos

Todos los tests residen en `tests/test_monte_carlo.py` y siguen las convenciones pytest del proyecto.

| Test | Objetivo | Condición de Éxito |
|:---|:---|:---|
| `test_reproducibility_with_fixed_seed` | Verificar que dos ejecuciones con `seed=42` producen idénticos `MonteCarloResult`. | `result_1 == result_2` bit a bit. |
| `test_robust_strategy_low_ruin` | Estrategia con alta expectativa positiva y bajo drawdown histórico. | `risk_of_ruin_pct < 0.05`. |
| `test_fragile_strategy_high_ruin` | Estrategia con alta expectativa negativa. | `risk_of_ruin_pct > 0.50`. |
| `test_insufficient_trades_warning` | Entrada con 15 trades (< 30). | `result.low_confidence == True` y sin excepción. |
| `test_too_few_trades_exception` | Entrada con 5 trades (< 10). | Lanza `InsufficientTradesError`. |
| `test_p95_drawdown_is_greater_than_median` | Verificar orden estadístico de percentiles. | `p95 >= p50 >= worst_case_or_min`. |
| `test_output_structure_complete` | Verificar que todos los campos de `MonteCarloResult` están presentes. | Pydantic validation pasa sin errores. |
| `test_approved_for_real_always_false` | Constante de seguridad. | `result.approved_for_real == False` siempre. |
| `test_no_network_calls` | El módulo no realiza llamadas externas. | Ejecución sin acceso a red mockeado. |
| `test_no_mt5_dependency` | El módulo no importa ni necesita `MetaTrader5`. | Ejecución limpia en entorno sin MT5. |
| `test_bootstrap_vs_shuffle_different` | Los dos métodos producen distribuciones distintas. | `bootstrap_result != shuffle_result` con misma `seed`. |
| `test_equity_curve_monotonic_calculation` | Verificar que la curva de equity se construye correctamente. | Suma acumulada coherente con trades recibidos. |

---

## 11. Riesgos Técnicos

| Riesgo | Descripción | Mitigación |
|:---|:---|:---|
| **Falsa precisión estadística** | Con pocos trades, los percentiles calculados carecen de significado estadístico real. El resultado puede aparentar certeza que no existe. | Flag `low_confidence`, advertencia explícita en metadata y bloqueo para `PAPER_TRADING_READY`. |
| **Muestra pequeña** | Backtests cortos (< 30 trades) generan distribuciones bootstrap no representativas. | `min_trades_recommended = 30`. Excepción dura en < 10. |
| **Distribución no estacionaria** | Los trades del backtest pueden provenir de regímenes de mercado diferentes (alta volatilidad, baja volatilidad, tendencia, rango). El bootstrap asume que todos son igualmente probables en el futuro. | Documentar explícitamente esta limitación en el output (`low_confidence` no la cubre, es una advertencia separada). Futura Fase: análisis por régimen. |
| **Bootstrap excesivamente optimista** | Si los trades con mejores resultados son pocos y representan eventos extraordinarios, el bootstrap los remuestrea con la misma probabilidad que el resto. | Considerar el shuffle como alternativa conservadora. Documentar en el diseño. |
| **Coste computacional** | Con `n_simulations = 10000` y `n_trades = 1000`, el tiempo de cómputo puede ser relevante. | Default en `1000`. Para análisis intensivo, parametrizable. Futura optimización con `numpy` vectorizado. |
| **Interpretación incorrecta** | El `risk_of_ruin_pct` no es una probabilidad de ruina en trading real; es una probabilidad de ruina dado que el futuro se comporta como el backtest remuestreado. | Documentar limitación explícita en la docstring del módulo y en este diseño. |
| **Seeds no gestionadas en tests paralelos** | Tests paralelos con pytest-xdist pueden interferir con el estado del generador aleatorio global. | Usar generadores de random locales (`random.Random(seed)`) en lugar del estado global. |

---

## 12. Alcance Explícito de la Fase 4.2B

### ✅ Incluido en la Fase 4.2B

| Componente | Descripción |
|:---|:---|
| `core/metrics/monte_carlo.py` | Implementación del `MonteCarloEngine` |
| `MonteCarloResult` (Pydantic) | Modelo de salida estructurado en `core/strategy_models.py` |
| `BacktestReport.monte_carlo_result` | Campo opcional añadido sin romper contratos existentes |
| `tests/test_monte_carlo.py` | Batería completa de tests unitarios deterministas |
| Bootstrap con reemplazo | Método primario de simulación |
| Shuffle sin reemplazo | Método alternativo de simulación |
| Risk of Ruin | Cálculo de fracción de trayectorias en ruina |
| Distribuciones de drawdown | Percentiles p50, p95, p99 |
| Distribuciones de equity final | Percentiles p05, p50, p95, media |
| Rachas p95/p99 en simulaciones | Análisis probabilístico de rachas de pérdida |
| Reproducibilidad con seed fija | Condición técnica para testabilidad |

### ❌ Excluido de la Fase 4.2B

| Componente | Razón |
|:---|:---|
| Modificación de `BacktestValidator` | Reservado para fase específica de refactoring de validación |
| Inteligencia Artificial / LLMs | Fuera del scope cuantitativo determinista |
| Telegram / Approval Layer | Capa de comunicación fuera del motor analítico |
| MT5 vivo / Gatekeeper | Sin conectividad operativa en esta fase |
| TradingView / n8n | Integraciones externas fuera de alcance |
| Ejecución demo | Ningún trade real o simulado es ejecutado |
| Ejecución real | ALLOW_REAL_EXECUTION = False. Bloqueado por diseño invariante. |
| Análisis por régimen de mercado | Complejidad futura (Fase 4.3 o posterior) |
| Sortino temporal diario | Queda en la definición de Fase 4.2B estocástica a decidir separadamente |

---

## 13. Decisiones Abiertas

Las siguientes decisiones requieren aprobación del Director Técnico antes de iniciar la implementación:

| ID | Decisión | Opciones |
|:---|:---|:---|
| D1 | **Librería de aleatoriedad** | `random` stdlib (sin dependencias nuevas) vs `numpy.random` (más eficiente para n_simulations grandes). Recomendación: `numpy.random.default_rng(seed)` para evitar estado global. |
| D2 | **Localización del `MonteCarloResult`** | Dentro de `core/strategy_models.py` (junto al resto) vs archivo propio `core/metrics/monte_carlo_models.py`. |
| D3 | **Umbral de ruina por defecto** | `0.30` (30%) propuesto. ¿Se acepta o se modifica a `0.20` o `0.50`? |
| D4 | **Comportamiento con `low_confidence`** | ¿El BacktestValidator debe bloquear automáticamente `PAPER_TRADING_READY` si `low_confidence=True` aunque no se haya actualizado el validador? ¿O solo advertencia? |
| D5 | **Número de decimales en percentiles** | Precisión de los percentiles calculados: `float` con 4 decimales o `Decimal` para reproducibilidad estricta. Recomendación: `float` + `round(..., 4)`. |
| D6 | **Test de rendimiento** | ¿Se incluye un test de tiempo de ejecución (`< 5 segundos` para `n_simulations=1000, n_trades=200`)? |

---

## 14. Dictamen del Director

**Resolución:** PENDIENTE DE APROBACIÓN

**Condición para inicio de implementación:** Aprobación explícita del Director Técnico, con resolución de las Decisiones Abiertas D1, D2 y D3 como mínimo.

**Versión recomendada de implementación:** Se recomienda implementar inicialmente con `random` stdlib (D1 conservador), `MonteCarloResult` en `core/strategy_models.py` (D2 consistente con el resto), y umbral de ruina del 30% (D3).

---

*Documento de diseño académico. No implementar hasta aprobación explícita. No ejecuta operaciones. No conecta con brokers. No utiliza IA externa.*
*approved_for_real = False | ALLOW_REAL_EXECUTION = False*
