"""CocktailUpdatedEvent for syncing cocktail data with the embedding system."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from injector import inject
from mediatr import GenericQuery, Mediator
from pydantic import Field

from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent
from cezzis_com_cloudsync_api.domain.config.app_options import AppOptions
from cezzis_com_cloudsync_api.domain.services.i_message_bus import IMessageBus


class CocktailUpdatedSchedulingEvent(IIntegrationEvent, GenericQuery[bool]):
    """Event triggered when a cocktail is updated and needs to sync with the embedding system."""

    raw_payload: dict[str, Any] = Field(...)


@Mediator.handler
class CocktailUpdatedSchedulingEventCommandHandler:
    """Handler for CocktailUpdatedSchedulingEvent - syncs cocktail data with the embedding system."""

    @inject
    def __init__(self, message_bus: IMessageBus, app_options: AppOptions) -> None:
        """Initialize the handler."""
        self.logger = logging.getLogger("cocktail_updated_scheduling_event_command_handler")
        self.message_bus = message_bus
        self.app_options = app_options

    async def handle(self, event: CocktailUpdatedSchedulingEvent) -> bool:
        """Sync the cocktail updated event."""

        # scheduling for tomorrow morning at 00:00 UTC to allow for any potential updates that come in throughout the day to be batched together, and to ensure the cocktail data is fully updated in the source system before we attempt to sync it with the embedding system
        midnightTomorrow = (
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        ).astimezone(UTC)

        try:
            await self.message_bus.publish_event_async(
                event=event.raw_payload,
                message_label=self.app_options.cocktail_update_scheduling_sync_label,
                config_name=self.app_options.cocktail_update_scheduling_sync_dapr_binding,
                topic_name=self.app_options.cocktail_update_scheduling_sync_topic,
                content_type="application/json",
                raw_payload=True,
                scheduledEnqueueTimeUtc=midnightTomorrow,
            )

            return True
        except Exception as ex:
            if self.app_options.cocktail_update_sync_dapr_deadletter_pubsub:
                self.logger.exception(
                    "Handler returned failure for cocktail_updated_scheduling event, dead-lettering message",
                    exc_info=ex,
                )
                await self._dead_letter(event.raw_payload)
                return False
            else:
                raise

    async def _dead_letter(self, body: dict[str, Any]) -> None:
        """Publish a failed message to the dead-letter exchange.

        Uses the same routing key (message label) so the dead-letter exchange
        can route the message to the appropriate dead-letter queue.

        Args:
            body: The original message body to dead-letter. If None, a marker payload is sent.
        """
        try:
            await self.message_bus.publish_event_async(
                event=body,
                message_label=self.app_options.cocktail_update_sync_dapr_deadletter_label,
                config_name=self.app_options.cocktail_update_sync_dapr_deadletter_pubsub,
                topic_name=self.app_options.cocktail_update_sync_dapr_deadletter_topic,
                content_type="application/json",
                raw_payload=True,
            )
            self.logger.info("Message published to dead-letter exchange")
        except Exception as dlx_err:
            self.logger.critical("Failed to dead-letter message — message will be lost: %s", str(dlx_err))
