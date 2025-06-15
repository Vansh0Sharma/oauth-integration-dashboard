import os
import json
import httpx
from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from urllib.parse import urlencode
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Redis client for storing tokens
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Real credentials from .env
CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
REDIRECT_URI = os.getenv("HUBSPOT_REDIRECT_URI")

AUTH_URL = "https://app.hubspot.com/oauth/authorize"
TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

# Step 1: Start OAuth flow — frontend will POST to this
@router.post("/integrations/hubspot/authorize")
async def authorize_hubspot(user_id: str = "123", org_id: str = "456"):
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "crm.objects.contacts.read crm.objects.contacts.write oauth",
        "state": f"{user_id}:{org_id}",
        "response_type": "code",
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    return {"url": url}  # 👈 frontend uses this to redirect

# Step 2: HubSpot redirects to this callback with ?code=...
@router.get("/integrations/hubspot/oauth2callback")
async def oauth2callback_hubspot(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state:
        return {"error": "Missing code or state"}

    user_id, org_id = state.split(":")

    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        }

        response = await client.post(TOKEN_URL, data=data, headers=headers)

    if response.status_code != 200:
        return {"error": "Token exchange failed", "details": response.text}

    token_data = response.json()
    token_data.update({"user_id": user_id, "org_id": org_id})

    await r.set(f"hubspot:{user_id}:{org_id}", json.dumps(token_data))
    return RedirectResponse("http://localhost:3000")  # 👈 optional redirect to frontend

# Called from main.py to retrieve stored credentials
async def get_hubspot_credentials(user_id, org_id):
    value = await r.get(f"hubspot:{user_id}:{org_id}")
    if value:
        return json.loads(value)
    return {"access_token": "not-found"}

# Called to load data using stored credentials
async def get_items_hubspot(credentials):
    access_token = credentials.get("access_token")
    if not access_token:
        return {"error": "Missing access token"}

    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "HubSpot API error", "details": response.text}

    return response.json()
