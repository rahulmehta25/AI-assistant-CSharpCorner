"""
Job Queue Service for Async AI Operations
Handles long-running tasks like roadmap generation and batch resume analysis
"""

import json
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict

import redis
from redis.exceptions import RedisError


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(int, Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class Job:
    """Represents a background job"""
    id: str
    job_type: str
    payload: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    priority: int = JobPriority.NORMAL
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    attempts: int = 0
    max_attempts: int = 3

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        data["status"] = JobStatus(data.get("status", "pending"))
        return cls(**data)


class QueueService:
    """Redis-based job queue service"""

    # Job type configurations
    JOB_CONFIG = {
        "roadmap_generation": {
            "max_attempts": 3,
            "timeout": 300,  # 5 minutes
            "priority": JobPriority.HIGH,
        },
        "batch_resume_analysis": {
            "max_attempts": 2,
            "timeout": 600,  # 10 minutes
            "priority": JobPriority.NORMAL,
        },
        "skill_assessment": {
            "max_attempts": 3,
            "timeout": 180,  # 3 minutes
            "priority": JobPriority.NORMAL,
        },
        "career_recommendation": {
            "max_attempts": 3,
            "timeout": 120,  # 2 minutes
            "priority": JobPriority.HIGH,
        },
        "cover_letter_generation": {
            "max_attempts": 2,
            "timeout": 120,
            "priority": JobPriority.NORMAL,
        },
        "interview_prep": {
            "max_attempts": 2,
            "timeout": 180,
            "priority": JobPriority.NORMAL,
        },
    }

    QUEUE_PREFIX = "career:queue"
    JOB_PREFIX = "career:job"

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: Optional[redis.Redis] = None
        self._handlers: Dict[str, Callable] = {}

    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
        return self._client

    def register_handler(self, job_type: str, handler: Callable):
        """Register a handler for a job type"""
        self._handlers[job_type] = handler

    async def enqueue(
        self,
        job_type: str,
        payload: Dict[str, Any],
        user_id: Optional[str] = None,
        priority: Optional[int] = None,
    ) -> Job:
        """
        Add a job to the queue

        Args:
            job_type: Type of job (e.g., 'roadmap_generation')
            payload: Job data
            user_id: Optional user ID
            priority: Optional priority override

        Returns:
            Created Job object
        """
        config = self.JOB_CONFIG.get(job_type, {})

        job = Job(
            id=str(uuid.uuid4()),
            job_type=job_type,
            payload=payload,
            status=JobStatus.QUEUED,
            priority=priority or config.get("priority", JobPriority.NORMAL),
            user_id=user_id,
            created_at=datetime.utcnow().isoformat(),
            max_attempts=config.get("max_attempts", 3),
        )

        try:
            # Store job data
            job_key = f"{self.JOB_PREFIX}:{job.id}"
            self.client.hset(job_key, mapping={
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in job.to_dict().items()
            })
            self.client.expire(job_key, 86400 * 7)  # 7 days TTL

            # Add to priority queue
            queue_key = f"{self.QUEUE_PREFIX}:{job_type}"
            self.client.zadd(queue_key, {job.id: -job.priority})

            # Track user's jobs
            if user_id:
                user_queue_key = f"{self.QUEUE_PREFIX}:user:{user_id}"
                self.client.lpush(user_queue_key, job.id)
                self.client.ltrim(user_queue_key, 0, 99)  # Keep last 100

            return job

        except RedisError as e:
            raise RuntimeError(f"Failed to enqueue job: {e}")

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        try:
            job_key = f"{self.JOB_PREFIX}:{job_id}"
            data = self.client.hgetall(job_key)

            if not data:
                return None

            # Parse JSON fields
            for key in ["payload", "result"]:
                if key in data and data[key]:
                    try:
                        data[key] = json.loads(data[key])
                    except json.JSONDecodeError:
                        pass

            # Parse integer fields
            for key in ["priority", "attempts", "max_attempts"]:
                if key in data:
                    data[key] = int(data[key])

            return Job.from_dict(data)

        except RedisError as e:
            print(f"Error getting job: {e}")
            return None

    async def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        result: Optional[Dict] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update job status and result"""
        try:
            job_key = f"{self.JOB_PREFIX}:{job_id}"

            updates = {}
            if status:
                updates["status"] = status.value
            if result:
                updates["result"] = json.dumps(result)
            if error_message:
                updates["error_message"] = error_message

            if status == JobStatus.PROCESSING:
                updates["started_at"] = datetime.utcnow().isoformat()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                updates["completed_at"] = datetime.utcnow().isoformat()

            if updates:
                self.client.hset(job_key, mapping=updates)

            return True

        except RedisError as e:
            print(f"Error updating job: {e}")
            return False

    async def get_user_jobs(
        self,
        user_id: str,
        limit: int = 20,
        status: Optional[JobStatus] = None
    ) -> List[Job]:
        """Get jobs for a user"""
        try:
            user_queue_key = f"{self.QUEUE_PREFIX}:user:{user_id}"
            job_ids = self.client.lrange(user_queue_key, 0, limit - 1)

            jobs = []
            for job_id in job_ids:
                job = await self.get_job(job_id)
                if job and (status is None or job.status == status):
                    jobs.append(job)

            return jobs

        except RedisError as e:
            print(f"Error getting user jobs: {e}")
            return []

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job"""
        job = await self.get_job(job_id)
        if not job:
            return False

        if job.status not in [JobStatus.PENDING, JobStatus.QUEUED]:
            return False

        return await self.update_job(job_id, status=JobStatus.CANCELLED)

    async def dequeue(self, job_type: str) -> Optional[Job]:
        """
        Get the next job from the queue (for workers)

        Returns:
            Next job to process or None
        """
        try:
            queue_key = f"{self.QUEUE_PREFIX}:{job_type}"

            # Get highest priority job
            result = self.client.zpopmin(queue_key, count=1)
            if not result:
                return None

            job_id = result[0][0]
            job = await self.get_job(job_id)

            if job:
                # Update status to processing
                job.status = JobStatus.PROCESSING
                job.attempts += 1
                await self.update_job(job_id, status=JobStatus.PROCESSING)

                # Update attempts
                job_key = f"{self.JOB_PREFIX}:{job_id}"
                self.client.hincrby(job_key, "attempts", 1)

            return job

        except RedisError as e:
            print(f"Error dequeuing job: {e}")
            return None

    async def requeue_failed(self, job_id: str) -> bool:
        """Requeue a failed job for retry"""
        job = await self.get_job(job_id)
        if not job:
            return False

        if job.attempts >= job.max_attempts:
            return False

        try:
            # Reset status
            await self.update_job(job_id, status=JobStatus.QUEUED)

            # Re-add to queue with lower priority
            queue_key = f"{self.QUEUE_PREFIX}:{job.job_type}"
            new_priority = max(1, job.priority - 1)
            self.client.zadd(queue_key, {job_id: -new_priority})

            return True

        except RedisError:
            return False

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            stats = {
                "queues": {},
                "total_pending": 0,
                "total_processing": 0,
            }

            for job_type in self.JOB_CONFIG.keys():
                queue_key = f"{self.QUEUE_PREFIX}:{job_type}"
                count = self.client.zcard(queue_key)
                stats["queues"][job_type] = count
                stats["total_pending"] += count

            return stats

        except RedisError as e:
            return {"error": str(e)}

    async def cleanup_old_jobs(self, days: int = 7) -> int:
        """Clean up completed/failed jobs older than specified days"""
        # This would need to be implemented with a scan of job keys
        # For now, we rely on Redis TTL
        return 0


# Singleton instance
_queue_service: Optional[QueueService] = None


def get_queue_service() -> QueueService:
    """Get the global queue service instance"""
    global _queue_service
    if _queue_service is None:
        _queue_service = QueueService()
    return _queue_service
