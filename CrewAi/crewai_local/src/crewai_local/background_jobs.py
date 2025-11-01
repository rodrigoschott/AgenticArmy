"""
Background job management for async workflow execution.

Manages job queue, status tracking, and webhook callbacks.
"""

import time
import asyncio
from datetime import datetime
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
import httpx

from .models.responses import JobStatus, JobStatusResponse
from .api_config import APIConfig


@dataclass
class Job:
    """Job data structure."""

    job_id: str
    workflow: str
    status: JobStatus = JobStatus.QUEUED
    input_data: dict = field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0  # 0-100

    def elapsed_time(self) -> Optional[float]:
        """Calculate elapsed time in seconds."""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()


class JobManager:
    """
    Manages background job execution and status tracking.

    Features:
    - Job queue with status tracking
    - Concurrent job execution limit
    - Webhook callbacks on completion
    - Job cancellation support
    """

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self._lock = asyncio.Lock()

    def create_job(self, job_id: str, workflow: str, input_data: dict) -> Job:
        """Create a new job."""
        job = Job(
            job_id=job_id,
            workflow=workflow,
            input_data=input_data,
        )
        self.jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def get_job_status(self, job_id: str) -> JobStatusResponse:
        """Get job status response."""
        job = self.jobs.get(job_id)

        if not job:
            raise ValueError(f"Job {job_id} not found")

        return JobStatusResponse(
            job_id=job.job_id,
            workflow=job.workflow,
            status=job.status,
            progress=job.progress,
            started_at=job.started_at,
            completed_at=job.completed_at,
            elapsed_time=job.elapsed_time(),
            result=job.result if job.status == JobStatus.COMPLETED else None,
            error=job.error if job.status == JobStatus.FAILED else None,
        )

    def get_active_jobs(self) -> list[dict]:
        """Get list of active jobs (queued or running)."""
        active = []
        for job in self.jobs.values():
            if job.status in [JobStatus.QUEUED, JobStatus.RUNNING]:
                active.append({
                    "job_id": job.job_id,
                    "workflow": job.workflow,
                    "status": job.status.value,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "elapsed_time": job.elapsed_time(),
                })
        return active

    def get_active_count(self) -> int:
        """Get count of active jobs."""
        return len([j for j in self.jobs.values() if j.status in [JobStatus.QUEUED, JobStatus.RUNNING]])

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        job = self.jobs.get(job_id)

        if not job:
            return False

        if job.status in [JobStatus.QUEUED, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            return True

        return False

    def cancel_all_jobs(self):
        """Cancel all running jobs (called on shutdown)."""
        for job in self.jobs.values():
            if job.status in [JobStatus.QUEUED, JobStatus.RUNNING]:
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.now()

    async def execute_job(
        self,
        job_id: str,
        executor: Callable,
        request_data: Any,
        webhook_url: Optional[str] = None
    ):
        """
        Execute a job in the background.

        Args:
            job_id: Unique job identifier
            executor: Async function to execute the workflow
            request_data: Request data to pass to executor
            webhook_url: Optional webhook URL for callback
        """
        job = self.jobs.get(job_id)

        if not job:
            print(f"[ERROR] Job {job_id} not found")
            return

        try:
            # Update status to running
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            print(f"[START] Job {job_id} started ({job.workflow})")

            # Execute workflow
            start_time = time.time()
            workflow_result = await executor(request_data)
            execution_time = time.time() - start_time

            # Update job with result
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.progress = 100
            job.result = {
                **workflow_result,
                "execution_time": execution_time,
            }

            print(f"[OK] Job {job_id} completed in {execution_time:.1f}s")

            # Send webhook if configured
            if webhook_url:
                await self._send_webhook(
                    url=webhook_url,
                    job_id=job_id,
                    workflow=job.workflow,
                    status="completed",
                    result=job.result
                )

        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            print(f"[STOP] Job {job_id} cancelled")

        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error = str(e)
            print(f"[ERROR] Job {job_id} failed: {e}")

            # Send webhook with error
            if webhook_url:
                await self._send_webhook(
                    url=webhook_url,
                    job_id=job_id,
                    workflow=job.workflow,
                    status="failed",
                    error=str(e)
                )

    async def _send_webhook(
        self,
        url: str,
        job_id: str,
        workflow: str,
        status: str,
        result: Optional[dict] = None,
        error: Optional[str] = None,
    ):
        """Send webhook callback."""
        payload = {
            "job_id": job_id,
            "workflow": workflow,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }

        if result:
            payload["result"] = result

        if error:
            payload["error"] = error

        # Retry logic
        async with httpx.AsyncClient(timeout=APIConfig.WEBHOOK_TIMEOUT) as client:
            for attempt in range(APIConfig.WEBHOOK_RETRY_COUNT):
                try:
                    response = await client.post(url, json=payload)
                    if response.status_code < 400:
                        print(f"[OK] Webhook sent to {url} (job {job_id})")
                        return

                    print(f"[WARN] Webhook returned {response.status_code}, retrying...")
                except Exception as e:
                    print(f"[ERROR] Webhook error (attempt {attempt + 1}/{APIConfig.WEBHOOK_RETRY_COUNT}): {e}")

                if attempt < APIConfig.WEBHOOK_RETRY_COUNT - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        print(f"[ERROR] Webhook failed after {APIConfig.WEBHOOK_RETRY_COUNT} attempts (job {job_id})")
