"""Test cases for MessageBus."""

from datetime import UTC, datetime, timedelta
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
            config_name="pubsub-cocktail-updates-sync-topic",
            topic_name="cocktail-updates",
        )

        dapr_client.publish_event.assert_called_once()
        call_kwargs = dapr_client.publish_event.call_args[1]
        assert call_kwargs["pubsub_name"] == "pubsub-cocktail-updates-sync-topic"
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

    @pytest.mark.anyio
    async def test_publish_event_formats_scheduled_enqueue_time_as_rfc3339_utc(self):
        """Test that scheduled enqueue metadata uses RFC3339 UTC formatting."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)

        await bus.publish_event_async(
            event={"key": "val"},
            message_label="label",
            config_name="config",
            scheduledEnqueueTimeUtc=datetime(
                2024,
                1,
                2,
                16,
                4,
                5,
                987654,
                tzinfo=UTC,
            )
            - timedelta(hours=1),
        )

        metadata = dapr_client.publish_event.call_args[1]["metadata"]
        assert metadata["ScheduledEnqueueTimeUtc"] == "2024-01-02T15:04:05Z"

    @pytest.mark.anyio
    async def test_publish_event_raises_for_blank_pubsub_name(self):
        """Test that blank pubsub names fail before calling the Dapr SDK."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)

        with pytest.raises(ValueError, match="pubsub component name"):
            await bus.publish_event_async(
                event={"key": "val"},
                message_label="label",
                config_name="   ",
                topic_name="my-topic",
            )

        dapr_client.publish_event.assert_not_called()

    @pytest.mark.anyio
    async def test_publish_event_strips_pubsub_and_topic_names(self):
        """Test that publish uses trimmed pubsub and topic names."""
        dapr_client = MagicMock()
        dapr_client.publish_event = AsyncMock()

        bus = MessageBus(dapr_client)

        await bus.publish_event_async(
            event={"key": "val"},
            message_label="label",
            config_name=" my-config ",
            topic_name=" my-topic ",
        )

        call_kwargs = dapr_client.publish_event.call_args[1]
        assert call_kwargs["pubsub_name"] == "my-config"
        assert call_kwargs["topic_name"] == "my-topic"
