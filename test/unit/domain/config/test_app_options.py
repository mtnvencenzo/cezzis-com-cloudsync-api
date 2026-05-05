import os
from unittest.mock import patch

import pytest

from cezzis_com_cloudsync_api.domain.config.app_options import (
    AppOptions,
    get_app_options,
)


class TestAppOptions:
    """Test cases for AppOptions configuration."""

    def test_app_options_init_with_defaults(self):
        """Test AppOptions initialization with default values."""
        with patch.dict(os.environ, {}, clear=True):
            options = AppOptions()

            assert options.allowed_origins == ""
            assert options.cocktail_update_sync_topic == ""
            assert options.cocktail_update_sync_label == ""
            assert options.cocktail_update_sync_dapr_binding == ""
            assert options.cocktail_update_sync_dapr_input_binding == ""
            assert options.cocktail_update_sync_dapr_deadletter_label == ""
            assert options.cocktail_update_sync_dapr_deadletter_topic == ""
            assert options.cocktail_update_sync_scheduled_dapr_input_binding == ""
            assert options.cocktail_update_sync_dapr_deadletter_pubsub == ""
            assert options.cocktail_update_scheduling_sync_topic == ""
            assert options.cocktail_update_scheduling_sync_label == ""
            assert options.cocktail_update_scheduling_sync_dapr_binding == ""
            assert options.cocktail_update_sync_scheduled_dapr_deadletter_pubsub == ""
            assert options.cocktail_update_sync_scheduled_dapr_deadletter_label == ""
            assert options.cocktail_update_sync_scheduled_dapr_deadletter_topic == ""

    def test_app_options_init_with_env_vars(self):
        """Test AppOptions initialization with environment variables."""
        with patch.dict(
            os.environ,
            {
                "CLOUDSYNC_API_ALLOWED_ORIGINS": "http://localhost:3000,https://example.com",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_TOPIC": "cocktail-update-topic",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_LABEL": "cocktail-update-label",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_BINDING": "cocktail-update-binding",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_INPUT_BINDING": "bindings-cocktail-updates-queue",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_DEADLETTER_LABEL": "cocktail.data.updated",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_DEADLETTER_TOPIC": "cocktail-updates-dlx",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_SCHEDULED_DAPR_INPUT_BINDING": "bindings-cocktail-updates-scheduled-queue",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SCHEDULING_SYNC_TOPIC": "cocktail-update-scheduling-topic",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SCHEDULING_SYNC_LABEL": "cocktail-update-scheduling-label",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SCHEDULING_SYNC_DAPR_BINDING": "cocktail-update-scheduling-binding",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_SCHEDULED_DAPR_DEADLETTER_PUBSUB": "pubsub-sync-scheduled-deadletter-topic",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_SCHEDULED_DAPR_DEADLETTER_LABEL": "cocktail.data.updated-scheduled",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_SCHEDULED_DAPR_DEADLETTER_TOPIC": "cocktail-updates-scheduled-dlx",
                "CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_DAPR_DEADLETTER_PUBSUB": "pubsub-sync-deadletter-topic",
            },
        ):
            options = AppOptions()

            assert options.allowed_origins == "http://localhost:3000,https://example.com"
            assert options.cocktail_update_sync_topic == "cocktail-update-topic"
            assert options.cocktail_update_sync_label == "cocktail-update-label"
            assert options.cocktail_update_sync_dapr_binding == "cocktail-update-binding"
            assert options.cocktail_update_sync_dapr_input_binding == "bindings-cocktail-updates-queue"
            assert options.cocktail_update_sync_dapr_deadletter_pubsub == "pubsub-sync-deadletter-topic"
            assert options.cocktail_update_sync_dapr_deadletter_label == "cocktail.data.updated"
            assert options.cocktail_update_sync_dapr_deadletter_topic == "cocktail-updates-dlx"
            assert (
                options.cocktail_update_sync_scheduled_dapr_input_binding == "bindings-cocktail-updates-scheduled-queue"
            )
            assert options.cocktail_update_scheduling_sync_topic == "cocktail-update-scheduling-topic"
            assert options.cocktail_update_scheduling_sync_label == "cocktail-update-scheduling-label"
            assert options.cocktail_update_scheduling_sync_dapr_binding == "cocktail-update-scheduling-binding"
            assert (
                options.cocktail_update_sync_scheduled_dapr_deadletter_pubsub
                == "pubsub-sync-scheduled-deadletter-topic"
            )
            assert options.cocktail_update_sync_scheduled_dapr_deadletter_label == "cocktail.data.updated-scheduled"
            assert options.cocktail_update_sync_scheduled_dapr_deadletter_topic == "cocktail-updates-scheduled-dlx"

    def test_get_app_options_singleton(self):
        """Test that get_app_options returns a singleton instance."""
        import cezzis_com_cloudsync_api.domain.config.app_options as app_options_module

        app_options_module._app_options = None

        with patch.dict(os.environ, {"CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_TOPIC": "singleton-test"}):
            options1 = get_app_options()
            options2 = get_app_options()

            assert options1 is options2
            assert options1.cocktail_update_sync_topic == "singleton-test"

    def test_get_app_options_caching(self):
        """Test that get_app_options caches the instance."""
        import cezzis_com_cloudsync_api.domain.config.app_options as app_options_module

        app_options_module._app_options = None

        with patch.dict(os.environ, {"CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_TOPIC": "cached-topic"}):
            options1 = get_app_options()

        # Change env var after first call
        with patch.dict(os.environ, {"CLOUDSYNC_API_COCKTAIL_UPDATE_SYNC_TOPIC": "new-topic"}):
            options2 = get_app_options()

            # Should still return the cached instance with old value
            assert options1 is options2
            assert options2.cocktail_update_sync_topic == "cached-topic"
