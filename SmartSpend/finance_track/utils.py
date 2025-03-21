import urllib.parse
from django.conf import settings
import uuid

def get_truelayer_auth_url():
    base_auth_url = "https://auth.truelayer-sandbox.com/?response_type=code&client_id=sandbox-smartspend-9f4cc6&scope=info%20accounts%20balance%20cards%20transactions%20direct_debits%20standing_orders%20offline_access&redirect_uri=http://127.0.0.1:5432/truelayer/callback&providers=uk-cs-mock%20uk-ob-all%20uk-oauth-all"

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

def get_client_ip(request):
    """
    Extracts the client's IP address from the Django request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # In case of multiple IPs, take the first one
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip