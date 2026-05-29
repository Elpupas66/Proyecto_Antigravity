"""
tests/test_mt5_html_parser.py
-------------------------------
Suite de pruebas unitarias TDD para la Fase 4.1: Backtest Import Layer.
Cubre los 5 tests obligatorios del plan de implementación aprobado,
más el test de compatibilidad con BacktestValidator.

Sin red. Sin MT5 en vivo. Sin base de datos. Sin ejecución real.
"""

import hashlib
import os
from datetime import datetime, timezone

import pytest

from core.parsers.base_parser import ParserLanguageError, ParserStructureError
from core.parsers.mt5_html_parser import MT5HtmlParser
from core.parsers.parser_factory import ParserFactory
from core.strategy_models import (
    AssetClass,
    BacktestPeriod,
    BacktestReport,
    BiasChecklist,
    MarketRegimeChecklist,
    StrategyClassification,
    StrategyMetadata,
)
from core.backtest_validator import BacktestValidator, MetricThresholds

# ─── RUTAS A LOS ARCHIVOS MOCK ───────────────────────────────────────────────
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_VALID_EN_HTML = os.path.join(_DATA_DIR, "sample_mt5_report_en.html")
_INVALID_ES_HTML = os.path.join(_DATA_DIR, "sample_mt5_report_es.html")

# ─── PERÍODOS MOCK REUTILIZABLES ─────────────────────────────────────────────
_IS_PERIOD = BacktestPeriod(
    start_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
    end_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
    label="IS",
)
_OOS_PERIOD = BacktestPeriod(
    start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
    end_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    label="OOS",
)


# ═══════════════════════════════════════════════════════════════════════════════
# T1 – PARSEO CORRECTO DE UN HTML MT5 VÁLIDO EN INGLÉS
# ═══════════════════════════════════════════════════════════════════════════════
class TestT1ParseValidEnglishHtml:
    """
    Verifica que el parser extrae correctamente las métricas del HTML mock
    en inglés y las mapea con exactitud al objeto BacktestReport.
    """

    def setup_method(self):
        self.parser = MT5HtmlParser()
        self.report = self.parser.parse(
            file_path=_VALID_EN_HTML,
            strategy_id="ST-TEST-001",
            version="1.0",
            is_period=_IS_PERIOD,
            oos_period=_OOS_PERIOD,
        )

    def test_returns_backtest_report_instance(self):
        """El objeto retornado debe ser una instancia de BacktestReport."""
        assert isinstance(self.report, BacktestReport)

    def test_strategy_id_injected_correctly(self):
        assert self.report.strategy_id == "ST-TEST-001"

    def test_version_injected_correctly(self):
        assert self.report.version == "1.0"

    def test_data_source_is_mt5_html(self):
        assert self.report.data_source == "MetaTrader 5 HTML"

    def test_total_trades_extracted(self):
        """El mock tiene 300 trades."""
        assert self.report.total_trades == 300

    def test_profit_factor_extracted(self):
        """El mock tiene Profit Factor 2.61."""
        assert self.report.profit_factor_oos == pytest.approx(2.61, abs=0.01)

    def test_max_drawdown_pct_extracted(self):
        """El mock tiene Maximal drawdown (8.45%)."""
        assert self.report.max_drawdown_pct == pytest.approx(8.45, abs=0.01)

    def test_recovery_factor_extracted(self):
        """El mock tiene Recovery Factor 6.58."""
        assert self.report.recovery_factor == pytest.approx(6.58, abs=0.01)

    def test_sharpe_ratio_extracted(self):
        """El mock tiene Sharpe Ratio 1.87."""
        assert self.report.sharpe_ratio == pytest.approx(1.87, abs=0.01)

    def test_expectancy_extracted(self):
        """El mock tiene Expected Payoff 5.83."""
        assert self.report.expectancy == pytest.approx(5.83, abs=0.01)

    def test_average_win_extracted(self):
        """El mock tiene Average profit trade 86.96."""
        assert self.report.average_win == pytest.approx(86.96, abs=0.01)

    def test_average_loss_is_positive_absolute(self):
        """average_loss debe ser positivo (valor absoluto de la pérdida media)."""
        assert self.report.average_loss > 0

    def test_win_rate_extracted(self):
        """El mock tiene Profit trades (76.67%)."""
        assert self.report.win_rate == pytest.approx(76.67, abs=0.01)

    def test_max_losing_streak_extracted(self):
        """El mock tiene Maximum consecutive losses 3."""
        assert self.report.max_losing_streak == 3

    def test_sortino_and_complex_metrics_are_zero(self):
        """Métricas pendientes del Metrics Engine deben ser 0.0 por defecto."""
        assert self.report.sortino_ratio == 0.0
        assert self.report.risk_of_ruin_pct == 0.0
        assert self.report.max_daily_loss_pct == 0.0
        assert self.report.simultaneous_exposure_pct == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# T2 – RECHAZO DE INFORME NO INGLÉS
