# 📋 Extracción Completa de Lógica — ORB_MultiSymbol_v4.7
**Fuente**: `ORB_MultiSymbol_v4_7_ES.mq5` | BlackSheep Quant Lab
**Fecha análisis**: 2026-05-22 | **Analizado por**: Antigravity (Director)

---

## 1. RESUMEN EJECUTIVO

El EA implementa una estrategia de **Opening Range Breakout (ORB)** multi-símbolo. Opera en la apertura de sesiones de trading (Londres, Nueva York, Asia), define un "rango" con la/s primera/s vela/s de 15 o 30 minutos, y entra al mercado cuando el precio rompe ese rango hacia arriba (LONG) o hacia abajo (SHORT). Dispone de 3 modos: ORB normal, Anti-ORB (fade), y Fakeout (segunda ruptura). Gestiona el riesgo con TP dual (T1 cierra, T2 continúa con trailing o runner). Solo aplica el filtro CSI a pares FX; índices, metales y energía lo ignoran.

---

## 2. LÓGICA DE ENTRADA

### 2.1 Condición base — Definición del Rango ORB

| Paso | Condición |
|---|---|
| 1 | Esperar la vela de apertura de sesión (hora configurada en GMT + offset bróker) |
| 2 | Si TF=M15: el rango es el High y Low de ESA vela de 15 min |
| 3 | Si TF=M30: el rango es High/Low de las DOS primeras velas de 15 min |
| 4 | Si TF=AMBOS: se calculan ambos rangos en paralelo |
| 5 | **Filtro de tamaño**: Rechazar si `(High-Low) / pip < MinPips` (default: 3p) |
| 6 | **Filtro de tamaño**: Rechazar si `(High-Low) / pip > MaxPips` (default: 50p) |
| 7 | El rango solo se usa cuando la vela de apertura está completamente cerrada |

### 2.2 Condición de entrada — ORB Normal (MODO_ORB)

**LONG** (compra): Se cumplen TODAS las siguientes:
- `close > rng_high` (cierre de la vela M15 anterior por encima del High del rango)
- `InpDirection != DIR_SOLO_VENTAS`
- `SpreadOK()` → spread actual ≤ InpMaxSpread (si MaxSpread > 0)
- `IsStrengthAligned(sym, +1)` → CSI apoya la compra (base más fuerte que quote)
- `VWAP activado` → `close > VWAP` (precio por encima del VWAP anclado)
- Dentro de la ventana horaria de la sesión activa
- `trades_today < InpMaxPerDay` (por símbolo)
- `CountOpen() + CountPending() < InpMaxTotal` (total concurrente)
- `CanInitiateTrade(sym)` → caps diarios globales OK

**SHORT** (venta): Idéntico pero:
- `close < rng_low`
- `InpDirection != DIR_SOLO_COMPRAS`
- `IsStrengthAligned(sym, -1)` → CSI apoya la venta
- `VWAP activado` → `close < VWAP`

### 2.3 Modos de entrada

| Modo | Descripción |
|---|---|
| `ENTRADA_MERCADO` | Orden a mercado inmediata al detectar ruptura |
| `ENTRADA_PULLBACK` | Orden límite a `rng_high + PBOffset pips` (LONG) o `rng_low - PBOffset pips` (SHORT) |
| `ENTRADA_AMBAS` | Abre ambas simultáneamente (una a mercado + una límite) |

### 2.4 Modo Anti-ORB (MODO_ANTI)

Hace lo contrario: cuando el precio rompe el High → VENTA (fade), cuando rompe el Low → COMPRA (fade). El SL se coloca en el extremo de la vela de ruptura. **No usa filtro VWAP ni fakeout**.

### 2.5 Modo Fakeout

Detecta una "trampa": la primera ruptura del rango se ignora (o se opera si FAKEOUT_Y_NORMAL). Cuando el precio vuelve al rango y lo rompe en dirección CONTRARIA, eso es la señal real (fakeout confirmado). El SL de la entrada fakeout va al extremo del primer movimiento (máximo del fake-up o mínimo del fake-down).

---

## 3. LÓGICA DE SALIDA

### 3.1 Estructura de posición — SIEMPRE 2 tickets

Cada señal abre **2 posiciones de igual tamaño** (T1 y T2):

| Ticket | Función | TP | SL |
|---|---|---|---|
| T1 | Primera salida | `entry + TP1 pips` | Extremo del rango opuesto |
| T2 | Runner / segunda salida | `entry + TP2 pips` (o 0 si runner) | Mismo SL inicial que T1 |

### 3.2 Stop Loss

- **LONG**: SL = `rng_low - 1 pip` (debajo del rango)
- **SHORT**: SL = `rng_high + 1 pip` (encima del rango)
- En **Fakeout**: SL = extremo del movimiento falso

### 3.3 Take Profit 1 (T1)

