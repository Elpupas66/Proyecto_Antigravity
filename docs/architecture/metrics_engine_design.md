# Diseño Técnico: Metrics Engine (Fase 4.2)
**Estado:** APROBADO CON OBSERVACIONES (Fase 4.2A en ejecución)
**Autor:** Director Técnico y Arquitecto Principal del Proyecto Antigravity
**Fecha de Creación:** 2026-05-29
**Última Modificación:** 2026-05-29 (Ajuste según directrices del Director)

---

## 1. Propósito del Metrics Engine

El **Metrics Engine** es un componente desacoplado del núcleo de ingesta y validación cuyo objetivo principal es calcular métricas cuantitativas, estadísticas y matemáticas derivadas a partir del historial de operaciones (`TradeRecord`).

Siguiendo el **Principio de Responsabilidad Única (SRP)**, este motor se independiza por las siguientes razones de arquitectura:
* **Separación de Ingesta y Cálculo:** El `MT5HtmlParser` debe limitarse a extraer y estructurar sintácticamente los datos brutos del HTML del broker. No debe asumir lógica financiera ni fórmulas matemáticas complejas.
* **Separación de Cálculo y Decisión:** El `BacktestValidator` es un motor de políticas y reglas de negocio. Su función es evaluar si los resultados cumplen ciertos criterios cuantitativos, no calcularlos. El validador debe ser agnóstico de *cómo* se calcula un Sortino Ratio.
* **Extensibilidad e Interoperabilidad:** Al independizar el cálculo de métricas, el `Metrics Engine` podrá procesar en el futuro listas de operaciones provenientes de otras fuentes (e.g., CSV genéricos, logs de TradingView, APIs de cTrader) sin modificar el motor matemático.
* **Testabilidad Aislada:** Permite escribir suites de tests unitarios puros sobre funciones matemáticas sin necesidad de mockear estructuras HTML complejas, bases de datos o conexiones de red.

---

## 2. Responsabilidades del Metrics Engine (Fase 4.2A)

El motor procesará la secuencia cronológica de operaciones cerradas y calculará de manera determinista pura:

1. **Expectancy (Esperanza Matemática) Recalculada:** Esperanza neta por operación basada en los importes de ganancia/pérdida, incluyendo de forma estricta las comisiones y los costes de swap.
2. **Sortino Ratio (Trade-based):** Medida de rendimiento ajustada al riesgo que penaliza únicamente la volatilidad de los retornos negativos (downside deviation), calculada bajo la aproximación *trade-based* (considerando cada operación individual como una muestra i.i.d.).
3. **Pérdida Diaria Máxima (Max Daily Loss):** Mayor pérdida agregada ocurrida dentro de un mismo día natural (24 horas UTC o zona horaria del broker), agrupando los resultados netos de las operaciones cerradas en dicha fecha.
4. **Exposición Simultánea Inicial (`max_simultaneous_trades`):** Identificación del número máximo de operaciones abiertas en paralelo mediante la detección de solapamiento temporal de las duraciones `[open_time, close_time]`.
5. **Rachas de Pérdidas y Ganancias (Streaks):** Contabilización secuencial del máximo número de operaciones perdedoras y ganadoras consecutivas.
6. **Métricas de Coste Operativo:** Cálculo del coste medio por operación en comisiones y swaps, así como el slippage medio si existe información en el reporte.

---

## 3. Qué NO debe hacer (Límites del Módulo en la Fase 4.2A)

Para mantener la cohesión y mitigar riesgos arquitectónicos, el Metrics Engine tiene prohibido:
* ❌ **No leer archivos físicos:** No debe abrir HTML, CSV o JSON. Recibe listas de datos ya tipados y estructurados.
* ❌ **No parsear informes MT5:** No conoce la estructura tabular de MetaTrader 5.
* ❌ **No decidir clasificación final ni integrarse con el validador:** No decide si un backtest es `REJECTED`, `OBSERVATION` o `PAPER_TRADING_READY`. Esta versión de la Fase 4.2A no interfiere ni modifica el comportamiento del `BacktestValidator` actual.
* ❌ **No modificar esquemas persistidos o base de datos en exceso:** Se evitará la modificación profunda del `BacktestReport` para no romper la compatibilidad regresiva del core ni de los tests existentes de la Fase 4.1.
* ❌ **No usar Monte Carlo ni Risk of Ruin:** Quedan totalmente excluidos de esta Fase 4.2A por ser estocásticos y de complejidad adicional.
* ❌ **No conectarse a internet o APIs externas:** El motor es 100% offline y determinista local.
* ❌ **No usar Inteligencia Artificial ni LLMs:** Todos los algoritmos son puramente matemáticos y estadísticos convencionales.
* ❌ **No ejecutar operaciones ni interactuar con brokers:** Módulo puramente analítico y pasivo.

