import logging
from importlib.metadata import version

from injector import inject
from mediatr import GenericQuery, Mediator

from cezzis_com_cloudsync_api.application.concerns.health.models.health_check_rs import HealthCheckRs


class HealthCheckQuery(GenericQuery[HealthCheckRs]):
    def __init__(self):
        pass


@Mediator.handler
class HealthCheckQueryHandler:
    @inject
    def __init__(self):
        self.logger = logging.getLogger("health_check_query_handler")

    async def handle(self, command: HealthCheckQuery) -> HealthCheckRs:
        return HealthCheckRs(
            status="healthy",
            version=version("cezzis_com_cloudsync_api"),
            output="API is running",
            details={},
        )
