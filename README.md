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
| FastAPI | REST API layer that clients and frontends call |
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
├── Dockerfile           # Builds the API container image
├── docker-compose.yml   # Runs the database and API together
├── .dockerignore        # Files excluded from the image
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

## Run Everything with Docker (recommended)

The fastest way to run the whole project — database and API together:

```bash
cp .env.example .env          # then add your OPENAI_API_KEY
docker compose up --build
```

> **You must supply your own OpenAI API key** (from platform.openai.com, with a
> small amount of credit) in `.env` before starting — the app calls the OpenAI
> API at runtime and will fail without a valid key.

That's it. The API is available at http://localhost:8000 and the interactive
docs at http://localhost:8000/docs. To stop it: `docker compose down`.

> When running this way, the API reaches the database inside Docker, so you do
> not need PostgreSQL installed on your machine.

## Run Locally Without Docker

Use this if you want to run the API directly (e.g. with auto-reload while coding).
You still need a PostgreSQL database — the simplest option is to run just the
database in Docker: `docker compose up -d db`.

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

## Evaluation Suite

An automated quality check for the AI's output. It runs a set of realistic ED
cases and verifies the responses are well-formed (all SOAP sections present,
every medication dosed, diagnoses ranked) and clinically relevant (e.g. a chest
pain case must mention ECG/troponin/aspirin). It exits non-zero on failure, so it
can gate changes in CI.

```bash
python -m backend.evaluations.runner
```

## Logs (Observability)

Every request is logged with a unique ID and its duration, and the clinical
workflow logs how long generation takes. To follow the logs live:

```bash
docker compose logs -f app        # when running via Docker
```

When running locally, the logs print straight to your terminal.

## Design Notes

A few deliberate decisions, documented so they're not mistaken for oversights:

- **Workflow shape.** The spec recommends a graph with separate diagnosis,
  investigation, medication, and schedule nodes. These are merged into a single
  `suggestions` node — one LLM call returning all four. This is cheaper (one
  round-trip instead of four), lower-latency, and keeps the suggestions coherent
  with each other. The retrieval and SOAP steps remain their own nodes.
- **Human review is an API step, not a graph node.** Generation and approval are
  separate endpoints rather than a `human_review` node inside the graph, so the
  AI run and the clinician's decision are cleanly decoupled and independently
  auditable.
- **Empty `agents/` and `governance/` folders** are intentional placeholders that
  mirror the spec's structure. The governance *rules* are enforced across the app
  (see below), not isolated in that folder.
- **Backend-only MVP.** There is no frontend by design — the deliverables are the
  API, workflow, persistence, and Docker setup. A UI would consume these same
  endpoints in a later phase.

## Governance

- AI suggestions are never auto-approved
- Physicians are always responsible for clinical decisions
- All AI outputs are logged with prompt version and model used
- AI-generated content is always clearly labelled as such

## Status

MVP complete. All Phase 1 deliverables are implemented:

- Structured SOAP note generation
- Clinical suggestions (diagnoses, investigations, medications, care schedule)
- LangGraph workflow with RAG retrieval over uploaded guidelines (pgvector)
- Physician review and approval workflow
- PostgreSQL persistence with full audit logging
- Request logging / observability
- Automated evaluation suite
- Fully Dockerised (one-command run)
