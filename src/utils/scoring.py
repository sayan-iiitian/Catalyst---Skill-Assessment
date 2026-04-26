"""
Skill gap and fit scoring logic
"""
from typing import List, Dict, Tuple
from src.schemas.models import SkillAssessment, ProficiencyLevel, SkillGap


class ScoringEngine:
    """Calculate proficiency scores and fit metrics"""

    PROFICIENCY_SCORES = {
        ProficiencyLevel.BEGINNER: 1,
        ProficiencyLevel.INTERMEDIATE: 2,
        ProficiencyLevel.ADVANCED: 3,
        ProficiencyLevel.EXPERT: 4,
    }

    JOB_REQUIREMENT_SCORES = {
        "required": 4,
        "critical": 4,
        "essential": 4,
        "must": 4,
        "preferred": 2,
        "nice": 1,
        "bonus": 1,
    }

    @classmethod
    def calculate_skill_gap(
        cls,
        assessment: SkillAssessment,
        required_level: ProficiencyLevel
    ) -> SkillGap:
        """Calculate gap between assessed and required proficiency"""

        current_score = cls.PROFICIENCY_SCORES.get(assessment.proficiency_level, 1)
        required_score = cls.PROFICIENCY_SCORES.get(required_level, 3)
        gap = required_score - current_score

        # Determine priority
        if gap <= 0:
            priority = "none"
        elif gap == 1:
            priority = "low"
        elif gap == 2:
            priority = "medium"
        else:
            priority = "critical"

        # Generate gap description
        current_level = assessment.proficiency_level
        description = f"Currently at {current_level} level, need to reach {required_level}. "

        if gap > 0:
            steps = {
                1: "Need minor skill enhancement",
                2: "Need significant skill development",
                3: "Need major skill transformation"
            }
            description += steps.get(min(gap, 3), "Need comprehensive reskilling")

        return SkillGap(
            skill_name=assessment.skill_name,
            required_level=required_level,
            current_level=assessment.proficiency_level,
            priority=priority,
            gap_description=description
        )

    @classmethod
    def calculate_overall_fit(cls, assessments: List[SkillAssessment]) -> float:
        """Calculate overall fit score (0-1)"""
        if not assessments:
            return 0.0

        total_score = sum(
            cls.PROFICIENCY_SCORES.get(a.proficiency_level, 1) * a.confidence_score
            for a in assessments
        )

        max_possible = sum(
            4 * a.confidence_score for a in assessments  # Max proficiency = 4
        )

        if max_possible == 0:
            return 0.5

        fit_score = total_score / max_possible
        return min(1.0, max(0.0, fit_score))

    @classmethod
    def calculate_learning_priority(
        cls,
        gaps: List[SkillGap],
        total_hours_available: int = 100
    ) -> Dict[str, int]:
        """Calculate time allocation for learning based on gaps"""

        priority_mapping = {
            "critical": 40,  # 40% of time
            "high": 30,      # 30% of time
            "medium": 20,    # 20% of time
            "low": 10,       # 10% of time
        }

        allocation = {}
        critical_gaps = [g for g in gaps if g.priority == "critical"]
        high_gaps = [g for g in gaps if g.priority == "high"]
        medium_gaps = [g for g in gaps if g.priority == "medium"]
        low_gaps = [g for g in gaps if g.priority == "low"]

        # Distribute time proportionally within each priority level
        for gap in critical_gaps:
            time = int((total_hours_available * priority_mapping["critical"] / 100) / len(critical_gaps)) if critical_gaps else 0
            allocation[gap.skill_name] = max(5, time)

        for gap in high_gaps:
            time = int((total_hours_available * priority_mapping["high"] / 100) / len(high_gaps)) if high_gaps else 0
            allocation[gap.skill_name] = max(4, time)

        for gap in medium_gaps:
            time = int((total_hours_available * priority_mapping["medium"] / 100) / len(medium_gaps)) if medium_gaps else 0
            allocation[gap.skill_name] = max(3, time)

        for gap in low_gaps:
            time = int((total_hours_available * priority_mapping["low"] / 100) / len(low_gaps)) if low_gaps else 0
            allocation[gap.skill_name] = max(2, time)

        return allocation
