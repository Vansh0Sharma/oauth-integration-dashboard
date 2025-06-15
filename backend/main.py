import os
import json
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware

# Airtable, Notion, HubSpot integrations
from integrations.airtable import (
    authorize_airtable,
    get_items_airtable,
    oauth2callback_airtable,
    get_airtable_credentials
)

from integrations.notion import (
    authorize_notion,
    get_items_notion,
    oauth2callback_notion,
    get_notion_credentials
)

from integrations.hubspot import (
    get_hubspot_credentials,
    get_items_hubspot,
)
from integrations.hubspot import router as hubspot_router  # ✅ includes authorize + callback routes

app = FastAPI()

# Register HubSpot router (contains /authorize and /oauth2callback)
app.include_router(hubspot_router)

# CORS config for frontend (React at localhost:3000)
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Ping": "Pong"}

# ------------------- Airtable -------------------
@app.post("/integrations/airtable/authorize")
async def authorize_airtable_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await authorize_airtable(user_id, org_id)

@app.get("/integrations/airtable/oauth2callback")
async def oauth2callback_airtable_integration(request: Request):
    return await oauth2callback_airtable(request)

@app.post("/integrations/airtable/credentials")
async def get_airtable_credentials_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await get_airtable_credentials(user_id, org_id)

@app.post("/integrations/airtable/load")
async def get_airtable_items_integration(credentials: str = Form(...)):
    return await get_items_airtable(json.loads(credentials))

# ------------------- Notion -------------------
@app.post("/integrations/notion/authorize")
async def authorize_notion_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await authorize_notion(user_id, org_id)

@app.get("/integrations/notion/oauth2callback")
async def oauth2callback_notion_integration(request: Request):
    return await oauth2callback_notion(request)

@app.post("/integrations/notion/credentials")
async def get_notion_credentials_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await get_notion_credentials(user_id, org_id)

@app.post("/integrations/notion/load")
async def get_notion_items_integration(credentials: str = Form(...)):
    return await get_items_notion(json.loads(credentials))

# ------------------- HubSpot -------------------
# ✅ /authorize and /oauth2callback come from hubspot_router

@app.post("/integrations/hubspot/credentials")
async def get_hubspot_credentials_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await get_hubspot_credentials(user_id, org_id)

@app.post("/integrations/hubspot/get_hubspot_items")
async def load_hubspot_items_integration(credentials: str = Form(...)):
    return await get_items_hubspot(json.loads(credentials))
