"""Dapr client wrapper using the official Dapr Python SDK."""

import json
import logging
from typing import Any

from dapr.clients import DaprClient as OfficialDaprClient

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
        return OfficialDaprClient(
            address=self._grpc_endpoint,
            headers_callback=self._get_headers_callback if self._options.dapr_api_token else None,
        )

    def _get_headers_callback(self) -> dict[str, str]:
        """Get headers for Dapr API authentication.

        Sends the dapr-api-token header which is validated by the Dapr sidecar.
        This is DAPR_API_TOKEN - the token the app sends TO Dapr.

        Returns:
            Dictionary of header key-value pairs.
        """
        return {"dapr-api-token": self._options.dapr_api_token}

    async def invoke_binding(
        self,
        binding_name: str,
        operation: str,
        data: bytes | str | dict[str, Any] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> bytes | None:
        """Invoke an output binding.

        Args:
            binding_name: The name of the binding component.
            operation: The operation to perform (e.g., 'create', 'delete', 'get').
            data: The data to send with the binding invocation.
            metadata: Optional metadata for the binding operation.

        Returns:
            The response data from the binding, or None.
        """
        # Convert data to appropriate format
        if isinstance(data, dict):
            binding_data = json.dumps(data).encode("utf-8")
        elif isinstance(data, str):
            binding_data = data.encode("utf-8")
        elif isinstance(data, bytes):
            binding_data = data
        else:
            binding_data = b""

        with self._create_client() as client:
            response = client.invoke_binding(
                binding_name=binding_name,
                operation=operation,
                data=binding_data,
                binding_metadata=metadata or {},
            )
            return response.data if response.data else None

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
        with self._create_client() as client:
            client.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic_name,
                data=json.dumps(data),
                data_content_type="application/json",
                publish_metadata=metadata or {},
            )

    async def get_state(
        self,
        store_name: str,
        key: str,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        """Get state from a state store.

        Args:
            store_name: The name of the state store component.
            key: The key to retrieve.
            metadata: Optional metadata for the state operation.

        Returns:
            The state value or None if not found.
        """
        with self._create_client() as client:
            response = client.get_state(
                store_name=store_name,
                key=key,
                state_metadata=metadata or {},
            )
            if response.data:
                return json.loads(response.data)
            return None

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Save state to a state store.

        Args:
            store_name: The name of the state store component.
            key: The key to save.
            value: The value to save.
            metadata: Optional metadata for the state operation.
        """
        with self._create_client() as client:
            client.save_state(
                store_name=store_name,
                key=key,
                value=json.dumps(value),
                state_metadata=metadata or {},
            )

    async def delete_state(
        self,
        store_name: str,
        key: str,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Delete state from a state store.

        Args:
            store_name: The name of the state store component.
            key: The key to delete.
            metadata: Optional metadata for the state operation.
        """
        with self._create_client() as client:
            client.delete_state(
                store_name=store_name,
                key=key,
                state_metadata=metadata or {},
            )

    async def invoke_method(
        self,
        app_id: str,
        method_name: str,
        data: dict[str, Any] | None = None,
        http_verb: str = "POST",
        metadata: dict[str, str] | None = None,
    ) -> bytes | None:
        """Invoke a method on another Dapr application.

        Args:
            app_id: The app ID of the target application.
            method_name: The method to invoke.
            data: Optional data to send with the invocation.
            http_verb: The HTTP verb to use (default: POST).
            metadata: Optional metadata for the invocation.

        Returns:
            The response data from the invocation, or None.
        """
        request_data = json.dumps(data).encode("utf-8") if data else b""

        with self._create_client() as client:
            response = client.invoke_method(
                app_id=app_id,
                method_name=method_name,
                data=request_data,
                http_verb=http_verb,
                metadata=tuple(metadata.items()) if metadata else None,
            )
            return response.data if response.data else None

    async def get_secret(
        self,
        store_name: str,
        key: str,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, str] | None:
        """Get a secret from a secret store.

        Args:
            store_name: The name of the secret store component.
            key: The secret key to retrieve.
            metadata: Optional metadata for the secret operation.

        Returns:
            The secret value(s) or None if not found.
        """
        with self._create_client() as client:
            response = client.get_secret(
                store_name=store_name,
                key=key,
                secret_metadata=metadata or {},
            )
            return response.secret if response.secret else None
