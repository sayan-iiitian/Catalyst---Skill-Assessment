"""
Pydantic models for data validation and serialization
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class ProficiencyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class SkillAssessment(BaseModel):
    """Assessment result for a single skill"""
    skill_name: str
    proficiency_level: ProficiencyLevel
    confidence_score: float = Field(ge=0, le=1)
    gap_analysis: str
    evidence: List[str] = Field(default_factory=list)


class LearningResource(BaseModel):
    """A resource for learning"""
    title: str
    description: str
    resource_type: str  # 'course', 'book', 'tutorial', 'documentation', 'project'
    url: Optional[str] = None
    estimated_hours: int = Field(ge=1, le=100)
    difficulty: str  # 'beginner', 'intermediate', 'advanced'


class SkillGap(BaseModel):
    """Identified skill gap"""
    skill_name: str
    required_level: ProficiencyLevel
    current_level: ProficiencyLevel
    priority: str  # 'critical', 'high', 'medium', 'low'
    gap_description: str


class LearningPlan(BaseModel):
    """Personalized learning plan for a candidate"""
    candidate_name: str
    job_title: str
    created_at: str
    skill_gaps: List[SkillGap]
    learning_recommendations: Dict[str, List[LearningResource]]
    total_estimated_hours: int
    priority_focus_areas: List[str]
    success_metrics: List[str]


class AssessmentRequest(BaseModel):
    """Request for skill assessment"""
    job_description: str
    resume: str
    candidate_name: Optional[str] = "Candidate"


class AssessmentResult(BaseModel):
    """Complete assessment result"""
    assessments: List[SkillAssessment]
    learning_plan: LearningPlan
    overall_fit_score: float = Field(ge=0, le=1)
    summary: str
