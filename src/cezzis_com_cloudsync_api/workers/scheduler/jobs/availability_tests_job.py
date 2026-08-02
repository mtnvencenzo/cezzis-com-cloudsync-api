import asyncio
import logging
from typing import cast

from injector import inject
from mediatr import Mediator

from cezzis_com_cloudsync_api.application.concerns.availability.commands.availability_test_command import (
    AvailabilityTestCommand,
)
from cezzis_com_cloudsync_api.domain.config.scheduler_options import SchedulerOptions

logger = logging.getLogger("availability_tests_job")


class AvailabilityTestsJob:
    """Job class for running availability tests."""

    @inject
    def __init__(self, mediator: Mediator, scheduler_options: SchedulerOptions):
        self.mediator = mediator
        self.scheduler_options = scheduler_options

    async def _run_single_test_with_delay(self, test, delay: int) -> None:
        """Helper to delay and then safely execute a single test."""
        if delay > 0:
            # Non-blocking wait before starting this specific test
            await asyncio.sleep(delay)

        try:
            cast(
                bool,
                await self.mediator.send_async(AvailabilityTestCommand(test)),
            )
        except Exception as ex:
            logger.exception("Availability test '%s' encountered an error: %s", test.name, str(ex), exc_info=ex)

    async def execute(self) -> None:
        """Execute the availability tests job."""
        logger.info("Executing availability tests job")
        tests = self.scheduler_options.availability_tests
        total_tests = len(tests)
        MAX_START_WINDOW = 600
        interval = MAX_START_WINDOW // (total_tests - 1) if total_tests > 1 else 0

        # Build a list of delayed background tasks
        tasks = []
        for index, test in enumerate(tests):
            delay = index * interval

            task = self._run_single_test_with_delay(test, delay)
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks)
