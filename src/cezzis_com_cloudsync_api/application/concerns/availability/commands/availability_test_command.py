"""AvailabilityTestCommand and handler."""

import logging

import httpx
from injector import inject
from mediatr import GenericQuery, Mediator

from cezzis_com_cloudsync_api.domain.config.scheduler_options import AvailabilityTest

logger = logging.getLogger("availability_test_command")


class AvailabilityTestCommand(GenericQuery[bool]):
    """Command to perform an availability test."""

    def __init__(self, test: AvailabilityTest):
        self.test = test


@Mediator.handler
class AvailabilityTestCommandHandler:
    """Handler for AvailabilityTestCommand."""

    @inject
    def __init__(self):
        pass

    async def handle(self, command: AvailabilityTestCommand) -> bool:
        """Handle the availability test command."""
        if not command.test:
            raise ValueError("AvailabilityTest must not be None")

        logger.info(
            "Running availability test '%s' for URL: %s",
            command.test.name,
            command.test.url,
        )

        if not command.test.url:
            raise ValueError("AvailabilityTest URL must not be None")

        if not command.test.expected_status_code:
            raise ValueError("AvailabilityTest expected_status_code must not be None")

        try:
            headers = {}

            # Parse the custom header format "Key: Value"
            if command.test.authorization_header and ":" in command.test.authorization_header:
                key, value = command.test.authorization_header.split(":", 1)
                headers[key.strip()] = value.strip()

            response = httpx.get(command.test.url, headers=headers, timeout=10.0)

            string_data = response.content.decode("utf-8") if response.content else ""

            if command.test.response_string and command.test.response_string not in string_data:
                logger.error(
                    "Availability test '%s' for URL: %s failed. Expected response string: '%s' not found in response.",
                    command.test.name,
                    command.test.url,
                    command.test.response_string,
                )
                return False

            # Determine success by comparing status codes
            is_success = response.status_code == command.test.expected_status_code

            if not is_success:
                logger.error(
                    "Availability test '%s' for URL: %s failed. Expected status code: %s, but got: %s",
                    command.test.name,
                    command.test.url,
                    command.test.expected_status_code,
                    response.status_code,
                )
            else:
                logger.info(
                    "Availability test '%s' for URL: %s succeeded with status code: %s",
                    command.test.name,
                    command.test.url,
                    response.status_code,
                )

            return is_success

        except Exception as ex:
            logger.exception(
                "Availability test '%s' for URL: %s failed with exception: %s",
                command.test.name,
                command.test.url,
                str(ex),
                exc_info=ex,
            )
            return False