- Fijo en `entry ± TP1 pips` (default: 10 pips)
- Al cerrarse T1 por TP → **activa Break-Even en T2**

### 3.4 Break-Even (T2)

- Condición: T1 ya no existe (cerrado por TP)
- Mueve el SL de T2 a `entry + BEOffset pips` (default: 1 pip extra)
- Solo si el nuevo SL es mejor que el actual

### 3.5 Take Profit 2 (T2) — Modos

| Modo | Configuración | Comportamiento |
|---|---|---|
| TP fijo | `TP2 > 0` (default: 30p) | Cierra T2 automáticamente al alcanzar TP2 |
| Runner | `TP2 = 0` | T2 no tiene TP fijo → solo cierra por trailing stop |

### 3.6 Trailing Stop (T2)

- Solo activo si `InpTrail = true` O si `TP2 = 0` (runner, forzado)
- Solo funciona DESPUÉS de que se active el Break-Even (T1 cerrado)
- Lógica: rastrea el mejor precio (bid para LONG, ask para SHORT)
- Nuevo SL = `mejor_precio - TrailStep pips`
- Solo mueve el SL si mejora la posición actual

### 3.7 Cierre por fin de sesión (opcional)

- Si `InpCloseEOS = true`: cuando la sesión termina, cierra todas las posiciones abiertas y cancela las órdenes límite pendientes de esa sesión

---

## 4. FILTROS ACTIVOS

### 4.1 Filtro VWAP

| Parámetro | Default | Descripción |
|---|---|---|
| `InpVWAP` | true | Activa/desactiva filtro |
| `InpVWAP_TF` | M15 | Timeframe para calcular el VWAP |
| `InpVWAP_Anchor` | 1 | 0=día entero, 1=apertura Londres (08:00 GMT), 2=apertura Asia |
| `InpVWAP_Days` | 3 | Días históricos para dibujar el VWAP |

**Cálculo**: VWAP = ΣΣ(típico * volumen_tick) / Σvolumen_tick, desde el punto de anclaje.

**Uso en señal**:
- LONG válido solo si `close > VWAP`
- SHORT válido solo si `close < VWAP`

### 4.2 Filtro CSI (Currency Strength Index)

**Solo aplica a pares FX. Índices, metales y energía lo ignoran siempre.**

| Parámetro | Default | Descripción |
|---|---|---|
| `InpCSI` | true | Activa filtro |
| `InpCSI_Mode` | CSI_FILTRO | Filtro=bloquea dirección contraria, Estricto=solo mejor par, Info=solo display |
| `InpCSI_Lookback` | 10 | Velas para calcular % de cambio por par |
| `InpCSI_TF` | H1 | Timeframe del cálculo |
| `InpCSI_MinDiff` | 15.0 | Diferencia mínima de score entre base y quote (-100 a +100) |
| `InpMaxPairs` | 2 | Máx pares activos por sesión (ranking) |
| `InpCSI_MinConv` | 0.05% | Spread mínimo real entre divisas para operar |

**Cálculo**: Para cada uno de los 28 cruces de 8 divisas mayores, calcula el % de cambio en N velas. Acumula para cada divisa (sube el par → base +, quote −). Normaliza a −100..+100.

**Uso en señal LONG**: `score_base − score_quote ≥ InpCSI_MinDiff`
**Uso en señal SHORT**: `score_quote − score_base ≥ InpCSI_MinDiff`

**Ranking de pares**: Al inicio de cada sesión, ordena los pares por `|score_base − score_quote| + bonificaciones`. Solo los `InpMaxPairs` mejores pueden operar esa sesión.

### 4.3 Filtro de Spread

- Si `InpMaxSpread > 0`: bloquea entrada si spread actual en pips > MaxSpread
- Si `InpMaxSpread = 0`: sin filtro

### 4.4 Filtro de Dirección

- `DIR_AMBAS`: opera compras y ventas
- `DIR_SOLO_COMPRAS`: solo entradas LONG
- `DIR_SOLO_VENTAS`: solo entradas SHORT

### 4.5 Filtro de Días de la Semana

- Configurable por día (Lun-Vie). Viernes puede desactivarse para evitar fines de semana.

### 4.6 Filtro de Pérdida Diaria (Kill Switch)

- Si `P&L_diario ≤ -InpMaxLoss%` de la balance del día: el EA se detiene completamente hasta el día siguiente.
- Incluye tanto posiciones cerradas como flotantes.

---

## 5. GESTIÓN DE RIESGO

| Parámetro | Default | Descripción |
|---|---|---|
| `InpLot` | 0.02 | Lote fijo (si RiskPct=false) |
| `InpRiskPct` | false | Activar cálculo por % de riesgo |
| `InpRisk` | 1.0% | % de la balance a arriesgar por operación (si RiskPct=true) |
| `InpMaxPerDay` | 2 | Máx trades por símbolo por día |
| `InpMaxTotal` | 4 | Máx posiciones+pendientes concurrentes (global) |
| `InpMaxTradesDia` | 2 | Máx trades totales al día (todos los símbolos) — v4.6 |
| `InpMaxParesDia` | 2 | Máx pares distintos operados al día — v4.6 |
| `InpMaxLoss` | 3.0% | Pérdida máxima diaria (kill switch) |

