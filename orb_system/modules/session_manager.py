"""SessionManager: Gestiona las sesiones de trading activas."""

from datetime import datetime, time, timedelta
from typing import Optional


class SessionManager:
    """Gestiona las sesiones de trading activas según la configuración."""

    def __init__(self, config):
        """
        Inicializa el SessionManager.

        Args:
            config: Instancia de ConfigLoader con configuraciones cargadas.
        """
        self.config = config
        self.session_config = config.session
        self.rules_config = config.rules

    def get_active_session(self, timestamp: datetime) -> Optional[str]:
        """
        Determina la sesión activa para un timestamp dado.

        Args:
            timestamp: Timestamp en UTC.

        Returns:
            Nombre de la sesión activa (ej: "LDN") o None si no hay sesión activa.
        """
        # Verificar si el día de la semana está permitido
        weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        current_weekday = weekday_names[timestamp.weekday()]
        
        allowed_days = self.session_config.get("allowed_days", [])
        if current_weekday not in allowed_days:
            return None

        # Aplicar gmt_offset para obtener hora local del bróker
        gmt_offset = self.session_config.get("gmt_offset", 0)
        local_timestamp = timestamp + timedelta(hours=gmt_offset)
        local_time = local_timestamp.time()

        # Obtener sesiones activas
        active_sessions = self.session_config.get("active_sessions", [])
        
        # Verificar cada sesión activa
        for session_name in active_sessions:
            session_info = self.session_config.get(session_name, {})
            open_gmt = session_info.get("open_gmt", "")
            close_gmt = session_info.get("close_gmt", "")
            
            # Convertir strings de hora a objetos time
            try:
                open_time = time.fromisoformat(open_gmt)
                close_time = time.fromisoformat(close_gmt)
                
                # Manejar sesiones que cruzan medianoche
                if open_time > close_time:
                    # Sesión cruza medianoche (ej: 22:00 a 06:00)
                    if local_time >= open_time or local_time <= close_time:
                        return session_name
                else:
                    # Sesión normal (ej: 08:00 a 12:00)
                    if open_time <= local_time <= close_time:
                        return session_name
                        
            except ValueError:
                # Error al parsear las horas, continuar con la siguiente sesión
                continue

        return None