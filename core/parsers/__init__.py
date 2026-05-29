"""
core/parsers/__init__.py
------------------------
Paquete de parsers de informes de backtesting.
Fase 4.1: Import Layer — MT5 HTML únicamente.

Sin red, sin MT5 en vivo, sin base de datos, sin ejecución real.
"""

from core.parsers.base_parser import BaseParser, ParserLanguageError, ParserStructureError
from core.parsers.mt5_html_parser import MT5HtmlParser
from core.parsers.parser_factory import ParserFactory

__all__ = [
    "BaseParser",
    "ParserLanguageError",
    "ParserStructureError",
    "MT5HtmlParser",
    "ParserFactory",
]
