# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   CATALYST APPLICATION                           │
│                    (Streamlit Frontend)                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
     ┌───────────┴────────────┐
     │                        │
     ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│   JOB DESC       │    │  RESUME INPUT    │
│   + METADATA     │    │  + METADATA      │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │ ASSESSMENT ORCHESTRATOR│
         │  (AssessmentAgent)    │
         └───────────┬───────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│  SKILL   │  │  RESUME  │  │   JOB REQ    │
│ EXTRACTOR│  │  PARSER  │  │  PARSER      │
└────┬─────┘  └────┬─────┘  └────┬─────────┘
     │             │             │
     └─────────────┼─────────────┘
                   ▼
         ┌──────────────────────┐
         │   SKILL ASSESSOR     │
         │  (Multi-skill eval)  │
         └─────────┬────────────┘
                   │
                   ▼
        ┌────────────────────────┐
        │  LLM CLIENT (Abstract) │
        │  ├─ HuggingFace API   │
        │  ├─ Ollama (Local)    │
        │  └─ Mock (Demo)       │
        └─────────┬──────────────┘
                  │
     ┌────────────┴────────────┐
     │                         │
     ▼                         ▼
┌──────────────┐      ┌──────────────────┐
│ ASSESSMENTS  │      │   LLM RESPONSES  │
│ + EVIDENCE   │      │  (Proficiency)   │
└────────┬─────┘      └──────────────────┘
         │
         ▼
    ┌─────────────┐
    │SCORING      │
    │ENGINE       │
    └─────┬───────┘
          │
    ┌─────┴──────────┐
    │                │
    ▼                ▼
┌──────────┐  ┌──────────────┐
│SKILL GAPS│  │OVERALL FIT   │
│+ PRIORITY│  │SCORE (0-1)   │
└────┬─────┘  └──────────────┘
     │
     ▼
┌──────────────────────┐
│ PLANNING AGENT       │
│(PlanningAgent)       │
└─────────┬────────────┘
          │
    ┌─────┴──────────────┐
    │                    │
    ▼                    ▼
┌──────────────────┐ ┌─────────────────┐
│RESOURCE          │ │TIME ALLOCATION  │
│CURATION          │ │(by priority)    │
└────────┬─────────┘ └────────┬────────┘
         │                    │
         └─────────┬──────────┘
                   ▼
        ┌──────────────────────────┐
        │ PERSONALIZED LEARNING    │
        │ PLAN                     │
        │ ├─ Skill gaps            │
        │ ├─ Resources (3-5 each)  │
        │ ├─ Time budget           │
        │ ├─ Success metrics       │
        │ └─ Priority focus areas  │
        └──────────┬───────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
 ┌─────┐      ┌─────────┐    ┌────────┐
 │JSON │      │MARKDOWN │    │STREAMLIT│
 │Export       │Export   │    │DISPLAY │
 └─────┘      └─────────┘    └────────┘
```

## Component Architecture

### 1. Input Layer
- **Streamlit Frontend** (`app.py`)
  - Job description textarea
  - Resume textarea
  - Candidate metadata (name, etc.)
  - Interactive UI with tabs

### 2. Processing Pipeline

#### A. Extraction Phase
- **SkillExtractor** (`src/models/assessment.py`)
  - Regex pattern matching for common skills
  - Custom skill extraction from JD
  - Skill deduplication and limiting

- **DocumentParser** (`src/utils/parser.py`)
  - Resume section extraction
  - Contact info parsing
  - Experience years calculation
  - Job requirement structural parsing

#### B. Assessment Phase
- **SkillAssessor** (`src/models/assessment.py`)
  - Per-skill proficiency evaluation
  - Confidence scoring
  - Evidence extraction from resume
  - Assessment question generation

- **LLM Client** (`src/models/llm_client.py`)
  - Abstract interface for multiple providers
  - Mock implementation for demo
  - HuggingFace Inference API
  - Ollama local LLM support

#### C. Analysis Phase
- **ScoringEngine** (`src/utils/scoring.py`)
  - Proficiency gap calculation (Beginner/Intermediate/Advanced/Expert)
  - Gap priority assignment (Critical/High/Medium/Low)
  - Overall job fit score (0-1)
  - Time allocation by priority

#### D. Planning Phase
- **PlanningAgent** (`src/agents/planner_agent.py`)
  - Gap-to-resource mapping
  - Curated resource selection
  - Time-based resource filtering
  - Success metric generation

- **LearningResourceDB**
  - Pre-curated resources for common skills
  - Resource metadata (type, difficulty, hours, url)
  - Dynamic resource generation via LLM for custom skills

### 3. Data Models (Pydantic)
All data validated using `src/schemas/models.py`:
- `SkillAssessment`
- `SkillGap`
- `LearningResource`
- `LearningPlan`
- `AssessmentResult`

### 4. Output Layer
- **Streamlit Display**
  - Assessment results with metrics
  - Interactive resource exploration
  - Downloadable reports (JSON, Markdown)
  - Responsive tabbed UI

## Data Flow

### 1. Assessment Flow
```
JobDesc + Resume 
    ↓
