"""VersionQuery and handler for health version endpoint."""

from mediatr import GenericQuery, Mediator

from cezzis_com_cloudsync_api.application.concerns.health.app_version import get_app_version
from cezzis_com_cloudsync_api.application.concerns.health.models.version_rs import VersionRs


class VersionQuery(GenericQuery[VersionRs]):
    """Query to get application version."""

    pass


@Mediator.handler
class VersionQueryHandler:
    """Handler for VersionQuery."""

    async def handle(self, query: VersionQuery) -> VersionRs:
        """Return application version."""
        return VersionRs(version=get_app_version())
