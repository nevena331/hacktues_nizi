from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Receipt, Transaction
from .expense_classifier import classify_expense
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
import requests
from .utils import get_client_ip
from django.shortcuts import redirect
from .utils import get_truelayer_auth_url
from django.shortcuts import get_object_or_404, render
from .models import Receipt

def receipt_detail(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id)
    return render(request, "/finance_track/receipt_detail.html", {"receipt": receipt})


def frontpage(request):
    return render(request, '/finance_track/frontpage.html')

def process_receipt(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id)
    if receipt.scanned_text and not receipt.processed:
        category = classify_expense(receipt.scanned_text)
        receipt.predicted_category = category
        receipt.processed = True
        receipt.save()

        Transaction.objects.create(
            user=receipt.user,
            transaction_type="EXPENSE",
            amount=receipt.predicted_amount if receipt.predicted_amount else 0,
            category=category,
            description="Auto-created from receipt scan",
            source="receipt"
        )
    return render(request, "/finance_track/receipt_details.html", {"receipt": receipt})



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
    # Store tokens in session (for demo purposes)
    request.session['access_token'] = token_data.get('access_token')
    request.session['refresh_token'] = token_data.get('refresh_token')
    request.session['expires_in'] = token_data.get('expires_in')

    return JsonResponse(token_data)


def connect_truelayer(request):
    auth_url = get_truelayer_auth_url()
    return redirect(auth_url)




def get_accounts(request, access_token):
    """
    Retrieves user account data from TrueLayer Data API,
    including the end-user's IP address to avoid rate limits.
    """
    user_ip = get_client_ip(request)
    url = "https://api.truelayer-sandbox.com/data/v1/accounts"  # Use sandbox URL; update if live.
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-PSU-IP": user_ip,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
def frontpage(request):
    return render(request, "frontpage.html")