Extract Skills (30+ candidates)
    ↓
Limit to TOP-10 required
    ↓
For each skill:
  ├─ Build assessment prompt
  ├─ Query LLM
  ├─ Parse JSON response
  └─ Create SkillAssessment object
    ↓
Collect all assessments
    ↓
Output: List[SkillAssessment]
```

### 2. Gap Analysis Flow
```
SkillAssessment + JobRequirementLevel
    ↓
For each assessment:
  ├─ Get current proficiency score (1-4)
  ├─ Get required proficiency score (1-4)
  ├─ Calculate gap (required - current)
  ├─ Map gap to priority (critical/high/medium/low)
  └─ Create SkillGap object
    ↓
Calculate overall fit score (sum/max)
    ↓
Output: List[SkillGap], float (fit score)
```

### 3. Learning Plan Flow
```
SkillGaps
    ↓
Sort by priority (critical > high > medium > low)
    ↓
Allocate time budget:
  ├─ Critical gaps: 40% of budget
  ├─ High gaps: 30% of budget
  ├─ Medium gaps: 20% of budget
  └─ Low gaps: 10% of budget
    ↓
For each gap:
  ├─ Get/generate learning resources
  ├─ Filter by difficulty level
  ├─ Sort by estimated hours
  └─ Select best 3 within budget
    ↓
Generate success metrics (5 key metrics)
    ↓
Output: LearningPlan object
```

## LLM Integration Points

### 1. Skill Assessment
```python
Prompt: "Assess Python proficiency given this resume and JD"
Response: {"proficiency_level": "Intermediate", "gap_analysis": "..."}
Provider: HuggingFace / Ollama / Mock
```

### 2. Assessment Questions Generation
```python
Prompt: "Generate 2-3 interview questions to assess Python"
Response: ["Tell me about decorators...", "How would you..."]
Provider: HuggingFace / Ollama / Mock
```

### 3. Resource Generation
```python
Prompt: "Suggest 3 resources to go from Intermediate to Advanced Python"
Response: [{"title": "...", "type": "course", "hours": 20}, ...]
Provider: HuggingFace / Ollama / Mock
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Skill extraction | ~100ms | Regex-based, very fast |
| Resume parsing | ~50ms | Pattern matching |
| Per-skill LLM call | 2-5s | Depends on LLM provider |
| 10-skill assessment | 20-50s | Parallel or sequential |
| Gap scoring | ~100ms | In-memory calculation |
| Resource curation | ~500ms | DB lookup + filtering |
| Full assessment | ~30-60s | End-to-end |

## Scalability Considerations

### Current Implementation
- Single candidate per session
- Synchronous LLM calls
- In-memory processing

### Future Enhancements
- Batch processing for multiple candidates
- Async LLM calls for parallelization
- Database backend for caching results
- Redis for resource recommendations caching
- Microservices for assessment, planning, and LLM layers

## Error Handling

### LLM Failures
- Fallback to mock LLM if API unavailable
- JSON parsing with regex fallback
- Graceful degradation with default values

### Input Validation
- Pydantic schema validation
- Empty input checking
- Resume/JD length validation

### Output Assurance
- Default values for all optional fields
- Defensive JSON parsing
- Try/catch blocks around critical operations

## Security Considerations

- No sensitive data stored (stateless processing)
- API tokens via environment variables
- No user authentication required (local/trusted deployment)
- Input sanitization before LLM queries
- No external data exposed in prompts

## Testing Strategy

### Unit Tests
- Scoring engine calculations
- Gap priority assignment
- Parser regex patterns

### Integration Tests
- Assessment flow with mock LLM
- Learning plan generation
- Resource curation logic

### End-to-End Tests
- Full assessment with sample inputs
- Output format validation
- PDF/JSON export functionality
