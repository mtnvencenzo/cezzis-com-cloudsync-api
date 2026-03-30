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


def _create_router(mediator: MagicMock | None = None, app_options: MagicMock | None = None) -> IntegrationsRouter:
    """Helper to create an IntegrationsRouter with mocked dependencies."""
    if mediator is None:
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)
    if app_options is None:
        app_options = MagicMock()
        app_options.cocktail_update_sync_dapr_input_binding = BINDING_NAME
        app_options.cocktail_update_sync_label = "cocktail-updates"
        app_options.cocktail_update_sync_dapr_binding = "pubsub-cocktail-updates-topic"
        app_options.cocktail_update_sync_topic = "cocktail-updates"
    return IntegrationsRouter(mediator=mediator, app_options=app_options)


def _create_app(router: IntegrationsRouter) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


class TestIntegrationsRouter:
    """Test cases for IntegrationsRouter."""

    def test_init_registers_post_and_options_routes(self):
        """Test that initialization registers POST and OPTIONS routes for the binding."""
        router = _create_router()
        paths = [r.path for r in router.routes if isinstance(r, APIRoute)]
        assert f"/{BINDING_NAME}" in paths

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_success(self):
        """Test successful cocktail update sync returns 200."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)

        # Need to recreate router after patching the decorator
        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123", "action": "updated"},
            )

        assert response.status_code == status.HTTP_200_OK
        mediator.send_async.assert_called_once()

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_handler_returns_false(self):
        """Test that handler returning False yields 500."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=False)

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["title"] == "Processing Failed"

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_handler_raises_value_error(self):
        """Test that a ValueError results in 400."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(side_effect=ValueError("bad data"))

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["title"] == "Validation Error"

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_handler_raises_unexpected(self):
        """Test that an unexpected exception results in 500."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(side_effect=RuntimeError("boom"))

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["title"] == "Internal Server Error"

    @pytest.mark.anyio
    async def test_options_handler_returns_200(self):
        """Test OPTIONS handler returns 200."""
        router = _create_router()
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.options(f"/{BINDING_NAME}")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_forwards_raw_payload(self):
        """Test that the raw payload dict is forwarded as-is."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        payload = {"cocktailId": "abc-123", "action": "updated", "nested": {"key": "val"}}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(f"/{BINDING_NAME}", json=payload)

        event = mediator.send_async.call_args[0][0]
        assert event.raw_payload == payload
