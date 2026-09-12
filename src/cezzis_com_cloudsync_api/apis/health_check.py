from typing import cast

from fastapi import APIRouter, Response, status
from injector import inject
from mediatr import Mediator

from cezzis_com_cloudsync_api.application.concerns.health.models.health_check_rs import HealthCheckRs
from cezzis_com_cloudsync_api.application.concerns.health.models.ping_rs import PingRs
from cezzis_com_cloudsync_api.application.concerns.health.models.version_rs import VersionRs
from cezzis_com_cloudsync_api.application.concerns.health.queries.health_check_query import HealthCheckQuery
from cezzis_com_cloudsync_api.application.concerns.health.queries.ping_query import PingQuery
from cezzis_com_cloudsync_api.application.concerns.health.queries.readiness_check_query import ReadinessCheckQuery
from cezzis_com_cloudsync_api.application.concerns.health.queries.version_query import VersionQuery


class HealthCheckRouter(APIRouter):
    @inject
    def __init__(self, mediator: Mediator):
        super().__init__()
        self.mediator = mediator
        self.add_api_route(
            path="/api/v1/health/liveness",
            endpoint=self.liveness_check,
            methods=["GET"],
            include_in_schema=False,
            responses={
                200: {"model": HealthCheckRs, "description": "Successful liveness check"},
            },
        )
        self.add_api_route(
            path="/api/v1/health/readiness",
            endpoint=self.readiness_check,
            methods=["GET"],
            include_in_schema=False,
            responses={
                200: {"model": HealthCheckRs, "description": "Service is ready"},
                503: {"model": HealthCheckRs, "description": "Service is not ready"},
            },
        )
        self.add_api_route(
            path="/api/v1/health/ping",
            endpoint=self.ping,
            methods=["GET"],
            include_in_schema=True,
            responses={
                200: {"model": PingRs, "description": "Health ping with server info"},
            },
        )
        self.add_api_route(
            path="/api/v1/health/version",
            endpoint=self.get_version,
            methods=["GET"],
            include_in_schema=True,
            responses={
                200: {"model": VersionRs, "description": "Application version"},
            },
        )

    async def liveness_check(self) -> HealthCheckRs:
        """
        Performs a liveness check of the API.
        """

        return cast(HealthCheckRs, await self.mediator.send_async(HealthCheckQuery()))

    async def readiness_check(self, response: Response) -> HealthCheckRs:
        """
        Performs a readiness check verifying connectivity to Dapr components (messaging).
        """

        result = cast(HealthCheckRs, await self.mediator.send_async(ReadinessCheckQuery()))
        if result.status != "healthy":
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return result

    async def ping(self) -> PingRs:
        """
        Returns server info including machine name, version, OS details and memory usage.
        """
        return cast(PingRs, await self.mediator.send_async(PingQuery()))

    async def get_version(self) -> VersionRs:
        """
        Returns the application version. Used by CI/CD to verify deployments.
        """
        return cast(VersionRs, await self.mediator.send_async(VersionQuery()))
