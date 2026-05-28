# 📊 Estándar Oficial de Métricas Cuantitativas (Metrics Standard)
### Rol: Director Técnico (CTO) y Arquitecto Principal del Proyecto Antigravity
### Estado: Vigente · Versión: 1.0 (Académica)
### Restricción: PROHIBIDA LA EJECUCIÓN REAL EN MERCADOS FINANCIEROS

> [!IMPORTANT]
> **Filosofía del Ecosistema Antigravity**:
> Este estándar define las ecuaciones, interpretaciones y umbrales matemáticos rígidos obligatorios para toda estrategia o bot de trading. En Antigravity priorizamos de manera innegociable la **supervivencia de la cuenta, la estabilidad temporal de la equidad, el control riguroso de pérdidas y la robustez científica fuera de muestra** por encima de cualquier tasa de acierto (win rate) artificialmente inflada o beneficio bruto proyectado.

---

## 1. Propósito del Documento

Las métricas cuantitativas representan la base operativa del ecosistema de validación de Antigravity. La función de este estándar es actuar como un **filtro matemático infranqueable** para impedir que estrategias aparentemente rentables en el backtest, pero estructuralmente frágiles, inestables o sobreoptimizadas, entren en el pipeline en vivo de simulación del Core. 

Toda métrica descrita aquí debe ser calculada de manera homogénea antes de permitir que cualquier bot o estrategia sea clasificada como `OBSERVATION`, `PAPER_TRADING_READY` o `APPROVED_FOR_DEMO`.

---

## 2. Filosofía Cuantitativa del Proyecto

Nuestros pilares matemáticos y metodológicos son los siguientes:
* **El Win Rate NO es la Métrica Principal**: Una tasa de acierto del 90% es irrelevante si las pérdidas medias superan con creces a las ganancias medias o si el sistema incurre en riesgos de ruina asimétricos catastróficos.
* **El Control de Pérdidas es la Prioridad**: Un bot diseñado en Antigravity se construye y optimiza para minimizar las pérdidas en regímenes desfavorables de mercado, asumiendo que las ganancias serán la consecuencia natural de una ventaja matemática bien gestionada.
* **El Drawdown es una Métrica Crítica**: El drawdown determina la supervivencia del capital y el impacto psicológico. Evaluamos la profundidad y duración de las caídas de equidad de forma exhaustiva.
* **La Robustez Out-of-Sample (OOS) es Obligatoria**: Un sistema cuya equidad florece en el periodo In-Sample pero colapsa en el Out-of-Sample carece de robustez estructural y es rechazado de inmediato.
* **Una Curva Bonita No Implica Robustez**: Las curvas de balance lineales perfectas suelen ser el síntoma inequívoco de sobreoptimización de parámetros (curve fitting) o de estrategias de riesgo destructivas no declaradas (ej. martingalas o grids sin stops).
* **Estabilidad y Repetibilidad**: Buscamos sistemas con retornos distribuidos de manera uniforme a lo largo del tiempo, en lugar de sistemas cuyo beneficio depende de un puñado de operaciones aisladas o de condiciones hiper-específicas de mercado.

---

## 3. Métricas Principales Obligatorias

Toda estrategia o reporte de backtest debe calcular, documentar e interpretar los siguientes **19 parámetros cuantitativos obligatorios**:

---

### 3.1. Profit Factor (PF)
* **Definición**: Relación entre el beneficio bruto y la pérdida bruta.
  $$\text{Profit Factor} = \frac{\text{Beneficio Bruto Total}}{\text{Pérdida Bruta Total}}$$
* **Interpretación**: Indica cuántos euros o dólares de beneficio se generan por cada unidad monetaria perdida.
* **Riesgos de Mala Interpretación**: Un PF extremadamente alto (e.g. $> 3.5$) suele ser señal de overfitting o de un volumen estadístico irrelevante ($N < 30$).
* **Ejemplo Correcto**: "El bot tiene un PF de 1.45 sobre 200 operaciones, lo que demuestra una ventaja estadística real y consistente".
* **Ejemplo Incorrecto**: "El bot tiene un PF de 12.0 en 8 operaciones; es la mejor estrategia de la historia".

---

