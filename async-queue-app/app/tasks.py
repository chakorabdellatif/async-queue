"""
tasks.py — Celery task definitions

Each task:
  1. Immediately writes "processing" to Redis so the status endpoint can see it
  2. Does some simulated work
  3. Writes the final result back to Redis

The `bind=True` parameter gives the task access to `self`, which lets us
call `self.retry()` and inspect retry metadata.
"""

import time
import random
import json
import redis
import logging

from app.celery_app import celery

logger = logging.getLogger(__name__)

# Direct Redis client — we write job status here ourselves so the
# GET /jobs/{id} endpoint can read progress even mid-task.
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _set_status(job_id: str, status: str, result=None, error=None):
    """Persist job state to a Redis hash keyed by job_id."""
    data = {"status": status}
    if result is not None:
        data["result"] = json.dumps(result)
    if error is not None:
        data["error"] = error
    r.hset(f"job:{job_id}", mapping=data)
    r.expire(f"job:{job_id}", 3600)   # Auto-clean after 1 h


# ── Tasks ─────────────────────────────────────────────────────────────────────

@celery.task(
    bind=True,
    name="app.tasks.process_data",
    max_retries=3,
    default_retry_delay=5,   # seconds between retries (base; see autoretry note)
)
def process_data(self, job_id: str, payload: dict):
    """
    Simulates a data-processing job (ETL, transformation, etc.).
    Always succeeds — good baseline task to study.
    """
    logger.info("[%s] process_data started | payload=%s", job_id, payload)
    _set_status(job_id, "processing")

    # Simulate actual work taking some time
    rows    = payload.get("rows", 500)
    seconds = min(rows / 1000, 5)   # Cap at 5 s so demos stay snappy
    time.sleep(seconds)

    result = {
        "rows_processed": rows,
        "format": payload.get("format", "csv"),
        "duration_s": round(seconds, 2),
    }

    _set_status(job_id, "done", result=result)
    logger.info("[%s] process_data done | result=%s", job_id, result)
    return result


@celery.task(
    bind=True,
    name="app.tasks.send_report",
    max_retries=3,
    default_retry_delay=10,
)
def send_report(self, job_id: str, payload: dict):
    """
    Simulates a slow external API call (email, Slack notification, etc.).
    Always succeeds but takes longer — shows how async decouples latency.
    """
    logger.info("[%s] send_report started | payload=%s", job_id, payload)
    _set_status(job_id, "processing")

    time.sleep(4)   # Pretend we're waiting on a third-party API

    result = {
        "recipient": payload.get("recipient", "team@example.com"),
        "subject":   payload.get("subject",   "Weekly Report"),
        "sent":      True,
    }

    _set_status(job_id, "done", result=result)
    logger.info("[%s] send_report done | result=%s", job_id, result)
    return result


@celery.task(
    bind=True,
    name="app.tasks.flaky_job",
    max_retries=3,
    default_retry_delay=2,
)
def flaky_job(self, job_id: str, payload: dict):
    """
    Randomly fails ~60 % of the time to demonstrate:
      - Task retries with exponential backoff
      - Dead-letter behaviour when max_retries is exhausted
      - The "failed" state visible via GET /jobs/{id}

    Watch in Flower: you'll see the task move from RETRY → RETRY → SUCCESS/FAILURE.
    """
    logger.info(
        "[%s] flaky_job attempt %d/%d",
        job_id, self.request.retries + 1, self.max_retries + 1,
    )
    _set_status(job_id, "processing")

    time.sleep(1)

    # Fail 60 % of the time
    if random.random() < 0.6:
        err_msg = f"Transient error on attempt {self.request.retries + 1}"
        logger.warning("[%s] flaky_job FAILED — %s", job_id, err_msg)

        try:
            # Exponential backoff: 2s, 4s, 8s
            raise self.retry(
                exc=RuntimeError(err_msg),
                countdown=2 ** (self.request.retries + 1),
            )
        except self.MaxRetriesExceededError:
            _set_status(job_id, "failed", error="Max retries exceeded: " + err_msg)
            raise

    result = {"lucky": True, "attempt": self.request.retries + 1}
    _set_status(job_id, "done", result=result)
    logger.info("[%s] flaky_job done | result=%s", job_id, result)
    return result
