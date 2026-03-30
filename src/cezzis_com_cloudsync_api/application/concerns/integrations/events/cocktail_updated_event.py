"""CocktailUpdatedEvent for syncing cocktail data with the embedding system."""

import logging
from typing import Any

from injector import inject
from mediatr import GenericQuery, Mediator
from pydantic import Field

from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent
from cezzis_com_cloudsync_api.domain.config.app_options import AppOptions
from cezzis_com_cloudsync_api.domain.services.i_message_bus import IMessageBus

logger = logging.getLogger("cocktail_updated_event")


class CocktailUpdatedEvent(IIntegrationEvent, GenericQuery[bool]):
    """Event triggered when a cocktail is updated and needs to sync with the embedding system."""

    raw_payload: dict[str, Any] = Field(...)


@Mediator.handler
class CocktailUpdatedEventCommandHandler:
    """Handler for CocktailUpdatedEvent - syncs cocktail data with the embedding system."""

    @inject
    def __init__(self, message_bus: IMessageBus, app_options: AppOptions) -> None:
        """Initialize the handler."""
        self.logger = logging.getLogger("cocktail_updated_event_command_handler")
        self.message_bus = message_bus
        self.app_options = app_options

    async def handle(self, event: CocktailUpdatedEvent) -> bool:
        """Sync the cocktail updated event."""

        await self.message_bus.publish_event_async(
            event=event.raw_payload,
            message_label=self.app_options.cocktail_update_sync_label,
            config_name=self.app_options.cocktail_update_sync_dapr_binding,
            topic_name=self.app_options.cocktail_update_sync_topic,
            content_type="application/json",
            raw_payload=True,
        )

        return True
