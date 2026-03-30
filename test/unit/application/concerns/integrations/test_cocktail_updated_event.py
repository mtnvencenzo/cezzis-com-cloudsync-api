"""Test cases for CocktailUpdatedEvent and CocktailUpdatedEventCommandHandler."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_updated_event import (
    CocktailUpdatedEvent,
    CocktailUpdatedEventCommandHandler,
)


class TestCocktailUpdatedEvent:
    """Test cases for CocktailUpdatedEvent model."""

    def test_create_with_raw_payload(self):
        """Test creating event with raw payload."""
        payload = {"cocktailId": "abc-123", "action": "updated"}
        event = CocktailUpdatedEvent(raw_payload=payload)
        assert event.raw_payload == payload

    def test_raw_payload_preserves_nested_data(self):
        """Test that nested structures are preserved."""
        payload = {"data": {"id": 1, "tags": ["a", "b"]}, "meta": {"source": "test"}}
        event = CocktailUpdatedEvent(raw_payload=payload)
        assert event.raw_payload == payload

    def test_raw_payload_is_required(self):
        """Test that raw_payload is a required field."""
        with pytest.raises(Exception):  # noqa: B017
            CocktailUpdatedEvent(raw_payload=None)  # type: ignore[arg-type]

    def test_no_extra_base_fields(self):
        """Test that no wasted base fields (correlation_id, id, creation_date) are generated."""
        payload = {"key": "value"}
        event = CocktailUpdatedEvent(raw_payload=payload)
        field_names = set(type(event).model_fields.keys())
        assert "correlation_id" not in field_names
        assert "creation_date" not in field_names


class TestCocktailUpdatedEventCommandHandler:
    """Test cases for CocktailUpdatedEventCommandHandler."""

    @pytest.mark.anyio
    async def test_handle_publishes_raw_payload(self):
        """Test that handle publishes the raw payload via message bus."""
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock()

        app_options = MagicMock()
        app_options.cocktail_update_sync_label = "cocktail-updates"
        app_options.cocktail_update_sync_dapr_binding = "pubsub-cocktail-updates-topic"
        app_options.cocktail_update_sync_topic = "cocktail-updates"

        handler = CocktailUpdatedEventCommandHandler(
            message_bus=message_bus,
            app_options=app_options,
        )

        payload = {"cocktailId": "abc-123", "action": "updated"}
        event = CocktailUpdatedEvent(raw_payload=payload)
        result = await handler.handle(event)

        assert result is True
        message_bus.publish_event_async.assert_called_once_with(
            event=payload,
            message_label="cocktail-updates",
            config_name="pubsub-cocktail-updates-topic",
            topic_name="cocktail-updates",
            content_type="application/json",
            raw_payload=True,
        )

    @pytest.mark.anyio
    async def test_handle_propagates_exception(self):
        """Test that exceptions from message bus propagate."""
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock(side_effect=RuntimeError("publish failed"))

        app_options = MagicMock()
        app_options.cocktail_update_sync_label = "label"
        app_options.cocktail_update_sync_dapr_binding = "binding"
        app_options.cocktail_update_sync_topic = "topic"

        handler = CocktailUpdatedEventCommandHandler(
            message_bus=message_bus,
            app_options=app_options,
        )

        event = CocktailUpdatedEvent(raw_payload={"key": "val"})

        with pytest.raises(RuntimeError, match="publish failed"):
            await handler.handle(event)
