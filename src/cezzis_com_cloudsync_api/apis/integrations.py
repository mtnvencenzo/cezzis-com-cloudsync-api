"""Integrations API endpoints for Dapr input bindings."""

import logging
from typing import Any

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from injector import inject
from mediatr import Mediator

from cezzis_com_cloudsync_api.application.behaviors.dapr_app_token_authorization.dapr_app_token_authorization import (
    dapr_app_token_authorization,
)
from cezzis_com_cloudsync_api.application.behaviors.error_handling.problem_details import ProblemDetails
from cezzis_com_cloudsync_api.application.concerns.integrations.events.cocktail_updated_event import (
    CocktailUpdatedEvent,
)

logger = logging.getLogger("integrations_router")


class IntegrationsRouter(APIRouter):
    """API router for Dapr integration binding endpoints."""

    # Dapr binding names matching .dapr configuration
    BINDING_IDP_ACCOUNT_PROFILE_SYNC = "bindings-idp-account-profile-sync-queue"

    @inject
    def __init__(self, mediator: Mediator) -> None:
        # No prefix - Dapr calls bindings at root path (e.g., POST /bindings-idp-account-profile-sync-queue)
        super().__init__(tags=["Integrations"])
        self.mediator = mediator

        # POST /integrations/idp-account-profile-sync - Sync account profile with identity provider
        self.add_api_route(
            path=f"/{self.BINDING_IDP_ACCOUNT_PROFILE_SYNC}",
            endpoint=self.cocktail_updated_sync,
            methods=["POST"],
            description="Syncs a cocktail updated message into the internal embedding system (Dapr input binding)",
            include_in_schema=False,
            responses={
                200: {"description": "Cocktail update synced successfully"},
                400: {"model": ProblemDetails, "description": "Invalid request"},
                500: {"model": ProblemDetails, "description": "Internal server error"},
            },
        )

        # OPTIONS endpoints for Dapr binding discovery
        self.add_api_route(
            path=f"/{self.BINDING_IDP_ACCOUNT_PROFILE_SYNC}",
            endpoint=self._options_handler,
            methods=["OPTIONS"],
            include_in_schema=False,
        )

    async def _options_handler(self) -> JSONResponse:
        """Handle OPTIONS requests for Dapr binding discovery."""
        return JSONResponse(content={}, status_code=status.HTTP_200_OK)

    @dapr_app_token_authorization
    async def cocktail_updated_sync(self, _rq: Request) -> JSONResponse:
        """Sync a cocktail updated message into the internal embedding system.

        This endpoint is called by Dapr when a message arrives on the
        idp-account-profile-sync-queue binding.

        Args:
            _rq: The FastAPI request object containing the event payload.

        Returns:
            JSON response indicating success or failure.
        """
        try:
            body: dict[str, Any] = await _rq.json()
            logger.debug("Received cocktail_updated event: %s", body)

            # Extract event data from CloudEvent envelope if present
            event_data = body.get("data", body)
            event = CocktailUpdatedEvent(**event_data)
            result = await self.mediator.send_async(event)

            if result:
                return JSONResponse(content={}, status_code=status.HTTP_200_OK)

            return JSONResponse(
                content=ProblemDetails(
                    type="about:blank",
                    title="Processing Failed",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to sync cocktail update with internal embedding system",
                ).model_dump(exclude_none=True),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/problem+json",
            )

        except ValueError as ex:
            logger.warning("Invalid cocktail_updated event: %s", str(ex))
            return JSONResponse(
                content=ProblemDetails(
                    type="about:blank",
                    title="Validation Error",
                    status=status.HTTP_400_BAD_REQUEST,
                    detail=str(ex),
                ).model_dump(exclude_none=True),
                status_code=status.HTTP_400_BAD_REQUEST,
                media_type="application/problem+json",
            )
        except Exception as ex:
            logger.error("Error processing cocktail_updated event: %s", str(ex))
            return JSONResponse(
                content=ProblemDetails(
                    type="about:blank",
                    title="Internal Server Error",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred",
                ).model_dump(exclude_none=True),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/problem+json",
            )