### 3.2. Max Drawdown (MDD)
* **Definición**: La mayor caída porcentual o monetaria de la curva de equidad medida desde el pico más alto hasta el valle subsiguiente en un periodo determinado.
  $$\text{Max Drawdown \%} = \max \left( \frac{\text{Pico} - \text{Valle}}{\text{Pico}} \right) \times 100$$
* **Interpretación**: Mide la peor racha acumulada y el nivel máximo de estrés financiero al que se expone la cuenta.
* **Riesgos de Mala Interpretación**: Evaluar el Drawdown basándose únicamente en el saldo cerrado (balance) ocultando el drawdown intradía o flotante (equity drawdown), lo cual es sumamente peligroso en estrategias grid.
* **Ejemplo Correcto**: "El Drawdown Máximo de equidad durante el backtest de 5 años alcanzó el 9.5%, lo que se mantiene dentro de los límites seguros".
* **Ejemplo Incorrecto**: "El Drawdown sobre el balance es del 2%, obviando que la equidad flotante estuvo expuesta a una pérdida del 45% en operaciones abiertas".

---

### 3.3. Recovery Factor (RF)
* **Definición**: Relación entre el beneficio neto total y la pérdida acumulada máxima (Max Drawdown).
  $$\text{Recovery Factor} = \frac{\text{Beneficio Neto Total}}{\text{Max Drawdown Absoluto}}$$
* **Interpretación**: Mide la eficiencia y velocidad del sistema para recuperarse de su peor racha.
* **Riesgos de Mala Interpretación**: Un RF alto en un periodo histórico extremadamente largo (e.g. 15 años) puede enmascarar un sistema que tardó 5 años de estancamiento en recuperarse del Drawdown.
* **Ejemplo Correcto**: "Con un beneficio de 6,000 USD y un MDD de 1,500 USD, el RF es de 4.0, indicando una recuperación ágil".
* **Ejemplo Incorrecto**: "El Recovery Factor es de 10.0 porque el MDD fue de 10 USD sobre una cuenta que ganó 100 USD en total; el tamaño de muestra es irrelevante".

---

### 3.4. Sharpe Ratio
* **Definición**: Retorno excedente anualizado del sistema dividido por la desviación estándar de los retornos (volatilidad).
  $$\text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}$$
  *(Donde $R_p$ es el retorno de la estrategia, $R_f$ la tasa libre de riesgo y $\sigma_p$ la volatilidad de los retornos).*
* **Interpretación**: Evalúa si el beneficio de la estrategia compensa la volatilidad a la que se expone el capital.
* **Riesgos de Mala Interpretación**: El Sharpe Ratio asume una distribución normal de los retornos. Si la estrategia tiene una distribución asimétrica (como opciones o sistemas tendenciales de baja tasa de acierto), el Sharpe puede penalizar injustamente la volatilidad positiva.
* **Ejemplo Correcto**: "El Sharpe Ratio es de 1.45, lo que demuestra un retorno superior por cada unidad de volatilidad experimentada".
* **Ejemplo Incorrecto**: "El Sharpe Ratio semanal es de 3.0, por lo tanto el anualizado será enorme (sin considerar el ajuste temporal por raíz de tiempo)".

---

### 3.5. Sortino Ratio
* **Definición**: Retorno excedente dividido únicamente por la desviación estándar de los retornos negativos (volatilidad a la baja).
  $$\text{Sortino Ratio} = \frac{R_p - R_f}{\sigma_d}$$
  *(Donde $\sigma_d$ es la desviación estándar de los retornos negativos o inferiores al objetivo).*
* **Interpretación**: Similar al Sharpe, pero penaliza únicamente la volatilidad perjudicial (las pérdidas), ignorando las fluctuaciones positivas de la equidad.
* **Riesgos de Mala Interpretación**: Utilizarlo con pocas muestras, donde la volatilidad a la baja parece cero debido a la ausencia temporal de rachas negativas.
* **Ejemplo Correcto**: "El Sortino Ratio de 1.85 indica que el bot gestiona eficientemente el riesgo de cola y las caídas sin limitar las rachas ganadoras".
* **Ejemplo Incorrecto**: "El Sortino es infinito porque no registramos pérdidas durante el primer mes de prueba".

---