**Cálculo de lote por %**:
```
lote = (balance × riesgo%) / ((SL_pips × tick_size) / tick_value)
```

---

## 6. SESIONES Y HORARIOS

| Sesión | GMT Open | GMT Close | Default bróker (+2) |
|---|---|---|---|
| Londres (LDN) | 08:00 | 12:00 | 10:00–14:00 |
| Nueva York (NY) | 13:30 | 20:00 | 15:30–22:00 |
| Asia (ASN) | 00:00 | 06:00 | 02:00–08:00 |

**Combinaciones disponibles**: LDN | NY | LDN+NY | ASIA | ASIA+LDN | TODAS

**Detección GMT**: Automática (redondea al cuarto de hora más cercano) o manual.

**Zona horaria**: El EA convierte siempre internamente a hora del servidor del bróker.

---

## 7. PARÁMETROS CLAVE (tabla completa)

| Parámetro | Default | Descripción |
|---|---|---|
| `InpPreset` | PRESET_GRAFICO | Universo de símbolos |
| `InpSession` | SESION_NY | Sesión(es) a operar |
| `InpTF` | ORB_AMBOS | Timeframe del rango (M15, M30, ambos) |
| `InpMinPips` | 3.0 | Rango mínimo aceptable (pips) |
| `InpMaxPips` | 50.0 | Rango máximo aceptable (pips) |
| `InpVWAP` | true | Filtro VWAP activo |
| `InpCSI` | true | Filtro fuerza de divisas activo |
| `InpMode` | MODO_ORB | Modo operativo |
| `InpEntry` | ENTRADA_MERCADO | Tipo de entrada |
| `InpPBOffset` | 0.5 | Offset pullback (pips) |
| `InpFakeout` | FAKEOUT_OFF | Modo fakeout |
| `InpDirection` | DIR_AMBAS | Dirección permitida |
| `InpMaxSpread` | 0 | Spread máximo (0=off) |
| `InpTP1` | 10.0 | TP1 en pips |
| `InpTP2` | 30.0 | TP2 en pips (0=runner) |
| `InpBE` | true | Break-even activo |
| `InpBEOff` | 1.0 | Pips extra en BE |
| `InpTrail` | false | Trailing stop |
| `InpTrailStep` | 10.0 | Distancia trailing (pips) |
| `InpCloseEOS` | false | Cerrar al fin de sesión |
| `InpLot` | 0.02 | Lote fijo |
| `InpRiskPct` | false | Modo % riesgo |
| `InpRisk` | 1.0 | % riesgo por trade |
| `InpMaxPerDay` | 2 | Máx trades/símbolo/día |
| `InpMaxTotal` | 4 | Máx posiciones concurrentes |
| `InpMaxTradesDia` | 2 | Máx trades globales/día |
| `InpMaxParesDia` | 2 | Máx pares distintos/día |
| `InpMaxLoss` | 3.0 | Kill switch pérdida diaria (%) |

---

## 8. NOTAS PARA PINE SCRIPT

### ✅ Traducible directamente
- Lógica de rango ORB (M15/M30): 100% traducible con `request.security()`
- Señal de ruptura (close > High, close < Low): nativa en Pine
- Filtro VWAP anchored: disponible con `ta.vwap()` o cálculo manual
- SL en extremo del rango: nativo
- TP1 fijo: nativo con `strategy.exit()`
- Break-even: requiere variable `var` y condición de estado
- Filtro de días: `dayofweek` nativo
- Filtro de sesión (horas): `hour` y `minute` nativos
- Ventanas IS/OOS: `time >= timestamp()` nativo

### ⚠️ Requiere simplificación
- **CSI**: Pine no tiene acceso a múltiples símbolos en tiempo real fácilmente. Se puede aproximar con `request.security()` para cada par → cálculo de % cambio. Costoso pero posible.
- **Multi-símbolo**: En Pine el backtesting es siempre 1 gráfico. No hay multi-símbolo nativo. Solución: script separado por par.
- **Trailing stop dinámico en T2**: requiere gestión de estado con variables `var`.

### ❌ No traducible / Eliminar
- Gestión de órdenes simultáneas T1+T2 como tickets separados: Pine Strategy maneja posiciones, no tickets individuales. Se usará `strategy.exit()` con `qty_percent` para simular T1 (50%) y T2 (50%).
- Detección automática GMT del bróker: en Pine se usa `syminfo.timezone` o el usuario configura manualmente.
- Funciones de Market Watch (SymbolSelect, SymbolsTotal): no aplicable en Pine.
