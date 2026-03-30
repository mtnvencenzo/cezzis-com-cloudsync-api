"""CocktailRatingEvent for publishing cocktail ratings to the cocktails API."""

from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent
from pydantic import Field, field_validator


class CocktailRatingEvent(IIntegrationEvent):
    """Event for publishing cocktail rating updates to the cocktails service.

    This event is published by the RateCocktailCommand and UnRateCocktailCommand
    to notify the cocktails-api of rating changes so it can update aggregate ratings.
    """

    owned_account_id: str = Field(...)
    owned_account_subject_id: str = Field(...)
    cocktail_id: str = Field(...)
    stars: int = Field(..., ge=1, le=5)
    decrement_rating: bool = Field(default=False)

    @field_validator("owned_account_id", mode="before")
    @classmethod
    def validate_owned_account_id(cls, v: str) -> str:
        """Validate that owned_account_id is not empty and has minimum length."""
        if not v or len(v.strip()) < 36:
            raise ValueError("owned_account_id is required and must be at least 36 characters")
        return v

    @field_validator("owned_account_subject_id", mode="before")
    @classmethod
    def validate_owned_account_subject_id(cls, v: str) -> str:
        """Validate that owned_account_subject_id is not empty."""
        if not v or not v.strip():
            raise ValueError("owned_account_subject_id is required")
        return v

    @field_validator("cocktail_id", mode="before")
    @classmethod
    def validate_cocktail_id(cls, v: str) -> str:
        """Validate that cocktail_id is not empty."""
        if not v or not v.strip():
            raise ValueError("cocktail_id is required")
        return v
