import json
import requests
from dateutil import parser

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model, views as auth_views

from .models import Receipt, Transaction
from .expense_classifier import classify_expense
from .utils import get_client_ip, get_truelayer_auth_url
from .forms import RegistrationForm

User = get_user_model()

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
    state = request.POST.get('state') or request.GET.get('state')
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
        return JsonResponse({'error': 'Token exchange failed', 'details': token_response.text}, status=token_response.status_code)
    token_data = token_response.json()
    request.session['access_token'] = token_data.get('access_token')
    request.session['refresh_token'] = token_data.get('refresh_token')
    request.session['expires_in'] = token_data.get('expires_in')
    return HttpResponse("TrueLayer tokens obtained and stored in session.")

def connect_truelayer(request):
    auth_url = get_truelayer_auth_url()
    return redirect(auth_url)

def get_accounts(request, access_token):
    user_ip = get_client_ip(request)
    url = "https://api.truelayer-sandbox.com/data/v1/accounts"
    headers = {"Authorization": f"Bearer {access_token}", "X-PSU-IP": user_ip}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_transactions(access_token, request, account_id):
    user_ip = get_client_ip(request)
    url = f"https://api.truelayer-sandbox.com/data/v1/accounts/{account_id}/transactions"
    headers = {"Authorization": f"Bearer {access_token}", "X-PSU-IP": user_ip}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def transactions_view(request):
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
    print(transactions_all)
    return HttpResponse("Transactions retrieved. Check server logs for output.")

def homepage(request):
    context = {'page_title': 'HomePage'}
    return render(request, 'finance_track/homepage.html', context)

def dashboard(request):
    context = {'page_title': 'Dashboard'}
    return render(request, 'finance_track/dashboard.html', context)

def transactions_page(request):
    transactions = Transaction.objects.filter(user=request.user) if request.user.is_authenticated else []
    context = {'page_title': 'Transactions'}
    return render(request, 'finance_track/transactions.html', context)

def receipt_results(request):
    context = {'page_title': 'Receipt Results'}
    return render(request, 'finance_track/receipt_results.html', context)

def add_expense(request):
    context = {'page_title': 'Add Expense'}
    return render(request, 'finance_track/add_expense.html', context)

def auth_page(request):
    context = {'page_title': 'Authentification'}
    return render(request, 'finance_track/auth.html', context)

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("finance_track:transaction_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegistrationForm()
    return render(request, "finance_track/register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("finance_track:homepage")
