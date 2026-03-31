from cezzis_com_cloudsync_api.apis.health_check import (
    HealthCheckRouter,
)
from cezzis_com_cloudsync_api.apis.integrations import (
    IntegrationsRouter,
)
from cezzis_com_cloudsync_api.apis.scalar_docs import (
    ScalarDocsRouter,
)

__all__ = [
    "IntegrationsRouter",
    "HealthCheckRouter",
    "ScalarDocsRouter",
]
