"""Test cases for exception handlers."""

import json
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from cezzis_com_cloudsync_api.application.behaviors.error_handling.exception_handlers import (
    generic_exception_handler,
    http_exception_handler,
    problem_details_exception_handler,
    validation_exception_handler,
)
from cezzis_com_cloudsync_api.application.behaviors.error_handling.exception_types import (
    BadRequestException,
    ForbiddenException,
    InternalServerErrorException,
    NotFoundException,
    ProblemDetailsException,
    UnauthorizedException,
    UnprocessableEntityException,
)


def _make_request(path: str = "/test") -> MagicMock:
    request = MagicMock()
    request.url.path = path
    return request


class TestProblemDetailsExceptionHandler:
    """Test cases for problem_details_exception_handler."""

    @pytest.mark.anyio
    async def test_returns_correct_status_code(self):
        """Test that the response has the correct status code."""
        request = _make_request()
        exc = BadRequestException(detail="something went wrong")

        response = await problem_details_exception_handler(request, exc)

        assert response.status_code == 400
        assert response.media_type == "application/problem+json"

    @pytest.mark.anyio
    async def test_sets_instance_from_request_path(self):
        """Test that instance is set to request path when not provided."""
        request = _make_request("/v1/integrations")
        exc = BadRequestException(detail="bad")

        response = await problem_details_exception_handler(request, exc)

        body = json.loads(bytes(response.body))
        assert body["instance"] == "/v1/integrations"

    @pytest.mark.anyio
    async def test_preserves_explicit_instance(self):
        """Test that an explicitly set instance is preserved."""
        request = _make_request("/v1/integrations")
        exc = BadRequestException(detail="bad", instance="/custom/path")

        response = await problem_details_exception_handler(request, exc)

        body = json.loads(bytes(response.body))
        assert body["instance"] == "/custom/path"

    @pytest.mark.anyio
    async def test_forbidden_exception(self):
        """Test ForbiddenException handler."""
        request = _make_request()
        exc = ForbiddenException(detail="access denied")

        response = await problem_details_exception_handler(request, exc)
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_not_found_exception(self):
        """Test NotFoundException handler."""
        request = _make_request()
        exc = NotFoundException(detail="resource not found")

        response = await problem_details_exception_handler(request, exc)
        assert response.status_code == 404

    @pytest.mark.anyio
    async def test_unauthorized_exception(self):
        """Test UnauthorizedException handler."""
        request = _make_request()
        exc = UnauthorizedException(detail="not authenticated")

        response = await problem_details_exception_handler(request, exc)
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_unprocessable_entity_exception(self):
        """Test UnprocessableEntityException handler."""
        request = _make_request()
        exc = UnprocessableEntityException(detail="invalid data")

        response = await problem_details_exception_handler(request, exc)
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_internal_server_error_exception(self):
        """Test InternalServerErrorException handler."""
        request = _make_request()
        exc = InternalServerErrorException(detail="server error")

        response = await problem_details_exception_handler(request, exc)
        assert response.status_code == 500


class TestHttpExceptionHandler:
    """Test cases for http_exception_handler."""

    @pytest.mark.anyio
    async def test_maps_400_to_problem_details(self):
        """Test that HTTP 400 is mapped to correct problem details."""
        request = _make_request()
        exc = HTTPException(status_code=400, detail="bad request")

        response = await http_exception_handler(request, exc)

        assert response.status_code == 400

        body = json.loads(bytes(response.body))
        assert body["title"] == "Bad Request"
        assert body["detail"] == "bad request"

    @pytest.mark.anyio
    async def test_maps_404_to_problem_details(self):
        """Test that HTTP 404 is mapped correctly."""
        request = _make_request()
        exc = HTTPException(status_code=404)

        response = await http_exception_handler(request, exc)
        assert response.status_code == 404

    @pytest.mark.anyio
    async def test_unknown_status_uses_about_blank(self):
        """Test that unknown status codes use about:blank type."""
        request = _make_request()
        exc = HTTPException(status_code=418, detail="I'm a teapot")

        response = await http_exception_handler(request, exc)

        assert response.status_code == 418

        body = json.loads(bytes(response.body))
        assert body["type"] == "about:blank"


class TestValidationExceptionHandler:
    """Test cases for validation_exception_handler."""

    @pytest.mark.anyio
    async def test_handles_request_validation_error(self):
        """Test handling of FastAPI RequestValidationError."""
        request = _make_request("/v1/test")
        errors = [
            {"loc": ("body", "name"), "msg": "Field required", "type": "missing"},
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(request, exc)

        assert response.status_code == 422

        body = json.loads(bytes(response.body))
        assert body["title"] == "Validation Error"
        assert "name" in body["errors"]

    @pytest.mark.anyio
    async def test_field_path_excludes_body_and_query(self):
        """Test that body and query are excluded from field path."""
        request = _make_request()
        errors = [
            {"loc": ("query", "page"), "msg": "value is not a valid integer", "type": "int_parsing"},
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(request, exc)

        body = json.loads(bytes(response.body))
        assert "page" in body["errors"]


class TestGenericExceptionHandler:
    """Test cases for generic_exception_handler."""

    @pytest.mark.anyio
    async def test_returns_500_for_unhandled_exception(self):
        """Test that unhandled exceptions return 500."""
        request = _make_request()
        exc = RuntimeError("something unexpected")

        response = await generic_exception_handler(request, exc)

        assert response.status_code == 500

        body = json.loads(bytes(response.body))
        assert body["title"] == "Internal Server Error"
        assert body["status"] == 500
