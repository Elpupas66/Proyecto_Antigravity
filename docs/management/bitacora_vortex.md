# 🗺️ Bitácora de Estrategia: Blacksheep Vortex
### Laboratorio de Trading Automatizado

> **Propósito:** Este documento mantiene un registro determinista de todas las acciones, decisiones y progresos específicos para la estrategia **Blacksheep Vortex**. Sigue el ciclo de vida estándar del proyecto.

---

## 📍 Estado Actual (17/05/2026)
**⛔ ESTRATEGIA DESCARTADA — Backtesting completado sin resultados rentables.**
- La infraestructura de automatización (TradingView → n8n → Gatekeeper API → MT5) fue validada con éxito usando esta estrategia como banco de pruebas.
- El código final del indicador queda archivado en `trading/deploy/TradingView_BVortex_Final.txt` para referencia futura.
- No se realizarán más pruebas con esta estrategia.

---

## 📝 Bitácora de Actividades (Vortex)

### Sesión 1 - 02/05/2026
- **Decisión estratégica:** Descartar archivos de texto/Word intermedios (`Estrategia v1`, `Vortex-Patxi`, etc.) para basar la codificación exclusivamente en la fuente original de la academia ubicada en `Vortex_Original\Blacksheep_Vortex.pdf`.

### Sesión 2 - 16/05/2026
- **Validación de Reglas:** Se confirma que la lógica de gatillo, Stop Loss (mínimo absoluto del pullback) y Take Profit (1:1) implementada es 100% fiel al texto original del PDF.
- **Decisión estratégica (Criptomonedas):** Debido a la naturaleza tendencial de BTCUSD y sus ciclos diferentes, se decide suspender temporalmente el despliegue directo del Indicador con Alertas. En su lugar, se crea una versión `strategy()` en Pine Script para realizar Backtesting riguroso en TradingView.
- **Objetivo de Optimización:** Encontrar el marco temporal óptimo (1D vs 4H) y el Nivel Extremo del oscilador (+-15 vs +-17 vs +-20) que maximice el Profit Factor y el Win Rate histórico para Bitcoin.
- **Directriz Operativa (Flujo de Backtesting en TradingView):**
  1. **Persistencia:** El código debe guardarse manualmente ("Guardar") en el Pine Editor para que se almacene en "Mis Scripts".
  2. **Ejecución Automática:** Al pulsar "Añadir al gráfico", la estrategia (`strategy()`) ejecuta un backtest histórico completo de forma instantánea usando los parámetros por defecto.
  3. **Ciclo de Optimización:** La optimización es visual y en tiempo real. Cualquier modificación en la configuración del indicador (icono de engranaje en el gráfico, ej. cambiar de -17 a -15) recalculará automáticamente todo el historial, facilitando la búsqueda rápida de la mejor parametrización.
- **Auditoría de Código y Correcciones (Pine Script v6):** Se ha sometido el código del Indicador a una auditoría estricta para garantizar fiabilidad algorítmica. Se han integrado y guardado las siguientes mejoras críticas:
  - Eliminación de *repainting* (repintado) utilizando `barstate.isconfirmed` para forzar que los gatillos solo se validen en velas cerradas.
  - Corrección de la lógica de giro (solo `hist > hist[1]`) eliminando falsos positivos en zonas prolongadas.
  - Reset robusto del estado persistente (`pending_buy_sl`, `pending_buy_tp`, etc.) post-ejecución y post-anulación para prevenir fugas de estado.
  - Inclusión de parámetros configurables (Risk:Reward ratio y fondo de estado visual).
  - Lógica de limpieza pura: Reseteo de estados de "armado" si el histograma cruza la línea cero (cambio de tendencia).
- **Resultados de Backtesting (BTCUSD - 5 Años):** 
  - Las operaciones de Venta (Shorts) resultan sistemáticamente en pérdidas.
  - Las operaciones de Compra (Longs) son ligeramente positivas, pero la rentabilidad total en 5 años (incluso ajustando el Risk:Reward ratio a 1:2 o 1:3) es marginal (~1% de beneficio sobre la cuenta simulada).
  - **Conclusión Estratégica:** La estrategia Blacksheep Vortex (basada en retrocesos profundos y stops ajustados) **no es óptima para BTCUSD**. La volatilidad inherente y la estructura de tirones de liquidez de Bitcoin tienden a cazar los Stop Losses tan estrictos requeridos por esta estrategia. Se descarta Bvortex para criptomonedas y se reservará su uso para índices (DAX) o Forex, donde los retrocesos son más ordenados.
### Sesión 3 - 17/05/2026

