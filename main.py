import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
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
async def global_handler(request, exc):
    status = getattr(exc, 'status_code', None) or getattr(exc, 'status', None) or 500
    return JSONResponse(status_code=status, content={"error": str(exc)})

class TrackReq(BaseModel):
    userId: str
    event: str
    attributes: dict = {}

class BatchTrackReq(BaseModel):
    events: list[dict]

class IdentifyReq(BaseModel):
    userId: str
    email: str | None = None
    properties: dict = {}

class BatchIdentifyReq(BaseModel):
    contacts: list[dict]

class SendReq(BaseModel):
    templateSlug: str
    to: dict
    attributes: dict = {}

class ContactUpdateReq(BaseModel):
    properties: dict = {}

class TemplateCreateReq(BaseModel):
    slug: str
    name: str
    subject: str
    body_html: str
    sender_name: str
    from_email: str

class TemplateUpdateReq(BaseModel):
    subject: str | None = None
    body_html: str | None = None

class PreviewReq(BaseModel):
    contact: dict = {}

def to_dict(obj):
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return obj

# Core
@app.post("/api/track")
async def track(r: TrackReq):
    assert synapse
    return to_dict(await synapse.track(external_id=r.userId, event_name=r.event, attributes=r.attributes))

@app.post("/api/track/batch")
async def track_batch(r: BatchTrackReq):
    assert synapse
    return to_dict(await synapse.track_batch(events=r.events))

@app.post("/api/identify")
async def identify(r: IdentifyReq):
    assert synapse
    return to_dict(await synapse.identify(external_id=r.userId, email=r.email, properties=r.properties))

@app.post("/api/identify/batch")
async def identify_batch(r: BatchIdentifyReq):
    assert synapse
    return to_dict(await synapse.identify_batch(contacts=r.contacts))

@app.post("/api/send")
async def send(r: SendReq):
    assert synapse
    return to_dict(await synapse.send(template_slug=r.templateSlug, to=r.to, attributes=r.attributes))

# Contacts
@app.get("/api/contacts")
async def list_contacts(page: int = 1, limit: int = 20):
    assert synapse
    return await synapse.contacts.list(page=page, per_page=limit)

@app.get("/api/contacts/{cid}")
async def get_contact(cid: str):
    assert synapse
    return to_dict(await synapse.contacts.get(cid))

@app.put("/api/contacts/{eid}")
async def update_contact(eid: str, r: ContactUpdateReq):
    assert synapse
    return to_dict(await synapse.contacts.update(eid, data=r.model_dump(exclude_none=True)))

@app.delete("/api/contacts/{eid}")
async def delete_contact(eid: str):
    assert synapse
    await synapse.contacts.delete(eid)
    return {"success": True}

# Templates
@app.get("/api/templates")
async def list_templates():
    assert synapse
    r = await synapse.templates.list()
    return [to_dict(t) for t in r] if isinstance(r, list) else r

@app.post("/api/templates")
async def create_template(r: TemplateCreateReq):
    assert synapse
    return to_dict(await synapse.templates.create(r.model_dump()))

@app.get("/api/templates/{slug}")
async def get_template(slug: str):
    assert synapse
    return to_dict(await synapse.templates.get(slug))

@app.put("/api/templates/{slug}")
async def update_template(slug: str, r: TemplateUpdateReq):
    assert synapse
    return to_dict(await synapse.templates.update(slug, params=r.model_dump(exclude_none=True)))

@app.delete("/api/templates/{slug}")
async def delete_template(slug: str):
    assert synapse
    await synapse.templates.delete(slug)
    return {"success": True}

@app.post("/api/templates/{slug}/preview")
async def preview_template(slug: str, r: PreviewReq):
    assert synapse
    return to_dict(await synapse.templates.preview(slug, params={"contact": r.contact}))
