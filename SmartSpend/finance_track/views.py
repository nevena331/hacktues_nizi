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
    return render(request, "finance_track/receipt_detail.html", {"receipt": receipt})


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
    return render(request, "finance_track/receipt_detail.html", {"receipt": receipt})





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

    return print()


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

def get_transactions(access_token, request, account_id):
    """Retrieve transactions for a given account."""
    user_ip = get_client_ip(request)
    url = f"https://api.truelayer-sandbox.com/data/v1/accounts/{account_id}/transactions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-PSU-IP": user_ip,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()  # Expected to include a "results" list

def transactions_view(request):
    """View to display transaction history for all linked accounts."""
    access_token = request.session.get("access_token")
    if not access_token:
        return HttpResponseBadRequest("No access token available. Please connect your bank account first.")

    try:
        accounts_data = get_accounts(access_token, request)
        accounts = accounts_data.get("results", [])
        transactions_all = {}
        for account in accounts:
            account_id = account.get("account_id")
            if account_id:
                tx_data = get_transactions(access_token, request, account_id)
                transactions_all[account_id] = tx_data.get("results", [])
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    # Render the transactions in a template
    #return render(request, "transactions.html", {"transactions_all": transactions_all})
    print(transactions_all)


def homepage(request):
    """
    Renders the homepage.
    """
    context = {'page_title': 'HomePage'}
    return render(request, 'homepage.html', context)
def dashboard(request):
    """
    Renders the Dashboard.
    """
    context = {'page_title': 'Dashboard'}
    return render(request, 'dashboard.html', context)
def transactions(request):
    """
    Renders the Transactions.
    """
    context = {'page_title': 'Transactions'}
    return render(request, 'transactions.html', context)
def receipt_detail(request):
    """
    Renders the receipt_detail.
    """
    context = {'page_title': 'Receipt Detail'}
    return render(request, 'receipt_detail.html', context)
def receipt_results(request):
    """
    Renders the receipt_results.
    """
    context = {'page_title': 'Receipt Results'}
    return render(request, 'receipt_results.html', context)
def add_expense(request):
    """
    Renders the add_expense.
    """
    context = {'page_title': 'Add Expense'}
    return render(request, 'add_expense.html', context)
def auth(request):
    """
    Renders the auth.
    """
    context = {'page_title': 'Authentification'}
    return render(request, 'auth.html', context)