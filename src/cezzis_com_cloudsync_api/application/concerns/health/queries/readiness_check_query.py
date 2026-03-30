import logging
import time
from importlib.metadata import version

import httpx
from injector import inject
from mediatr import GenericQuery, Mediator

from cezzis_com_cloudsync_api.application.concerns.health.models.health_check_rs import HealthCheckRs
from cezzis_com_cloudsync_api.domain.config.dapr_options import DaprOptions

_start_time = time.monotonic()
DAPR_GRACE_PERIOD_SECONDS = 120  # 2 minutes


class ReadinessCheckQuery(GenericQuery[HealthCheckRs]):
    def __init__(self):
        pass


@Mediator.handler
class ReadinessCheckQueryHandler:
    @inject
    def __init__(self, dapr_options: DaprOptions):
        self.logger = logging.getLogger("readiness_check_query_handler")
        self._dapr_options = dapr_options

    async def handle(self, command: ReadinessCheckQuery) -> HealthCheckRs:
        details = {}
        overall_healthy = True

        # Check Dapr outbound component health — covers pubsub (messaging) and all other components
        try:
            headers = {}
            if self._dapr_options.dapr_api_token:
                headers["dapr-api-token"] = self._dapr_options.dapr_api_token

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._dapr_options.http_endpoint}/v1.0/healthz/outbound",
                    headers=headers,
                    timeout=5.0,
                )

            if response.status_code == 204:
                details["dapr"] = "healthy"
            else:
                details["dapr"] = f"unhealthy (status {response.status_code})"
                overall_healthy = False
        except Exception as exc:
            self.logger.exception("Dapr health check failed: %s", exc)
            elapsed = time.monotonic() - _start_time
            if elapsed < DAPR_GRACE_PERIOD_SECONDS:
                details["dapr"] = f"degraded (starting, {elapsed:.0f}s/{DAPR_GRACE_PERIOD_SECONDS}s elapsed)"
            else:
                details["dapr"] = "unhealthy"
                overall_healthy = False

        return HealthCheckRs(
            status="healthy" if overall_healthy else "unhealthy",
            version=version("cezzis_com_cloudsync_api"),
            output="All dependencies are reachable" if overall_healthy else "One or more dependencies are unreachable",
            details=details,
        )
