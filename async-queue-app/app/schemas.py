# Pydantic models
# used to define :
# what data the API accepts and returns with validation rules
from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum


class JobType(str, Enum):
    """
    The type of simulated job to run.
    Each maps to a different code path in tasks.py.
    """
    PROCESS_DATA = "process_data"   # Simulates a data transformation
    SEND_REPORT  = "send_report"    # Simulates a slow external API call
    FLAKY_JOB    = "flaky_job"      # Randomly fails — demonstrates retry logic


class JobStatus(str, Enum):
    PENDING    = "pending"     # Enqueued, not yet picked up by a worker
    PROCESSING = "processing"  # Worker has started on it
    DONE       = "done"        # Finished successfully
    FAILED     = "failed"      # Failed after all retries exhausted


# ── Request body for POST /jobs ───────────────────────────────────────────────

class JobRequest(BaseModel):
    job_type: JobType
    payload: dict = {}           # Arbitrary data the task can use

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_type": "process_data",
                "payload": {"rows": 1000, "format": "csv"},
            }
        }
    }


# ── Response bodies ───────────────────────────────────────────────────────────

class JobSubmitResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[Any] = None   # Present when status == "done"
    error:  Optional[str] = None   # Present when status == "failed"
