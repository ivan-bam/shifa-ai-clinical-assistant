# Shifa AI Clinical Documentation Assistant

An AI-assisted clinical documentation tool for Emergency Department physicians. Physicians enter brief notes and the AI generates structured SOAP notes, suggested diagnoses, investigations, medications, and care schedules. All AI output requires physician review and approval before being saved.

## What it does

1. Physician opens a patient encounter and types a short summary of findings
2. The AI generates a full structured clinical note and suggestions
3. The physician reviews, edits if needed, and approves
4. The final note is saved to the Shifa EHR system

## Tech Stack

| Technology | Role |
|---|---|
| Python 3.13 | Core programming language |
| FastAPI | REST API that the frontend talks to |
| LangChain + LangGraph | AI workflow orchestration |
| OpenAI API | Large language model (GPT-4o) |
| PostgreSQL + pgvector | Database with AI-powered search |
| Docker | Containerised deployment |

## Project Structure

```
shifa-ai-clinical-assistant/
├── backend/
│   ├── agents/          # AI agent definitions
│   ├── api/             # FastAPI route handlers
│   ├── graphs/          # LangGraph workflow definitions
│   ├── models/          # Database models
│   ├── prompts/         # LLM prompt templates
│   ├── rag/             # Retrieval-Augmented Generation logic
│   ├── services/        # Business logic
│   ├── evaluations/     # AI output quality testing
│   ├── observability/   # Logging and monitoring
│   └── governance/      # Audit trails and compliance
├── .env.example         # Template for environment variables
├── requirements.txt     # Python dependencies
└── README.md
```

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (with pgvector extension)
- Docker (optional for local DB)
- An OpenAI API key (platform.openai.com)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd shifa-ai-clinical-assistant
```

### 2. Create a virtual environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o
DATABASE_URL=postgresql://postgres:password@localhost:5432/shifa_db
```

### 5. Start the API server

```bash
uvicorn backend.api.main:app --reload
```

## Governance

- AI suggestions are never auto-approved
- Physicians are always responsible for clinical decisions
- All AI outputs are logged with prompt version and model used
- AI-generated content is always clearly labelled as such

## Status

MVP in active development.
