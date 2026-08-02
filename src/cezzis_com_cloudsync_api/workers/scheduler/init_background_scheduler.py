"""This module initializes the background scheduler for the accounts API.

The scheduler is responsible for running periodic background jobs, such as sending notifications for new cocktails. It uses the APScheduler library to manage job scheduling and execution.
The `start_background_scheduler` function sets up the scheduler and adds the necessary jobs. This function should be called during the application startup phase, typically within the FastAPI lifespan event handler.
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from injector import Injector

from cezzis_com_cloudsync_api.domain.config.scheduler_options import get_scheduler_options
from cezzis_com_cloudsync_api.workers.scheduler.cron_utils import parse_cron_schedule
from cezzis_com_cloudsync_api.workers.scheduler.jobs.availability_tests_job import AvailabilityTestsJob

logger = logging.getLogger("init_background_scheduler")


def start_background_scheduler(injector: Injector) -> None:
    """Start the background scheduler and add jobs.

    Should be called during application startup (FastAPI lifespan).

    Args:
        injector: The Injector instance for resolving job dependencies.
    """
    scheduler = AsyncIOScheduler(
        {
            "apscheduler.executors.default": {
                "class": "apscheduler.executors.asyncio:AsyncIOExecutor",
            },
            "apscheduler.executors.threadpool": {
                "class": "apscheduler.executors.pool:ThreadPoolExecutor",
                "max_workers": "20",
            },
            "apscheduler.executors.processpool": {"type": "processpool", "max_workers": "5"},
            "apscheduler.job_defaults.coalesce": "false",
            "apscheduler.job_defaults.max_instances": "1",
            "apscheduler.timezone": "UTC",
        }
    )
    scheduler.start()

    scheduler_options = get_scheduler_options()

    availability_tests_job_cron = parse_cron_schedule(scheduler_options.availability_tests_cron)
    availability_tests_job = injector.get(AvailabilityTestsJob)

    scheduler.add_job(
        id="availability_tests_job",
        func=availability_tests_job.execute,
        name="Availability Tests Job",
        max_instances=1,
        trigger="cron",
        **availability_tests_job_cron,
    )
