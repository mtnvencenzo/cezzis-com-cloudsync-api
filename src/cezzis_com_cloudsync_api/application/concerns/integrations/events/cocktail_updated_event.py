"""CocktailUpdatedEvent for syncing cocktail data with the embedding system."""

import logging

from injector import inject
from mediatr import GenericQuery, Mediator
from pydantic import Field

from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent
from cezzis_com_cloudsync_api.domain.services.i_message_bus import IMessageBus
from cezzis_com_cloudsync_api.infrastructure.clients.cocktails_api.cocktail_api import CocktailModel

logger = logging.getLogger("account_owned_profile_updated_event")


class CocktailUpdatedEvent(IIntegrationEvent, GenericQuery[bool]):
    """Event triggered when a cocktail is updated and needs to sync with the embedding system."""

    data: list[CocktailModel] = Field(...)


@Mediator.handler
class CocktailUpdatedEventCommandHandler:
    """Handler for CocktailUpdatedEvent - syncs cocktail data with the embedding system."""

    @inject
    def __init__(self, message_bus: IMessageBus):
        """Initialize the handler."""
        self.logger = logging.getLogger("cocktail_updated_event_command_handler")
        self.message_bus = message_bus

    async def handle(self, event: CocktailUpdatedEvent) -> bool:
        """Sync the cocktail updated event."""

        await self.message_bus.publish_event_async(
            event=event.model_dump(mode="json", by_alias=True),
            message_label="cocktail.updated",
            config_name="pubsub-cocktail-updates-topic",
            topic_name="cocktail-updates-topic",
            content_type="application/json",
        )

        return True
