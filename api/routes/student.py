"""
Student pathway endpoints.
"""

from fastapi import APIRouter, Depends

from api.dependencies.rate_limit import rate_limit_ai
from models.student import StudentPathway, StudentPathwayRequest
from services.student_service import student_service

router = APIRouter(prefix="/student", tags=["Student Pathways"])


@router.post("/pathway", response_model=StudentPathway)
async def generate_pathway(
    request: StudentPathwayRequest,
    _: None = Depends(rate_limit_ai),
):
    """
    Generate a personalized student pathway.

    For high school and college students planning their career.

    Includes:
    - Academic milestones
    - Course recommendations
    - Extracurricular activities
    - Skills to develop
    - Timeline by semester/year
    - AI-powered personalized advice
    """
    return await student_service.generate_pathway(request)
