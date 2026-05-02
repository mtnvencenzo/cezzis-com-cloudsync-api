"""Dapr client wrapper using the official Dapr Python SDK."""

import asyncio
import json
import logging
from typing import Any

from dapr.clients import DaprClient as OfficialDaprClient
from dapr.clients.grpc.interceptors import DaprClientInterceptor
from grpc import (  # type: ignore
    StreamStreamClientInterceptor,
    StreamUnaryClientInterceptor,
    UnaryStreamClientInterceptor,
    UnaryUnaryClientInterceptor,
)

from cezzis_com_cloudsync_api.domain.config.dapr_options import DaprOptions

logger = logging.getLogger("dapr_client")


class DaprClient:
    """Wrapper around the official Dapr Python SDK client."""

    def __init__(self, options: DaprOptions):
        """Initialize the Dapr client wrapper.

        Args:
            options: Dapr configuration options.
        """
        self._options = options
        # The official Dapr SDK uses gRPC by default
        # Format should be "localhost:port" without http:// prefix
        self._grpc_endpoint = options.grpc_endpoint

    def _create_client(self) -> OfficialDaprClient:
        """Create a new Dapr client instance.

        Returns:
            A configured Dapr client.
        """
        interceptors: (
            list[
                UnaryUnaryClientInterceptor
                | UnaryStreamClientInterceptor
                | StreamUnaryClientInterceptor
                | StreamStreamClientInterceptor
            ]
            | None
        ) = None
        if self._options.dapr_api_token:
            interceptors = [DaprClientInterceptor([("dapr-api-token", self._options.dapr_api_token)])]

        return OfficialDaprClient(
            address=self._grpc_endpoint,
            headers_callback=self._get_headers_callback if self._options.dapr_api_token else None,
            interceptors=interceptors,
        )

    def _get_headers_callback(self) -> dict[str, str]:
        """Get headers for Dapr API authentication.

        Sends the dapr-api-token header which is validated by the Dapr sidecar.
        This is DAPR_API_TOKEN - the token the app sends TO Dapr.

        Returns:
            Dictionary of header key-value pairs.
        """
        return {"dapr-api-token": self._options.dapr_api_token}

    async def publish_event(
        self,
        pubsub_name: str,
        topic_name: str,
        data: dict[str, Any],
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Publish an event to a pub/sub topic.

        Args:
            pubsub_name: The name of the pub/sub component.
            topic_name: The topic to publish to.
            data: The event data to publish.
            metadata: Optional metadata for the event.
        """

        def _publish():
            with self._create_client() as client:
                client.publish_event(
                    pubsub_name=pubsub_name,
                    topic_name=topic_name,
                    data=json.dumps(data),
                    data_content_type="application/json",
                    publish_metadata=metadata or {},
                )

        await asyncio.to_thread(_publish)
