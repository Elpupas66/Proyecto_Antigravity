"""Script de prueba para ConfigLoader, SessionManager y SignalGenerator."""

from datetime import datetime
from modules.config_loader import ConfigLoader
from modules.session_manager import SessionManager
from modules.signal_generator import SignalGenerator


def main():
    """Prueba la carga de configuraciones JSON, SessionManager y SignalGenerator."""
    print("Iniciando prueba de ConfigLoader, SessionManager y SignalGenerator...")
    
    # Instanciar ConfigLoader
    loader = ConfigLoader()
    
    # Cargar todos los archivos JSON
    try:
        loader.load_all()
        print("✅ Todos los archivos JSON cargados correctamente.")
    except Exception as e:
        print(f"❌ Error al cargar archivos JSON: {e}")
        return
    
    # Mostrar resumen de configuraciones cargadas
    print("\n--- Resumen de Configuraciones ---")
    
    if loader.params:
        print(f"📊 Params: {list(loader.params.keys())}")
    
    if loader.session:
        print(f"🕒 Session: {list(loader.session.keys())}")
    
    if loader.risk:
        print(f"⚠️ Risk: {list(loader.risk.keys())}")
    
    if loader.rules:
        print(f"📋 Rules: {list(loader.rules.keys())}")
    
    # Probar SessionManager
    print("\n--- Probando SessionManager ---")
    
    try:
        session_manager = SessionManager(loader)
        
        # Crear timestamps de prueba
        test_cases = [
            (datetime(2026, 5, 26, 9, 0), "martes 09:00 GMT"),  # Martes a las 09:00 GMT
            (datetime(2026, 5, 26, 22, 0), "martes 22:00 GMT"),  # Martes a las 22:00 GMT
            (datetime(2026, 5, 24, 10, 0), "domingo 10:00 GMT"),  # Domingo a las 10:00 GMT
        ]
        
        for timestamp, description in test_cases:
            active_session = session_manager.get_active_session(timestamp)
            print(f"{description}: {active_session}")
        
        print("\n✅ Prueba de SessionManager completada exitosamente.")
        
    except Exception as e:
        print(f"❌ Error en SessionManager: {e}")
        return
    
    # Probar SignalGenerator
    print("\n--- Probando SignalGenerator ---")
    
    try:
        signal_generator = SignalGenerator(loader, session_manager)
        
        # Crear velas simuladas ajustadas para gmt_offset: 2
        test_bars = [
            {
                "timestamp": datetime(2026, 5, 26, 5, 45),
                "description": "Vela 1: martes 05:45 GMT (fuera de sesión)",
                "bar_data": {"high": 1.1000, "low": 1.0980, "close": 1.0990}
            },
            {
                "timestamp": datetime(2026, 5, 26, 6, 0),
                "description": "Vela 2: martes 06:00 GMT (apertura efectiva LDN en UTC)",
                "bar_data": {"high": 1.1020, "low": 1.0990, "close": 1.1005}
            },
            {
                "timestamp": datetime(2026, 5, 26, 6, 15),
                "description": "Vela 3: martes 06:15 GMT (ruptura alcista)",
                "bar_data": {"high": 1.1050, "low": 1.1000, "close": 1.1030}
            }
        ]
        
        for bar in test_bars:
            signal = signal_generator.process_bar(bar["bar_data"], bar["timestamp"])
            
            # Obtener sesión activa para mostrar
            active_session = session_manager.get_active_session(bar["timestamp"])
            
            print(f"\n{bar['description']}")
            print(f"  Timestamp: {bar['timestamp'].strftime('%Y-%m-%d %H:%M GMT')}")
            print(f"  Sesión activa: {active_session}")
            print(f"  ORB High: {signal_generator.orb_high}")
            print(f"  ORB Low: {signal_generator.orb_low}")
            print(f"  Señal: {signal}")
        
        print("\n✅ Prueba de SignalGenerator completada exitosamente.")
        
    except Exception as e:
        print(f"❌ Error en SignalGenerator: {e}")
        return
    
    print("\n✅ Todas las pruebas completadas exitosamente.")


if __name__ == "__main__":
    main()