"""
core/parsers/mt5_html_parser.py
--------------------------------
Implementación concreta del parser para informes HTML de MetaTrader 5 en inglés.
Fase 4.1: Import Layer — Única implementación autorizada en esta fase.

Responsabilidades:
  - Leer archivos HTML locales generados por MT5.
  - Validar que el idioma sea inglés (English).
  - Validar que la estructura sea reconocible como un informe MT5.
  - Extraer métricas directamente del DOM.
  - Calcular el hash SHA-256 del archivo original.
  - Construir y retornar un objeto BacktestReport Pydantic.

Sin red. Sin MT5 en vivo. Sin base de datos. Sin ejecución real.
"""

import re
from typing import Optional

from bs4 import BeautifulSoup

from core.parsers.base_parser import BaseParser, ParserLanguageError, ParserStructureError
from core.strategy_models import BacktestPeriod, BacktestReport

# ─── ANCLAS DE IDENTIDAD MT5 ─────────────────────────────────────────────────
# Cadenas que DEBEN existir en el HTML para confirmar que es un informe MT5 en inglés.
_MT5_ENGLISH_ANCHORS = [
    "Profit factor",
    "Total trades",
    "Maximal drawdown",
]

# Cadenas que, si se encuentran, indican que el informe NO está en inglés.
_NON_ENGLISH_INDICATORS = [
    "Factor de beneficio",
    "Total de transacciones",
    "Caída máxima",
    "Facteur de profit",
    "Gewinnfaktor",
]


