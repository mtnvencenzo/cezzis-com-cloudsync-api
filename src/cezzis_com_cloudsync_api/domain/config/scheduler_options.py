"""Scheduler configuration options."""

import logging
import os

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AvailabilityTest(BaseSettings):
    name: str
    expected_status_code: int
    authorization_header: str | None = None
    url: str | None = None
    response_string: str | None = None


class SchedulerOptions(BaseSettings):
    """Configuration options for the scheduler."""

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.environ.get('ENV')}"), env_file_encoding="utf-8", extra="allow"
    )

    # Whether the init job is enabled (runs migrations and seeds test account)
    init_job_enabled: bool = Field(default=True, validation_alias="SCHEDULER_INIT_JOB_ENABLED")

    # Delay in seconds before running the init job (allows old pods to terminate during rolling updates)
    init_delay_seconds: int = Field(default=30, validation_alias="SCHEDULER_INIT_DELAY_SECONDS")

    cocktails_api_availability_test_url: str | None = Field(
        default="",
        validation_alias="COCKTAILS_API_AVAILABILITY_TEST_URL",
    )
    cocktails_api_availability_test_auth_header: str | None = Field(
        default="", validation_alias="COCKTAILS_API_AVAILABILITY_TEST_AUTH_HEADER"
    )
    accounts_api_availability_test_url: str | None = Field(
        default="",
        validation_alias="ACCOUNTS_API_AVAILABILITY_TEST_URL",
    )
    accounts_api_availability_test_auth_header: str | None = Field(
        default="", validation_alias="ACCOUNTS_API_AVAILABILITY_TEST_AUTH_HEADER"
    )
    cezzis_com_availability_test_url: str | None = Field(
        default="", validation_alias="CEZZIS_COM_AVAILABILITY_TEST_URL"
    )
    cezzis_com_availability_test_response_string: str | None = Field(
        default="", validation_alias="CEZZIS_COM_AVAILABILITY_TEST_RESPONSE_STRING"
    )

    availability_tests_cron: str = Field(default="0 * * * *", validation_alias="AVAILABILITY_TESTS_CRON")

    availability_tests: list[AvailabilityTest] = Field(default_factory=list)

    @model_validator(mode="after")
    def populate_availability_tests(self) -> "SchedulerOptions":
        """Populates the availability tests list after strings are parsed from env/config."""

        if not self.availability_tests:
            tests = [
                AvailabilityTest(
                    name="Cocktails API",
                    url=self.cocktails_api_availability_test_url,
                    expected_status_code=200,
                    authorization_header=self.cocktails_api_availability_test_auth_header,
                ),
                AvailabilityTest(
                    name="Accounts API",
                    url=self.accounts_api_availability_test_url,
                    expected_status_code=200,
                    authorization_header=self.accounts_api_availability_test_auth_header,
                ),
                AvailabilityTest(
                    name="Cezzis.com",
                    url=self.cezzis_com_availability_test_url,
                    expected_status_code=200,
                    authorization_header=None,
                    response_string=self.cezzis_com_availability_test_response_string,
                ),
            ]
            self.availability_tests = tests
        return self


_logger: logging.Logger = logging.getLogger("scheduler_options")

_scheduler_options: SchedulerOptions | None = None


def get_scheduler_options() -> SchedulerOptions:
    """Get the singleton instance of SchedulerOptions.

    Returns:
        SchedulerOptions: The scheduler options instance.
    """
    global _scheduler_options
    if _scheduler_options is None:
        _scheduler_options = SchedulerOptions()

        _logger.info("Scheduler options loaded successfully.")

    return _scheduler_options


def clear_scheduler_options_cache() -> None:
    """Clear the cached options instance. Useful for testing."""
    global _scheduler_options
    _scheduler_options = None
