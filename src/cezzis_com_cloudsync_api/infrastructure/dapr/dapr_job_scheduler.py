"""Dapr job scheduling for application initialization."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx

from cezzis_com_cloudsync_api.domain.config.dapr_options import DaprOptions, get_dapr_options

logger = logging.getLogger("dapr_job_scheduler")

_dapr_options: DaprOptions = get_dapr_options()


async def _wait_for_dapr_sidecar() -> bool:
    """Wait for the Dapr sidecar to become ready, with retries.

    Returns True if the sidecar is ready, False if it could not be reached.
    """
    health_url = f"{_dapr_options.http_endpoint}/v1.0/healthz"
    headers = {}
    if _dapr_options.dapr_api_token:
        headers["dapr-api-token"] = _dapr_options.dapr_api_token

    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(health_url, headers=headers, timeout=5.0)
                if response.status_code in (200, 204):
                    logger.info("Dapr sidecar is ready (attempt %d/%d)", attempt, max_attempts)
                    return True
                logger.info(
                    "Dapr sidecar not ready yet: status=%d (attempt %d/%d)", response.status_code, attempt, max_attempts
                )
        except httpx.ConnectError:
            logger.info("Dapr sidecar not reachable yet (attempt %d/%d)", attempt, max_attempts)
        except Exception:
            logger.info("Dapr sidecar health check failed (attempt %d/%d)", attempt, max_attempts)

        await asyncio.sleep(3)

    return False


async def schedule_dapr_init_job() -> None:
    """Schedule the initialize-app Dapr job to run after a short delay.

    This function schedules a one-time Dapr job that will call the /job/initialize-app
    endpoint after 10 seconds. This is used to run database migrations and seed the
    test account on application startup.

    The job is scheduled via the Dapr Jobs API (scheduler building block).
    If the job scheduling fails (e.g., Dapr scheduler not available), the error is
    logged but does not prevent the application from starting.
    """
    if not _dapr_options.init_job_enabled:
        logger.info("Dapr init job is disabled, skipping job scheduling")
        return

    try:
        # Wait for the Dapr sidecar to be ready before scheduling the job
        sidecar_ready = await _wait_for_dapr_sidecar()
        if not sidecar_ready:
            logger.warning(
                "Dapr sidecar did not become ready after retries. App initialization can be triggered manually."
            )
            return

        # Calculate when the job should run (120 seconds from now to allow old pods to terminate during rolling updates)
        due_time = datetime.now(timezone.utc) + timedelta(seconds=120)

        # Job specification for Dapr scheduler
        # Note: The 'data' field must be a valid protobuf Value (string, number, bool, struct, list)
        # An empty object or missing data can cause "none of the oneof fields is set" errors
        job_spec = {
            "dueTime": due_time.isoformat(),
            "repeats": 1,
            "data": {
                "@type": "type.googleapis.com/google.protobuf.StringValue",
                "value": "initialize",
            },
        }

        # Build the Dapr jobs API URL
        jobs_url = f"{_dapr_options.http_endpoint}/v1.0-alpha1/jobs/initialize-app"

        headers = {
            "Content-Type": "application/json",
        }
        if _dapr_options.dapr_api_token:
            headers["dapr-api-token"] = _dapr_options.dapr_api_token

        logger.info("Scheduling initialize-app Dapr job to run at %s", due_time.isoformat())

        async with httpx.AsyncClient() as client:
            response = await client.post(
                jobs_url,
                json=job_spec,
                headers=headers,
                timeout=10.0,
            )

            if response.status_code in (200, 201, 204):
                logger.info("Successfully scheduled initialize-app job")
            else:
                logger.warning(
                    "Failed to schedule initialize-app job: status=%d, body=%s",
                    response.status_code,
                    response.text,
                )

    except httpx.ConnectError:
        logger.warning(
            "Could not connect to Dapr sidecar to schedule init job. "
            "Dapr scheduler may not be available. App initialization can be triggered manually."
        )
    except Exception as e:
        logger.error("Failed to schedule initialize-app job", exc_info=e)


def schedule_init_job_background() -> None:
    """Schedule the init job to run in the background.

    This function creates a background task to schedule the Dapr init job.
    It should be called during application startup.
    """
    if not _dapr_options.init_job_enabled:
        logger.info("Dapr init job is disabled")
        return

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(schedule_dapr_init_job())
        logger.info("Background task created to schedule Dapr init job")
    except RuntimeError:
        # No running event loop, try to run directly
        logger.warning("No running event loop, attempting to run job scheduling synchronously")
        asyncio.run(schedule_dapr_init_job())