class MT5HtmlParser(BaseParser):
    """
    Parser determinista para informes HTML de MetaTrader 5 generados en inglés.

    Lanza:
        ParserLanguageError:  Si el informe está en un idioma distinto al inglés.
        ParserStructureError: Si el HTML no corresponde a un informe MT5.
        FileNotFoundError:    Si el archivo no existe.
    """

    def parse(
        self,
        file_path: str,
        strategy_id: str,
        version: str,
        is_period: BacktestPeriod,
        oos_period: BacktestPeriod,
    ) -> BacktestReport:
        """
        Parsea un informe HTML de MT5 en inglés y retorna un BacktestReport.
        """
        # ── 1. LEER ARCHIVO LOCAL ─────────────────────────────────────────────
        raw_html = self._read_file(file_path)

        # ── 2. CALCULAR HASH SHA-256 ANTES DE CUALQUIER MODIFICACIÓN ──────────
        source_hash = self._calculate_file_hash(file_path)

        # ── 3. CONSTRUIR DOM ──────────────────────────────────────────────────
        soup = BeautifulSoup(raw_html, "lxml")
        full_text = soup.get_text()

        # ── 4. VALIDAR IDIOMA ─────────────────────────────────────────────────
        self._validate_language(full_text)

        # ── 5. VALIDAR ESTRUCTURA MT5 ─────────────────────────────────────────
        self._validate_mt5_structure(full_text)

        # ── 6. EXTRAER MÉTRICAS ───────────────────────────────────────────────
        metrics = self._extract_metrics(soup, full_text)

        # ── 7. CONSTRUIR Y RETORNAR BacktestReport ────────────────────────────
        return BacktestReport(
            strategy_id=strategy_id,
            version=version,
            data_source="MetaTrader 5 HTML",
            in_sample_period=is_period,
            out_of_sample_period=oos_period,
            total_trades=metrics["total_trades"],
            profit_factor_is=metrics["profit_factor_is"],
            profit_factor_oos=metrics["profit_factor_oos"],
            max_drawdown_pct=metrics["max_drawdown_pct"],
            recovery_factor=metrics["recovery_factor"],
            sharpe_ratio=metrics["sharpe_ratio"],
            sortino_ratio=0.0,           # Requiere Metrics Engine (Fase futura)
            expectancy=metrics["expectancy"],
            average_win=metrics["average_win"],
            average_loss=metrics["average_loss"],
            win_rate=metrics["win_rate"],
            max_losing_streak=metrics["max_losing_streak"],
            max_daily_loss_pct=0.0,      # Requiere análisis trade-by-trade (Fase futura)
            simultaneous_exposure_pct=0.0,  # Requiere análisis temporal (Fase futura)
            risk_of_ruin_pct=0.0,        # Requiere Monte Carlo (Fase futura)
            average_slippage=0.0,        # No disponible en cabecera HTML
            average_trade_cost=0.0,      # No disponible en cabecera HTML
            raw_metrics={
                "source_file_hash": source_hash,
                "parser": "MT5HtmlParser-V1",
                **metrics,
            },
        )

    # ─── MÉTODOS PRIVADOS ─────────────────────────────────────────────────────

    def _read_file(self, file_path: str) -> str:
        """Lee el archivo HTML local. Lanza FileNotFoundError si no existe."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"[MT5HtmlParser] Archivo no encontrado: {file_path}"
            )

    def _validate_language(self, text: str) -> None:
        """
        Rechaza el informe si contiene indicadores de idiomas distintos al inglés,
        o si no contiene los anclas obligatorias en inglés.
        """
        for indicator in _NON_ENGLISH_INDICATORS:
            if indicator in text:
                raise ParserLanguageError(
                    f"[MT5HtmlParser] Informe rechazado: idioma no inglés detectado "
                    f"(encontrado: '{indicator}'). "
                    "All MT5 reports must be generated in English."
                )

    def _validate_mt5_structure(self, text: str) -> None:
        """
        Verifica que el HTML contenga las cadenas ancla de un informe MT5 válido.
        Si alguna falta, el DOM es irreconocible y se lanza ParserStructureError.
        """
        missing = [anchor for anchor in _MT5_ENGLISH_ANCHORS if anchor not in text]
        if missing:
            raise ParserStructureError(
                f"[MT5HtmlParser] Estructura MT5 no reconocida. "
                f"Etiquetas faltantes: {missing}. "
                "El archivo puede no ser un informe de MetaTrader 5."
            )

    def _extract_metrics(self, soup: BeautifulSoup, text: str) -> dict:
        """
        Extrae las métricas disponibles directamente del DOM HTML del informe MT5.
        Para métricas no encontradas, asigna valores por defecto seguros (0.0 / 0).
        """
        return {
            "total_trades": self._extract_int(text, "Total trades"),
            "profit_factor_is": self._extract_float(text, "Profit factor"),
            "profit_factor_oos": self._extract_float(text, "Profit factor"),
            "max_drawdown_pct": self._extract_drawdown_pct(text),
            "recovery_factor": self._extract_float(text, "Recovery factor"),
            "sharpe_ratio": self._extract_float(text, "Sharpe ratio"),
            "expectancy": self._extract_float(text, "Expected payoff"),
            "average_win": self._extract_float(text, "Average profit trade"),
            "average_loss": self._extract_float_abs(text, "Average loss trade"),
            "win_rate": self._extract_win_rate(text),
            "max_losing_streak": self._extract_int(text, "Maximum consecutive losses"),
        }

    def _extract_float(self, text: str, label: str) -> float:
        """
        Busca en el texto la línea que contiene el 'label' de MT5 y extrae
        el valor numérico inmediatamente siguiente.
        """
        pattern = re.compile(
            re.escape(label) + r"[^\d\-]*?([\-]?\d[\d\s]*[\.,]?\d*)",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return self._to_float(match.group(1))
        return 0.0

    def _extract_float_abs(self, text: str, label: str) -> float:
        """Igual que _extract_float pero devuelve el valor absoluto (para pérdidas)."""
        return abs(self._extract_float(text, label))

    def _extract_int(self, text: str, label: str) -> int:
        """Extrae un entero tras el label indicado."""
        pattern = re.compile(
            re.escape(label) + r"[^\d]*?(\d+)",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return int(match.group(1).replace(" ", ""))
        return 0

    def _extract_drawdown_pct(self, text: str) -> float:
        """
        Extrae el drawdown relativo (%) de la línea 'Maximal drawdown'.
        MT5 lo reporta en formato: 'Maximal drawdown   1234.56 (12.34%)'
        """
        pattern = re.compile(
            r"Maximal drawdown[^\d]*[\d\s\.,]+\(([\d\.,]+)%\)",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return self._to_float(match.group(1))
        # Fallback: intentar extraer cualquier número tras "Maximal drawdown"
        return self._extract_float(text, "Maximal drawdown")

    def _extract_win_rate(self, text: str) -> float:
        """
        Extrae el Win Rate del campo 'Profit trades (% of total)'.
        MT5 lo reporta como: 'Profit trades (% of total)   230 (76.67%)'
        Retorna el valor como decimal (ej. 76.67 → 76.67, NO 0.7667).
        Usa re.DOTALL para capturar el patrón aunque BeautifulSoup
        introduzca saltos de línea entre el label y el valor.
        """
        pattern = re.compile(
            r"Profit trades[\s\S]*?\((\d+[\.,]\d+)%\)",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return self._to_float(match.group(1))
        return 0.0

    @staticmethod
    def _to_float(value: str) -> float:
        """Normaliza un string numérico (comas/espacios) a float."""
        try:
            return float(value.replace(" ", "").replace(",", "."))
        except (ValueError, AttributeError):
            return 0.0