### 3.6. Expectancy (Esperanza Matemática)
* **Definición**: El beneficio o pérdida neta esperada de media por cada operación ejecutada.
  $$\text{Expectancy} = (\text{Win Rate} \times \text{Average Win}) - (\text{Loss Rate} \times \text{Average Loss})$$
* **Interpretación**: Mide la rentabilidad teórica por transacción. Debe ser positiva para compensar costes operativos.
* **Riesgos de Mala Interpretación**: Un Expectancy positivo distorsionado por una única operación extremadamente ganadora atípica (outlier) en un set de datos de pocas muestras.
* **Ejemplo Correcto**: "Nuestra esperanza matemática es de 15 USD por trade en una muestra de 300 operaciones, lo que cubre con creces las comisiones y deslizamientos".
* **Ejemplo Incorrecto**: "El Expectancy es de 500 USD por trade porque en una muestra de 10 trades, uno ganó 5,000 USD y los otros 9 perdieron 50 USD de media".

---

### 3.7. Average Win (Ganancia Media)
* **Definición**: Beneficio medio de todas las operaciones cerradas con saldo positivo.
* **Interpretación**: Mide el tamaño medio del "premio" de los trades ganadores.
* **Riesgos de Mala Interpretación**: Ignorar la frecuencia de estas ganancias en favor de la magnitud absoluta.
* **Ejemplo Correcto**: "El Average Win es de 45 pips, lo que permite evaluar el recorrido objetivo del precio".
* **Ejemplo Incorrecto**: "El Average Win es muy alto, por lo tanto la estrategia ganará dinero independientemente de las pérdidas".

---

### 3.8. Average Loss (Pérdida Media)
* **Definición**: Pérdida media de todas las operaciones cerradas con saldo negativo.
* **Interpretación**: Mide la magnitud media del "castigo" de los trades perdedores.
* **Riesgos de Mala Interpretación**: Evaluar la pérdida media sin contrastarla contra la ganancia media y la esperanza matemática.
* **Ejemplo Correcto**: "Nuestra Pérdida Media es de -30 pips, lo cual está alineado con la política de control de drawdown".
* **Ejemplo Incorrecto**: "La pérdida media es pequeña, así que el sistema es robusto (sin considerar que la tasa de acierto es inferior al 10%)".

---

### 3.9. Win/Loss Ratio
* **Definición**: Relación simple entre la Ganancia Media y la Pérdida Media.
  $$\text{Win/Loss Ratio} = \frac{\text{Average Win}}{\text{Average Loss}}$$
* **Interpretación**: Mide la asimetría monetaria de los retornos medios de la estrategia.
* **Riesgos de Mala Interpretación**: Asumir que un Win/Loss Ratio $< 1.0$ invalida una estrategia (sistemas de alta tasa de aciertos como la reversión de rango a menudo tienen ratios menores a 1.0 y son rentables).
* **Ejemplo Correcto**: "El Win/Loss Ratio es de 1.5, indicando que de media ganamos un 50% más de lo que perdemos por trade".
* **Ejemplo Incorrecto**: "El Win/Loss Ratio es de 0.2, pero como el winrate es del 95% el bot es perfecto (ignorando que un solo fallo borra 5 ganancias consecutivas)".

---

### 3.10. Risk/Reward Ratio (R:R)
* **Definición**: Relación de diseño entre la distancia del Stop Loss y el Take Profit al momento de apertura.
* **Interpretación**: La asimetría planteada en el setup.
* **Riesgos de Mala Interpretación**: Confundir el R:R proyectado en el gráfico con el Win/Loss Ratio real ejecutado (muchos bots cierran operaciones antes de tocar el TP/SL teórico, alterando el ratio real).
* **Ejemplo Correcto**: "Nuestra estrategia busca operaciones con un R:R mínimo de 1:2 en el diseño del setup".
* **Ejemplo Incorrecto**: "La estrategia tiene un R:R de 1:10, por tanto de media la ganancia media es 10 veces la pérdida (cuando el winrate es de 2% y casi nunca toca el TP)".

---

