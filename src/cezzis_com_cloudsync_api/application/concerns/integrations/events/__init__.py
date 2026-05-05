"""Integration events for Dapr input bindings."""

from cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_updated_scheduled_event import (
    CocktailUpdatedScheduledEvent,
    CocktailUpdatedScheduledEventCommandHandler,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_updated_scheduling_event import (
    CocktailUpdatedSchedulingEvent,
    CocktailUpdatedSchedulingEventCommandHandler,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent

# Backward-compatible aliases for the pre-scheduling rename.
CocktailUpdatedEvent = CocktailUpdatedSchedulingEvent
CocktailUpdatedEventCommandHandler = CocktailUpdatedSchedulingEventCommandHandler

__all__ = [
    "IIntegrationEvent",
    "CocktailUpdatedEvent",
    "CocktailUpdatedEventCommandHandler",
    "CocktailUpdatedSchedulingEvent",
    "CocktailUpdatedSchedulingEventCommandHandler",
    "CocktailUpdatedScheduledEvent",
    "CocktailUpdatedScheduledEventCommandHandler",
]
