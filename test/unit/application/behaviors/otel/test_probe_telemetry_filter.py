import logging

import pytest
from opentelemetry.context import _SUPPRESS_INSTRUMENTATION_KEY, get_value
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from cezzis_com_cloudsync_api.application.behaviors.otel.probe_telemetry_filter import (
    ProbeLoggingFilter,
    ProbeTelemetryMiddleware,
    _is_probe_request,
)


class TestProbeLoggingFilter:
    """Test cases for ProbeLoggingFilter."""

    def test_allows_records_outside_probe_context(self):
        """Log records are allowed when not in a probe request context."""
        filt = ProbeLoggingFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        assert filt.filter(record) is True

    def test_drops_info_records_inside_probe_context(self):
        """INFO log records are suppressed when inside a probe request context."""
        filt = ProbeLoggingFilter()
        token = _is_probe_request.set(True)
        try:
            record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
            assert filt.filter(record) is False
        finally:
            _is_probe_request.reset(token)

    def test_drops_debug_records_inside_probe_context(self):
        """DEBUG log records are suppressed when inside a probe request context."""
        filt = ProbeLoggingFilter()
        token = _is_probe_request.set(True)
        try:
            record = logging.LogRecord("test", logging.DEBUG, "", 0, "msg", (), None)
            assert filt.filter(record) is False
        finally:
            _is_probe_request.reset(token)

    def test_allows_warning_records_inside_probe_context(self):
        """WARNING log records are allowed through even during a probe request."""
        filt = ProbeLoggingFilter()
        token = _is_probe_request.set(True)
        try:
            record = logging.LogRecord("test", logging.WARNING, "", 0, "msg", (), None)
            assert filt.filter(record) is True
        finally:
            _is_probe_request.reset(token)

    def test_allows_error_records_inside_probe_context(self):
        """ERROR log records are allowed through even during a probe request."""
        filt = ProbeLoggingFilter()
        token = _is_probe_request.set(True)
        try:
            record = logging.LogRecord("test", logging.ERROR, "", 0, "msg", (), None)
            assert filt.filter(record) is True
        finally:
            _is_probe_request.reset(token)


class TestProbeTelemetryMiddleware:
    """Test cases for ProbeTelemetryMiddleware."""

    def _build_app(self, handler):
        app = Starlette(
            routes=[
                Route("/v1/liveness", handler),
                Route("/v1/readiness", handler),
                Route("/v1/other", handler),
            ]
        )
        app.add_middleware(ProbeTelemetryMiddleware)
        return app

    def test_probe_path_sets_logging_context_flag(self):
        """Probe paths should set _is_probe_request so logs are suppressed."""
        captured = {}

        async def handler(request: Request):
            captured["is_probe"] = _is_probe_request.get()
            return PlainTextResponse("ok")

        client = TestClient(self._build_app(handler))
        client.get("/v1/liveness")
        assert captured["is_probe"] is True

    def test_probe_path_sets_otel_suppression_flag(self):
        """Probe paths should set the OTel suppress-instrumentation flag."""
        captured = {}

        async def handler(request: Request):
            captured["suppressed"] = get_value(_SUPPRESS_INSTRUMENTATION_KEY)
            return PlainTextResponse("ok")

        client = TestClient(self._build_app(handler))
        client.get("/v1/readiness")
        assert captured["suppressed"] is True

    def test_non_probe_path_does_not_set_flags(self):
        """Non-probe paths should not set any suppression flags."""
        captured = {}

        async def handler(request: Request):
            captured["is_probe"] = _is_probe_request.get()
            captured["suppressed"] = get_value(_SUPPRESS_INSTRUMENTATION_KEY)
            return PlainTextResponse("ok")

        client = TestClient(self._build_app(handler))
        client.get("/v1/other")
        assert captured["is_probe"] is False
        assert captured["suppressed"] is None

    def test_flags_are_reset_after_probe_request(self):
        """Suppression flags should be cleaned up after the request completes."""

        async def handler(request: Request):
            return PlainTextResponse("ok")

        client = TestClient(self._build_app(handler))
        client.get("/v1/liveness")

        # After the request, the outer context should be clean
        assert _is_probe_request.get() is False
        assert get_value(_SUPPRESS_INSTRUMENTATION_KEY) is None