# ═══════════════════════════════════════════════════════════════════════════════
class TestT2RejectNonEnglishReport:
    """
    Verifica que el parser lanza ParserLanguageError cuando el HTML contiene
    indicadores de idioma distinto al inglés.
    """

    def test_spanish_report_raises_language_error(self):
        parser = MT5HtmlParser()
        with pytest.raises(ParserLanguageError):
            parser.parse(
                file_path=_INVALID_ES_HTML,
                strategy_id="ST-TEST-ES",
                version="1.0",
                is_period=_IS_PERIOD,
                oos_period=_OOS_PERIOD,
            )

    def test_error_message_mentions_english_requirement(self):
        parser = MT5HtmlParser()
        with pytest.raises(ParserLanguageError, match="English"):
            parser.parse(
                file_path=_INVALID_ES_HTML,
                strategy_id="ST-TEST-ES",
                version="1.0",
                is_period=_IS_PERIOD,
                oos_period=_OOS_PERIOD,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# T3 – RECHAZO DE HTML INVÁLIDO (NO MT5)
# ═══════════════════════════════════════════════════════════════════════════════
class TestT3RejectInvalidDom:
    """
    Verifica que el parser lanza ParserStructureError cuando el HTML no
    corresponde a un informe MetaTrader 5.
    """

    def test_random_html_raises_structure_error(self, tmp_path):
        """Un HTML genérico sin etiquetas MT5 debe ser rechazado."""
        non_mt5_html = tmp_path / "generic_page.html"
        non_mt5_html.write_text(
            "<html><body><h1>Welcome to my website</h1><p>Hello world.</p></body></html>",
            encoding="utf-8",
        )
        parser = MT5HtmlParser()
        with pytest.raises(ParserStructureError):
            parser.parse(
                file_path=str(non_mt5_html),
                strategy_id="ST-INVALID",
                version="1.0",
                is_period=_IS_PERIOD,
                oos_period=_OOS_PERIOD,
            )

    def test_missing_file_raises_file_not_found(self):
        """Un archivo inexistente debe lanzar FileNotFoundError."""
        parser = MT5HtmlParser()
        with pytest.raises(FileNotFoundError):
            parser.parse(
                file_path="/ruta/que/no/existe/informe.html",
                strategy_id="ST-NOFILE",
                version="1.0",
                is_period=_IS_PERIOD,
                oos_period=_OOS_PERIOD,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# T4 – TRAZABILIDAD SHA-256
# ═══════════════════════════════════════════════════════════════════════════════
class TestT4Sha256Traceability:
    """
    Verifica que el hash SHA-256 almacenado en raw_metrics["source_file_hash"]
    coincide matemáticamente con el hash calculado directamente sobre el archivo.
    """

    def test_hash_in_raw_metrics_matches_file(self):
        parser = MT5HtmlParser()
        report = parser.parse(
            file_path=_VALID_EN_HTML,
            strategy_id="ST-HASH-TEST",
            version="1.0",
            is_period=_IS_PERIOD,
            oos_period=_OOS_PERIOD,
        )

        # Calcular el hash directamente sobre el archivo
        sha256 = hashlib.sha256()
        with open(_VALID_EN_HTML, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        expected_hash = sha256.hexdigest()

        assert report.raw_metrics is not None
        assert "source_file_hash" in report.raw_metrics
        assert report.raw_metrics["source_file_hash"] == expected_hash

    def test_hash_is_64_char_hex_string(self):
        """SHA-256 produce exactamente 64 caracteres hexadecimales."""
        parser = MT5HtmlParser()
        report = parser.parse(
            file_path=_VALID_EN_HTML,
            strategy_id="ST-HASH-LEN",
            version="1.0",
            is_period=_IS_PERIOD,
            oos_period=_OOS_PERIOD,
        )
        h = report.raw_metrics["source_file_hash"]
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ═══════════════════════════════════════════════════════════════════════════════
# T5 – EL FACTORY RETORNA EL PARSER CORRECTO
# ═══════════════════════════════════════════════════════════════════════════════
class TestT5FactoryReturnsCorrectParser:
    """
    Verifica que ParserFactory.get_parser() retorna la instancia adecuada
    y rechaza formatos fuera del alcance de la Fase 4.1.
    """

    def test_factory_returns_mt5_html_parser_for_html(self):
        parser = ParserFactory.get_parser(_VALID_EN_HTML)
        assert isinstance(parser, MT5HtmlParser)

    def test_factory_raises_for_xml(self, tmp_path):
        xml_file = tmp_path / "report.xml"
        xml_file.write_text("<root></root>", encoding="utf-8")
        with pytest.raises(ParserStructureError, match="XML"):
            ParserFactory.get_parser(str(xml_file))

    def test_factory_raises_for_csv(self, tmp_path):
        csv_file = tmp_path / "report.csv"
        csv_file.write_text("col1,col2\n1,2", encoding="utf-8")
        with pytest.raises(ParserStructureError, match="CSV"):
            ParserFactory.get_parser(str(csv_file))

    def test_factory_raises_for_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            ParserFactory.get_parser("/no/existe/report.html")


# ═══════════════════════════════════════════════════════════════════════════════
# T6 – COMPATIBILIDAD CON BacktestValidator
# ═══════════════════════════════════════════════════════════════════════════════
class TestT6BacktestValidatorCompatibility:
    """
    Verifica que el BacktestReport generado por el parser es directamente
    compatible con el BacktestValidator de la Fase 3.2.
    Confirma que approved_for_real es siempre False en toda la cadena.
    """

    def setup_method(self):
        parser = MT5HtmlParser()
        self.report = parser.parse(
            file_path=_VALID_EN_HTML,
            strategy_id="ST-COMPAT-001",
            version="1.0",
            is_period=_IS_PERIOD,
            oos_period=_OOS_PERIOD,
        )
        self.metadata = StrategyMetadata(
            strategy_id="ST-COMPAT-001",
            name="Antigravity Test Strategy",
            version="1.0",
            config_hash="abc123def456",
            author_or_source="Test Suite",
            asset="EURUSD",
            asset_class=AssetClass.FOREX,
            timeframe="H1",
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        self.bias = BiasChecklist(
            look_ahead_bias_checked=True,
            survivorship_bias_checked=True,
            data_snooping_checked=True,
            overfitting_checked=True,
            curve_fitting_checked=True,
            selection_bias_checked=True,
            period_bias_checked=True,
            realistic_costs_checked=True,
            realistic_execution_checked=True,
            spread_slippage_checked=True,
        )
        self.regime = MarketRegimeChecklist(
            trend_tested=True,
            range_tested=True,
            high_volatility_tested=True,
            low_volatility_tested=True,
            session_variability_tested=True,
        )

    def test_validator_accepts_parsed_report(self):
        """El BacktestValidator no debe lanzar ninguna excepción con el reporte parseado."""
        validator = BacktestValidator()
        evaluation = validator.validate(
            metadata=self.metadata,
            report=self.report,
            bias_checklist=self.bias,
            market_regime_checklist=self.regime,
        )
        assert evaluation is not None

    def test_approved_for_real_is_always_false(self):
        """
        ENCLAVAMIENTO DE SEGURIDAD CRÍTICO:
        approved_for_real DEBE ser False en todo momento,
        desde el parser hasta el resultado final de la evaluación.
        """
        validator = BacktestValidator()
        evaluation = validator.validate(
            metadata=self.metadata,
            report=self.report,
            bias_checklist=self.bias,
            market_regime_checklist=self.regime,
        )
        assert evaluation.approved_for_real is False

    def test_evaluation_returns_valid_classification(self):
        """La evaluación debe retornar una clasificación válida del enum."""
        validator = BacktestValidator()
        evaluation = validator.validate(
            metadata=self.metadata,
            report=self.report,
            bias_checklist=self.bias,
            market_regime_checklist=self.regime,
        )
        assert evaluation.classification in list(StrategyClassification)

    def test_full_pipeline_produces_strategy_evaluation(self):
        """
        Test de integración completo: MT5 HTML → Parser → BacktestReport → Validator → Evaluation.
        Verifica que toda la cadena funciona sin errores.
        """
        # 1. Factory
        parser = ParserFactory.get_parser(_VALID_EN_HTML)
        assert isinstance(parser, MT5HtmlParser)

        # 2. Parse
        report = parser.parse(
            file_path=_VALID_EN_HTML,
            strategy_id="ST-PIPELINE-001",
            version="1.0",
            is_period=_IS_PERIOD,
            oos_period=_OOS_PERIOD,
        )
        assert isinstance(report, BacktestReport)
        # BacktestReport NO contiene approved_for_real (ese campo pertenece a
        # StrategyEvaluation). Verificamos que efectivamente no existe.
        assert not hasattr(report, "approved_for_real")

        # 3. Validate
        validator = BacktestValidator()
        evaluation = validator.validate(
            metadata=self.metadata,
            report=report,
            bias_checklist=self.bias,
            market_regime_checklist=self.regime,
        )

        # 4. Verificaciones finales de seguridad
        assert evaluation.approved_for_real is False
        assert evaluation.classification in list(StrategyClassification)
        assert evaluation.evaluator == "BacktestValidator-Determinista"
