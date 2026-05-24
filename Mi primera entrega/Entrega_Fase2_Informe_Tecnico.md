# Entrega Fase 2: Orquestación en la Nube y Control de Riesgo con IA

**Estudiante:** José Manuel Blázquez  
**Proyecto:** Gatekeeper de Trading - Proyecto Antigravity  
**Estado:** Fase 2 Completada con Éxito (10/05/2026)

---

## 1. Resumen de la Fase 2
En esta etapa, el sistema ha evolucionado de un script monolítico local a una **arquitectura distribuida y orquestada desde la nube**. Se ha implementado un flujo de trabajo en **n8n (alojado en AWS)** que actúa como el cerebro del sistema, conectando múltiples APIs y delegando la ejecución final a un entorno seguro local.

## 2. Arquitectura Técnica Implementada

El sistema utiliza cuatro capas de tecnología integradas:

1.  **Capa de Interfaz:** Bot de Telegram que recibe órdenes parametrizadas y justificaciones cualitativas.
2.  **Capa de Orquestación (AWS):** Instancia de n8n que procesa los Webhooks, extrae datos mediante Regex y coordina las validaciones.
3.  **Capa Cognitiva (IA):** API de DeepSeek que analiza el sentimiento y la lógica de la justificación, bloqueando operaciones impulsivas.
4.  **Capa de Ejecución (Local Bridge):** Un servidor FastAPI en el PC local, expuesto mediante un **Túnel de Cloudflare**, que interactúa directamente con la API de MetaTrader 5.

### Diagrama de Flujo:
`Telegram` ➡️ `n8n (AWS)` ➡️ `DeepSeek (Filtro IA)` ➡️ `Local Bridge (Filtro Riesgo)` ➡️ `MetaTrader 5`

## 3. Hitos Técnicos Conseguidos

-   **Conectividad Segura:** Implementación de un túnel reverso mediante `cloudflared` para permitir que un servidor en AWS llame a una máquina local detrás de un firewall sin abrir puertos.
-   **Seguridad de API:** Creación de un sistema de validación mediante `X-API-Key` para asegurar que solo el orquestador autorizado pueda ejecutar órdenes en el broker.
-   **Validación Matemática y Emocional:** El sistema ahora deniega órdenes si:
    -   El trader tiene más de 2 activos abiertos (Regla de sobreoperación).
    -   La IA detecta ansiedad o falta de soporte técnico en la justificación.

## 4. Pruebas de Funcionamiento (Validación)

Se ha validado el sistema mediante una operación real en cuenta Demo:
-   **Instrumento:** BTCUSD
-   **Veredicto IA:** APROBADO (Justificación técnica válida)
-   **Veredicto MT5:** PASSED (Riesgo controlado)
-   **Resultado:** Orden ejecutada automáticamente en MetaTrader 5 con Ticket único de operación.

## 5. Próximos Pasos (Fase 3)
-   Integración de **Google Sheets** como Diario de Trading persistente.
-   Configuración de servicios de Windows para ejecución 24/7 sin intervención manual.

---
*Documento generado como parte de la entrega del Laboratorio de IA para Trading Cuantitativo.*
