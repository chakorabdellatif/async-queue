# FastAPO main endpoints
"""
main.py — FastAPI application

Two endpoints:
  POST /jobs        — Accept a job, enqueue it via Celery, return job_id immediately
  GET  /jobs/{id}   — Read current status/result from Redis

The key async insight: POST /jobs returns in < 5 ms regardless of how long
the job takes, because the actual work happens in a separate Celery worker process.
"""

import uuid
import json
import redis
import logging

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from app.schemas import (
    JobRequest, JobStatus,
    JobSubmitResponse, JobStatusResponse,
)
from app.tasks import process_data, send_report, flaky_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Redis client — same instance the workers write to
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# Map job_type string → Celery task function
TASK_MAP = {
    "process_data": process_data,
    "send_report":  send_report,
    "flaky_job":    flaky_job,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 async-queue-app API starting up")
    yield
    logger.info("🛑 async-queue-app API shutting down")


app = FastAPI(
    title="async-queue-app",
    description=(
        "async and queue systems mini app with FastAPI + Celery + Redis.\n\n"
        "**Flow:** POST /jobs → Celery enqueues → worker processes → GET /jobs/{id} polls result"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── POST /jobs ────────────────────────────────────────────────────────────────

@app.post("/jobs", response_model=JobSubmitResponse, status_code=202)
async def submit_job(body: JobRequest):
    """
    Submit a new background job.

    Returns a `job_id` immediately (HTTP 202 Accepted).
    The actual work happens asynchronously in a Celery worker.
    Poll `GET /jobs/{job_id}` to check progress.
    """
    job_id = str(uuid.uuid4())

    # Write initial "pending" state to Redis BEFORE enqueuing.
    # This prevents a race where the client polls before the worker
    # has had a chance to write its own "processing" state.
    r.hset(f"job:{job_id}", mapping={"status": "pending"})
    r.expire(f"job:{job_id}", 3600)

    # .delay() is shorthand for .apply_async() — it serialises the arguments
    # to JSON and pushes the message onto the Redis queue. Non-blocking.
    task_fn = TASK_MAP[body.job_type]
    task_fn.delay(job_id, body.payload)

    logger.info("Enqueued job %s | type=%s", job_id, body.job_type)

    return JobSubmitResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Job enqueued. Poll GET /jobs/{job_id} for status.",
    )


# ── GET /jobs/{job_id} ────────────────────────────────────────────────────────

@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Check the current status of a job.

    Status lifecycle: `pending → processing → done | failed`
    """
    data = r.hgetall(f"job:{job_id}")

    if not data:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    result = None
    if "result" in data:
        try:
            result = json.loads(data["result"])
        except json.JSONDecodeError:
            result = data["result"]

    return JobStatusResponse(
        job_id=job_id,
        status=JobStatus(data["status"]),
        result=result,
        error=data.get("error"),
    )


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Used by Docker Compose healthcheck."""
    try:
        r.ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    return {"api": "ok", "redis": "ok" if redis_ok else "unavailable"}