### 3.11. Número de Operaciones ($N$)
* **Definición**: Cantidad total de transacciones cerradas dentro del periodo histórico.
* **Interpretación**: Mide el nivel de relevancia estadística del estudio del backtest.
* **Riesgos de Mala Interpretación**: Aceptar backtests con $N < 100$ asumiendo que los resultados son extrapolables al futuro.
* **Ejemplo Correcto**: "El backtest reporta 350 operaciones, lo que nos da la significancia matemática mínima exigida por el framework".
* **Ejemplo Incorrecto**: "El bot ha hecho 12 operaciones en 3 años con un Sharpe excelente; está listo para Demo".

---

### 3.12. Racha Máxima de Pérdidas (Max Consecutive Losses)
* **Definición**: El número máximo de operaciones consecutivas cerradas con pérdidas.
* **Interpretación**: Mide el peor escenario de rachas negativas y el estrés de Drawdown que debe soportar la cuenta.
* **Riesgos de Mala Interpretación**: Ignorar la probabilidad de que esta racha aumente significativamente en el futuro al ampliar la muestra.
* **Ejemplo Correcto**: "La racha máxima fue de 6 pérdidas consecutivas, lo que de media provocaría un DD controlado del 6%".
* **Ejemplo Incorrecto**: "La racha máxima de pérdidas fue de 2, por lo tanto nunca perderemos 3 veces seguidas en vivo".

---

### 3.13. Racha Máxima de Ganancias (Max Consecutive Wins)
* **Definición**: El número máximo de operaciones ganadoras consecutivas.
* **Interpretación**: Mide las rachas de euforia o tendencias continuas capturadas por el bot.
* **Riesgos de Mala Interpretación**: Sobreestimar la capacidad del bot basándose en periodos de rachas atípicas altamente rentables.
* **Ejemplo Correcto**: "La racha máxima de ganancias fue de 8 trades durante el fuerte rally del SP500 en 2024".
* **Ejemplo Incorrecto**: "La racha de 10 victorias seguidas garantiza que el bot no sufrirá caídas severas".

---

### 3.14. Pérdida Diaria Máxima
* **Definición**: La máxima caída sufrida por la equidad en un periodo cerrado de 24 horas.
* **Interpretación**: Clave para el enclavamiento de seguridad del RiskEngine determinista.
* **Riesgos de Mala Interpretación**: Evaluar la pérdida diaria en base a posiciones cerradas, obviando las flotantes intradía.
* **Ejemplo Correcto**: "La pérdida diaria máxima registrada en el histórico fue del 1.8%, quedando dentro del límite del Core (2%)".
* **Ejemplo Incorrecto**: "La pérdida diaria máxima es del 0.5% porque solo cerramos trades pequeños (mientras manteníamos posiciones con -8% flotante abiertas durante días)".

---

### 3.15. Exposición Simultánea
* **Definición**: El volumen de capital y número de lotes agregados que están abiertos al mismo tiempo en el mercado.
* **Interpretación**: Mide el riesgo de correlación de mercado (ej. estar expuesto al USD en 4 pares simultáneos).
* **Riesgos de Mala Interpretación**: Asumir que los riesgos están diversificados porque operamos activos distintos que en realidad están altamente correlacionados.
* **Ejemplo Correcto**: "La exposición simultánea máxima se limita a 3 trades concurrentes de 0.01 lotes cada uno".
* **Ejemplo Incorrecto**: "Operamos 10 posiciones de 0.1 lotes a la vez en EURUSD, GBPUSD, AUDUSD e NZDUSD; está diversificado".

---

### 3.16. Riesgo de Ruina (RoR)
* **Definición**: Probabilidad estadística de que el capital de la cuenta se reduzca a cero o por debajo de un nivel catastrófico.
* **Interpretación**: Calculado mediante simulaciones de Monte Carlo barajando el orden de los trades para modelar el peor escenario probabilístico.
* **Riesgos de Mala Interpretación**: Suponer que el RoR es 0% porque la secuencia histórica original del backtest no quebró la cuenta.
* **Ejemplo Correcto**: "La simulación de Monte Carlo de 5,000 iteraciones arroja un Riesgo de Ruina del 0.02% para una pérdida del 50% de la cuenta".
* **Ejemplo Incorrecto**: "El riesgo de ruina es del 0% porque en el orden del backtest nunca perdimos más del 10%".

---

