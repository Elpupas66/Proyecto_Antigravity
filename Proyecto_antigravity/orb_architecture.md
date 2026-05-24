# Arquitectura Modular del Sistema ORB

## Estructura de Archivos y Contratos de Módulos

### Estructura de Directorios

orb_system/
├── config/
│   ├── orb_params.json        ← parámetros del rango
│   ├── session_config.json    ← sesiones y horarios GMT
│   ├── risk_config.json       ← gestión de riesgo
│   └── entry_rules.json       ← reglas de entrada/salida
├── modules/
│   ├── config_loader.py       ← carga y valida JSONs
│   ├── session_manager.py     ← detecta sesión activa
│   ├── signal_generator.py    ← lógica ORB + filtros
│   ├── risk_manager.py        ← cálculo lotes, caps diarios
│   └── execution_engine.py   ← simula/ejecuta trades
├── backtester.py              ← orquesta IS/OOS
└── main.py                    ← punto de entrada

### Flujo de Datos

JSON configs
    ↓
ConfigLoader.load_all()
    ↓
SessionManager.is_active(timestamp) → bool
    ↓ (si sesión activa)
SignalGenerator.check_breakout(ohlc_data) → Signal | None
    ↓ (si hay señal)
RiskManager.validate_signal(signal) → Signal | Blocked
    ↓ (si pasa filtros)
ExecutionEngine.open_trade(signal) → Trade
    ↓
ExecutionEngine.manage_trade(trade) → [BE, Trail, Close]

### Dependencias entre Módulos

Módulo           Depende de
ConfigLoader     Nada (raíz)
SessionManager   ConfigLoader
SignalGenerator  ConfigLoader, SessionManager
RiskManager      ConfigLoader
ExecutionEngine  RiskManager, SignalGenerator
Backtester       Todos los anteriores

### Esquemas JSON Requeridos

// orb_params.json
{
  "orb_timeframes": ["M15", "M30"],
  "min_range_pips": 3.0,
  "max_range_pips": 50.0,
  "mode": "ORB",
  "entry_type": "MARKET",
  "tp1_pips": 10.0,
  "tp2_pips": 30.0,
  "sl_type": "range_opposite",
  "breakeven": true,
  "be_offset_pips": 1.0,
  "trailing": false,
  "trail_step_pips": 10.0
}

// session_config.json
{
  "active_sessions": ["LDN"],
  "gmt_offset": 2,
  "LDN": {"open_gmt": "08:00", "close_gmt": "12:00"},
  "NY":  {"open_gmt": "13:30", "close_gmt": "20:00"},
  "ASIA": {"open_gmt": "00:00", "close_gmt": "06:00"},
  "allowed_days": ["Mon","Tue","Wed","Thu","Fri"]
}

// risk_config.json
{
  "use_risk_pct": false,
  "fixed_lot": 0.01,
  "risk_pct": 1.0,
  "max_daily_loss_pct": 3.0,
  "max_trades_per_day": 2,
  "max_pairs_per_day": 2,
  "max_concurrent": 4,
  "kill_switch_active": true
}

// entry_rules.json
{
  "filters": {
    "vwap": {"enabled": true, "anchor": "LDN_open"},
    "spread": {"enabled": false, "max_pips": 2.0},
    "direction": "BOTH",
    "fakeout_mode": "OFF"
  },
  "forex_pairs": {
    "majors": ["EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD"],
    "crosses": ["EURJPY","GBPJPY","EURGBP","GBPCHF","EURAUD","GBPAUD"]
  }
}
















