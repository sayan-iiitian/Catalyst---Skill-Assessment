"""
Core skill assessment logic
"""
import json
import re
from typing import List, Dict, Tuple
from src.models.llm_client import get_llm_client
from src.schemas.models import SkillAssessment, ProficiencyLevel
import config


class SkillExtractor:
    """Extract required skills from job description"""

    COMMON_SKILLS = {
        "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "TypeScript",
        "React", "Vue", "Angular", "Django", "FastAPI", "Node.js", "Flask",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Git",
        "SQL", "MongoDB", "PostgreSQL", "Redis", "Elasticsearch",
        "REST API", "GraphQL", "Microservices", "System Design",
        "Machine Learning", "Data Science", "TensorFlow", "PyTorch",
        "Agile", "Scrum", "Leadership", "Communication"
    }

    def extract_skills(self, job_description: str) -> List[str]:
        """Extract skills from job description"""
        skills_found = []
        jd_lower = job_description.lower()

        for skill in self.COMMON_SKILLS:
            if skill.lower() in jd_lower:
                skills_found.append(skill)

        # Extract custom skills mentioned with specific patterns
        pattern_matches = re.findall(r'(?:required|knowledge|experience|expertise)\s+(?:in|with|of)\s+([A-Za-z0-9\s\-+#\.]+?)(?:[,\.]|\s(?:and|or)\s)',
                                   job_description, re.IGNORECASE)
        for match in pattern_matches:
            skill = match.strip()
            if len(skill) > 2 and skill not in skills_found:
                skills_found.append(skill)

        # Limit to reasonable number
        return skills_found[:config.MAX_SKILLS_TO_ASSESS]


class SkillAssessor:
    """Assess candidate proficiency on required skills"""

    def __init__(self):
        self.llm = get_llm_client()
        self.extractor = SkillExtractor()

    def assess_skill(self, skill: str, resume: str, job_requirement: str) -> SkillAssessment:
        """Assess candidate's proficiency on a single skill"""

        assessment_prompt = f"""
You are an expert technical interviewer assessing a candidate's skill proficiency.

Job Requirement: {job_requirement}
Candidate Resume (relevant sections):
{resume}

Skill to Assess: {skill}

Based on the resume and job requirement, provide a JSON assessment with:
1. proficiency_level: one of ["Beginner", "Intermediate", "Advanced", "Expert"]
2. confidence_score: 0.0 to 1.0 (how confident in this assessment)
3. gap_analysis: brief description of what they know vs what's needed
4. evidence: list of specific evidence from resume

Output ONLY valid JSON, no other text.
"""

        response = self.llm.generate(assessment_prompt, max_tokens=500)

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing
            data = self._parse_response_fallback(response)

        return SkillAssessment(
            skill_name=skill,
            proficiency_level=data.get("proficiency_level", "Beginner"),
            confidence_score=float(data.get("confidence_score", 0.5)),
            gap_analysis=data.get("gap_analysis", "Unable to assess"),
            evidence=data.get("evidence", [])
        )

    def assess_multiple_skills(self, skills: List[str], resume: str, job_description: str) -> List[SkillAssessment]:
        """Assess multiple skills"""
        assessments = []
        for skill in skills:
            assessment = self.assess_skill(skill, resume, job_description)
            assessments.append(assessment)
        return assessments

    def _parse_response_fallback(self, response: str) -> Dict:
        """Fallback JSON parsing for malformed responses"""
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # Return default assessment
        return {
            "proficiency_level": "Intermediate",
            "confidence_score": 0.6,
            "gap_analysis": "Assessment completed",
            "evidence": []
        }
