"""Dapr app token authorization decorator for securing Dapr input binding endpoints."""

import logging
import os
from functools import wraps
from typing import cast

from fastapi import Request

from cezzis_com_cloudsync_api.application.behaviors.error_handling.exception_types import ForbiddenException
from cezzis_com_cloudsync_api.domain.config.dapr_options import DaprOptions, get_dapr_options

_logger = logging.getLogger("dapr_app_token_authorization")
_dapr_options: DaprOptions = get_dapr_options()


def dapr_app_token_authorization(func):
    """Decorator to validate Dapr app token for input binding endpoints.

    This decorator checks for the presence and validity of the Dapr app token
    in the request headers (dapr-app-token). This is used to secure endpoints
    that receive messages from Dapr input bindings.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = cast(Request, kwargs.get("_rq"))
        supplied_app_token = request.headers.get("dapr-api-token", "")

        # Validate against APP_API_TOKEN - the token Dapr sidecar sends to the app
        if len(_dapr_options.app_api_token.strip()) == 0:
            if os.getenv("ENV") != "local":
                _logger.warning("Dapr app token authorization bypassed due to unconfigured app api token")
        else:
            if supplied_app_token != _dapr_options.app_api_token:
                _logger.warning("Dapr app token authorization failed due to invalid supplied app token")
                raise ForbiddenException(detail="Invalid Dapr app token")

        return await func(*args, **kwargs)

    return wrapper