---

## 4. Datos de Entrada Previstos

El Metrics Engine requerirá una lista homogénea de operaciones estructurada según el siguiente modelo de datos de entrada:

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `ticket` / `deal_id` | `str` | Identificador único de la transacción en el broker. |
| `symbol` | `str` | Activo negociado (e.g., `EURUSD`, `XAUUSD`). |
| `open_time` | `datetime` | Fecha y hora exacta de apertura. |
| `close_time` | `datetime` | Fecha y hora exacta de cierre. |
| `direction` | `enum` | Dirección de la orden: `BUY` o `SELL`. |
| `volume` | `float` | Tamaño de la posición expresado en lotes. |
| `open_price` | `float` | Precio de ejecución de entrada. |
| `close_price` | `float` | Precio de ejecución de salida. |
| `commission` | `float` | Comisión cobrada por el broker (valor negativo o cero). |
| `swap` | `float` | Cargo por mantenimiento de posición nocturna (swap). |
| `profit_loss` | `float` | Resultado bruto del trade (excluyendo comisión/swap). |
| `slippage` | `Optional[float]`| Desviación entre precio solicitado y ejecutado en puntos/pips. |

Adicionalmente, podrá requerir parámetros de configuración global de la cuenta:
* `initial_balance` (`float`): Balance inicial con el que arrancó el backtest (por defecto `10000.0`).
* `risk_free_rate` (`float`): Tasa libre de riesgo para cálculos de Sortino/Sharpe (por defecto `0.0`).

---

## 5. Datos de Salida Previstos

La salida del Metrics Engine será un modelo estructurado **`CalculatedMetrics`** (Pydantic Model). 

Para no modificar el `BacktestReport` en exceso de cara al almacenamiento e integraciones en la base de datos de producción, este se mantendrá como un atributo **opcional** dentro de la entidad `BacktestReport`:

```python
# En core/models.py
class BacktestReport(BaseModel):
    # ... campos existentes intactos ...
    calculated_metrics: Optional[CalculatedMetrics] = None  # Opcional, sin alterar tests previos
```

---

## 6. Propuesta de Modelos Pydantic (Fase 4.2A)

Se detalla la estructura formal de los modelos a implementar en `core/models.py` (o en su propio módulo, importado de forma no invasiva):

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class TradeDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradeRecord(BaseModel):
    ticket: str = Field(..., description="ID de transacción único")
    symbol: str = Field(..., description="Activo financiero")
    open_time: datetime = Field(..., description="Fecha de apertura")
    close_time: datetime = Field(..., description="Fecha de cierre")
    direction: TradeDirection = Field(..., description="Dirección BUY/SELL")
    volume: float = Field(..., gt=0.0, description="Volumen en lotes")
    open_price: float = Field(..., gt=0.0, description="Precio de apertura")
    close_price: float = Field(..., gt=0.0, description="Precio de cierre")
    commission: float = Field(default=0.0, description="Comisión del broker")
    swap: float = Field(default=0.0, description="Swap cargado")
    profit_loss: float = Field(..., description="Resultado neto o bruto del trade")
    slippage: Optional[float] = Field(default=None, description="Slippage experimentado")

class CalculatedMetrics(BaseModel):
    total_trades: int = Field(..., description="Número total de trades analizados")
    profit_factor: float = Field(..., description="Factor de beneficio neto recalculado")
    expectancy: float = Field(..., description="Esperanza matemática de beneficio por trade")
    average_win: float = Field(..., description="Ganancia promedio")
    average_loss: float = Field(..., description="Pérdida promedio")
    win_rate: float = Field(..., description="Porcentaje de operaciones ganadoras")
    max_winning_streak: int = Field(..., description="Racha máxima de ganancias consecutivas")
    max_losing_streak: int = Field(..., description="Racha máxima de pérdidas consecutivas")
    max_daily_loss: float = Field(..., description="Pérdida máxima acumulada en un único día natural")
    max_daily_loss_pct: float = Field(..., description="Pérdida diaria máxima relativa al balance inicial")
    max_simultaneous_trades: int = Field(..., description="Exposición simultánea máxima de trades")
    sortino_ratio: float = Field(..., description="Sortino Ratio aproximado trade-based")
    cost_per_trade: float = Field(..., description="Cargos medios (comisión + swap) por trade")