### 3.17. Slippage Medio (Deslizamiento)
* **Definición**: Diferencia media entre el precio de ejecución solicitado por el bot y el precio real al que se ejecutó la orden.
* **Interpretación**: Mide la latencia de red, la velocidad del broker y el impacto en la rentabilidad del bot.
* **Riesgos de Mala Interpretación**: Asumir en backtests que no habrá deslizamiento en momentos de volatilidad.
* **Ejemplo Correcto**: "Modelamos un Slippage Medio de 1.5 pips en el simulador para penalizar la ejecución en vivo".
* **Ejemplo Incorrecto**: "El bot asume una ejecución perfecta con slippage de 0 pips en las noticias de la Fed".

---

### 3.18. Coste Medio por Operación (Cost per Trade)
* **Definición**: El coste medio en comisiones, swaps y spreads incurrido en cada transacción de ida y vuelta.
* **Interpretación**: Indica el umbral de rentabilidad mínimo que debe superar la esperanza matemática del bot para no ser devorado por costes.
* **Riesgos de Mala Interpretación**: Ignorar los costes acumulativos de swap nocturno en bots que mantienen posiciones abiertas durante semanas.
* **Ejemplo Correcto**: "El Coste Medio es de 6.0 USD por lote, por lo que todo trade de 0.01 lotes tiene una fricción de 0.06 USD".
* **Ejemplo Incorrecto**: "El bot no paga comisiones en este broker, así que el coste es cero (omitiendo spreads gigantescos)".

---

### 3.19. Duración Media de Operación (Holding Time)
* **Definición**: El intervalo de tiempo medio transcurrido entre la apertura y el cierre de las posiciones.
* **Interpretación**: Ayuda a tipificar la estrategia (Scalping, Day trading, Swing) y detectar comportamientos no deseados de sobreoptimización.
* **Riesgos de Mala Interpretación**: Asumir que una duración media alta es necesariamente más segura o estable.
* **Ejemplo Correcto**: "La duración media es de 4.2 horas, clasificándola sólidamente como estrategia Intradía".
* **Ejemplo Incorrecto**: "La duración media es de 1 segundo en el backtest (ejecución que colapsará en vivo en cuenta demo)".

---

## 4. Métricas Prioritarias del Ecosistema

Para el enrutamiento de señales en el Core, el sistema Antigravity ponderará con **mayor peso jerárquico** el siguiente grupo de métricas de resiliencia y supervivencia:

```
┌────────────────────────────────────────────────────────┐
│               MÉTRICAS PRIORITARIAS                    │
├────────────────────────────────────────────────────────┤
│  1. Max Drawdown de Equidad (MDD)    [≤ 12%]           │
│  2. Recovery Factor (RF)             [≥ 3.0]           │
│  3. Estabilidad Temporal de Equidad  [Linealidad]      │
│  4. Consistencia OOS                 [PF ≥ 1.25]       │
│  5. Esperanza Matemática Positiva    [Expectancy > 0]  │
│  6. Riesgo de Ruina Monte Carlo      [< 0.1%]          │
│  7. Pérdida Diaria Máxima            [≤ 2.0%]          │
│  8. Significancia Estadística ($N$)  [≥ 150 trades]    │
└────────────────────────────────────────────────────────┘
```

El Core de Antigravity prioriza la **Consistencia Estadística** y la **Robustez Fuera de Muestra (OOS)**. Si un bot muestra métricas sobresalientes en In-Sample pero decae drásticamente en OOS, será automáticamente degradado a `REJECTED`, independientemente de lo atractiva que sea su curva IS.

---

## 5. Métricas Secundarias (Advertencias)

Las siguientes métricas son catalogadas como **secundarias y potencialmente engañosas** si se evalúan de forma aislada:

* **Win Rate**: Es sumamente manipulable. Una estrategia martingale o un grid sin Stop Loss puede tener un Win Rate del 99% ganando centavos, antes de sufrir un único trade que barra el 100% de la cuenta. **El Win Rate solo tiene sentido combinado con el Win/Loss Ratio y el Expectancy.**
* **Beneficio Bruto / Retorno Total**: Los beneficios absolutos son engañosos si para lograrlos el sistema tuvo que exponer la cuenta a Drawdowns catastróficos del 50% o al apalancamiento excesivo.
* **Curva de Equity Visual**: Una curva de balance perfectamente recta e inclinada hacia arriba suele ocultar una estrategia "no declarada" de aplazamiento de pérdidas flotantes (ej. mantener pérdidas flotantes abiertas semanas sin ejecutar los Stop Loss reales).