#### 🔬 Backtesting Exhaustivo (Conclusión Final)
- **Activos probados:** BTCUSD, EURUSD, GBPUSD, USDJPY, XAUUSD (Oro), Petróleo, Plata. Los índices (DAX, SP500) no generaban datos históricos en TradingView (instrumentos de solo precio, sin volumen negociable).
- **Temporalidades probadas:** 1H, 4H, 1D.
- **Parámetros de nivel extremo probados:** ±15, ±17, ±20.
- **Ratios Risk:Reward probados:** 1:1, 1:2, 1:3.
- **Resultado:** En **ninguna** combinación de activo, temporalidad, nivel extremo o ratio R:R la estrategia alcanzó rentabilidad positiva sostenida. Los Shorts son sistemáticamente negativos. Los Longs de BTCUSD en 1D son marginalmente positivos (~50-100$ en 5 años), pero no superan el umbral mínimo de Profit Factor > 1.3 exigido por las normas del proyecto.
- **Causa probable:** La estrategia Bvortex depende de retrocesos ordenados hacia el oscilador. Bitcoin y Forex realizan *liquidity grabs* (tirones de liquidez) que cazan los Stop Losses ajustados antes de que el precio se mueva a favor. El sistema es matemáticamente inviable para los activos probados.
- **Decisión:** **Estrategia Bvortex descartada definitivamente.** El código queda archivado pero no se realizarán más iteraciones.

#### ✅ Prueba E2E del Pipeline de Automatización (ÉXITO)
- **Objetivo:** Validar el flujo completo TradingView → Webhook n8n → AI (DeepSeek) → Gatekeeper API → MetaTrader 5.
- **Resultado:** **Pipeline completamente funcional.** Se abrieron 2 órdenes de prueba en MT5 (BTCUSD, tickets 399179955 y 399179956) a las 11:40 del 17/05/2026, confirmando el funcionamiento E2E.
- **Regla de límite validada:** Tras las 2 órdenes abiertas, el Gatekeeper API rechazó correctamente nuevas órdenes por la regla `posiciones >= 2`.

#### 🛠️ Guía de Resolución de Errores de Conexión (Para futuras estrategias)
Documentados para evitar repetición:

1. **Error: "404 Not Found" en el webhook de TradingView**
   - **Causa:** TradingView intenta entregar la alerta usando la **Test URL** de n8n, pero el modo test de n8n caducó (timeout de 2 minutos).
   - **Solución:** Activar el escenario de n8n con el interruptor **"Active"** (verde, esquina superior derecha). Usar siempre la **Production URL** (`/webhook/` en lugar de `/webhook-test/`) en la configuración de la alerta de TradingView.

2. **Error: "502 Bad Gateway" en nodo "Check MT5 Rules" de n8n**
   - **Causa A (más común):** La API Python (`gatekeeper_api.py`) no está arrancada. El puerto 8000 está cerrado.
   - **Solución A:** Ejecutar `start_gatekeeper.bat` en la raíz del proyecto. Verificar con `netstat -ano | findstr :8000` que aparece `LISTENING`.
   - **Causa B:** La ventana CMD de la API se cerró accidentalmente.
   - **Solución B:** Relanzar la API con `cmd /k python scripts\gatekeeper_api.py` desde la raíz del proyecto.
   - **Verificación:** Abrir `https://gatekeeper.jmbv-trader.org/health` en el navegador. Debe devolver `{"status":"ok","mt5_connected":true}`.

3. **Error: La URL del dominio no responde pero `localhost:8000` sí**
   - **Causa:** El túnel de Cloudflare no apunta al puerto correcto, o el subdominio configurado no coincide con el que se usa.
   - **Solución:** Verificar en [one.dash.cloudflare.com](https://one.dash.cloudflare.com) → Networks → Tunnels → Configure → Public Hostname que el servicio apunta a `http://localhost:8000`. El subdominio correcto es `gatekeeper.jmbv-trader.org` (NO `jmbv-trader.org` a secas).

4. **Error: La alerta de TradingView no dispara (código "Prueba Fuerza N8N")**
   - **Causa:** `alertcondition(true, ...)` o `alertcondition(close > 0, ...)` TradingView lo optimiza y no lo vuelve a evaluar tras el primer disparo.
   - **Solución:** Usar la función moderna `alert(mensaje, alert.freq_once_per_bar_close)` dentro de un bloque `if barstate.isconfirmed` (sin el `freq_once_per_bar_close` duplicado en el `if`). En la condición de la alerta en TradingView, seleccionar **"Cualquier llamada a la función alert()"**. En el campo Mensaje, escribir `{{alert_message}}`.

5. **Error: `ModuleNotFoundError: No module named 'MetaTrader5'` al arrancar la API**
   - **Causa:** El entorno virtual `.venv` está corrupto o no tiene los módulos instalados.
   - **Solución:** Usar el Python del sistema directamente: `cmd /k python scripts\gatekeeper_api.py`. Los módulos ya están instalados en `C:\Users\34628\AppData\Roaming\Python\Python314\site-packages`.

---

## 📦 Artefactos Archivados

- **Código indicador final (Pine Script v6):** `trading/deploy/TradingView_BVortex_Final.txt` — Versión auditada y lista para alertas. Archivada para referencia.
- **Script TradingView de prueba E2E:** Guardado en TradingView bajo el nombre "BVortex Strategy Backtest" (contenía el código de "Prueba Fuerza N8N" al cierre). El usuario puede eliminar dicho script de TradingView ya que no se publicó.
- **Código strategy() para backtesting:** Documentado en el walkthrough de la sesión de Antigravity.
