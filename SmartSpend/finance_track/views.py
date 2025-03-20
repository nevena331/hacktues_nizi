from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, JsonResponse, HttpResponseBadRequest
import requests
# from SmartSpend.settings import REVOLUT_API_KEY
from django.views.decorators.http import require_http_methods
from django.conf import settings

# Create your views here.

def frontpage(request):
    return render(request, "dashboard.html")

def test(request):
    return HttpResponse()




# Use the sandbox URL for testing; switch to production as needed.
# API_BASE_URL = "https://sandbox-b2b.revolut.com/api/1.0/"
# api_key =  REVOLUT_API_KEY
#  # Replace with your actual API key

# # Set up headers with your authorization token.
# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json"
# }

# # Example: Fetch account information
# endpoint = f"{API_BASE_URL}accounts"
# response = requests.get(endpoint, headers=headers)

# if response.ok:
#     accounts = response.json()
#     print("Account details:", accounts)
# else:
#     print("Error:", response.status_code, response.text)


@require_http_methods(["GET", "POST"])
def truelayer_callback(request):
    """
    Handles the callback from TrueLayer after user consent.
    Extracts the authorization code and exchanges it for an access token.
    """
    auth_code = request.POST.get('code') or request.GET.get('code')
    state = request.POST.get('state') or request.GET.get('state')  # Optional: validate state if used

    if not auth_code:
        return HttpResponseBadRequest("No authorization code provided.")

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': settings.TRUELAYER_REDIRECT_URI,
        'client_id': settings.TRUELAYER_CLIENT_ID,
        'client_secret': settings.TRUELAYER_CLIENT_SECRET,
    }

    token_response = requests.post(settings.TRUELAYER_TOKEN_URL, data=data)
    if token_response.status_code != 200:
        return JsonResponse(
            {'error': 'Token exchange failed', 'details': token_response.text},
            status=token_response.status_code
        )

    token_data = token_response.json()
    # For demonstration, store tokens in the session (for production, use secure storage)
    request.session['access_token'] = token_data.get('access_token')
    request.session['refresh_token'] = token_data.get('refresh_token')
    request.session['expires_in'] = token_data.get('expires_in')

    print(f"Token data: {token_data}")
    return JsonResponse(token_data)


from django.shortcuts import redirect
from .utils import get_truelayer_auth_url

def connect_truelayer(request):
    # Generate the TrueLayer auth URL
    auth_url = get_truelayer_auth_url()
    # Redirect the user to TrueLayer's authentication dialog
    return redirect(auth_url)
