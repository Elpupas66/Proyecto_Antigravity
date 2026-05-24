# 📖 Especificación Técnica: Blacksheep Vortex
**Fuente:** `Blacksheep_Vortex.pdf` (Manual Original de la Academia)
**Propósito:** Este es el Documento Maestro (Golden Source) que dicta las reglas deterministas para el código, backtesting y automatización.

---

## 1. Marcos Temporales (Timeframes)
La estrategia está diseñada para operativas tipo **Swing**.
- **Análisis de Tendencia Mayor:** `1D` (Diario) o incluso `W` (Semanal).
- **Gatillo de Entrada:** `4H` (Gráfico de 4 Horas).

## 2. Los 4 Pasos de la Estrategia

### PASO 1: Analizar Tendencia en 1D
Identificar la dirección del mercado observando la estructura de precios:
- **Tendencia Alcista:** Altos Crecientes (AC) y Bajos Crecientes (BC).
- **Tendencia Bajista:** Altos Decrecientes (AD) y Bajos Decrecientes (BD).
*Nota:* A veces la tendencia macro no es clara, en ese caso nos apoyamos en la estructura más reciente.

### PASO 2: Esperar Pullback (Retroceso)
El precio debe realizar un movimiento en contra de la tendencia principal (retroceso) que evaluaremos en el gráfico de 4H.

### PASO 3: Vortex en Extremos
El indicador Vortex nos avisa del posible final del retroceso cuando llega a sus niveles extremos:
- Para buscar **COMPRAS** (Tendencia Alcista): El histograma del Vortex debe tocar el **extremo inferior** (Abajo).
- Para buscar **VENTAS** (Tendencia Bajista): El histograma del Vortex debe tocar el **extremo superior** (Arriba).

### PASO 4: Confirmar Entrada (Gatillo y Patrón en V)
La entrada **NO** se hace a mercado, se hace mediante órdenes pendientes (*Buy Stop* / *Sell Stop*).

#### Para Compras (Largos):
1. El Vortex cambia de color (gira al alza).
2. Aparece una **vela verde** (que cierre a favor del movimiento esperado).
3. Colocamos una orden pendiente de compra (**Buy Stop**) en el **MÁXIMO** de esa vela.
4. El Stop Loss (**SL**) se coloca en el **MÍNIMO** absoluto del pullback.

#### Para Ventas (Cortos):
1. El Vortex cambia de color (gira a la baja).
2. Aparece una **vela roja** (que cierre a favor del movimiento).
3. Colocamos una orden pendiente de venta (**Sell Stop**) en el **MÍNIMO** de esa vela.
4. El Stop Loss (**SL**) se coloca en el **MÁXIMO** absoluto del pullback.

---

## 3. Reglas de Excepción y Gestión de Órdenes (A tener en cuenta)

1. **Anulación por vela contraria:** Si la vela que sigue a la vela gatillo (donde pusimos la orden) cierra en contra (ej. roja en compras), **se anula la orden pendiente** y se espera a una nueva vela a favor de la tendencia.
2. **Reinicio de Vortex:** Si la orden aún no se ha activado y el Vortex vuelve a cambiar de color (en contra), cancelamos y esperamos a que el Vortex vuelva a girar a nuestro favor para recolocar la orden.
3. **Reajuste de SL:** Si el precio, antes de activar la orden, crea un nuevo máximo o mínimo (extendiendo el pullback), debemos reajustar el Stop Loss al nuevo mínimo/máximo y esperar a que el Vortex siga favorable.
4. **Re-entradas tras tocar Stop Loss:** Si perdemos una operación por SL, solo podemos reentrar si:
   - El Vortex en 4H ha vuelto a tocar el nivel extremo.
   - O si el Vortex tocó el extremo en el gráfico Diario (D1).
   - *Siempre* esperando de nuevo el patrón de gatillo en 4H.

---

## 4. Gestión del Riesgo (Money Management)

Se divide el riesgo total por idea de trading en **0.5% del capital**, abriendo 2 operaciones simultáneas del 0.25% de riesgo cada una (Recomendado / GBS):
- **Operación 1:** Se cierra con un Ratio Beneficio/Riesgo de **1:1** (Ej. SL 100 pips, TP 100 pips).
- **Operación 2 ("Oveja Negra"):** Una vez la Op.1 toca TP, la Op.2 se protege (Break Even) y se deja correr para capturar la tendencia mayor.
