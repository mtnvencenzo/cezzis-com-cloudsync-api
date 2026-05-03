"""Integrations API endpoints for Dapr input bindings."""

import logging

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
from cezzis_com_cloudsync_api.domain.config.app_options import AppOptions
from cezzis_com_cloudsync_api.domain.services.i_message_bus import IMessageBus

logger = logging.getLogger("integrations_router")


class IntegrationsRouter(APIRouter):
    """API router for Dapr integration binding endpoints."""

    @inject
    def __init__(self, mediator: Mediator, app_options: AppOptions, message_bus: IMessageBus) -> None:
        super().__init__(tags=["Integrations"])
        self.mediator = mediator
        self.message_bus = message_bus
        self.app_options = app_options

        cocktail_updates_sync_binding_name = app_options.cocktail_update_sync_dapr_input_binding
        cocktail_updates_scheduled_binding_name = app_options.cocktail_update_sync_scheduled_dapr_input_binding

        self.add_api_route(
            path=f"/{cocktail_updates_sync_binding_name}",
            endpoint=self._options_handler,
            methods=["OPTIONS"],
            description="Dapr input binding options endpoint",
            include_in_schema=False,
        )

        self.add_api_route(
            path=f"/{cocktail_updates_sync_binding_name}",
            endpoint=self.cocktail_updated_sync,
            methods=["POST"],
            description="Forwards a cocktail updated message to be scheduled into the internal embedding system (Dapr input binding)",
            include_in_schema=False,
            responses={
                200: {"description": "Cocktail update processed successfully"},
                400: {"description": "Invalid request payload", "model": ProblemDetails},
                500: {"description": "Internal server error", "model": ProblemDetails},
            },
        )

        self.add_api_route(
            path=f"/{cocktail_updates_scheduled_binding_name}",
            endpoint=self._options_handler,
            methods=["OPTIONS"],
            description="Dapr input binding options endpoint",
            include_in_schema=False,
        )

        self.add_api_route(
            path=f"/{cocktail_updates_scheduled_binding_name}",
            endpoint=self.cocktail_updated_scheduled_sync,
            methods=["POST"],
            description="Syncs a scheduled cocktail updated message into the internal embedding system (Dapr input binding)",
            include_in_schema=False,
            responses={
                200: {"description": "Scheduled cocktail update processed successfully"},
                400: {"description": "Invalid request payload", "model": ProblemDetails},
                500: {"description": "Internal server error", "model": ProblemDetails},
            },
        )

    async def _options_handler(self, _rq: Request) -> JSONResponse:
        """Respond to Dapr input binding OPTIONS probe."""
        return JSONResponse(content={}, status_code=status.HTTP_200_OK)

    @dapr_app_token_authorization
    async def cocktail_updated_sync(self, _rq: Request) -> JSONResponse:
        """Sync a cocktail updated message into the internal embedding system.

        This endpoint is called by Dapr when a message arrives on the
        input binding for the cocktail updates queue.

        On processing failure, the message is published to the dead-letter
        exchange before returning success (ack). This prevents infinite
        redelivery on classic queues which lack delivery-count tracking.

        Args:
            _rq: The FastAPI request object containing the binding payload.

        Returns:
            Empty JSON on success, ProblemDetails on failure.
        """
        try:
            body = await _rq.json()
            event = CocktailUpdatedEvent(raw_payload=body)
            await self.mediator.send_async(event)

        except Exception as ex:
            if not self.app_options.cocktail_update_sync_dapr_deadletter_pubsub:
                logger.exception("Error processing cocktail_updated event", exc_info=ex)
                raise
            else:
                logger.exception("Error processing cocktail_updated event, invalid body", exc_info=ex)

        return JSONResponse(content={}, status_code=status.HTTP_200_OK)

    @dapr_app_token_authorization
    async def cocktail_updated_scheduled_sync(self, _rq: Request) -> JSONResponse:
        """Sync a cocktail updated message into the internal embedding system.

        This endpoint is called by Dapr when a message arrives on the
        input binding for the cocktail updates queue.

        On processing failure, the message is published to the dead-letter
        exchange before returning success (ack). This prevents infinite
        redelivery on classic queues which lack delivery-count tracking.

        Args:
            _rq: The FastAPI request object containing the binding payload.

        Returns:
            Empty JSON on success, ProblemDetails on failure.
        """
        try:
            body = await _rq.json()
            event = CocktailUpdatedEvent(raw_payload=body)
            await self.mediator.send_async(event)

        except Exception as ex:
            if not self.app_options.cocktail_update_sync_dapr_deadletter_pubsub:
                logger.exception("Error processing cocktail_updated event", exc_info=ex)
                raise
            else:
                logger.exception("Error processing cocktail_updated event, invalid body", exc_info=ex)

        return JSONResponse(content={}, status_code=status.HTTP_200_OK)
