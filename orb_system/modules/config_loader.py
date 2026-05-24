"""ConfigLoader: Carga y valida archivos JSON de configuración."""

import json
from pathlib import Path


class ConfigLoader:
    """Carga los archivos de configuración JSON del sistema ORB."""

    def __init__(self, base_path: str = None):
        """
        Inicializa el ConfigLoader.

        Args:
            base_path: Ruta base donde se encuentran los archivos de configuración.
                       Por defecto, usa orb_system/config/ relativo al directorio actual.
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent / "config"
        self.base_path = Path(base_path)

        # Atributos para almacenar los configuraciones
        self.params = None
        self.session = None
        self.risk = None
        self.rules = None

    def load_all(self) -> None:
        """Carga los 4 archivos JSON y guarda su contenido en los atributos."""
        config_files = {
            "params": "orb_params.json",
            "session": "session_config.json",
            "risk": "risk_config.json",
            "rules": "entry_rules.json"
        }

        for attr_name, filename in config_files.items():
            file_path = self.base_path / filename

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    setattr(self, attr_name, json.load(f))
            except FileNotFoundError:
                raise FileNotFoundError(f"Archivo de configuración no encontrado: {file_path}")
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Error al decodificar JSON en {file_path}: {e.msg}",
                    e.doc,
                    e.pos
                )
