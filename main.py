import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from pyrx_synapse import AsyncSynapse

synapse: AsyncSynapse | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global synapse
    synapse = AsyncSynapse(
        api_key=os.environ["SYNAPSE_API_KEY"],
        workspace_id=os.environ["SYNAPSE_WORKSPACE_ID"],
    )
    yield
    if synapse:
        await synapse.close()

app = FastAPI(title="Synapse FastAPI Example", lifespan=lifespan)

class TrackRequest(BaseModel):
    user_id: str
    event: str
    attributes: dict = {}

class IdentifyRequest(BaseModel):
    user_id: str
    email: str
    properties: dict = {}

class SendRequest(BaseModel):
    template_slug: str
    user_id: str
    email: str
    attributes: dict = {}

@app.post("/api/track")
async def track_event(req: TrackRequest):
    assert synapse is not None
    await synapse.track(external_id=req.user_id, event_name=req.event, attributes=req.attributes)
    return {"success": True}

@app.post("/api/identify")
async def identify_contact(req: IdentifyRequest):
    assert synapse is not None
    await synapse.identify(external_id=req.user_id, email=req.email, properties=req.properties)
    return {"success": True}

@app.post("/api/send")
async def send_email(req: SendRequest):
    assert synapse is not None
    await synapse.send(template_slug=req.template_slug, to={"user_id": req.user_id, "email": req.email}, attributes=req.attributes)
    return {"success": True}
