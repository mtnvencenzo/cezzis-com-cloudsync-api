"""CocktailRecommendationEmailEvent for sending recommendation emails via Zoho."""

import logging

from cezzis_com_cloudsync_api.application.concerns.integrations.events.integration_event import IIntegrationEvent
from cezzis_com_cloudsync_api.domain.aggregates.common.email_message import EmailAddress, EmailMessage, EmailPriority
from cezzis_com_cloudsync_api.domain.services.i_zoho_email_client import IZohoEmailClient
from injector import inject
from mediatr import GenericQuery, Mediator
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

logger = logging.getLogger("cocktail_recommendation_email_event")


class EmailAddressModel(BaseModel):
    """Email address model for event deserialization."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    address: str
    display_name: str | None = None


class CocktailRecommendationEmailEvent(IIntegrationEvent, GenericQuery[bool]):
    """Event triggered when a cocktail recommendation email needs to be sent."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    subject: str | None = None
    body: str | None = None
    from_address: EmailAddressModel | None = Field(default=None, alias="from")
    to: list[EmailAddressModel] | None = None
    cc: list[EmailAddressModel] | None = None
    bcc: list[EmailAddressModel] | None = None
    reply_to: EmailAddressModel | None = None
    priority: int = Field(default=1)  # 0=Low, 1=Normal, 2=High

    @field_validator("to", mode="before")
    @classmethod
    def validate_to(cls, v: list | None) -> list | None:
        """Validate that at least one recipient is provided."""
        if v is None or len(v) == 0:
            raise ValueError("At least one recipient is required")
        return v

    @field_validator("from_address", mode="before")
    @classmethod
    def validate_from(cls, v: dict | EmailAddressModel | None) -> dict | EmailAddressModel:
        """Validate that from address is provided."""
        if v is None:
            raise ValueError("From address is required")
        return v


@Mediator.handler
class CocktailRecommendationEmailEventHandler:
    """Handler for CocktailRecommendationEmailEvent - sends emails via Zoho."""

    @inject
    def __init__(self, zoho_email_client: IZohoEmailClient):
        """Initialize the handler.

        Args:
            zoho_email_client: The Zoho email client for sending emails.
        """
        self._zoho_email_client = zoho_email_client

    async def handle(self, event: CocktailRecommendationEmailEvent) -> bool:
        """Handle the email event.

        Args:
            event: The email event.

        Returns:
            True if the email was sent successfully.

        Raises:
            ValueError: If the event is invalid.
            RuntimeError: If the email fails to send.
        """
        if not event:
            raise ValueError("Event must not be None")

        # Validate body or subject
        if not event.subject and not event.body:
            raise ValueError("Either subject or body is required")

        try:
            # Convert event to EmailMessage
            email_message = EmailMessage(
                subject=event.subject,
                body=event.body,
                from_address=EmailAddress(
                    address=event.from_address.address,
                    display_name=event.from_address.display_name,
                )
                if event.from_address
                else None,
                to=[EmailAddress(address=addr.address, display_name=addr.display_name) for addr in event.to]
                if event.to
                else None,
                cc=[EmailAddress(address=addr.address, display_name=addr.display_name) for addr in event.cc]
                if event.cc
                else None,
                bcc=[EmailAddress(address=addr.address, display_name=addr.display_name) for addr in event.bcc]
                if event.bcc
                else None,
                reply_to=EmailAddress(
                    address=event.reply_to.address,
                    display_name=event.reply_to.display_name,
                )
                if event.reply_to
                else None,
                priority=EmailPriority(event.priority),
            )

            await self._zoho_email_client.send_email(email_message)

            logger.info(
                "Successfully sent cocktail recommendation email to %s",
                ", ".join(addr.address for addr in event.to) if event.to else "unknown",
            )
            return True

        except Exception as ex:
            logger.error("Failed to send cocktail recommendation email: %s", str(ex))
            raise
