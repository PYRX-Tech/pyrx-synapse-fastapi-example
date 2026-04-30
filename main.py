import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pyrx_synapse import AsyncSynapse

synapse: AsyncSynapse | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global synapse
    synapse = AsyncSynapse(api_key=os.environ["SYNAPSE_API_KEY"], workspace_id=os.environ["SYNAPSE_WORKSPACE_ID"], base_url=os.environ.get("SYNAPSE_API_URL", "https://synapse-api.pyrx.tech"))
    yield
    if synapse:
        await synapse.close()

app = FastAPI(title="Synapse FastAPI Example", lifespan=lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    status = getattr(exc, "status_code", 500) or getattr(exc, "status", 500) or 500
    return JSONResponse(status_code=status, content={"error": str(exc)})

class TrackReq(BaseModel):
    user_id: str; event: str; attributes: dict = {}
class IdentifyReq(BaseModel):
    user_id: str; email: str; properties: dict = {}; tags: list[str] = []
class BatchTrackReq(BaseModel):
    events: list[dict]
class BatchIdentifyReq(BaseModel):
    contacts: list[dict]
class SendReq(BaseModel):
    template_slug: str; user_id: str; email: str; attributes: dict = {}
class ContactUpdateReq(BaseModel):
    email: str | None = None; properties: dict = {}; tags: list[str] = []
class TemplateCreateReq(BaseModel):
    slug: str; name: str; subject: str; body_html: str; sender_name: str; from_email: str
class TemplateUpdateReq(BaseModel):
    name: str | None = None; subject: str | None = None; body_html: str | None = None
class PreviewReq(BaseModel):
    contact: dict = {}

# Core
@app.post("/api/track")
async def track(r: TrackReq):
    return await synapse.track(external_id=r.user_id, event_name=r.event, attributes=r.attributes)

@app.post("/api/track/batch")
async def track_batch(r: BatchTrackReq):
    return await synapse.track_batch(events=r.events)

@app.post("/api/identify")
async def identify(r: IdentifyReq):
    return await synapse.identify(external_id=r.user_id, email=r.email, properties=r.properties, tags=r.tags)

@app.post("/api/identify/batch")
async def identify_batch(r: BatchIdentifyReq):
    return await synapse.identify_batch(contacts=r.contacts)

@app.post("/api/send")
async def send(r: SendReq):
    return await synapse.send(template_slug=r.template_slug, to={"user_id": r.user_id, "email": r.email}, attributes=r.attributes)

# Contacts
@app.get("/api/contacts")
async def list_contacts(page: int = 1, limit: int = 20):
    return await synapse.contacts.list(page=page, limit=limit)

@app.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: str):
    return await synapse.contacts.get(contact_id)

@app.put("/api/contacts/{ext_id}")
async def update_contact(ext_id: str, r: ContactUpdateReq):
    return await synapse.contacts.update(ext_id, data=r.model_dump(exclude_none=True))

@app.delete("/api/contacts/{ext_id}")
async def delete_contact(ext_id: str):
    await synapse.contacts.delete(ext_id)
    return {"success": True}

# Templates
@app.get("/api/templates")
async def list_templates():
    return await synapse.templates.list()

@app.post("/api/templates")
async def create_template(r: TemplateCreateReq):
    return await synapse.templates.create(r.model_dump())

@app.get("/api/templates/{slug}")
async def get_template(slug: str):
    return await synapse.templates.get(slug)

@app.put("/api/templates/{slug}")
async def update_template(slug: str, r: TemplateUpdateReq):
    return await synapse.templates.update(slug, params=r.model_dump(exclude_none=True))

@app.delete("/api/templates/{slug}")
async def delete_template(slug: str):
    await synapse.templates.delete(slug)
    return {"success": True}

@app.post("/api/templates/{slug}/preview")
async def preview_template(slug: str, r: PreviewReq):
    return await synapse.templates.preview(slug, params={"contact": r.contact})
