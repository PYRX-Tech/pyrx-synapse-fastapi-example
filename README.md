# Synapse FastAPI Example

All 16 SDK endpoints with [pyrx-synapse](https://pypi.org/project/pyrx-synapse/) + FastAPI (async).

## Setup

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. `uvicorn main:app --reload`

## Endpoints

### Core
- `POST /api/track` — Track event
- `POST /api/track/batch` — Batch track
- `POST /api/identify` — Identify contact
- `POST /api/identify/batch` — Batch identify
- `POST /api/send` — Send email

### Contacts
- `GET /api/contacts?page=&limit=&tag=&search=` — List
- `GET /api/contacts/{id}` — Get
- `PUT /api/contacts/{id}` — Update
- `DELETE /api/contacts/{id}` — Delete

### Templates
- `GET /api/templates` — List
- `POST /api/templates` — Create
- `GET /api/templates/{slug}` — Get
- `PUT /api/templates/{slug}` — Update
- `DELETE /api/templates/{slug}` — Delete
- `POST /api/templates/{slug}/preview` — Preview

Interactive docs at: http://localhost:8000/docs

## Learn more

- [Synapse Documentation](https://synapse.pyrx.tech/developers)
- [Python SDK Reference](https://synapse.pyrx.tech/developers/sdks/python)
