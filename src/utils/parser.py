"""
Resume and Job Description parsing utilities
"""
import re
from typing import Dict, List, Tuple


class DocumentParser:
    """Parse resumes and job descriptions"""

    @staticmethod
    def extract_contact_info(resume: str) -> Dict[str, str]:
        """Extract contact information from resume"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

        email = re.search(email_pattern, resume)
        phone = re.search(phone_pattern, resume)

        return {
            "email": email.group(0) if email else "Not found",
            "phone": phone.group(0) if phone else "Not found"
        }

    @staticmethod
    def extract_experience_years(resume: str) -> int:
        """Estimate years of experience from resume"""
        year_pattern = r'(?:19|20)\d{2}'
        years_found = re.findall(year_pattern, resume)

        if len(years_found) >= 2:
            try:
                return int(years_found[-1]) - int(years_found[0])
            except:
                return 0
        return 0

    @staticmethod
    def extract_sections(document: str) -> Dict[str, str]:
        """Extract major sections from document"""
        sections = {}
        section_headers = [
            r'(?:EDUCATION|Education)',
            r'(?:EXPERIENCE|Experience|WORK EXPERIENCE)',
            r'(?:SKILLS|Technical Skills)',
            r'(?:PROJECTS|Projects)',
            r'(?:CERTIFICATIONS|Certifications)',
        ]

        current_section = "header"
        current_content = ""

        for line in document.split('\n'):
            matched = False
            for header_pattern in section_headers:
                if re.match(header_pattern, line, re.IGNORECASE):
                    if current_section:
                        sections[current_section] = current_content.strip()
                    current_section = header_pattern.replace(r'(?:', '').replace('|', ' / ').replace(')', '')
                    current_content = ""
                    matched = True
                    break

            if not matched:
                current_content += line + "\n"

        if current_section:
            sections[current_section] = current_content.strip()

        return sections

    @staticmethod
    def extract_job_requirements(job_description: str) -> Dict[str, List[str]]:
        """Extract structured requirements from JD"""
        requirements = {
            "must_have": [],
            "nice_to_have": [],
            "years_required": 0
        }

        # Extract years of experience required
        years_pattern = r'(\d+)\+?\s+(?:years?|yrs?)'
        years_match = re.search(years_pattern, job_description, re.IGNORECASE)
        if years_match:
            requirements["years_required"] = int(years_match.group(1))

        # Parse must-have requirements
        must_have_section = re.search(
            r'(?:MUST HAVE|REQUIRED|REQUIREMENTS).*?(?=(?:NICE|PREFERRED|$))',
            job_description, re.IGNORECASE | re.DOTALL
        )
        if must_have_section:
            items = re.findall(r'[-•]\s*(.+?)(?=[-•]|$)', must_have_section.group(0))
            requirements["must_have"] = [item.strip() for item in items]

        # Parse nice-to-have requirements
        nice_section = re.search(
            r'(?:NICE|PREFERRED|BONUS).*?(?=$)',
            job_description, re.IGNORECASE | re.DOTALL
        )
        if nice_section:
            items = re.findall(r'[-•]\s*(.+?)(?=[-•]|$)', nice_section.group(0))
            requirements["nice_to_have"] = [item.strip() for item in items]

        return requirements
