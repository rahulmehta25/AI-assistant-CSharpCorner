"""
Queue Worker for Processing Background Jobs
Handles roadmap generation, resume analysis, and other async AI operations
"""

import asyncio
import json
import os
import signal
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.queue import QueueService, JobStatus, get_queue_service
from backend.services.cache import CacheService, get_cache_service


class QueueWorker:
    """Background worker for processing queued jobs"""

    def __init__(self, debug: bool = False):
        self.queue = get_queue_service()
        self.cache = get_cache_service()
        self.debug = debug
        self.running = True
        self.current_job = None

        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        # Register job handlers
        self._handlers = {
            "roadmap_generation": self._process_roadmap_generation,
            "batch_resume_analysis": self._process_batch_resume_analysis,
            "skill_assessment": self._process_skill_assessment,
            "career_recommendation": self._process_career_recommendation,
            "cover_letter_generation": self._process_cover_letter_generation,
            "interview_prep": self._process_interview_prep,
        }

    def _handle_shutdown(self, signum, frame):
        """Handle graceful shutdown"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.utcnow().isoformat()
        print(f"[{timestamp}] [{level}] {message}")

    async def _process_roadmap_generation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process roadmap generation job"""
        self.log(f"Processing roadmap generation for user: {payload.get('user_id')}")

        try:
            # Import the roadmap generator
            from modules.roadmap_generator import RoadmapGenerator

            generator = RoadmapGenerator()

            user_profile = payload.get("profile", {})
            target_role = payload.get("target_role")
            timeline = payload.get("timeline", "2 years")

            # Generate the roadmap
            roadmap = generator.generate_roadmap(
                current_skills=user_profile.get("skills", []),
                target_role=target_role,
                experience_years=user_profile.get("experience_years", 0),
                timeline=timeline,
            )

            # Cache the result
            cache_key = f"roadmap:{payload.get('user_id')}:{target_role}"
            await self.cache.set("roadmap", roadmap, cache_key)

            return {
                "success": True,
                "roadmap": roadmap,
                "cached": True,
            }

        except Exception as e:
            self.log(f"Roadmap generation failed: {e}", "ERROR")
            raise

    async def _process_batch_resume_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process batch resume analysis job"""
        self.log(f"Processing batch resume analysis: {len(payload.get('resumes', []))} resumes")

        try:
            from modules.application_assistant import ApplicationAssistant

            assistant = ApplicationAssistant()
            resumes = payload.get("resumes", [])
            job_description = payload.get("job_description", "")

            results = []
            for i, resume in enumerate(resumes):
                self.log(f"Analyzing resume {i + 1}/{len(resumes)}")

                analysis = assistant.analyze_resume(resume, job_description)
                results.append({
                    "index": i,
                    "analysis": analysis,
                })

            return {
                "success": True,
                "results": results,
                "total_analyzed": len(results),
            }

        except Exception as e:
            self.log(f"Batch resume analysis failed: {e}", "ERROR")
            raise

    async def _process_skill_assessment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process skill assessment job"""
        self.log(f"Processing skill assessment for user: {payload.get('user_id')}")

        try:
            from modules.skills_assessment import SkillsAssessment

            assessor = SkillsAssessment()

            user_skills = payload.get("skills", [])
            target_role = payload.get("target_role")

            assessment = assessor.assess_skills(
                current_skills=user_skills,
                target_role=target_role,
            )

            return {
                "success": True,
                "assessment": assessment,
            }

        except Exception as e:
            self.log(f"Skill assessment failed: {e}", "ERROR")
            raise

    async def _process_career_recommendation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process career recommendation job"""
        self.log(f"Processing career recommendation for user: {payload.get('user_id')}")

        try:
            from modules.recommendation_engine import RecommendationEngine

            engine = RecommendationEngine()

            profile = payload.get("profile", {})
            recommendations = engine.generate_recommendations(profile)

            return {
                "success": True,
                "recommendations": recommendations,
            }

        except Exception as e:
            self.log(f"Career recommendation failed: {e}", "ERROR")
            raise

    async def _process_cover_letter_generation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process cover letter generation job"""
        self.log(f"Processing cover letter for: {payload.get('company')}")

        try:
            from modules.application_assistant import ApplicationAssistant

            assistant = ApplicationAssistant()

            user_info = payload.get("user_info", {})
            job_info = payload.get("job_info", {})
            template_type = payload.get("template_type", "standard")

            cover_letter = assistant.generate_cover_letter(
                user_info=user_info,
                job_info=job_info,
                template_type=template_type,
            )

            return {
                "success": True,
                "cover_letter": cover_letter,
            }

        except Exception as e:
            self.log(f"Cover letter generation failed: {e}", "ERROR")
            raise

    async def _process_interview_prep(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process interview preparation job"""
        self.log(f"Processing interview prep for: {payload.get('job_title')}")

        try:
            from modules.application_assistant import ApplicationAssistant

            assistant = ApplicationAssistant()

            job_title = payload.get("job_title")
            job_description = payload.get("job_description", "")
            experience_level = payload.get("experience_level", "Mid-Level")

            questions = assistant.generate_interview_questions(
                job_title=job_title,
                job_description=job_description,
                experience_level=experience_level,
            )

            return {
                "success": True,
                "questions": questions,
            }

        except Exception as e:
            self.log(f"Interview prep failed: {e}", "ERROR")
            raise

    async def process_job(self, job) -> bool:
        """Process a single job"""
        self.current_job = job
        handler = self._handlers.get(job.job_type)

        if not handler:
            self.log(f"No handler for job type: {job.job_type}", "ERROR")
            await self.queue.update_job(
                job.id,
                status=JobStatus.FAILED,
                error_message=f"Unknown job type: {job.job_type}",
            )
            return False

        try:
            self.log(f"Processing job {job.id} ({job.job_type})")

            result = await handler(job.payload)

            await self.queue.update_job(
                job.id,
                status=JobStatus.COMPLETED,
                result=result,
            )

            self.log(f"Job {job.id} completed successfully")
            return True

        except Exception as e:
            error_msg = str(e)
            self.log(f"Job {job.id} failed: {error_msg}", "ERROR")

            # Check if we should retry
            if job.attempts < job.max_attempts:
                self.log(f"Requeuing job {job.id} (attempt {job.attempts}/{job.max_attempts})")
                await self.queue.requeue_failed(job.id)
            else:
                await self.queue.update_job(
                    job.id,
                    status=JobStatus.FAILED,
                    error_message=error_msg,
                )

            return False

        finally:
            self.current_job = None

    async def run(self, job_types: Optional[list] = None):
        """Main worker loop"""
        job_types = job_types or list(self._handlers.keys())

        self.log(f"Worker starting, processing: {', '.join(job_types)}")
        self.log(f"Debug mode: {self.debug}")

        while self.running:
            try:
                # Round-robin through job types
                for job_type in job_types:
                    if not self.running:
                        break

                    job = await self.queue.dequeue(job_type)

                    if job:
                        await self.process_job(job)
                    else:
                        # Small delay if no jobs found
                        await asyncio.sleep(0.1)

                # Pause between rounds if no jobs
                await asyncio.sleep(1)

            except Exception as e:
                self.log(f"Worker error: {e}", "ERROR")
                await asyncio.sleep(5)

        self.log("Worker stopped")


async def main():
    """Entry point for the worker"""
    import argparse

    parser = argparse.ArgumentParser(description="Queue Worker")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--job-types", nargs="+", help="Specific job types to process")
    args = parser.parse_args()

    worker = QueueWorker(debug=args.debug)
    await worker.run(job_types=args.job_types)


if __name__ == "__main__":
    asyncio.run(main())
