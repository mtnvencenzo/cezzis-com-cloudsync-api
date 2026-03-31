"""Test cases for MessageBus."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cezzis_com_cloudsync_api.infrastructure.message_bus import MessageBus


class TestMessageBus:
    """Test cases for MessageBus."""

    @pytest.mark.anyio
    async def test_publish_event_calls_dapr_client(self):
        """Test that publish_event_async delegates to DaprClient.publish_event."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)
        event = {"cocktailId": "abc-123"}

        await bus.publish_event_async(
            event=event,
            message_label="cocktail-updates",
            config_name="pubsub-cocktail-updates-topic",
            topic_name="cocktail-updates",
        )

        dapr_client.publish_event.assert_called_once()
        call_kwargs = dapr_client.publish_event.call_args[1]
        assert call_kwargs["pubsub_name"] == "pubsub-cocktail-updates-topic"
        assert call_kwargs["topic_name"] == "cocktail-updates"
        assert call_kwargs["data"] == event

    @pytest.mark.anyio
    async def test_publish_event_uses_config_name_as_topic_when_none(self):
        """Test that topic defaults to config_name when topic_name is None."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)

        await bus.publish_event_async(
            event={"key": "val"},
            message_label="label",
            config_name="my-config",
            topic_name=None,
        )

        call_kwargs = dapr_client.publish_event.call_args[1]
        assert call_kwargs["topic_name"] == "my-config"

    @pytest.mark.anyio
    async def test_publish_event_includes_metadata(self):
        """Test that metadata includes CorrelationId, ContentType, Label, routingKey."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)

        await bus.publish_event_async(
            event={"key": "val"},
            message_label="my-label",
            config_name="my-config",
            topic_name="my-topic",
            content_type="application/json",
        )

        metadata = dapr_client.publish_event.call_args[1]["metadata"]
        assert metadata["ContentType"] == "application/json"
        assert metadata["Label"] == "my-label"
        assert metadata["routingKey"] == "my-label"
        assert "CorrelationId" in metadata

    @pytest.mark.anyio
    async def test_publish_event_raw_payload_adds_metadata(self):
        """Test that raw_payload=True adds rawPayload metadata."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)

        await bus.publish_event_async(
            event={"key": "val"},
            message_label="label",
            config_name="config",
            raw_payload=True,
        )

        metadata = dapr_client.publish_event.call_args[1]["metadata"]
        assert metadata["rawPayload"] == "true"

    @pytest.mark.anyio
    async def test_publish_event_no_raw_payload_by_default(self):
        """Test that rawPayload is not in metadata by default."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)

        await bus.publish_event_async(
            event={"key": "val"},
            message_label="label",
            config_name="config",
        )

        metadata = dapr_client.publish_event.call_args[1]["metadata"]
        assert "rawPayload" not in metadata

    @pytest.mark.anyio
    async def test_publish_event_uses_provided_correlation_id(self):
        """Test that a provided correlation_id is used."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)

        await bus.publish_event_async(
            event={"key": "val"},
            message_label="label",
            config_name="config",
            correlation_id="my-corr-id",
        )

        metadata = dapr_client.publish_event.call_args[1]["metadata"]
        assert metadata["CorrelationId"] == "my-corr-id"
