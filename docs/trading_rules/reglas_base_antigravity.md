# 📐 Reglas Base — Antigravity (Genérico)
### Curso: IA Práctica para Crear Soluciones de Negocio
### Versión: 1.0 | Aplicable a: Cualquier proyecto

> **¿Para qué sirve este fichero?**
> Es la brújula de trabajo en Antigravity. Estas reglas aplican a **cualquier proyecto** independientemente del dominio (trading, CRM, automatización, etc.). Son la base determinista sobre la que se construye cualquier solución robusta.

---

## 🧭 REGLA 1 — Planifica antes de actuar

> *"Un buen plan evita el 80% de los problemas."*

- **Antes de crear o modificar cualquier flujo, agente o automatización**, genera un plan estructurado paso a paso y espera validación explícita.
- Trabaja en **pasos pequeños y verificables**. No intentes construir toda la solución en una sola sesión.
- Al terminar cada tarea, genera una evidencia (lista de verificación, captura, log) que demuestre que funciona correctamente.

**Un plan válido debe responder:**
- ¿Qué problema concreto resuelve este componente?
- ¿Qué herramienta es la más adecuada para esta tarea?
- ¿Qué datos entran, qué datos salen y dónde se almacenan?
- ¿Cómo se conecta con el resto del sistema?

### ❌ Evita:
- Lanzarte a construir sin entender bien el objetivo.
- Hacer cambios masivos en algo que ya funciona parcialmente.
- Dar una tarea por terminada sin haberla probado.

---

## 🧹 REGLA 2 — Simplicidad y orden (KISS + DRY)

> *"Si no lo entiendes en 30 segundos, es demasiado complejo."*

- **Escribe código simple, predecible y fácil de leer.** Prioriza la claridad sobre soluciones "inteligentes" o crípticas.
- **Divide la lógica en funciones o módulos pequeños**, cada uno con una única y clara responsabilidad.
- **Nombra todo con claridad**: flujos, agentes, variables y nodos deben tener nombres que expliquen para qué sirven.

**Convención de nombres:**
```
[herramienta]_[módulo]_[acción]

Correcto:   make_leads_registrar_nuevo
Incorrecto: flujo1, agente_nuevo, test_final_v3
```

### ❌ Evita:
- Crear un único flujo gigante que haga todo a la vez.
- Copiar y pegar la misma lógica en varios lugares.
- Usar nombres genéricos o números como identificadores.

---

## 💬 REGLA 3 — Comunica con claridad y transparencia

> *"Quien no puede explicar lo que hace, no lo entiende del todo."*

- **Sé directo y concreto** al presentar avances: muestra el plan, el estado actual o el resultado, sin rodeos.
- **Si algo no encaja técnicamente**, detente y consulta antes de continuar. Es mejor preguntar dos minutos que rehacer dos horas.
- **Cuando modifiques algo existente**, documenta exactamente qué cambiaste y por qué.

### ❌ Evita:
- Entregar una solución sin explicar cómo funciona.
- Ejecutar una instrucción que no comprendes bien esperando que "salga bien".
- Hacer cambios silenciosos en flujos ya existentes.

---

## 🛡️ REGLA 4 — Programa pensando en los errores

> *"Los sistemas reales fallan. Un buen desarrollador lo anticipa."*

- **Nunca asumas el "camino feliz".** ¿Qué pasa si los datos llegan vacíos? ¿Si la API no responde? ¿Si el formato es inesperado?
- **Incluye siempre un manejo de errores robusto**: mensajes claros cuando algo falla, flujos alternativos, o al menos una alerta.
- **Ante un bug**, no cambies código al azar. Formula una hipótesis sobre la causa raíz, revisa los logs, y aplica una solución basada en datos.

### ❌ Evita:
- Dejar flujos sin manejo de errores.
- Cambiar configuraciones aleatoriamente esperando que el problema se "arregle solo".
- Ignorar mensajes de error.

---

## 🔒 REGLA 5 — Seguridad y datos de prueba

> *"Un error de seguridad puede echar a perder toda una solución."*

- **Nunca expongas datos sensibles** (contraseñas, claves API, datos personales) en flujos visibles o mensajes.
- **Antes de ejecutar una automatización sobre datos reales**, pruébala con datos ficticios.
- Guarda las credenciales **únicamente en variables de entorno** de cada herramienta, nunca en el cuerpo de un flujo.

---

## 📋 Checklist de verificación (antes de dar por terminado cualquier entregable)

| # | Pregunta | ✅ / ❌ |
|---|----------|--------|
| 1 | ¿Tienes un plan documentado de lo que construiste? | |
| 2 | ¿Cada parte tiene un nombre claro y descriptivo? | |
| 3 | ¿Probaste con datos de prueba (no reales)? | |
| 4 | ¿Tu solución maneja al menos el error más probable? | |
| 5 | ¿Puedes explicar en 2 minutos qué hace y cómo? | |
| 6 | ¿Documentaste los cambios importantes? | |
| 7 | ¿No hay datos sensibles expuestos? | |

---

## 🔑 Regla de oro de distribución de herramientas

| Capa | Herramienta | Cuándo usarla |
|------|-------------|---------------|
| Inteligencia y conversación | Antigravity | Agentes IA, razonamiento, respuestas |
| Automatización de procesos | Make.com | Flujos sencillos, notificaciones |
| Pipelines de datos complejos | N8N | Transformaciones, lógica condicional avanzada |
| Persistencia y reportes | Sheets / Airtable / Notion | Registro, historial, dashboards |

> Si puedes hacerlo con Make, no lo hagas en N8N. Si puedes hacerlo en N8N, no lo hagas en Antigravity.

---

*Curso: IA Práctica para Crear Soluciones de Negocio con Antigravity · Base genérica v1.0*
