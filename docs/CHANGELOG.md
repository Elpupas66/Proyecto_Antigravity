# Changelog

Todos los cambios notables en el proyecto Antigravity serán documentados en este archivo.

## [Unreleased] - 2026-05-20
### Validado
- Pipeline E2E funcionando en pruebas reales (Telegram -> n8n -> MetaTrader 5).
- Alertas de TradingView conectadas y ejecutando órdenes automáticas en MetaTrader 5.
- Reglas de seguridad del Gatekeeper validadas (Límite matemático de posiciones y filtro emocional de IA).

## [2026-05-15]
### Añadido
- Reorganización de la documentación en la carpeta `/docs` subdividida por dominios (`architecture`, `environment`, `management`, `trading_rules`).
- Inicialización de `README.md` principal del proyecto.
- Creación de `.gitignore` para prevenir filtrado de credenciales, entornos virtuales y configuraciones locales de IA.
- Incorporación del documento PRD (`PRD_AI_DEV_ENV.md`) detallando la estrategia de modelos IA y automatización.
