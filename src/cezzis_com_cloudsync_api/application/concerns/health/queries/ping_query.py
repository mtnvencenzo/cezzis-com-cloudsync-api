"""PingQuery and handler for health ping endpoint."""

from injector import inject
from mediatr import GenericQuery, Mediator

from cezzis_com_cloudsync_api.application.concerns.health.models.ping_rs import PingRs


class PingQuery(GenericQuery[PingRs]):
    """Query to get server health ping information."""

    pass


@Mediator.handler
class PingQueryHandler:
    """Handler for PingQuery."""

    @inject
    def __init__(self):
        pass

    async def handle(self, query: PingQuery) -> PingRs:
        """Return server info including machine name, version, OS details and memory usage."""
        return PingRs.create()
