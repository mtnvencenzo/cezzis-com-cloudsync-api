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


DEADLETTER_PUBSUB = "pubsub-deadletter-topic"
DEADLETTER_LABEL = "cocktail-updated"
DEADLETTER_TOPIC = "cocktail-updates-dlx"


def _create_app_options() -> MagicMock:
    """Helper to create a mocked AppOptions with all needed fields."""
    app_options = MagicMock()
    app_options.cocktail_update_sync_label = "cocktail-updates"
    app_options.cocktail_update_sync_dapr_binding = "pubsub-cocktail-updates-topic"
    app_options.cocktail_update_sync_topic = "cocktail-updates"
    app_options.cocktail_update_sync_dapr_deadletter_pubsub = DEADLETTER_PUBSUB
    app_options.cocktail_update_sync_dapr_deadletter_label = DEADLETTER_LABEL
    app_options.cocktail_update_sync_dapr_deadletter_topic = DEADLETTER_TOPIC
    return app_options


class TestCocktailUpdatedEventCommandHandler:
    """Test cases for CocktailUpdatedEventCommandHandler."""

    @pytest.mark.anyio
    async def test_handle_publishes_raw_payload(self):
        """Test that handle publishes the raw payload via message bus."""
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock()
        app_options = _create_app_options()

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
    async def test_handle_publish_failure_dead_letters_and_returns_false(self):
        """Test that publish failure triggers dead-letter and returns False."""
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock(side_effect=[RuntimeError("publish failed"), None])
        app_options = _create_app_options()

        handler = CocktailUpdatedEventCommandHandler(
            message_bus=message_bus,
            app_options=app_options,
        )

        payload = {"cocktailId": "abc-123"}
        event = CocktailUpdatedEvent(raw_payload=payload)
        result = await handler.handle(event)

        assert result is False
        assert message_bus.publish_event_async.call_count == 2

        # Second call should be the dead-letter publish
        dlx_call = message_bus.publish_event_async.call_args_list[1]
        assert dlx_call[1]["config_name"] == DEADLETTER_PUBSUB
        assert dlx_call[1]["message_label"] == DEADLETTER_LABEL
        assert dlx_call[1]["topic_name"] == DEADLETTER_TOPIC
        assert dlx_call[1]["event"] == payload
        assert dlx_call[1]["raw_payload"] is True

    @pytest.mark.anyio
    async def test_handle_dead_letter_failure_still_returns_false(self):
        """Test that if dead-lettering itself fails, handler still returns False without raising."""
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock(
            side_effect=[RuntimeError("publish failed"), RuntimeError("dlx also failed")]
        )
        app_options = _create_app_options()

        handler = CocktailUpdatedEventCommandHandler(
            message_bus=message_bus,
            app_options=app_options,
        )

        event = CocktailUpdatedEvent(raw_payload={"key": "val"})
        result = await handler.handle(event)

        assert result is False
        assert message_bus.publish_event_async.call_count == 2

    @pytest.mark.anyio
    async def test_handle_success_does_not_dead_letter(self):
        """Test that successful publish does not trigger dead-letter."""
        message_bus = MagicMock()
        message_bus.publish_event_async = AsyncMock()
        app_options = _create_app_options()

        handler = CocktailUpdatedEventCommandHandler(
            message_bus=message_bus,
            app_options=app_options,
        )

        event = CocktailUpdatedEvent(raw_payload={"cocktailId": "abc-123"})
        result = await handler.handle(event)

        assert result is True
        message_bus.publish_event_async.assert_called_once()