---

## 6. Umbrales Conservadores Iniciales

A continuación se definen los umbrales cuantitativos orientativos. Deberán reajustarse según las condiciones intrínsecas de volatilidad y liquidez de cada tipo de activo:

| Activo | PF IS Mínimo | PF OOS Mínimo | Max DD Máximo | Recovery Factor Mín | Sharpe Mínimo | Sortino Mínimo | Operaciones Mínimas ($N$) | Pérdida Diaria Máx | Exposición Máx | Slippage Máx Tolerable |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Forex** | $\ge 1.40$ | $\ge 1.25$ | $\le 10.0\%$ | $\ge 3.0$ | $\ge 1.20$ | $\ge 1.50$ | $\ge 180$ | $\le 2.0\%$ | $\le 3.0\%$ | $1.5$ pips |
| **Índices** | $\ge 1.45$ | $\ge 1.30$ | $\le 8.0\%$ | $\ge 4.0$ | $\ge 1.30$ | $\ge 1.60$ | $\ge 150$ | $\le 1.5\%$ | $\le 2.0\%$ | $1.0$ puntos |
| **Oro (XAU)**| $\ge 1.50$ | $\ge 1.35$ | $\le 12.0\%$ | $\ge 3.0$ | $\ge 1.10$ | $\ge 1.40$ | $\ge 200$ | $\le 2.5\%$ | $\le 3.0\%$ | $2.0$ pips |
| **Cripto** | $\ge 1.60$ | $\ge 1.40$ | $\le 15.0\%$ | $\ge 3.0$ | $\ge 1.00$ | $\ge 1.30$ | $\ge 250$ | $\le 3.0\%$ | $\le 4.0\%$ | $3.5$ pips |

*Nota: Estos valores son de aplicación inicial para cuentas académicas estándar y deberán modularse por tipo de activo y timeframe.*

---

## 7. Interpretación de Resultados

Clasificamos el desempeño de las estrategias en 4 bandas discretas de viabilidad:

1. **EXCELENTE**:
   * Todos los umbrales de la Sección 6 son ampliamente superados.
   * La consistencia temporal (linealidad) es elevada.
   * El decaimiento de métricas de IS a OOS es inferior al **10%**.
   * Calificación: `PAPER_TRADING_READY` (autorizada de inmediato para simulación en vivo).
2. **ACEPTABLE**:
   * Cumple de manera holgada con los umbrales mínimos establecidos.
   * La robustez en OOS y significancia estadística está validada.
   * Calificación: `PAPER_TRADING_READY` o `OBSERVATION` bajo monitoreo preventivo.
3. **DUDOSO**:
   * Algún umbral crítico (e.g. Recovery Factor o Sharpe Ratio) no se cumple en OOS, o la muestra de operaciones es demasiado ajustada ($100 < N < 150$).
   * Calificación: `OBSERVATION` (bloqueada para pruebas en vivo, en observación preventiva).
4. **RECHAZADO**:
   * Falla en uno o más límites máximos intolerables (e.g. Drawdown $> 12\%$, Expectancy negativo, fallas en auditoría de sesgos).
   * Calificación: `REJECTED` (descarte automático del bot en la base de datos central).

> [!CAUTION]
> **Ganar dinero no es suficiente**:
> Una estrategia puede generar retornos netos positivos extremadamente atractivos y, a pesar de ello, ser **rotundamente rechazada** si vulnera los parámetros de exposición, presenta drawdowns flotantes ocultos o carece de consistencia en el OOS. La robustez científica prima sobre la rentabilidad teórica.

---

## 8. Señales de Alerta (Red Flags)

Cualquier analista o validador de IA del ecosistema debe rechazar o suspender de inmediato un bot si se detecta alguna de las siguientes **Señales de Alerta**:

