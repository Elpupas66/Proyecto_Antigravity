# 🧠 Laboratorio IA Local para Trading Cuantitativo  
## 📍 Proyecto: Proyecto_antigravity

---

## 1. Objetivo

Crear un laboratorio de IA capaz de:

- Ejecutar modelos en local
- Analizar estrategias de trading
- Automatizar procesos
- Realizar backtesting
- Escalar a trading algorítmico

---

## 2. Arquitectura

- Ollama → ejecución de modelos IA
- VS Code → desarrollo
- Claude Code → agente IA
- Antigravity → interfaz de agentes

---

## 3. Estructura
Proyecto_antigravity
├─ trading
├─ .claude
├─ scripts
└─ docs


---

## 4. Modelos IA

- gemma4:e4b → análisis profundo
- gemma4:e2b → rápido
- qwen3.5:4b → programación
- qwen3.5:0.8b → ligero

---

## 5. Motor de backtesting

Permite:

- cargar datos
- calcular indicadores
- generar señales
- exportar resultados

---

## 6. Estado actual

Prueba realizada con:

- Estrategia: BVortex (base)
- Activo: EURUSD
- Timeframe: H4
- Datos: CSV de prueba

---

## 7. Naturaleza de pruebas

Modo laboratorio:

- validación técnica
- pruebas de pipeline
- no resultados reales

---

## 8. Escalabilidad

El sistema permite trabajar con:

- múltiples estrategias
- múltiples activos
- múltiples timeframes

---

## 9. Cómo ampliar el sistema

### Estrategias

Ruta:


trading/strategies/


Añadir nuevos `.py`

---

### Activos

Ruta:


trading/data/raw/


Añadir CSV:


Date,Open,High,Low,Close


---

### Configuración

Archivo:


trading/config/settings.yaml


Modificar:

- activo
- timeframe
- parámetros

---

### Pipeline

Archivo:


run_backtest.py


Permite ejecutar diferentes combinaciones

---

### Indicadores

Archivo:


utils/indicators.py


Añadir lógica nueva

---

### Métricas

Archivo:


utils/metrics.py


Añadir análisis avanzado

---

## 10. Flujo


Datos → Indicadores → Señales → Backtest → Resultados


---

## 11. Próximos pasos

### Fase 2

- entradas/salidas reales
- TP / SL
- PnL

### Fase 3

- múltiples estrategias
- comparaciones

### Fase 4

- optimización

### Fase 5
