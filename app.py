"""
Main Streamlit Application - Catalyst Skill Assessment & Learning Plan Agent
"""
import streamlit as st
import json
from datetime import datetime
from typing import Dict, Any

from src.agents.assessor_agent import AssessmentAgent
from src.agents.planner_agent import PlanningAgent
from src.utils.scoring import ScoringEngine
from src.schemas.models import ProficiencyLevel
import config


def init_session_state():
    """Initialize session state variables"""
    if "assessment_result" not in st.session_state:
        st.session_state.assessment_result = None
    if "learning_plan" not in st.session_state:
        st.session_state.learning_plan = None
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Input"


def render_header():
    """Render application header"""
    st.set_page_config(
        page_title="Catalyst - Skill Assessment",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    # 🎯 Catalyst: AI-Powered Skill Assessment & Learning Plan

    Transform resumes into actionable learning paths. Conversationally assess real proficiency,
    identify skill gaps, and generate personalized learning plans with curated resources.
    """)


def render_input_section():
    """Render input section for JD and Resume"""
    st.header("📋 Assessment Input")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Job Description")
        job_description = st.text_area(
            "Paste the job description",
            height=250,
            placeholder="Paste complete job description here...",
            key="job_input"
        )

    with col2:
        st.subheader("Resume")
        resume = st.text_area(
            "Paste the resume",
            height=250,
            placeholder="Paste candidate resume here...",
            key="resume_input"
        )

    col1, col2 = st.columns([3, 1])
    with col1:
        candidate_name = st.text_input(
            "Candidate Name (optional)",
            value="Candidate",
            placeholder="Enter candidate name"
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        assess_button = st.button(
            "🚀 Run Assessment",
            use_container_width=True,
            type="primary"
        )

    return job_description, resume, candidate_name, assess_button


def run_assessment(job_description: str, resume: str, candidate_name: str):
    """Run the assessment process"""
    if not job_description.strip() or not resume.strip():
        st.error("Please provide both job description and resume.")
        return

    with st.spinner("🔍 Analyzing skills and assessing proficiency..."):
        assessor = AssessmentAgent()
        assessment_result = assessor.run_assessment(
            job_description,
            resume,
            candidate_name
        )

        # Calculate gaps and fit score
        required_levels = {
            skill: ProficiencyLevel.INTERMEDIATE
            for skill in assessment_result["skills_assessed"]
        }

        gaps = [
            ScoringEngine.calculate_skill_gap(assessment, required_levels[assessment.skill_name])
            for assessment in assessment_result["assessments"]
            if assessment.skill_name in required_levels
        ]

        overall_fit = ScoringEngine.calculate_overall_fit(assessment_result["assessments"])

        # Generate learning plan
        planner = PlanningAgent()
        # Extract job title from job description (first line usually)
        job_title = job_description.split('\n')[0] if job_description else "Target Position"
        learning_plan = planner.generate_learning_plan(
            gaps,
            candidate_name,
            job_title,
            available_hours=100
        )

        st.session_state.assessment_result = {
            "assessments": assessment_result["assessments"],
            "gaps": gaps,
            "overall_fit": overall_fit,
            "candidate_name": candidate_name,
            "skills_assessed": assessment_result["skills_assessed"],
            "assessment_questions": assessment_result["assessment_questions"]
        }

        st.session_state.learning_plan = learning_plan


def render_assessment_results():
    """Render assessment results"""
    if st.session_state.assessment_result is None:
        st.info("👈 Complete the assessment on the left to see results")
        return

    result = st.session_state.assessment_result

    # Overall Summary
    st.header("📊 Assessment Results")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fit_percentage = int(result["overall_fit"] * 100)
        st.metric(
            "Overall Job Fit",
            f"{fit_percentage}%",
            delta="Strong match" if fit_percentage > 70 else "Needs work"
        )
    with col2:
        st.metric("Skills Assessed", len(result["skills_assessed"]))
    with col3:
        critical_gaps = len([g for g in result["gaps"] if g.priority == "critical"])
        st.metric("Critical Gaps", critical_gaps)
    with col4:
        st.metric("Candidate", result["candidate_name"])

    # Detailed Assessments
    st.subheader("🎯 Skill Assessments")

    for assessment in result["assessments"]:
        with st.expander(f"**{assessment.skill_name}** - {assessment.proficiency_level}", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Proficiency", assessment.proficiency_level)
            with col2:
                st.metric("Confidence", f"{int(assessment.confidence_score * 100)}%")
            with col3:
                st.metric("Assessment", "Complete")

            st.write(f"**Gap Analysis:** {assessment.gap_analysis}")

            if assessment.evidence:
                st.write("**Evidence from Resume:**")
                for evidence in assessment.evidence:
                    st.write(f"• {evidence}")

            # Assessment questions
            if assessment.skill_name in result["assessment_questions"]:
                st.write("**Conversational Assessment Questions:**")
                for q in result["assessment_questions"][assessment.skill_name]:
                    st.write(f"• {q}")

    # Skill Gaps Summary
    st.subheader("⚠️ Skill Gaps & Priorities")

    gap_df_data = []
    for gap in result["gaps"]:
        gap_df_data.append({
            "Skill": gap.skill_name,
            "Current": gap.current_level,
            "Required": gap.required_level,
            "Priority": gap.priority.upper(),
            "Description": gap.gap_description
        })

    if gap_df_data:
        import pandas as pd
        gap_df = pd.DataFrame(gap_df_data)
        st.dataframe(gap_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No significant gaps identified!")


def render_learning_plan():
    """Render personalized learning plan"""
    if st.session_state.learning_plan is None:
        st.info("👈 Complete the assessment to generate a learning plan")
        return

    plan = st.session_state.learning_plan

    st.header("📚 Personalized Learning Plan")

    # Plan Overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Estimated Hours", plan.total_estimated_hours)
    with col2:
        st.metric("Skill Gaps", len(plan.skill_gaps))
    with col3:
        st.metric("Focus Areas", len(plan.priority_focus_areas))
    with col4:
        st.metric("Resources", sum(
            len(resources) for resources in plan.learning_recommendations.values()
        ))

    # Priority Focus Areas
    if plan.priority_focus_areas:
        st.subheader("🎯 Priority Focus Areas")
        for i, area in enumerate(plan.priority_focus_areas, 1):
            st.write(f"{i}. **{area}** - Focus here first for maximum impact")

    # Learning Recommendations by Skill
    st.subheader("📖 Learning Recommendations")

    for skill, resources in plan.learning_recommendations.items():
        with st.expander(f"**{skill}** - {len(resources)} resources", expanded=False):
            for resource in resources:
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.write(f"**{resource.title}**")
                    st.write(resource.description)
                    st.write(f"*Type: {resource.resource_type.title()} | Difficulty: {resource.difficulty.title()}*")
                    if resource.url:
                        st.write(f"[🔗 Visit Resource]({resource.url})")

                with col2:
                    st.metric(f"Hours", resource.estimated_hours)
                st.divider()

    # Success Metrics
    st.subheader("✅ Success Metrics")
    for i, metric in enumerate(plan.success_metrics, 1):
        st.write(f"{i}. {metric}")

    # Export Plan
    st.subheader("💾 Export Plan")

    plan_json = plan.model_dump_json(indent=2)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download as JSON",
            data=plan_json,
            file_name=f"learning_plan_{plan.candidate_name.replace(' ', '_')}.json",
            mime="application/json"
        )

    with col2:
        # Generate markdown report
        markdown_report = generate_markdown_report(plan)
        st.download_button(
            label="📄 Download as Markdown",
            data=markdown_report,
            file_name=f"learning_plan_{plan.candidate_name.replace(' ', '_')}.md",
            mime="text/markdown"
        )


def generate_markdown_report(plan) -> str:
    """Generate markdown report from learning plan"""
    report = f"""# Learning Plan for {plan.candidate_name}

**Position:** {plan.job_title}
**Generated:** {plan.created_at}
**Total Estimated Hours:** {plan.total_estimated_hours}

## Executive Summary

This personalized learning plan identifies skill gaps and provides a structured approach to reach proficiency for the {plan.job_title} role.

## Priority Focus Areas

"""

    for i, area in enumerate(plan.priority_focus_areas, 1):
        report += f"{i}. {area}\n"

    report += "\n## Skill Gaps\n\n"

    for gap in plan.skill_gaps:
        report += f"### {gap.skill_name}\n"
        report += f"- **Current Level:** {gap.current_level}\n"
        report += f"- **Required Level:** {gap.required_level}\n"
        report += f"- **Priority:** {gap.priority.upper()}\n"
        report += f"- **Description:** {gap.gap_description}\n\n"

    report += "## Learning Resources\n\n"

    for skill, resources in plan.learning_recommendations.items():
        report += f"### {skill}\n\n"
        for resource in resources:
            report += f"- **{resource.title}** ({resource.estimated_hours} hours)\n"
            report += f"  - Type: {resource.resource_type.title()}\n"
            report += f"  - Difficulty: {resource.difficulty.title()}\n"
            report += f"  - Description: {resource.description}\n"
            if resource.url:
                report += f"  - [Link]({resource.url})\n"
            report += "\n"

    report += "## Success Metrics\n\n"
    for i, metric in enumerate(plan.success_metrics, 1):
        report += f"{i}. {metric}\n"

    return report


def main():
    """Main application flow"""
    init_session_state()
    render_header()

    # Sidebar
    with st.sidebar:
        st.subheader("ℹ️ About")
        st.write("""
        **Catalyst** is an AI-powered assessment platform that:

        1. 🎯 **Assesses** real proficiency on required skills
        2. 🔍 **Identifies** critical skill gaps
        3. 📚 **Generates** personalized learning plans
        4. 📖 **Curates** resources matched to your level

        Submit your job description and resume to get started!
        """)

        st.divider()

        st.subheader("🔧 Application Info")
        st.caption(f"Version: 1.0.0")
        st.caption(f"Model: {config.LLM_MODEL}")
        st.caption(f"Provider: {config.LLM_API_PROVIDER}")

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 Input & Assessment", "📊 Results", "📚 Learning Plan"])

    with tab1:
        job_description, resume, candidate_name, assess_button = render_input_section()

        if assess_button:
            run_assessment(job_description, resume, candidate_name)
            st.success("✅ Assessment complete! Check the Results tab.")

    with tab2:
        render_assessment_results()

    with tab3:
        render_learning_plan()

    # Footer
    st.divider()
    st.caption("""
    **Catalyst** - AI-Powered Skill Assessment & Personalised Learning Plan Agent
    Built for Deccan AI Hackathon 2026
    """)


if __name__ == "__main__":
    main()
