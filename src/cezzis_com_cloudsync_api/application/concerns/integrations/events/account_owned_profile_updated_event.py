"""AccountOwnedProfileUpdatedEvent for syncing account profile with identity provider."""

import logging
from typing import Any

from cezzis_com_cloudsync_api.application.concerns.integrations.events.account_model import AccountModel
from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent
from cezzis_com_cloudsync_api.domain.services.i_auth0_management_client import IAuth0ManagementClient
from injector import inject
from mediatr import GenericQuery, Mediator
from pydantic import Field, field_validator

logger = logging.getLogger("account_owned_profile_updated_event")


class AccountOwnedProfileUpdatedEvent(IIntegrationEvent, GenericQuery[bool]):
    """Event triggered when an account profile is updated and needs to sync with the identity provider."""

    owned_account: AccountModel = Field(...)

    @field_validator("owned_account", mode="before")
    @classmethod
    def validate_owned_account(cls, v: Any) -> AccountModel:
        """Validate that owned_account is not None."""
        if v is None:
            raise ValueError("owned_account is required")
        return v


@Mediator.handler
class AccountOwnedProfileUpdatedEventHandler:
    """Handler for AccountOwnedProfileUpdatedEvent - syncs account profile with Auth0."""

    @inject
    def __init__(self, auth0_management_client: IAuth0ManagementClient):
        """Initialize the handler.

        Args:
            auth0_management_client: The Auth0 management client for user operations.
        """
        self._auth0_management_client = auth0_management_client

    async def handle(self, event: AccountOwnedProfileUpdatedEvent) -> bool:
        """Handle the account profile updated event.

        Args:
            event: The account profile updated event.

        Returns:
            True if the sync was successful.

        Raises:
            ValueError: If the event or account is invalid.
            RuntimeError: If the sync operation fails.
        """
        if not event or not event.owned_account:
            raise ValueError("Event and owned_account must not be None")

        account = event.owned_account

        if not account.given_name:
            raise ValueError("Given name is required")
        if not account.family_name:
            raise ValueError("Family name is required")

        try:
            # Build user metadata from address
            user_metadata: dict[str, Any] = {}
            if account.primary_address:
                if account.primary_address.address_line1:
                    user_metadata["StreetAddress"] = account.primary_address.address_line1
                if account.primary_address.city:
                    user_metadata["City"] = account.primary_address.city
                if account.primary_address.region:
                    user_metadata["State"] = account.primary_address.region
                if account.primary_address.postal_code:
                    user_metadata["PostalCode"] = account.primary_address.postal_code
                if account.primary_address.country:
                    user_metadata["Country"] = account.primary_address.country

            # Compute full name
            full_name = account.display_name
            if not full_name:
                full_name = f"{account.given_name} {account.family_name}"

            await self._auth0_management_client.patch_user(
                subject_id=account.subject_id,
                first_name=account.given_name,
                last_name=account.family_name,
                full_name=full_name,
                user_metadata=user_metadata if user_metadata else None,
            )

            logger.info(
                "Successfully synced account profile for subject %s",
                account.subject_id,
            )
            return True

        except Exception as ex:
            logger.error(
                "Failed to sync owned account with identity provider for subject %s: %s",
                account.subject_id,
                str(ex),
            )
            raise
