import urllib.parse
from django.conf import settings
import uuid

def get_truelayer_auth_url():
    base_auth_url = "https://auth.truelayer-sandbox.com/"

    # Generate a unique state token (in production, you may want to store and later validate this)
    state = str(uuid.uuid4())
    # Optionally, generate a nonce too
    nonce = str(uuid.uuid4())

    # Define the query parameters for the auth URL
    params = {
        "response_type": "code",
        "client_id": settings.TRUELAYER_CLIENT_ID,
        "redirect_uri": settings.TRUELAYER_REDIRECT_URI,
        "scope": "accounts transactions balance offline_access",
        "state": state,
        "nonce": nonce,
    }

    # Construct the URL with query parameters
    auth_url = f"{base_auth_url}?{urllib.parse.urlencode(params)}"
    return auth_url
