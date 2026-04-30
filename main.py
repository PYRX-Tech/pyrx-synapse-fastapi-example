import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from pydantic import BaseModel
from pyrx_synapse import AsyncSynapse

synapse: AsyncSynapse | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global synapse
    synapse = AsyncSynapse(api_key=os.environ["SYNAPSE_API_KEY"], workspace_id=os.environ["SYNAPSE_WORKSPACE_ID"])
    yield
    if synapse:
        await synapse.close()

app = FastAPI(title="Synapse FastAPI Example", lifespan=lifespan)

# ── Request models ──
class TrackRequest(BaseModel):
    user_id: str
    event: str
    attributes: dict = {}

class TrackBatchRequest(BaseModel):
    events: list[dict]

class IdentifyRequest(BaseModel):
    user_id: str
    email: str
    properties: dict = {}
    tags: list[str] = []

class IdentifyBatchRequest(BaseModel):
    contacts: list[dict]

class SendRequest(BaseModel):
    template_slug: str
    user_id: str
    email: str
    attributes: dict = {}

class ContactUpdateRequest(BaseModel):
    email: str | None = None
    properties: dict = {}
    tags: list[str] = []

class TemplateCreateRequest(BaseModel):
    slug: str
    name: str
    subject: str
    body: str

class TemplateUpdateRequest(BaseModel):
    name: str | None = None
    subject: str | None = None
    body: str | None = None

class PreviewRequest(BaseModel):
    attributes: dict = {}

# ── Core ──
@app.post("/api/track")
async def track_event(req: TrackRequest):
    assert synapse
    return await synapse.track(external_id=req.user_id, event_name=req.event, attributes=req.attributes)

@app.post("/api/track/batch")
async def track_batch(req: TrackBatchRequest):
    assert synapse
    return await synapse.track_batch(events=req.events)

@app.post("/api/identify")
async def identify_contact(req: IdentifyRequest):
    assert synapse
    return await synapse.identify(external_id=req.user_id, email=req.email, properties=req.properties, tags=req.tags)

@app.post("/api/identify/batch")
async def identify_batch(req: IdentifyBatchRequest):
    assert synapse
    return await synapse.identify_batch(contacts=req.contacts)

@app.post("/api/send")
async def send_email(req: SendRequest):
    assert synapse
    return await synapse.send(template_slug=req.template_slug, to={"user_id": req.user_id, "email": req.email}, attributes=req.attributes)

# ── Contacts ──
@app.get("/api/contacts")
async def list_contacts(page: int = Query(1), limit: int = Query(20), tag: str | None = None, search: str | None = None):
    assert synapse
    return await synapse.contacts.list(page=page, limit=limit, tag=tag, search=search)

@app.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: str):
    assert synapse
    return await synapse.contacts.get(contact_id)

@app.put("/api/contacts/{external_id}")
async def update_contact(external_id: str, req: ContactUpdateRequest):
    assert synapse
    return await synapse.contacts.update(external_id, data=req.model_dump(exclude_none=True))

@app.delete("/api/contacts/{external_id}")
async def delete_contact(external_id: str):
    assert synapse
    await synapse.contacts.delete(external_id)
    return {"success": True}

# ── Templates ──
@app.get("/api/templates")
async def list_templates():
    assert synapse
    return await synapse.templates.list()

@app.post("/api/templates")
async def create_template(req: TemplateCreateRequest):
    assert synapse
    return await synapse.templates.create(req.model_dump())

@app.get("/api/templates/{slug}")
async def get_template(slug: str):
    assert synapse
    return await synapse.templates.get(slug)

@app.put("/api/templates/{slug}")
async def update_template(slug: str, req: TemplateUpdateRequest):
    assert synapse
    return await synapse.templates.update(slug, params=req.model_dump(exclude_none=True))

@app.delete("/api/templates/{slug}")
async def delete_template(slug: str):
    assert synapse
    await synapse.templates.delete(slug)
    return {"success": True}

@app.post("/api/templates/{slug}/preview")
async def preview_template(slug: str, req: PreviewRequest):
    assert synapse
    return await synapse.templates.preview(slug, params={"attributes": req.attributes})
