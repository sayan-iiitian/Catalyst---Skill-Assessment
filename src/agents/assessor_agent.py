"""
Assessment Agent - Conducts skill assessment interviews
"""
import json
from typing import List, Dict
from src.models.assessment import SkillAssessor, SkillExtractor
from src.models.llm_client import get_llm_client
from src.schemas.models import SkillAssessment, ProficiencyLevel
from src.utils.parser import DocumentParser


class AssessmentAgent:
    """Intelligent assessment agent that interviews candidates"""

    def __init__(self):
        self.assessor = SkillAssessor()
        self.extractor = SkillExtractor()
        self.parser = DocumentParser()
        self.llm = get_llm_client()

    def run_assessment(
        self,
        job_description: str,
        resume: str,
        candidate_name: str = "Candidate"
    ) -> Dict:
        """Run full assessment process"""

        print(f"Starting assessment for {candidate_name}...")

        # Extract skills from JD
        skills_to_assess = self.extractor.extract_skills(job_description)
        print(f"Identified {len(skills_to_assess)} skills to assess: {skills_to_assess}")

        # Assess each skill
        assessments = self.assessor.assess_multiple_skills(
            skills_to_assess[:10],  # Limit to 10 skills
            resume,
            job_description
        )

        # Generate assessment questions for conversational element
        assessment_questions = self._generate_assessment_questions(assessments)

        # Extract candidate info
        experience_years = self.parser.extract_experience_years(resume)
        sections = self.parser.extract_sections(resume)
        job_requirements = self.parser.extract_job_requirements(job_description)

        return {
            "candidate_name": candidate_name,
            "skills_assessed": skills_to_assess,
            "assessments": assessments,
            "assessment_questions": assessment_questions,
            "candidate_experience_years": experience_years,
            "job_requirements": job_requirements,
            "resume_sections": sections,
            "job_description": job_description
        }

    def _generate_assessment_questions(self, assessments: List[SkillAssessment]) -> Dict[str, List[str]]:
        """Generate conversational assessment questions"""
        questions = {}

        for assessment in assessments:
            skill_questions = self._generate_skill_questions(assessment.skill_name)
            questions[assessment.skill_name] = skill_questions

        return questions

    def _generate_skill_questions(self, skill: str) -> List[str]:
        """Generate assessment questions for a specific skill"""

        prompt = f"""Generate 2-3 practical, behavioral interview questions to assess {skill} proficiency.
Format as JSON array of strings.
Example: ["Describe your most complex project using X", "How would you debug..."]

Questions for {skill}:"""

        response = self.llm.generate(prompt, max_tokens=300)

        try:
            questions = json.loads(response)
            return questions if isinstance(questions, list) else [skill + " assessment question"]
        except:
            return [
                f"Tell me about your experience with {skill}",
                f"Describe a challenging {skill} implementation you led",
                f"How do you stay current with {skill} developments?"
            ]
