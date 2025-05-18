#hubspot
import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from integrations.integration_item import IntegrationItem

CLIENT_ID = '8fd1fd7c-376e-4d3b-bf57-Dummy'
CLIENT_SECRET = 'b5767a51-934c-4fe9-b6fd-Dummy'
#for security purpose im not sharing the actual Client_ID and Client_secret
#but if I was to build a production grade application I would have used .env to store them
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
AUTH_URL = (
    f'https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}'
    f'&scope=crm.objects.contacts.read&redirect_uri={REDIRECT_URI}&response_type=code'
)

async def authorize_hubspot(user_id: str, org_id: str) -> str:
    """
    Generate HubSpot OAuth authorization URL with state saved in Redis.
    """
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)
    return f'{AUTH_URL}&state={encoded_state}'

async def oauth2callback_hubspot(request: Request):
    """
    Handle OAuth2 callback from HubSpot. Validate state and exchange code for access token.
    """
    # Check for OAuth error returned by HubSpot
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))

    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')

    if not code or not encoded_state:
        raise HTTPException(status_code=400, detail="Missing 'code' or 'state' parameter")

    try:
        state_data = json.loads(encoded_state)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in 'state' parameter")

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    if not user_id or not org_id or not original_state:
        raise HTTPException(status_code=400, detail="Invalid state contents")

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    if not saved_state:
        raise HTTPException(status_code=400, detail="State expired or not found in Redis")

    try:
        saved_state_data = json.loads(saved_state)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid saved state JSON in Redis")

    if original_state != saved_state_data.get('state'):
        raise HTTPException(status_code=400, detail='State mismatch.')

    # Exchange authorization code for access token
    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    # Save credentials in Redis with 10 minutes expiry
    await add_key_value_redis(
        f'hubspot_credentials:{org_id}:{user_id}',
        response.text,
        expire=600
    )

    # Return simple HTML to close the browser window
    return HTMLResponse(content="<html><script>window.close();</script></html>")

async def get_hubspot_credentials(user_id: str, org_id: str):
    """
    Retrieve stored HubSpot credentials from Redis and delete them after retrieval.
    """
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail="No credentials found")
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    return json.loads(credentials)

async def create_integration_item_metadata_object(response_json: dict) -> IntegrationItem:
    """
    Create IntegrationItem object from HubSpot contact data.
    """
    return IntegrationItem(
        id=response_json.get('id'),
        type='contact',
        name=(
            response_json.get('properties', {}).get('firstname', 'Unknown') + ' ' +
            response_json.get('properties', {}).get('lastname', '')
        ).strip(),
        creation_time=response_json.get('createdAt'),
        last_modified_time=response_json.get('updatedAt'),
        parent_id=None
    )

async def get_items_hubspot(credentials: dict) -> list[IntegrationItem]:
    """
    Fetch HubSpot contacts using access token and return as list of IntegrationItems.
    """
    access_token = credentials.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid credentials: access token missing")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://api.hubapi.com/crm/v3/objects/contacts',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    contacts = data.get('results', [])
    items = []

    for contact in contacts:
        item = await create_integration_item_metadata_object(contact)
        items.append(item)

    return items
