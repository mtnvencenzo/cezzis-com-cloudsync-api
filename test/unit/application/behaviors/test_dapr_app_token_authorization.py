"""Test cases for dapr_app_token_authorization decorator."""

import importlib
import os
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cezzis_com_cloudsync_api.application.behaviors.error_handling.exception_types import ForbiddenException

# The package __init__.py re-exports the function, shadowing the module name.
# Use importlib to get the actual module.
_auth_mod: types.ModuleType = importlib.import_module(
    "cezzis_com_cloudsync_api.application.behaviors.dapr_app_token_authorization.dapr_app_token_authorization"
)
_decorator = _auth_mod.dapr_app_token_authorization


class TestDaprAppTokenAuthorization:
    """Test cases for the dapr_app_token_authorization decorator."""

    @pytest.mark.anyio
    async def test_valid_token_allows_request(self):
        """Test that a valid app token allows the request through."""
        mock_options = MagicMock()
        mock_options.app_api_token = "valid-token"

        setattr(_auth_mod, "_dapr_options", mock_options)

        request = MagicMock()
        request.headers.get = MagicMock(return_value="valid-token")

        inner_func = AsyncMock(return_value="ok")
        decorated = _decorator(inner_func)

        result = await decorated(_rq=request)
        assert result == "ok"
        inner_func.assert_called_once_with(_rq=request)

    @pytest.mark.anyio
    async def test_invalid_token_raises_forbidden(self):
        """Test that an invalid app token raises ForbiddenException."""
        mock_options = MagicMock()
        mock_options.app_api_token = "valid-token"

        setattr(_auth_mod, "_dapr_options", mock_options)

        request = MagicMock()
        request.headers.get = MagicMock(return_value="wrong-token")

        inner_func = AsyncMock(return_value="ok")
        decorated = _decorator(inner_func)

        with pytest.raises(ForbiddenException, match="Invalid Dapr app token"):
            await decorated(_rq=request)

        inner_func.assert_not_called()

    @pytest.mark.anyio
    async def test_empty_configured_token_bypasses_auth(self):
        """Test that empty configured token bypasses authorization."""
        mock_options = MagicMock()
        mock_options.app_api_token = ""

        setattr(_auth_mod, "_dapr_options", mock_options)

        request = MagicMock()
        request.headers.get = MagicMock(return_value="")

        inner_func = AsyncMock(return_value="ok")
        decorated = _decorator(inner_func)

        with patch.dict(os.environ, {"ENV": "local"}):
            result = await decorated(_rq=request)

        assert result == "ok"

    @pytest.mark.anyio
    async def test_whitespace_only_token_bypasses_auth(self):
        """Test that whitespace-only configured token bypasses authorization."""
        mock_options = MagicMock()
        mock_options.app_api_token = "   "

        setattr(_auth_mod, "_dapr_options", mock_options)

        request = MagicMock()
        request.headers.get = MagicMock(return_value="")

        inner_func = AsyncMock(return_value="ok")
        decorated = _decorator(inner_func)

        with patch.dict(os.environ, {"ENV": "local"}):
            result = await decorated(_rq=request)

        assert result == "ok"
