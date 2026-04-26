"""
Learning Plan Agent - Generates personalized learning plans
"""
import json
from typing import List, Dict
from datetime import datetime
from src.models.llm_client import get_llm_client
from src.schemas.models import (
    SkillGap, LearningResource, LearningPlan, ProficiencyLevel
)
from src.utils.scoring import ScoringEngine


class PlanningAgent:
    """Generates personalized learning plans based on skill gaps"""

    LEARNING_RESOURCES_DB = {
        "Python": [
            LearningResource(
                title="Python for Everybody",
                description="Comprehensive Python course from basics to advanced",
                resource_type="course",
                url="https://www.coursera.org/learn/python",
                estimated_hours=30,
                difficulty="beginner"
            ),
            LearningResource(
                title="Advanced Python Programming",
                description="Deep dive into Python design patterns and advanced features",
                resource_type="course",
                url="https://realpython.com",
                estimated_hours=25,
                difficulty="advanced"
            ),
            LearningResource(
                title="Fluent Python by Luciano Ramalho",
                description="Master Python's elegant features",
                resource_type="book",
                estimated_hours=20,
                difficulty="advanced"
            ),
        ],
        "JavaScript": [
            LearningResource(
                title="The Complete JavaScript Course",
                description="Modern JavaScript from basics to async/await",
                resource_type="course",
                url="https://www.udemy.com/course/the-complete-javascript-course-2024",
                estimated_hours=40,
                difficulty="beginner"
            ),
            LearningResource(
                title="You Don't Know JS Yet",
                description="Deep JavaScript concepts and internals",
                resource_type="book",
                estimated_hours=25,
                difficulty="advanced"
            ),
        ],
        "React": [
            LearningResource(
                title="React Official Documentation",
                description="Official React docs with examples",
                resource_type="documentation",
                url="https://react.dev",
                estimated_hours=15,
                difficulty="beginner"
            ),
            LearningResource(
                title="Advanced React Patterns",
                description="High-order components, render props, hooks",
                resource_type="course",
                url="https://epicreact.dev",
                estimated_hours=20,
                difficulty="advanced"
            ),
        ],
        "AWS": [
            LearningResource(
                title="AWS Certified Solutions Architect",
                description="Comprehensive AWS cloud services training",
                resource_type="course",
                url="https://www.coursera.org/learn/aws-cloud-practitioner",
                estimated_hours=35,
                difficulty="intermediate"
            ),
            LearningResource(
                title="AWS Documentation & Labs",
                description="Hands-on AWS service exploration",
                resource_type="documentation",
                url="https://aws.amazon.com/training",
                estimated_hours=25,
                difficulty="intermediate"
            ),
        ],
        "System Design": [
            LearningResource(
                title="Designing Data-Intensive Applications",
                description="Foundational concepts for scalable systems",
                resource_type="book",
                estimated_hours=30,
                difficulty="advanced"
            ),
            LearningResource(
                title="System Design Interview Course",
                description="Practical system design problem solving",
                resource_type="course",
                url="https://www.educative.io/courses/grokking-the-system-design-interview",
                estimated_hours=25,
                difficulty="advanced"
            ),
        ],
    }

    def __init__(self):
        self.llm = get_llm_client()
        self.scoring = ScoringEngine()

    def generate_learning_plan(
        self,
        gaps: List[SkillGap],
        candidate_name: str,
        job_title: str,
        available_hours: int = 100
    ) -> LearningPlan:
        """Generate personalized learning plan"""

        # Calculate time allocation
        time_allocation = self.scoring.calculate_learning_priority(gaps, available_hours)

        # Generate resources for each gap
        learning_recommendations = {}
        total_hours = 0

        for gap in gaps:
            resources = self._get_learning_resources(
                gap.skill_name,
                gap.current_level,
                gap.required_level,
                time_allocation.get(gap.skill_name, 10)
            )
            learning_recommendations[gap.skill_name] = resources
            total_hours += sum(r.estimated_hours for r in resources)

        # Determine priority focus areas
        priority_focus = [g.skill_name for g in gaps if g.priority in ["critical", "high"]]

        # Generate success metrics
        success_metrics = self._generate_success_metrics(gaps, job_title)

        return LearningPlan(
            candidate_name=candidate_name,
            job_title=job_title,
            created_at=datetime.now().isoformat(),
            skill_gaps=gaps,
            learning_recommendations=learning_recommendations,
            total_estimated_hours=int(total_hours),
            priority_focus_areas=priority_focus,
            success_metrics=success_metrics
        )

    def _get_learning_resources(
        self,
        skill: str,
        current_level: ProficiencyLevel,
        required_level: ProficiencyLevel,
        time_budget: int
    ) -> List[LearningResource]:
        """Get curated learning resources for a skill"""

        # Check if we have pre-curated resources
        if skill in self.LEARNING_RESOURCES_DB:
            resources = self.LEARNING_RESOURCES_DB[skill]
        else:
            # Generate resources using LLM for unknown skills
            resources = self._generate_resources_for_skill(skill, current_level, required_level)

        # Filter and sort by difficulty and time
        difficulty_progression = ["beginner", "intermediate", "advanced"]
        current_idx = difficulty_progression.index(current_level.value.lower()) if current_level.value.lower() in difficulty_progression else 0

        appropriate_resources = [
            r for r in resources
            if difficulty_progression.index(r.difficulty.lower()) >= current_idx
        ]

        # Sort by estimated hours and return top resources within budget
        appropriate_resources.sort(key=lambda r: r.estimated_hours)
        selected = []
        hours_used = 0

        for resource in appropriate_resources:
            if hours_used + resource.estimated_hours <= time_budget * 1.2:
                selected.append(resource)
                hours_used += resource.estimated_hours
                if len(selected) >= 3:
                    break

        return selected if selected else appropriate_resources[:3]

    def _generate_resources_for_skill(
        self,
        skill: str,
        current_level: ProficiencyLevel,
        required_level: ProficiencyLevel
    ) -> List[LearningResource]:
        """Generate learning resources using LLM for custom skills"""

        prompt = f"""Suggest 3 learning resources for {skill} to progress from {current_level} to {required_level}.
Format as JSON array with objects containing: title, description, resource_type (course/book/tutorial/documentation), estimated_hours (int), difficulty (beginner/intermediate/advanced).
Return ONLY JSON array."""

        response = self.llm.generate(prompt, max_tokens=500)

        try:
            resources_data = json.loads(response)
            resources = [
                LearningResource(**r) for r in resources_data if isinstance(r, dict)
            ]
            return resources
        except:
            # Return default generic resources
            return [
                LearningResource(
                    title=f"{skill} Official Documentation",
                    description=f"Official {skill} documentation and guides",
                    resource_type="documentation",
                    estimated_hours=10,
                    difficulty="beginner"
                ),
                LearningResource(
                    title=f"{skill} Advanced Tutorial",
                    description=f"In-depth {skill} concepts and best practices",
                    resource_type="tutorial",
                    estimated_hours=15,
                    difficulty="intermediate"
                ),
                LearningResource(
                    title=f"Practice Projects with {skill}",
                    description=f"Build real projects to master {skill}",
                    resource_type="project",
                    estimated_hours=20,
                    difficulty="advanced"
                ),
            ]

    def _generate_success_metrics(self, gaps: List[SkillGap], job_title: str) -> List[str]:
        """Generate measurable success metrics"""

        metrics = []

        for gap in gaps[:5]:  # Top 5 gaps
            if gap.priority in ["critical", "high"]:
                metric = f"Achieve {gap.required_level} proficiency in {gap.skill_name}"
                metrics.append(metric)

        # Add role-specific metrics
        metrics.extend([
            f"Complete a real-world project relevant to {job_title}",
            "Pass technical assessment for required skills",
            "Build a portfolio demonstrating learned skills",
            "Achieve hands-on proficiency through practice"
        ])

        return metrics[:5]  # Return top 5 metrics
