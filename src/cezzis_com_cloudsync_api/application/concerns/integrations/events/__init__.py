"""Integration events for Dapr input bindings."""

from cezzis_com_cloudsync_api.application.concerns.integrations.events.account_owned_profile_updated_event import (
    AccountOwnedProfileUpdatedEvent,
    AccountOwnedProfileUpdatedEventHandler,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events.change_account_owned_email_event import (
    ChangeAccountOwnedEmailEvent,
    ChangeAccountOwnedEmailEventHandler,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events.change_account_owned_password_event import (
    ChangeAccountOwnedPasswordEvent,
    ChangeAccountOwnedPasswordEventHandler,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_rating_event import (
    CocktailRatingEvent,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_recommendation_email_event import (
    CocktailRecommendationEmailEvent,
    CocktailRecommendationEmailEventHandler,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent

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