* **Profit Factor Anomalamente Alto**: Un $PF > 3.0$ sobre un histórico significativo suele esconder un sesgo de *Look-Ahead* en el código (el bot "sabe" qué pasará y simula entradas perfectas).
* **Drawdown Oculto o Flotante Inusual**: Curva de balance limpia y ascendente, pero equidad flotante con profundas caídas y prolongadas mesetas de recuperación.
* **Dependencia de Operaciones Únicas**: El beneficio total neto del backtest se debe en más de un **30%** a una sola operación extremadamente ganadora atípica (outlier).
* **Mejora Excesiva en Optimización**: Una variación del $1\%$ en los parámetros del indicador provoca que el bot pase de perder el 50% de la cuenta a ganar el 200% (síntoma de extrema inestabilidad de parámetros).
* **Colapso en OOS**: Un periodo Out-of-Sample con métricas radicalmente inferiores al In-Sample (degradación $> 25\%$), demostrando que el bot se adaptó perfectamente a ruidos específicos del pasado.
* **Slippage y Costes Ignorados**: Backtests ejecutados con spread constante de cero y sin simular deslizamiento de latencia ni comisiones de broker.
* **Curva Excesivamente Perfecta**: Curva de equidad visual que asemeja una línea recta diagonal de 45 grados sin ninguna oscilación. Suele denotar martingalas, trampas de simulación o sobreajuste severo.
* **Distribución Anómala de Retornos**: La serie de transacciones muestra una distribución con colas excesivamente pesadas o comportamientos de asimetría negativa no controlada.

---

## 9. Relación con el Strategy Validation Framework

Este estándar matemático es el **complemento directo y la capa cuantitativa** del `STRATEGY_VALIDATION_FRAMEWORK.md`. 

Mientras que el Framework de Validación define las *políticas de ciclo de vida*, *fases*, *separación de carpetas* y *flujos de decisión*, el **Metrics Standard** provee las *ecuaciones*, *umbrales cuantitativos rígidos* y las *métricas de auditoría* que nutren los triggers lógicos del Core. Ninguna estrategia puede considerarse "validada" sin satisfacer simultáneamente ambos estándares.

---

## 10. Métricas y Régimen de Mercado

La consistencia estadística exige evaluar las métricas por separado segmentando el histórico en diferentes **Regímenes de Mercado**:

* **Tendencia vs Rango**: Calcular el Profit Factor y el Expectancy diferenciando periodos con fuerte tendencia (e.g. ADX $> 25$) de periodos de rango lateral (e.g. ADX $< 20$). Si un bot solo es rentable en tendencia y quiebra en rango, se debe evaluar si cuenta con filtros robustos de exclusión de rango.
* **Alta vs Baja Volatilidad**: Comprobar el Drawdown Máximo y el deslizamiento real (slippage) durante picos de volatilidad (medidos con ATR o Desviación Estándar).
* **Por Sesiones y Activos**: Monitorear y aislar el rendimiento del bot según la franja horaria activa (e.g. volumen transaccional y comisiones específicas en sesión de Nueva York vs Londres).

---

## 11. Métricas y Degradación (Strategy Decay)

El monitoreo de las métricas en tiempo real dentro del Core de Antigravity disparará de forma autónoma alertas de degradación y reclasificará el bot a `OBSERVATION` o `REJECTED` si se detecta:

1. **Caída del Profit Factor**: Desplome sostenido del PF por debajo de **$1.15$** evaluado en una ventana deslizante de las últimas 30 operaciones reales.
2. **Exceso de Drawdown Histórico**: El drawdown registrado en cuenta demo supera en un **20%** al drawdown máximo tolerado o estimado en el backtest.
3. **Pérdida de Esperanza Matemática**: Caída del Expectancy por debajo de cero en el monitoreo activo.
4. **Degradación Out-of-Sample Activa**: Desviación estadísticamente significativa entre las métricas de rendimiento en vivo y la proyección paramétrica del backtest.
5. **Rachas Negativas Anómalas**: El número de operaciones perdedoras consecutivas excede en más de dos unidades al límite observado en el backtest.

---

## 12. Recomendación para Futura Implementación

Para trasladar este estándar a código ejecutable en las siguientes iteraciones de desarrollo, se recomienda implementar los siguientes modelos de validación Pydantic en `core/models.py` (sin desarrollar código todavía):