```

---

## 7. Métricas Prioritarias de Primera Versión (Fase 4.2A)

De acuerdo con las directrices de diseño simplificado y determinista:

* **Expectancy recalculada:** Esperanza matemática determinista neta por trade (`profit_loss + commission + swap`).
* **Max Daily Loss Pct:** Pérdida diaria agregada determinista por fecha de cierre (`close_time`).
* **Losing/Winning Streaks:** Conteo de rachas consecutivas sin simulaciones.
* **max_simultaneous_trades:** Exposición simultánea inicial basada en solapamiento de fechas.
* **Sortino Ratio (Trade-based):** Se implementa usando los retornos netos de cada operación individual como muestras i.i.d. No se calcula sobre agregaciones temporales diarias ni curvas complejas en esta fase.

---

## 8. Tratamiento de Monte Carlo y Risk of Ruin

* **Decisión:** Estas métricas estocásticas quedan **totalmente fuera del alcance de la Fase 4.2A**.
* **Motivación:** Mantener la implementación base 100% determinista, aislada y sencilla de verificar. Se pospone cualquier lógica de remuestreo aleatorio (bootstrap) para fases futuras (e.g., Fase 4.2B o Fase 4.3).

---

## 9. Tratamiento del Sortino Ratio

Para la Fase 4.2A, el Sortino Ratio se implementa únicamente bajo la aproximación **Trade-based (basado en trades individuales)**:

* Se asume cada trade como una muestra independiente.
* Fórmula: $\text{Sortino} = \frac{\bar{R}_{trade} - R_f}{\sigma_{downside}}$
* Donde:
  * $\bar{R}_{trade}$ es el promedio de los rendimientos netos por trade (`profit_loss + commission + swap`).
  * $R_f$ es la tasa libre de riesgo configurada (por defecto `0.0`).
  * $\sigma_{downside}$ es la desviación estándar (semivarianza negativa) calculada únicamente sobre los trades que resultaron con rentabilidad neta inferior a $R_f$.
* Si no hay operaciones perdedoras ($\sigma_{downside} = 0$), el motor devolverá un valor representativo controlado (e.g., `99.0` o un valor predefinido de Sortino infinito).

---

## 10. Relación con el BacktestValidator (Fase 4.2A)

El motor de métricas se ejecutará de forma autónoma y no intrusiva. El `BacktestValidator` de la Fase 4.1 permanecerá inalterado para evitar regresiones de funcionalidad en las reglas de aceptación actuales.

El flujo simplificado de datos para la Fase 4.2A es:

```
MT5HtmlParser ──► List[TradeRecord] ──► [MetricsEngine] ──► CalculatedMetrics
                                                                     │
                                                                     ▼
MT5HtmlParser ──► [Genera BacktestReport con calculated_metrics (Opcional)] ──► BacktestValidator (Sin cambios en reglas)
```

Esto garantiza un aislamiento completo y estabilidad del software en producción.

---

## 11. Riesgos Técnicos y Mitigaciones

1. **Informes de MT5 sin listado de transacciones:**
   * *Mitigación:* El motor de métricas requiere al menos 2 operaciones. Si el input contiene menos de 2 trades, la ejecución arrojará la excepción `InsufficientTradesError`.
2. **Timezones y Agregaciones Diarias:**
   * *Mitigación:* Se procesan las fechas usando horas locales o de servidor de forma consistente, agrupando por fecha (`date()`) de cierre (`close_time`).
3. **Outliers no operativos:**
   * *Mitigación:* Se filtran las transacciones administrativas (ej. cargas y retiros de fondos) de forma previa a los cálculos.

---

## 12. Tests Unitarios Requeridos (Fase 4.2A)

Se implementarán tests unitarios deterministas estrictos para:
* `test_expectancy_recalculated_with_fees`: Validación de esperanza neta con comisiones y swaps.
* `test_max_losing_winning_streak`: Cómputo exacto de secuencias de rachas.
* `test_max_daily_loss`: Agregación de pérdidas agregadas diarias por fecha de cierre del trade.
* `test_max_simultaneous_trades`: Detección de trades abiertos concurrentemente en el tiempo.
* `test_sortino_ratio_trade_based`: Validación matemática de la desviación negativa y manejo de series sin pérdidas.
* `test_empty_or_insufficient_trades`: Lanzamiento de error ante sets sin suficientes datos operacionales.

---

## 13. Alcance Recomendado (Fase 4.2A)

* **INCLUIDO:**
  1. Definición del modelo Pydantic `CalculatedMetrics` y `TradeRecord`.
  2. Implementación de la clase `MetricsEngine` en `core/metrics/metrics_engine.py` (o similar).
  3. Tests unitarios deterministas completos en `tests/test_metrics_engine.py`.
* **EXCLUIDO:**
  1. Modificación activa de las reglas lógicas del `BacktestValidator`.
  2. Integración en base de datos del endpoint de validación.
  3. Lógica de Monte Carlo y Risk of Ruin.

---

## 14. Dictamen del Director

**Resolución:** **APROBAR** el inicio de la Fase 4.2A bajo el esquema determinista puro, garantizando el aislamiento de pruebas y la estabilidad absoluta del sistema de validación heredado de la Fase 4.1.
