"""Message bus implementation using Dapr pub/sub."""

import logging
import uuid
from typing import Any

from cezzis_com_cloudsync_api.domain.services.i_message_bus import IMessageBus
from cezzis_com_cloudsync_api.infrastructure.dapr.dapr_client import DaprClient

logger = logging.getLogger("message_bus")


class MessageBus(IMessageBus):
    """Message bus implementation using Dapr pub/sub."""

    def __init__(self, dapr_client: DaprClient):
        """Initialize the message bus.

        Args:
            dapr_client: The Dapr client for API interactions.
        """
        self._dapr_client = dapr_client

    async def publish_event_async(
        self,
        event: dict[str, Any],
        message_label: str,
        config_name: str,
        topic_name: str | None = None,
        content_type: str | None = "application/json",
        correlation_id: str | None = None,
        raw_payload: bool = False,
    ) -> None:
        """Publish an event to a topic.

        Args:
            event: The event data to publish.
            message_label: The message label/subject used for routing.
            config_name: The Dapr pub/sub component name.
            topic_name: The topic to publish to. Defaults to config_name if not provided.
            content_type: The content type of the message. Defaults to "application/json".
            correlation_id: The correlation ID for tracing. Defaults to a new UUID if not provided.
            raw_payload: Whether to publish as raw payload without CloudEvent wrapping. Defaults to False.
        """
        useable_topic_name = topic_name or config_name
        useable_correlation_id = correlation_id or str(uuid.uuid4())

        logger.info(
            "Publishing event to %s/%s [label=%s, correlationId=%s]",
            config_name,
            useable_topic_name,
            message_label,
            useable_correlation_id,
        )

        metadata = {
            "CorrelationId": useable_correlation_id,
            "ContentType": content_type or "application/json",
            "Label": message_label,
            "routingKey": message_label,
        }

        if raw_payload:
            metadata["rawPayload"] = "true"

        await self._dapr_client.publish_event(
            pubsub_name=config_name,
            topic_name=useable_topic_name,
            data=event,
            metadata=metadata,
        )

        logger.info("Message published [label=%s]", message_label)
