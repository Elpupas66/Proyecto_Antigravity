"""SignalGenerator: Genera señales de trading basadas en lógica ORB."""

from datetime import datetime
from typing import Optional


class SignalGenerator:
    """Genera señales de trading usando lógica ORB (Opening Range Breakout)."""

    def __init__(self, config, session_manager):
        """
        Inicializa el SignalGenerator.

        Args:
            config: Instancia de ConfigLoader con configuraciones cargadas.
            session_manager: Instancia de SessionManager.
        """
        self.config = config
        self.session_manager = session_manager
        
        # Variables de estado
        self.current_session = None
        self.orb_high = None
        self.orb_low = None
        self.trade_taken = False

    def process_bar(self, bar_data: dict, timestamp: datetime) -> Optional[str]:
        """
        Procesa una vela y genera señales si corresponde.

        Args:
            bar_data: Diccionario con datos de la vela {"high": float, "low": float, "close": float}
            timestamp: Timestamp de la vela en UTC.

        Returns:
            "LONG", "SHORT" o None si no hay señal.
        """
        # Verificar sesión activa
        active_session = self.session_manager.get_active_session(timestamp)
        
        # Reset si no hay sesión activa
        if active_session is None:
            self.current_session = None
            self.orb_high = None
            self.orb_low = None
            self.trade_taken = False
            return None
        
        # Guardar sesión activa
        self.current_session = active_session
        
        # Captura del rango ORB (primera vela válida de la sesión)
        if self.orb_high is None:
            self.orb_high = bar_data["high"]
            self.orb_low = bar_data["low"]
            return None
        
        # Generación de señal si ya existe rango ORB y no se ha tomado trade
        if not self.trade_taken:
            if bar_data["close"] > self.orb_high:
                self.trade_taken = True
                return "LONG"
            elif bar_data["close"] < self.orb_low:
                self.trade_taken = True
                return "SHORT"
        
        # Si ya se tomó un trade, no generar más señales
        return None