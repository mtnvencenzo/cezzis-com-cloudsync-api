"""ChangeAccountOwnedPasswordEvent for initiating password change flow with identity provider."""

import logging

from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent
from cezzis_com_cloudsync_api.domain.services.i_auth0_management_client import IAuth0ManagementClient
from injector import inject
from mediatr import GenericQuery, Mediator
from pydantic import EmailStr, Field, field_validator

logger = logging.getLogger("change_account_owned_password_event")


class ChangeAccountOwnedPasswordEvent(IIntegrationEvent, GenericQuery[bool]):
    """Event triggered when a password change is requested for an account."""

    owned_account_id: str = Field(...)
    owned_account_subject_id: str = Field(...)
    email: EmailStr = Field(...)

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


@Mediator.handler
class ChangeAccountOwnedPasswordEventHandler:
    """Handler for ChangeAccountOwnedPasswordEvent - initiates password change flow with Auth0."""

    @inject
    def __init__(self, auth0_management_client: IAuth0ManagementClient):
        """Initialize the handler.

        Args:
            auth0_management_client: The Auth0 management client for user operations.
        """
        self._auth0_management_client = auth0_management_client

    async def handle(self, event: ChangeAccountOwnedPasswordEvent) -> bool:
        """Handle the password change event.

        Args:
            event: The password change event.

        Returns:
            True if the password change flow was initiated successfully.

        Raises:
            ValueError: If the event is invalid.
            RuntimeError: If the operation fails.
        """
        if not event:
            raise ValueError("Event must not be None")

        try:
            await self._auth0_management_client.initiate_change_password_flow(
                email=event.email,
            )

            logger.info(
                "Successfully initiated password change flow for account %s (subject: %s)",
                event.owned_account_id,
                event.owned_account_subject_id,
            )
            return True

        except Exception as ex:
            logger.error(
                "Failed to initiate password change flow for account %s: %s",
                event.owned_account_id,
                str(ex),
            )
            raise
