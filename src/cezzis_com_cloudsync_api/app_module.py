from injector import Binder, Injector, Module, provider, singleton
from mediatr import Mediator

from cezzis_com_cloudsync_api.application.concerns.health.queries.health_check_query import HealthCheckQueryHandler
from cezzis_com_cloudsync_api.application.concerns.health.queries.readiness_check_query import (
    ReadinessCheckQueryHandler,
)
from cezzis_com_cloudsync_api.application.concerns.integrations.events import (
    CocktailUpdatedScheduledEventCommandHandler,
    CocktailUpdatedSchedulingEventCommandHandler,
)
from cezzis_com_cloudsync_api.domain.config.app_options import AppOptions, get_app_options
from cezzis_com_cloudsync_api.domain.config.dapr_options import DaprOptions, get_dapr_options
from cezzis_com_cloudsync_api.domain.config.oauth_options import OAuthOptions, get_oauth_options
from cezzis_com_cloudsync_api.domain.config.otel_options import OTelOptions, get_otel_options
from cezzis_com_cloudsync_api.domain.services.i_message_bus import IMessageBus
from cezzis_com_cloudsync_api.infrastructure.dapr.dapr_client import DaprClient
from cezzis_com_cloudsync_api.infrastructure.message_bus import MessageBus


def create_injector() -> Injector:
    _injector = Injector([AppModule()])

    def _mediator_manager(handler_class, is_behavior=False):
        return _injector.get(handler_class)

    # Re-bind the Mediator now that we have the injector reference
    _injector.binder.bind(Mediator, Mediator(handler_class_manager=_mediator_manager), scope=singleton)

    return _injector


class AppModule(Module):
    def configure(self, binder: Binder):
        # Configuration options
        binder.bind(AppOptions, get_app_options(), scope=singleton)
        binder.bind(OAuthOptions, get_oauth_options(), scope=singleton)
        binder.bind(OTelOptions, get_otel_options(), scope=singleton)
        binder.bind(DaprOptions, get_dapr_options(), scope=singleton)

        # Query handlers
        binder.bind(HealthCheckQueryHandler, HealthCheckQueryHandler, scope=singleton)
        binder.bind(ReadinessCheckQueryHandler, ReadinessCheckQueryHandler, scope=singleton)

        # Integration event handlers
        binder.bind(
            CocktailUpdatedSchedulingEventCommandHandler, CocktailUpdatedSchedulingEventCommandHandler, scope=singleton
        )
        binder.bind(
            CocktailUpdatedScheduledEventCommandHandler, CocktailUpdatedScheduledEventCommandHandler, scope=singleton
        )

    @provider
    @singleton
    def provide_dapr_client(self, dapr_options: DaprOptions) -> DaprClient:
        """Provide the Dapr client."""
        return DaprClient(dapr_options)

    @provider
    @singleton
    def provide_message_bus(self, dapr_client: DaprClient) -> IMessageBus:
        """Provide the message bus implementation."""
        return MessageBus(dapr_client)
