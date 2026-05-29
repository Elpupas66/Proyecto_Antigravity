"""
core/parsers/parser_factory.py
-------------------------------
Factory para instanciar el parser correcto según el tipo de archivo.
Fase 4.1: Solo MT5 HTML está implementado. Extensible para fases futuras.

Sin red. Sin MT5 en vivo. Sin base de datos. Sin ejecución real.
"""

import os

from core.parsers.base_parser import BaseParser, ParserStructureError
from core.parsers.mt5_html_parser import MT5HtmlParser


class ParserFactory:
    """
    Orquestador que inspecciona el archivo y retorna la instancia del parser
    adecuado. En la Fase 4.1, únicamente MT5 HTML en inglés está soportado.

    Uso:
        parser = ParserFactory.get_parser("ruta/al/informe.html")
        report  = parser.parse(file_path, strategy_id, version, is_period, oos_period)
    """

    @staticmethod
    def get_parser(file_path: str) -> BaseParser:
        """
        Analiza la extensión del archivo y devuelve la instancia del parser
        correspondiente.

        Args:
            file_path: Ruta local absoluta al archivo del informe.

        Returns:
            Una instancia de BaseParser (en esta fase: MT5HtmlParser).

        Raises:
            ParserStructureError: Si el formato del archivo no está soportado.
            FileNotFoundError:    Si el archivo no existe.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"[ParserFactory] Archivo no encontrado: {file_path}"
            )

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext in (".html", ".htm"):
            return MT5HtmlParser()

        # Formatos fuera de alcance de la Fase 4.1
        if ext == ".xml":
            raise ParserStructureError(
                "[ParserFactory] Formato XML no soportado en la Fase 4.1. "
                "Solo MT5 HTML en inglés está autorizado en esta fase."
            )
        if ext == ".csv":
            raise ParserStructureError(
                "[ParserFactory] Formato CSV no soportado en la Fase 4.1. "
                "Solo MT5 HTML en inglés está autorizado en esta fase."
            )

        raise ParserStructureError(
            f"[ParserFactory] Formato de archivo no reconocido: '{ext}'. "
            "Solo archivos .html / .htm de MT5 en inglés están soportados."
        )
