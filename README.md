# Catalyst: AI-Powered Skill Assessment & Personalised Learning Plan Agent

**Catalyst** is an intelligent assessment platform that transforms job descriptions and resumes into actionable learning plans. It conversationally assesses candidate proficiency on required skills, identifies critical gaps, and generates personalized learning recommendations with curated resources and realistic time estimates.

## Problem Statement

A resume tells you what someone *claims* to know — not how well they actually know it. Catalyst bridges this gap by:

1. **Real Skill Assessment** - Conversationally evaluates actual proficiency beyond resume claims
2. **Gap Identification** - Identifies specific, prioritized skill gaps relative to job requirements
3. **Personalized Learning** - Generates focused learning plans with adjacent skills candidates can realistically acquire
4. **Curated Resources** - Provides industry-standard learning materials with time estimates

## Features

✨ **Skill Extraction & Analysis**
- Automatically identifies required skills from job descriptions
- Extracts candidate experience and background from resumes
- Intelligent skill gap prioritization

🎯 **Conversational Assessment**
- AI-powered skill proficiency evaluation
- Behavioral interview questions for depth assessment
- Confidence scoring for assessment accuracy

📚 **Personalized Learning Plans**
- Gap-focused resource recommendations
- Time-based learning allocation
- Success metrics and milestones
- Multiple resource types (courses, books, documentation, projects)

📊 **Comprehensive Reporting**
- Detailed skill assessments with evidence
- Priority-based gap analysis
- Export in JSON and Markdown formats

## Technology Stack

- **Backend**: Python 3.12
- **Frontend**: Streamlit (fast, interactive UI)
- **LLM Integration**: Flexible provider support (HuggingFace, Ollama, Mock)
- **Data Validation**: Pydantic models
- **Architecture**: Industry-standard modular design

## Project Structure

```
catalyst-skill-assessment/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
│
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── llm_client.py          # LLM provider abstraction (HF, Ollama, Mock)
│   │   └── assessment.py          # Skill extraction & assessment logic
│   │
│   ├── agents/
│   │   ├── assessor_agent.py      # Assessment orchestration
│   │   └── planner_agent.py       # Learning plan generation
│   │
│   ├── utils/
│   │   ├── parser.py              # Resume/JD parsing utilities
│   │   └── scoring.py             # Gap calculation & scoring logic
│   │
│   └── schemas/
│       └── models.py              # Pydantic data models
│
├── data/
│   └── sample_inputs.json         # Example JD + Resume inputs
│
└── docs/
    ├── architecture.md            # System architecture & design
    └── DEPLOYMENT.md              # Deployment instructions
```

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/catalyst-skill-assessment.git
cd catalyst-skill-assessment
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate      # On macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure LLM provider** (optional)

Create `.env` file:
```bash
# Option A: HuggingFace Inference API (requires free account)
HF_API_TOKEN=your_huggingface_token
LLM_API_PROVIDER=huggingface

# Option B: Use Ollama (requires local installation)
# Install Ollama: https://ollama.ai
# Run: ollama serve
# Then set:
LLM_API_PROVIDER=ollama

# Option C: Use built-in mock (no setup needed)
LLM_API_PROVIDER=mock  # Uses pre-configured responses for demo
```

### Running the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Usage Example

### Input
**Job Description:**
```
Senior Python Developer - Fintech Startup
Requirements:
- 5+ years Python experience (REQUIRED)
- FastAPI/Django REST API development (REQUIRED)
- AWS & Docker knowledge (REQUIRED)
- PostgreSQL & Redis experience (PREFERRED)
- System design & scalability (NICE TO HAVE)
```

**Resume:**
```
John Doe
Senior Software Engineer (3 years)
Experience:
- 3 years Python/Django development
- 2 AWS projects, basic Kubernetes
- PostgreSQL optimization, Redis caching
- Led API modernization project
```

### Output

**Assessment:**
- Python: Intermediate (Gap: Needs senior-level patterns & architecture)
- FastAPI: Beginner (Gap: No framework experience, needs deep learning)
- AWS: Intermediate (Gap: Limited production experience)
- Docker: Intermediate (No Kubernetes experience)
- System Design: Beginner (Gap: Critical for senior role)

**Personalized Learning Plan:**
1. System Design (Critical Priority) - 30 hours
   - "Designing Data-Intensive Applications" book
   - System Design Interview course
   - Build a scalable project from scratch

