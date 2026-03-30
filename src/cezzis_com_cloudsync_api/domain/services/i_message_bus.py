"""Message bus interface for pub/sub operations."""

from abc import ABC, abstractmethod
from typing import Any


class IMessageBus(ABC):
    """Interface for message bus operations (pub/sub via Dapr)."""

    @abstractmethod
    async def publish_event_async(
        self,
        event: dict[str, Any],
        message_label: str,
        config_name: str,
        topic_name: str | None = None,
        content_type: str | None = "application/json",
        correlation_id: str | None = None,
    ) -> None:
        """Publish an event to a topic.

        Args:
            event: The event data to publish.
            message_label: The message label/subject used for routing.
            config_name: The Dapr pub/sub component name.
            topic_name: The topic to publish to. Defaults to config_name if not provided.
            content_type: The content type of the message. Defaults to "application/json".
            correlation_id: The correlation ID for tracing. Defaults to a new UUID if not provided.
        """
        ...
