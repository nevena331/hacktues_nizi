from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Receipt, Transaction
from .expense_classifier import classify_expense
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from SmartSpend.settings import *
import requests
from .utils import get_client_ip
from django.shortcuts import redirect
from .utils import get_truelayer_auth_url
from django.shortcuts import get_object_or_404, render
from .models import Receipt
from django.contrib.auth import views as auth_views
from requests.auth import HTTPBasicAuth

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





from .utils import get_truelayer_auth_url, get_client_ip

@require_http_methods(["GET", "POST"])
def truelayer_callback(request):
    # Extract the authorization code (and optionally the state)
    auth_code = request.POST.get('code') or request.GET.get('code')
    state = request.POST.get('state') or request.GET.get('state')  # Optionally validate state if needed

    if not auth_code:
        return HttpResponseBadRequest("No authorization code provided.")

    # Prepare the token exchange payload (do NOT include client_id/secret here)
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': TRUELAYER_REDIRECT_URI,
    }

    # Send client credentials using HTTP Basic Auth
    auth = HTTPBasicAuth(TRUELAYER_CLIENT_ID, TRUELAYER_CLIENT_SECRET)
    token_response = requests.post(TRUELAYER_TOKEN_URL, data=data, auth=auth)
    if token_response.status_code != 200:
        return JsonResponse(
            {'error': 'Token exchange failed', 'details': token_response.text},
            status=token_response.status_code
        )

    token_data = token_response.json()
    # Store tokens in session (for demonstration purposes)
    request.session['access_token'] = token_data.get('access_token')
    request.session['refresh_token'] = token_data.get('refresh_token')
    request.session['expires_in'] = token_data.get('expires_in')

    # Redirect to the homepage after successful token exchange
    return redirect('homepage')


def connect_truelayer(request):
    auth_url = get_truelayer_auth_url()
    return redirect(auth_url)


def get_accounts(request, access_token):
    """
    Retrieves user account data from TrueLayer Data API,
    including the end-user's IP address to avoid rate limits.
    """
    user_ip = get_client_ip(request)
    url = "https://api.truelayer-sandbox.com/data/v1/accounts"  # Use sandbox URL; update for live as needed
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
    return response.json()


def transactions_view(request):
    """View to display transaction history for all linked accounts."""
    access_token = request.session.get("access_token")
    if not access_token:
        return HttpResponseBadRequest("No access token available. Please connect your bank account first.")

    try:
        accounts_data = get_accounts(request, access_token)
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
    return render(request, "finance_track/transactions.html", {"transactions_all": transactions_all})


def homepage(request):
    """Renders the homepage."""
    context = {'page_title': 'HomePage'}
    return render(request, 'finance_track/homepage.html', context)

def dashboard(request):
    """Renders the Dashboard."""
    context = {'page_title': 'Dashboard'}
    return render(request, 'finance_track/dashboard.html', context)

def transactions(request):
    """Renders the Transactions page."""
    context = {'page_title': 'Transactions'}
    return render(request, 'finance_track/transactions.html', context)

def receipt_detail(request):
    """Renders the Receipt Detail page."""
    context = {'page_title': 'Receipt Detail'}
    return render(request, 'finance_track/receipt_detail.html', context)

def receipt_results(request):
    """Renders the Receipt Results page."""
    context = {'page_title': 'Receipt Results'}
    return render(request, 'finance_track/receipt_results.html', context)

def add_expense(request):
    """Renders the Add Expense page."""
    context = {'page_title': 'Add Expense'}
    return render(request, 'finance_track/add_expense.html', context)

def auth(request):
    """Renders the Authentication page."""
    context = {'page_title': 'Authentification'}
    return render(request, 'finance_track/auth.html', context)

from django.contrib.auth import authenticate, login, logout
# from .forms import RegisterForm, LoginForm
from django.contrib import messages

# def register_view(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()
#             messages.success(request, "Registration successful.")
#             return redirect('login')
#     else:
#         form = RegisterForm()
#     return render(request, 'accounts/register.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('home')  # redirect to homepage
#         else:
#             messages.error(request, "Invalid credentials.")
#     else:
#         form = LoginForm()
#     return render(request, 'accounts/login.html', {'form': form})

# def logout_view(request):
#     logout(request)
#     return redirect('login')