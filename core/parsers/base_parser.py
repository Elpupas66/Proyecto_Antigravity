"""
core/parsers/base_parser.py
---------------------------
Interfaz abstracta y utilidades base para el Backtest Import Layer.
Fase 4.1: Define el contrato de parseo y la trazabilidad SHA-256.

Sin red, sin MT5 en vivo, sin base de datos, sin ejecución real.
"""

import hashlib
from abc import ABC, abstractmethod

from core.strategy_models import BacktestPeriod, BacktestReport


# ─── EXCEPCIONES CUSTOM DEL IMPORT LAYER ─────────────────────────────────────

class ParserLanguageError(ValueError):
    """
    Lanzada cuando el informe MT5 no está en inglés.
    Todos los informes deben generarse con el terminal MT5 en English.
    """
    pass


class ParserStructureError(ValueError):
    """
    Lanzada cuando el archivo no tiene la estructura esperada de un
    informe de MetaTrader 5. El DOM es irreconocible o está corrupto.
    """
    pass


# ─── INTERFAZ ABSTRACTA ───────────────────────────────────────────────────────

class BaseParser(ABC):
    """
    Clase base abstracta para todos los parsers del Backtest Import Layer.

    Toda implementación concreta debe:
    - Implementar el método `parse()`.
    - Respetar el contrato Pydantic `BacktestReport`.
    - No abrir conexiones de red.
    - No conectarse a MT5 en vivo.
    - Calcular el SHA-256 del archivo original para la trazabilidad.
    """

    @abstractmethod
    def parse(
        self,
        file_path: str,
        strategy_id: str,
        version: str,
        is_period: BacktestPeriod,
        oos_period: BacktestPeriod,
    ) -> BacktestReport:
        """
        Lee un archivo de informe, extrae métricas, normaliza valores y
        devuelve un objeto `BacktestReport` listo para el BacktestValidator.

        Args:
            file_path:   Ruta local absoluta al archivo del informe.
            strategy_id: Identificador único de la estrategia.
            version:     Versión de la estrategia (ej. "1.0").
            is_period:   Período In-Sample del backtest.
            oos_period:  Período Out-of-Sample del backtest.

        Returns:
            Un objeto `BacktestReport` Pydantic válido y completo.

        Raises:
            ParserLanguageError:  Si el informe no está en inglés.
            ParserStructureError: Si el DOM/estructura del archivo no es reconocible.
            FileNotFoundError:    Si el archivo no existe en la ruta indicada.
        """
        ...  # pragma: no cover

    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calcula el hash SHA-256 del archivo original para garantizar
        la trazabilidad criptográfica entre el informe físico y el BacktestReport.

        Args:
            file_path: Ruta local absoluta al archivo.

        Returns:
            Cadena hexadecimal con el hash SHA-256 del archivo.
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
