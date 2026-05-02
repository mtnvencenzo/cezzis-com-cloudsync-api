"""Test cases for DaprClient."""

import json
from unittest.mock import MagicMock, patch

import pytest

from cezzis_com_cloudsync_api.infrastructure.dapr.dapr_client import DaprClient


def _make_dapr_options(**overrides) -> MagicMock:
    opts = MagicMock()
    opts.grpc_endpoint = overrides.get("grpc_endpoint", "localhost:50001")
    opts.dapr_api_token = overrides.get("dapr_api_token", "")
    return opts


class TestDaprClient:
    """Test cases for DaprClient."""

    def test_init_stores_endpoint(self):
        """Test that the gRPC endpoint is stored from options."""
        opts = _make_dapr_options(grpc_endpoint="myhost:12345")
        client = DaprClient(opts)
        assert client._grpc_endpoint == "myhost:12345"

    def test_get_headers_callback_returns_token(self):
        """Test that headers callback returns the dapr-api-token."""
        opts = _make_dapr_options(dapr_api_token="my-secret-token")
        client = DaprClient(opts)
        headers = client._get_headers_callback()
        assert headers == {"dapr-api-token": "my-secret-token"}

    def test_create_client_uses_headers_callback_and_interceptor_when_token_set(self):
        """Test that _create_client configures both HTTP and gRPC auth when token is set."""
        opts = _make_dapr_options(dapr_api_token="tok")
        client = DaprClient(opts)

        with patch(
            "cezzis_com_cloudsync_api.infrastructure.dapr.dapr_client.DaprClientInterceptor"
        ) as mock_interceptor:
            with patch("cezzis_com_cloudsync_api.infrastructure.dapr.dapr_client.OfficialDaprClient") as mock_cls:
                interceptor_instance = MagicMock()
                mock_interceptor.return_value = interceptor_instance

                client._create_client()

                mock_interceptor.assert_called_once_with([("dapr-api-token", "tok")])
            mock_cls.assert_called_once_with(
                address="localhost:50001",
                headers_callback=client._get_headers_callback,
                interceptors=[interceptor_instance],
            )

    def test_create_client_no_headers_callback_when_no_token(self):
        """Test that _create_client passes no auth hooks when no token."""
        opts = _make_dapr_options(dapr_api_token="")
        client = DaprClient(opts)

        with patch("cezzis_com_cloudsync_api.infrastructure.dapr.dapr_client.OfficialDaprClient") as mock_cls:
            client._create_client()
            mock_cls.assert_called_once_with(
                address="localhost:50001",
                headers_callback=None,
                interceptors=None,
            )

    @pytest.mark.anyio
    async def test_publish_event_calls_sdk(self):
        """Test that publish_event calls the official SDK publish_event."""
        opts = _make_dapr_options()
        client = DaprClient(opts)

        mock_sdk_client = MagicMock()
        mock_sdk_client.__enter__ = MagicMock(return_value=mock_sdk_client)
        mock_sdk_client.__exit__ = MagicMock(return_value=False)

        with patch.object(client, "_create_client", return_value=mock_sdk_client):
            await client.publish_event(
                pubsub_name="my-pubsub",
                topic_name="my-topic",
                data={"key": "value"},
                metadata={"Label": "test"},
            )

        mock_sdk_client.publish_event.assert_called_once_with(
            pubsub_name="my-pubsub",
            topic_name="my-topic",
            data=json.dumps({"key": "value"}),
            data_content_type="application/json",
            publish_metadata={"Label": "test"},
        )

    @pytest.mark.anyio
    async def test_publish_event_uses_empty_metadata_when_none(self):
        """Test that publish_event uses empty dict when metadata is None."""
        opts = _make_dapr_options()
        client = DaprClient(opts)

        mock_sdk_client = MagicMock()
        mock_sdk_client.__enter__ = MagicMock(return_value=mock_sdk_client)
        mock_sdk_client.__exit__ = MagicMock(return_value=False)

        with patch.object(client, "_create_client", return_value=mock_sdk_client):
            await client.publish_event(
                pubsub_name="ps",
                topic_name="tp",
                data={"k": "v"},
                metadata=None,
            )

        call_kwargs = mock_sdk_client.publish_event.call_args[1]
        assert call_kwargs["publish_metadata"] == {}
