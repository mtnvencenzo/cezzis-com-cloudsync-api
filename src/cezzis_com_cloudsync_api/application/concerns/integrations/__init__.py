"""Integrations concerns for handling Dapr integration events."""

from cezzis_com_cloudsync_api.application.concerns.integrations.events import (
    AccountOwnedProfileUpdatedEvent,
    AccountOwnedProfileUpdatedEventHandler,
    ChangeAccountOwnedEmailEvent,
    ChangeAccountOwnedEmailEventHandler,
    ChangeAccountOwnedPasswordEvent,
    ChangeAccountOwnedPasswordEventHandler,
    CocktailRatingEvent,
    CocktailRecommendationEmailEvent,
    CocktailRecommendationEmailEventHandler,
    IIntegrationEvent,
)

__all__ = [
    "IIntegrationEvent",
    "AccountOwnedProfileUpdatedEvent",
    "AccountOwnedProfileUpdatedEventHandler",
    "ChangeAccountOwnedEmailEvent",
    "ChangeAccountOwnedEmailEventHandler",
    "ChangeAccountOwnedPasswordEvent",
    "ChangeAccountOwnedPasswordEventHandler",
    "CocktailRatingEvent",
    "CocktailRecommendationEmailEvent",
    "CocktailRecommendationEmailEventHandler",
]