2. Advanced Python Patterns (High Priority) - 25 hours
   - Advanced Python course
   - Code review existing production code
   - Design pattern implementation projects

3. FastAPI Deep Dive (High Priority) - 20 hours
   - FastAPI official docs + advanced course
   - Build microservices project
   - Performance optimization labs

**Success Metrics:**
- Architect and implement a complete microservice from scratch
- Pass senior-level system design interview
- Contribute to production FastAPI codebase
- Master async Python patterns for high-concurrency scenarios

## Architecture

### Core Components

**1. AssessmentAgent** (`src/agents/assessor_agent.py`)
- Orchestrates the assessment workflow
- Extracts required skills from job description
- Conducts multi-round skill assessment
- Generates conversational interview questions

**2. SkillAssessor** (`src/models/assessment.py`)
- Evaluates proficiency level for each skill
- Generates gap analysis
- Extracts evidence from resume

**3. PlanningAgent** (`src/agents/planner_agent.py`)
- Generates personalized learning plans
- Curates relevant learning resources
- Allocates time based on gap priority
- Defines success metrics

**4. ScoringEngine** (`src/utils/scoring.py`)
- Calculates proficiency gaps
- Determines priority levels (critical/high/medium/low)
- Computes overall job fit score
- Allocates learning time budget

**5. LLM Client** (`src/models/llm_client.py`)
- Abstracts LLM provider (HuggingFace, Ollama, Mock)
- Enables easy provider switching
- Handles API communication

### Data Models

All data is validated using Pydantic models:
- `SkillAssessment` - Individual skill evaluation
- `SkillGap` - Identified gaps with priority
- `LearningResource` - Curated learning material
- `LearningPlan` - Complete personalized plan
- `AssessmentResult` - Full assessment output

## Scoring & Gap Logic

### Proficiency Levels (0-4 scale)
- **Beginner (1)**: Basic knowledge, learning phase
- **Intermediate (2)**: Practical hands-on experience
- **Advanced (3)**: Expert-level understanding, can teach others
- **Expert (4)**: Industry leader, architecture/design expertise

### Gap Priority
- **Critical**: 3+ level gap (needs major transformation)
- **High**: 2 level gap (significant development needed)
- **Medium**: 1 level gap (refinement needed)
- **Low**: No gap (already proficient)

### Time Allocation
- Critical gaps: 40% of learning budget
- High priority: 30% of learning budget
- Medium priority: 20% of learning budget
- Low priority: 10% of learning budget

## Sample Inputs & Outputs

See `data/sample_inputs.json` for complete example with:
- Realistic job descriptions
- Comprehensive resumes
- Expected assessment outputs
- Generated learning plans

## Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
```bash
# Push to GitHub, then:
# 1. Go to https://share.streamlit.io
# 2. Deploy from GitHub repo
# 3. Set environment variables in Cloud settings
```

### Docker
```bash
docker build -t catalyst .
docker run -p 8501:8501 -e HF_API_TOKEN=$TOKEN catalyst
```

See `docs/DEPLOYMENT.md` for detailed deployment instructions.

## Configuration

All settings in `config.py`:
- LLM model and provider
- Assessment parameters
- Learning plan generation settings
- Application defaults

Customize via environment variables or by editing `config.py`.

## Limitations & Future Work

### Current Limitations
- Assessment based on resume text (no live interviews yet)
- Curated resources limited to common skills
- Mock LLM used in demo (requires API token for production)

### Future Enhancements
- Live conversational interview sessions with recording
- Integration with more learning platforms (Coursera, Udemy, etc.)
- Skills marketplace for real-time market demand data
- Progress tracking and adaptive learning adjustments
- Multi-language support
- Integration with ATS systems

## Development

### Code Quality
- Industry-standard project structure
- Type hints with Pydantic validation
- Comprehensive error handling
- Modular, testable components

### Testing
```bash
# Future: Add pytest suite
pytest tests/ -v
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request
4. Follow existing code patterns

## License

MIT License - See LICENSE file for details

## Support

Questions or issues? 
- Email: support@deccanexperts.ai
- Discord: https://discord.gg/aczDnqNR
- GitHub Issues: Report bugs and feature requests

## Credits

Built for **Deccan AI Catalyst Hackathon 2026**

---

**Transform resumes into learning roadmaps. Catalyst helps candidates bridge skill gaps and land their dream roles.**