* **`BacktestReport`**: Estructura Pydantic para validar la carga de métricas cuantitativas desde los archivos del backtest (e.g. MT5 HTML Report o Excel parseado).
* **`StrategyEvaluation`**: Modelo relacional híbrido para asociar el historial y ficha de la estrategia en la base de datos SQLite.
* **`MetricThresholds`**: Modelo Pydantic para gestionar las configuraciones de umbrales dinámicos parametrizados por tipo de activo y timeframe.

---

## 13. Ejemplos Prácticos de Evaluación (Casos Ficticios)

---

### Caso A: Estrategia RECHAZADA por Drawdown Oculto
* **Bot**: `ST-GRID-EURUSD-v1`
* **Resultados**: 
  * Win Rate: $88\%$ | Profit Factor: $1.85$ | Operaciones ($N$): $190$.
  * Drawdown de Balance: $3.5\%$ | **Drawdown de Equidad Flotante: $42.0\%$**.
  * Recuperación (RF): $0.85$ (muy bajo debido al alto DD flotante).
* **Dictamen**: **`REJECTED`**. La estrategia aplica una técnica Grid de aplazamiento de pérdidas sin Stop Loss explícito. Aunque la curva visual de balance es limpia, el riesgo de ruina real por el drawdown de equidad flotante excede los límites permisibles ($\le 12\%$).

---

### Caso B: Estrategia RECHAZADA por Win Rate Alto con Expectancy Mala
* **Bot**: `ST-SCALPER-USDJPY-v2`
* **Resultados**: 
  * Win Rate: $92\%$ | Operaciones ($N$): $320$.
  * Ganancia Media: $+2$ pips | Pérdida Media: $-60$ pips.
  * Esperanza Matemática (Expectancy): $-2.96$ pips por trade (considerando comisiones).
* **Dictamen**: **`REJECTED`**. Presenta una asimetría matemática devastadora. Una sola pérdida consecutiva absorbe las ganancias de 30 operaciones consecutivas. Al añadir la fricción de comisiones y slippage real en demo, el sistema entra en pérdidas continuas.

---

### Caso C: Estrategia ACEPTABLE con Win Rate Bajo pero PF Sólido
* **Bot**: `ST-TREND-SP500-v1`
* **Resultados**: 
  * Win Rate: $38\%$ | Profit Factor: $1.48$ | Operaciones ($N$): $210$.
  * Ganancia Media: $+120$ puntos | Pérdida Media: $-40$ puntos.
  * Win/Loss Ratio: $3.0$ | Max Drawdown: $7.2\%$.
  * Recovery Factor: $4.5$.
* **Dictamen**: **`PAPER_TRADING_READY`**. A pesar de un winrate bajo, la sólida asimetría positiva ($3:1$) y el estricto control de pérdidas garantizan una esperanza matemática y una recuperación sobresalientes, con drawdowns muy controlados.

---

### Caso D: Estrategia SOSPECHOSA por Overfitting
* **Bot**: `ST-OVERFIT-GBPUSD-v1`
* **Resultados**: 
  * In-Sample (IS): PF: $2.10$ | Max Drawdown: $4.5\%$ | Sharpe: $2.20$.
  * Out-of-Sample (OOS): PF: $0.92$ | Max Drawdown: $22.0\%$ | Sharpe: $-0.15$.
* **Dictamen**: **`REJECTED`**. Evidencia de extrema sobreoptimización paramétrica sobre los datos In-Sample. El bot es incapaz de adaptarse a datos no vistos fuera de muestra.

---

## 14. Conclusión Estratégica

El objetivo final de Antigravity no es la obtención de un robot de trading con retornos teóricos exponenciales, sino la consolidación de un **ecosistema de trading algorítmico gobernado, auditable, científicamente evaluable y altamente adaptable**. 

El rigor cuantitativo estipulado en este estándar garantiza que el capital simulado del ecosistema se exponga únicamente a ventajas estadísticas contrastadas, controlando activamente el riesgo y permitiendo un crecimiento sostenido, seguro y reproducible del proyecto académico.

---
*Diseño y Especificación Cuantitativa bajo la autoría del Director Técnico y Arquitecto Principal del Proyecto Antigravity.*
