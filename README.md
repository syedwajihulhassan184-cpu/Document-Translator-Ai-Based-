# PDF Translator — AI-Powered Document Translation API

A production-grade Django REST API that translates PDF documents while preserving their original layout and formatting. Built as a portfolio project to demonstrate real backend engineering skills.

## What it does

Users upload a PDF document, select a target language, and receive a translated version with the same layout — same paragraph positions, same page structure. Large documents (600+ pages) are handled via chunked async processing so the server never blocks.

## Tech Stack

- **Django 6** — web framework and ORM
- **Django REST Framework** — API layer
- **Celery + Redis** — async task queue for background translation jobs
- **pdfplumber** — PDF text extraction with bounding box data
- **Anthropic Claude API** — AI translation engine
- **reportlab** — PDF reconstruction with translated text
- **SQLite** (dev) → PostgreSQL (prod)

## Architecture

```
User uploads PDF
      ↓
Django creates TranslationJob (status: PENDING)
      ↓
Celery task dispatched → returns job_id instantly to user
      ↓
Worker parses PDF → extracts text chunks with bbox positions
      ↓
Worker translates each chunk via Claude API (with retry + backoff)
      ↓
Worker rebuilds PDF → places translated text at original coordinates
      ↓
User polls GET /api/jobs/{id}/ → downloads translated PDF when DONE
```

## Database Schema

| Model | Purpose |
|-------|---------|
| `CustomUser` | Extended user with plan-based page quotas |
| `File` | Uploaded files with SHA-256 checksum and soft delete |
| `TranslationJob` | State machine (PENDING → PARSING → TRANSLATING → REBUILDING → DONE) |
| `Chunk` | Individual paragraph blocks with layout metadata (bbox) |
| `GlossaryTerm` | Per-user term memory for consistent translations |
| `AuditLog` | Immutable event log for debugging and compliance |

## Project Status

This project is actively under development. Below is the current build progress:

### ✅ Completed
- Custom User model with plan-based quota system (`Free / Pro / Premium`)
- File model with SHA-256 checksum deduplication and soft delete
- TranslationJob model with TextChoices state machine and custom manager
- Chunk model with JSONField layout metadata
- File upload endpoint (`POST /api/file/`) with size validation and checksum
- Job creation endpoint (`POST /api/jobs/`) with page count detection
- Job status polling endpoint (`GET /api/jobs/{id}/`) with progress percentage
- Celery + Redis async pipeline (end-to-end verified)
- PDF parsing pipeline (`extract_chunks`) using pdfplumber
- Paragraph grouping algorithm (`group_lines_into_blocks`) with gap threshold
- Chunk persistence (`save_chunks_to_db`) — 81 chunks extracted from a real PDF

### 🔄 In Progress
- Anthropic API integration (`translate_chunk`) with exponential backoff

### ⬜ Remaining
- PDF reconstruction with reportlab (`rebuild_pdf`)
- RTL support for Urdu/Arabic using `arabic_reshaper` + `python-bidi`
- Quota enforcement middleware
- Dead letter queue for failed chunks
- Duplicate upload detection
- Download endpoint (`GET /api/jobs/{id}/download/`)
- Management command for monthly quota resets

## API Endpoints

```
POST   /api/file/              Upload a PDF file
POST   /api/jobs/              Create a translation job
GET    /api/jobs/{id}/         Poll job status and progress
GET    /api/jobs/{id}/download/ Download translated PDF (coming soon)
```

## Key Engineering Decisions

**Why Celery?** Translating a 600-page PDF takes minutes. Running that inside an HTTP request would time out the browser. Celery dispatches the work to a background process and returns a job ID instantly — the user polls for progress.

**Why chunk by paragraph?** The Claude API has a context window limit. Sending an entire PDF at once is impossible for large documents. Chunking by paragraph keeps each API call small, allows parallel processing, and enables partial failure recovery (one failed chunk doesn't break the whole job).

**Why store bbox coordinates?** To reconstruct the translated PDF with the same layout, each chunk needs to know where it lives on the page — its x/y position, width, and height. This data is stored in `Chunk.layout_metadata` as JSON.

**Why 404 instead of 403 for unauthorized job access?** Returning 403 tells an attacker "this resource exists but you can't see it." Returning 404 reveals nothing — a standard security pattern called information hiding.

**Why soft delete?** Hard-deleting rows breaks foreign keys, loses audit history, and makes recovery impossible. Setting `deleted_at = now()` preserves all data while hiding it from normal queries.

## Local Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/pdf-translator.git
cd pdf-translator/backend/translator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (requires Docker)
docker run -d -p 6379:6379 redis

# Run migrations
python manage.py migrate

# Start Django
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A translator worker --loglevel=info
```

## Environment Variables

```
ANTHROPIC_API_KEY=your-key-here
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
```

## What I learned building this

- Designing a state machine with Django `TextChoices`
- Async job queues with Celery and Redis
- PDF text extraction and paragraph grouping algorithms
- Bounding box coordinate systems for layout-preserving reconstruction
- Exponential backoff for API rate limit handling
- Soft deletes, audit logging, and quota enforcement patterns
- The 404-vs-403 security pattern for resource ownership

---

*Built by Syed Wajih ul Hassan — backend developer*