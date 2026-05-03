import logging
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppOptions(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.environ.get('ENV')}"), env_file_encoding="utf-8", extra="allow"
    )

    allowed_origins: str = Field(default="", validation_alias="CLOUDSYNC_API_ALLOWED_ORIGINS")
    cocktail_update_sync_topic: str = Field(default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_TOPIC")
    cocktail_update_sync_label: str = Field(default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_LABEL")
    cocktail_update_sync_dapr_binding: str = Field(
        default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_BINDING"
    )
    cocktail_update_sync_dapr_input_binding: str = Field(
        default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_INPUT_BINDING"
    )
    cocktail_update_sync_scheduled_dapr_input_binding: str = Field(
        default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_SCHEDULED_DAPR_INPUT_BINDING"
    )
    cocktail_update_sync_dapr_deadletter_pubsub: str = Field(
        default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_DEADLETTER_PUBSUB"
    )
    cocktail_update_sync_dapr_deadletter_label: str = Field(
        default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_DEADLETTER_LABEL"
    )
    cocktail_update_sync_scheduled_dapr_deadletter_label: str = Field(
        default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_SCHEDULED_DAPR_DEADLETTER_LABEL"
    )
    cocktail_update_sync_dapr_deadletter_topic: str = Field(
        default="", validation_alias="CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_DEADLETTER_TOPIC"
    )


_logger: logging.Logger = logging.getLogger("app_options")

_app_options: AppOptions | None = None


def get_app_options() -> AppOptions:
    """Get the singleton instance of AppOptions.
    Returns:
        AppOptions: The application options instance.
    """

    global _app_options
    if _app_options is None:
        _app_options = AppOptions()

        if not _app_options.allowed_origins:
            _logger.warning("CLOUDSYNC_API_ALLOWED_ORIGINS environment variable is not configured")
        if not _app_options.cocktail_update_sync_topic:
            _logger.warning("CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_TOPIC environment variable is not configured")
        if not _app_options.cocktail_update_sync_label:
            _logger.warning("CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_LABEL environment variable is not configured")
        if not _app_options.cocktail_update_sync_dapr_binding:
            _logger.warning("CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_BINDING environment variable is not configured")
        if not _app_options.cocktail_update_sync_dapr_input_binding:
            _logger.warning(
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_INPUT_BINDING environment variable is not configured"
            )
        if not _app_options.cocktail_update_sync_dapr_deadletter_pubsub:
            if not _app_options.cocktail_update_sync_dapr_deadletter_label:
                _logger.warning(
                    "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_DEADLETTER_LABEL environment variable is not configured"
                )
            if not _app_options.cocktail_update_sync_dapr_deadletter_topic:
                _logger.warning(
                    "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_DEADLETTER_TOPIC environment variable is not configured"
                )

        _logger.info("Application options loaded successfully.")

    return _app_options
