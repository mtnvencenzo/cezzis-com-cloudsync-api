"""Test cases for IntegrationsRouter."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.routing import APIRoute
from httpx import ASGITransport, AsyncClient

from cezzis_com_cloudsync_api.apis.integrations import IntegrationsRouter
from cezzis_com_cloudsync_api.application.behaviors.error_handling.exception_types import ForbiddenException

BINDING_NAME = "bindings-cocktail-updates-queue"


def _create_router(
    mediator: MagicMock | None = None,
    app_options: MagicMock | None = None,
    message_bus: MagicMock | None = None,
) -> IntegrationsRouter:
    """Helper to create an IntegrationsRouter with mocked dependencies."""
    if mediator is None:
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)
    if app_options is None:
        app_options = MagicMock()
        app_options.cocktail_update_sync_dapr_input_binding = BINDING_NAME
        app_options.cocktail_update_sync_label = "cocktail-updated"
        app_options.cocktail_update_sync_dapr_binding = "pubsub-cocktail-updates-sync-topic"
        app_options.cocktail_update_sync_topic = "cocktail-updates"
        app_options.cocktail_update_sync_dapr_deadletter_pubsub = "pubsub-deadletter-topic"
    if message_bus is None:
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock()
    return IntegrationsRouter(mediator=mediator, app_options=app_options, message_bus=message_bus)


def _create_app(router: IntegrationsRouter) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


class TestIntegrationsRouter:
    """Test cases for IntegrationsRouter."""

    def test_init_registers_post_route(self):
        """Test that initialization registers POST route for the binding endpoint."""
        router = _create_router()
        paths = [r.path for r in router.routes if isinstance(r, APIRoute)]
        assert f"/{BINDING_NAME}" in paths

    def test_init_registers_options_route(self):
        """Test that initialization registers OPTIONS route for the binding endpoint."""
        router = _create_router()
        methods = []
        for r in router.routes:
            if isinstance(r, APIRoute) and r.path == f"/{BINDING_NAME}":
                methods.extend(r.methods or [])
        assert "OPTIONS" in methods

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_success(self):
        """Test successful cocktail update sync returns empty JSON."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123", "action": "updated"},
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}
        mediator.send_async.assert_called_once()

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_handler_returns_false(self):
        """Test that handler returning False still returns 200 (ack)."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=False)

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_handler_raises_value_error(self):
        """Test that a ValueError still returns 200 (ack)."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(side_effect=ValueError("bad data"))

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_handler_raises_unexpected(self):
        """Test that an unexpected exception still returns 200 (ack)."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(side_effect=RuntimeError("boom"))

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_forwards_raw_payload(self):
        """Test that the raw body is forwarded as the raw payload."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        payload = {"cocktailId": "abc-123", "action": "updated", "nested": {"key": "val"}}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(f"/{BINDING_NAME}", json=payload)

        event = mediator.send_async.call_args[0][0]
        assert event.raw_payload == payload

    @pytest.mark.anyio
    async def test_options_handler_returns_empty_json(self):
        """Test that OPTIONS handler returns empty JSON with 200 status."""
        router = _create_router()
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.options(f"/{BINDING_NAME}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_success_does_not_call_message_bus(self):
        """Test that a successful processing does not call message bus from the router."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock()

        router = _create_router(mediator=mediator, message_bus=message_bus)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_200_OK
        message_bus.publish_event_async.assert_not_called()
