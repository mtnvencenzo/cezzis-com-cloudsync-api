"""Test cases for IntegrationsRouter."""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.routing import APIRoute
from httpx import ASGITransport, AsyncClient

from cezzis_com_cloudsync_api.apis.integrations import IntegrationsRouter
from cezzis_com_cloudsync_api.application.behaviors.error_handling.exception_types import ForbiddenException
from cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_updated_scheduled_event import (
    CocktailUpdatedScheduledEvent,
    CocktailUpdatedScheduledEventCommandHandler,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_updated_scheduling_event import (
    CocktailUpdatedSchedulingEvent,
    CocktailUpdatedSchedulingEventCommandHandler,
)

BINDING_NAME = "bindings-cocktail-updates-queue"
SCHEDULED_BINDING_NAME = "bindings-cocktail-updates-scheduled-queue"


def _create_app_options() -> MagicMock:
    app_options = MagicMock()
    app_options.cocktail_update_sync_dapr_input_binding = BINDING_NAME
    app_options.cocktail_update_sync_scheduled_dapr_input_binding = SCHEDULED_BINDING_NAME
    app_options.cocktail_update_sync_label = "cocktail-updated"
    app_options.cocktail_update_sync_dapr_binding = "pubsub-cocktail-updates-sync-topic"
    app_options.cocktail_update_sync_topic = "cocktail-updates"
    app_options.cocktail_update_sync_dapr_deadletter_pubsub = "pubsub-sync-deadletter-topic"
    app_options.cocktail_update_sync_dapr_deadletter_label = "cocktail-updated"
    app_options.cocktail_update_sync_dapr_deadletter_topic = "cocktail-updates-dlx"
    app_options.cocktail_update_sync_scheduled_dapr_deadletter_pubsub = "pubsub-sync-scheduled-deadletter-topic"
    app_options.cocktail_update_sync_scheduled_dapr_deadletter_label = "cocktail-updated-scheduled"
    app_options.cocktail_update_sync_scheduled_dapr_deadletter_topic = "cocktail-updates-scheduled-dlx"
    app_options.cocktail_update_scheduling_sync_label = "cocktail-updates-scheduled"
    app_options.cocktail_update_scheduling_sync_dapr_binding = "pubsub-cocktail-updates-scheduling-topic"
    app_options.cocktail_update_scheduling_sync_topic = "cocktail-updates-scheduling"
    return app_options


class _DispatchingMediator:
    def __init__(self, handlers_by_event_type: dict[type, object]) -> None:
        self.handlers_by_event_type = handlers_by_event_type

    async def send_async(self, event: object) -> bool:
        handler = self.handlers_by_event_type[type(event)]
        return await handler.handle(event)


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
        app_options = _create_app_options()
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

    def test_init_registers_scheduled_post_route(self):
        """Test that initialization registers POST route for the scheduled binding endpoint."""
        router = _create_router()
        paths = [r.path for r in router.routes if isinstance(r, APIRoute)]
        assert f"/{SCHEDULED_BINDING_NAME}" in paths

    def test_init_registers_scheduled_options_route(self):
        """Test that initialization registers OPTIONS route for the scheduled binding endpoint."""
        router = _create_router()
        methods = []
        for r in router.routes:
            if isinstance(r, APIRoute) and r.path == f"/{SCHEDULED_BINDING_NAME}":
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

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_scheduled_sync_success(self):
        """Test successful scheduled cocktail update sync returns empty JSON."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{SCHEDULED_BINDING_NAME}",
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
    async def test_cocktail_updated_scheduled_sync_handler_returns_false(self):
        """Test that scheduled handler returning False still returns 200 (ack)."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=False)

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{SCHEDULED_BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_scheduled_sync_handler_raises_unexpected(self):
        """Test that an unexpected exception on the scheduled endpoint still returns 200 (ack)."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(side_effect=RuntimeError("boom"))

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/{SCHEDULED_BINDING_NAME}",
                json={"cocktailId": "abc-123"},
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_scheduled_sync_forwards_raw_payload(self):
        """Test that the scheduled raw body is forwarded as the raw payload."""
        mediator = MagicMock()
        mediator.send_async = AsyncMock(return_value=True)

        router = _create_router(mediator=mediator)
        app = _create_app(router)

        payload = {"cocktailId": "abc-123", "action": "updated", "nested": {"key": "val"}}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(f"/{SCHEDULED_BINDING_NAME}", json=payload)

        event = mediator.send_async.call_args[0][0]
        assert event.raw_payload == payload

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_sync_routes_to_scheduling_handler_and_publishes(self):
        """Test the inbound cocktail update route dispatches to the scheduling handler and publishes."""
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock()
        app_options = _create_app_options()
        handler = CocktailUpdatedSchedulingEventCommandHandler(message_bus=message_bus, app_options=app_options)
        mediator = _DispatchingMediator({CocktailUpdatedSchedulingEvent: handler})

        router = _create_router(mediator=mediator, app_options=app_options, message_bus=message_bus)
        app = _create_app(router)

        payload = {"cocktailId": "abc-123", "action": "updated"}
        fixed_now = datetime(2024, 1, 2, 15, 4, 5, tzinfo=UTC)

        with patch(
            "cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_updated_scheduling_event.datetime"
        ) as mocked_datetime:
            mocked_datetime.now.return_value = fixed_now

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(f"/{BINDING_NAME}", json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}
        message_bus.publish_event_async.assert_called_once_with(
            event=payload,
            message_label="cocktail-updates-scheduled",
            config_name="pubsub-cocktail-updates-scheduling-topic",
            topic_name="cocktail-updates-scheduling",
            content_type="application/json",
            raw_payload=True,
            scheduledEnqueueTimeUtc=datetime(2024, 1, 3, 0, 0, 0, tzinfo=UTC),
        )

    @pytest.mark.anyio
    @patch(
        "cezzis_com_cloudsync_api.apis.integrations.dapr_app_token_authorization",
        lambda func: func,
    )
    async def test_cocktail_updated_scheduled_sync_routes_to_handler_and_publishes(self):
        """Test the scheduled inbound route dispatches to the final sync handler and publishes."""
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock()
        app_options = _create_app_options()
        handler = CocktailUpdatedScheduledEventCommandHandler(message_bus=message_bus, app_options=app_options)
        mediator = _DispatchingMediator({CocktailUpdatedScheduledEvent: handler})

        router = _create_router(mediator=mediator, app_options=app_options, message_bus=message_bus)
        app = _create_app(router)

        payload = {"cocktailId": "abc-123", "action": "updated"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/{SCHEDULED_BINDING_NAME}", json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {}
        message_bus.publish_event_async.assert_called_once_with(
            event=payload,
            message_label="cocktail-updated",
            config_name="pubsub-cocktail-updates-sync-topic",
            topic_name="cocktail-updates",
            content_type="application/json",
            raw_payload=True,
        )
