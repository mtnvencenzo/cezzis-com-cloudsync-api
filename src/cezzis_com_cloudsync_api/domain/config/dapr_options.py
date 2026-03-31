"""Dapr configuration options."""

import logging
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DaprOptions(BaseSettings):
    """Configuration options for Dapr sidecar connection."""

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.environ.get('ENV')}"), env_file_encoding="utf-8", extra="allow"
    )

    host: str = Field(default="localhost", validation_alias="DAPR_HOST")
    http_port: int = Field(default=3500, validation_alias="DAPR_HTTP_PORT")
    grpc_port: int = Field(default=50001, validation_alias="DAPR_GRPC_PORT")

    # Full endpoint overrides (used by Dapr SDK for health checks)
    # These take precedence over host+port if set
    http_endpoint_override: str | None = Field(default=None, validation_alias="DAPR_HTTP_ENDPOINT")
    grpc_endpoint_override: str | None = Field(default=None, validation_alias="DAPR_GRPC_ENDPOINT")

    # Token the app sends TO the Dapr sidecar (for outgoing calls to Dapr APIs)
    # Dapr standard: DAPR_API_TOKEN — sidecar also reads this to enforce API auth
    dapr_api_token: str = Field(default="", validation_alias="DAPR_API_TOKEN")

    # Token the Dapr sidecar sends TO the app (for incoming input binding calls)
    # Dapr standard: APP_API_TOKEN — sidecar also reads this to know what to send
    app_api_token: str = Field(default="", validation_alias="APP_API_TOKEN")

    @property
    def http_endpoint(self) -> str:
        """Get the Dapr HTTP endpoint."""
        if self.http_endpoint_override:
            return self.http_endpoint_override
        return f"http://{self.host}:{self.http_port}"

    @property
    def grpc_endpoint(self) -> str:
        """Get the Dapr gRPC endpoint."""
        if self.grpc_endpoint_override:
            # Strip http:// or https:// prefix if present (gRPC uses host:port format)
            endpoint = self.grpc_endpoint_override
            if endpoint.startswith("http://"):
                endpoint = endpoint[7:]
            elif endpoint.startswith("https://"):
                endpoint = endpoint[8:]
            return endpoint
        return f"{self.host}:{self.grpc_port}"


_logger: logging.Logger = logging.getLogger("dapr_options")

_dapr_options: DaprOptions | None = None


def get_dapr_options() -> DaprOptions:
    """Get the singleton instance of DaprOptions.

    Returns:
        DaprOptions: The Dapr options instance.
    """
    global _dapr_options
    if _dapr_options is None:
        _dapr_options = DaprOptions()

        _logger.info("Dapr options loaded successfully.")

    return _dapr_options


def clear_dapr_options_cache() -> None:
    """Clear the cached options instance. Useful for testing."""
    global _dapr_options
    _dapr_options = None
