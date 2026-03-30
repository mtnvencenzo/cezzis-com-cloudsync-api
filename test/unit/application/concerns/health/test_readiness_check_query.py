"""Test cases for ReadinessCheckQueryHandler."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from cezzis_com_cloudsync_api.application.concerns.health.queries.readiness_check_query import (
    ReadinessCheckQuery,
    ReadinessCheckQueryHandler,
)


def _make_dapr_options(**overrides) -> MagicMock:
    opts = MagicMock()
    opts.http_endpoint = overrides.get("http_endpoint", "http://localhost:3500")
    opts.dapr_api_token = overrides.get("dapr_api_token", "")
    return opts


class TestReadinessCheckQueryHandler:
    """Test cases for ReadinessCheckQueryHandler."""

    @pytest.mark.anyio
    async def test_healthy_when_dapr_returns_204(self):
        """Test that handler returns healthy when Dapr healthz returns 204."""
        opts = _make_dapr_options()
        handler = ReadinessCheckQueryHandler(dapr_options=opts)

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_class.return_value = mock_client

            result = await handler.handle(ReadinessCheckQuery())

        assert result.status == "healthy"
        assert result.details is not None
        assert result.details["dapr"] == "healthy"

    @pytest.mark.anyio
    async def test_unhealthy_when_dapr_returns_non_204(self):
        """Test that handler returns unhealthy when Dapr healthz returns non-204."""
        opts = _make_dapr_options()
        handler = ReadinessCheckQueryHandler(dapr_options=opts)

        mock_response = MagicMock()
        mock_response.status_code = 503

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_class.return_value = mock_client

            result = await handler.handle(ReadinessCheckQuery())

        assert result.status == "unhealthy"
        assert result.details is not None
        assert "unhealthy" in result.details["dapr"]

    @pytest.mark.anyio
    async def test_sends_dapr_api_token_header_when_configured(self):
        """Test that the dapr-api-token header is sent when token is configured."""
        opts = _make_dapr_options(dapr_api_token="my-token")
        handler = ReadinessCheckQueryHandler(dapr_options=opts)

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_class.return_value = mock_client

            await handler.handle(ReadinessCheckQuery())

            call_kwargs = mock_client.get.call_args[1]
            assert call_kwargs["headers"]["dapr-api-token"] == "my-token"

    @pytest.mark.anyio
    async def test_dapr_exception_within_grace_period_reports_degraded(self):
        """Test that connection failure within grace period reports degraded."""
        opts = _make_dapr_options()
        handler = ReadinessCheckQueryHandler(dapr_options=opts)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_class.return_value = mock_client

            # Within grace period (_start_time is set at module load, so this should be within 120s)
            result = await handler.handle(ReadinessCheckQuery())

        assert result.details is not None
        assert "degraded" in result.details["dapr"]

    @pytest.mark.anyio
    async def test_returns_version(self):
        """Test that the response includes the version."""
        opts = _make_dapr_options()
        handler = ReadinessCheckQueryHandler(dapr_options=opts)

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_class.return_value = mock_client

            result = await handler.handle(ReadinessCheckQuery())

        assert result.version is not None
