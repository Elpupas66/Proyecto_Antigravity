# Proyecto Antigravity 🚀

**Proyecto Antigravity** es un entorno integral para el diseño, validación y ejecución de sistemas de trading algorítmico automatizados. El repositorio combina herramientas de inteligencia artificial, documentación técnica, utilidades de análisis y scripts operativos para soportar distintas fases del ciclo de vida de una estrategia: investigación, desarrollo, backtesting, paper trading y despliegue.

## Objetivo

Este proyecto sirve como laboratorio técnico para:

- Diseñar estrategias de trading algorítmico.
- Probar flujos asistidos por IA para análisis, documentación y automatización.
- Ejecutar validaciones y backtests sobre datos históricos.
- Preparar despliegues hacia entornos de paper trading y producción.
- Centralizar documentación, reglas de negocio y bitácoras del proyecto.

## Estructura del proyecto

### Documentación
- `docs/architecture/`: documentos de diseño técnico y PRDs.
- `docs/environment/`: guías de entorno local, VS Code, IA local y configuración.
- `docs/management/`: bitácoras, entregables y seguimiento del proyecto.
- `docs/trading_rules/`: reglas base, normativa del laboratorio y reportes funcionales.

### Núcleo de trading
- `trading/`: lógica principal del sistema de trading.
  - `config/`: configuración general.
  - `data/`: datos procesados y fuentes de mercado.
  - `deploy/`: artefactos finales para MT5 y TradingView.
  - `results/`: resultados de pruebas, comparativas y resúmenes.
  - `strategies/`: estrategias implementadas.
  - `utils/`: utilidades auxiliares.

### Estrategia y validación
- `estrategia/`: documentación funcional, scripts de MT5, TradingView y versiones de estrategia.
- `backtests/`: comparativas, datos brutos y resultados de backtesting.
- `paper_trading/`: logs y reportes semanales de simulación.
- `produccion/`: alertas, logs operativos y reportes de rendimiento.

### Automatización y soporte
- `automatizaciones/`: flujos automáticos, por ejemplo integraciones tipo n8n.
- `scripts/`: utilidades operativas y scripts de soporte.
- `scratch/`: pruebas rápidas, utilidades temporales y scripts auxiliares.

## Requisitos

- Python instalado.
- Entorno virtual recomendado (`.venv`).
- Archivo `.env` en la raíz con las variables necesarias.
- Dependencias instaladas desde `requirements.txt`.

## Inicio rápido

1. Activa el entorno virtual:

   ```bash
   # Windows
   .venv\Scripts\activate
   ```

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno:

   - Crea un archivo `.env` en la raíz del proyecto.
   - Nunca subas este archivo al repositorio.

4. Inicia los servicios o scripts necesarios:

   ```bash
   start_gatekeeper.bat
   ```

## Flujo de trabajo recomendado

1. Leer la documentación base del entorno y arquitectura.
2. Revisar reglas del laboratorio y documentación de estrategia.
3. Ejecutar pruebas o validaciones desde `scripts/` y `trading/`.
4. Guardar resultados en rutas de trabajo locales no versionadas cuando sean datos pesados.
5. Preparar despliegues finales desde `trading/deploy/`.

## Archivos y carpetas no versionadas

Algunas carpetas contienen datos pesados, resultados temporales o archivos multimedia y deben quedar excluidas mediante `.gitignore`, por ejemplo:

- `trading/data/raw/`
- `trading/results/raw/`
- `backtests/raw_data/`
- `backtests/resultados/`
- `analisis_mercado/`
- `paper_trading/`
- `produccion/`
- `VortexOriginal/`

## Documentación recomendada para empezar

Se recomienda comenzar por:

- [`docs/architecture/PRD_AI_DEV_ENV.md`](./docs/architecture/PRD_AI_DEV_ENV.md)
- `docs/environment/`
- `docs/trading_rules/`

## Estado del proyecto

Repositorio en evolución continua, con foco en:
- entorno de desarrollo asistido por IA,
- validación de estrategias,
- automatización operativa (Pipeline E2E validado: Telegram/TradingView -> n8n -> Gatekeeper API -> MT5),
- reglas de riesgo y filtros emocionales activos,
- integración con herramientas de trading y análisis.
## Comandos útiles

### Entorno y dependencias

```bash
# Activar entorno virtual en Windows
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Arranque de servicios

```bash
# Iniciar Gatekeeper desde Windows
start_gatekeeper.bat
```

### Scripts de soporte

```bash
# Lanzar bot/API Gatekeeper manualmente
python scripts/gatekeeper_bot.py
python scripts/gatekeeper_api.py

# Probar la API desde PowerShell
powershell -ExecutionPolicy Bypass -File test_api.ps1
```

### Trading y validación

```bash
# Ejecutar backtest principal
python trading/run_backtest.py

# Ejecutar pruebas o utilidades
python scripts/run_test_data.py
python scripts/test_mt5_deepseek.py
```

### Diagnóstico rápido

```bash
# Comprobar entorno
python scratch/debug_env.py

# Verificar estado y símbolo MT5
python scratch/check_mt5_status.py
python scratch/check_mt5_symbol.py
```