import json
import requests
import base64
import cv2
import re
import uuid
import numpy as np
import pytesseract
from dateutil import parser
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model, authenticate, views as auth_views
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

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name", "").strip()
        email      = request.POST.get("email", "").strip()
        password   = request.POST.get("password", "").strip()
        if not first_name or not last_name or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "finance_track/register.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "A user with that email already exists.")
            return render(request, "finance_track/register.html", {"first_name": first_name, "last_name": last_name, "email": email})
        user = User.objects.create_user(email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        messages.success(request, "Registration successful. Please log in.")
        return redirect('login')
    return render(request, "finance_track/register.html")

def logout_view(request):
    logout(request)
    return redirect("finance_track/homepage")

@csrf_exempt
def add_manual_transaction(request):
    if request.method == "POST":
        data = json.loads(request.body)
        date_str = data.get("date")
        description = data.get("description")
        amount = data.get("amount")
        transaction_type = data.get("transaction_type")
        user = request.user if request.user.is_authenticated else None
        try:
            date_obj = parser.parse(date_str)
        except:
            date_obj = timezone.now()
        transaction = Transaction.objects.create(
            user=user,
            transaction_type=transaction_type.upper(),
            amount=amount,
            category="Manual",
            description=description,
            date=date_obj,
            source="manual"
        )
        return JsonResponse({
            "id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "amount": float(transaction.amount),
            "description": transaction.description,
            "date": transaction.date.isoformat()
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def upload_receipt(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    image_data = data.get("image")
    if not image_data:
        return JsonResponse({"error": "No image data received"}, status=400)
    try:
        image_bytes = base64.b64decode(image_data)
    except:
        return JsonResponse({"error": "Image decoding failed"}, status=400)
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        return JsonResponse({"error": "Invalid image data"}, status=400)
    custom_config = r'--oem 3 --psm 6'
    scanned_text = pytesseract.image_to_string(image, config=custom_config, lang="eng")
    if len(scanned_text.strip()) < 10:
        scanned_text = pytesseract.image_to_string(image, config=custom_config, lang="eng")
    predicted_category = classify_expense(scanned_text)
    amount_match = re.search(r'(\d+[.,]?\d*)', scanned_text)
    if amount_match:
        try:
            predicted_amount = float(amount_match.group(1).replace(",", "."))
        except:
            predicted_amount = 0.0
    else:
        predicted_amount = 0.0
    image_file = ContentFile(image_bytes, name="receipt_%s.jpg" % uuid.uuid4().hex[:6])
    user = request.user if request.user.is_authenticated else None
    receipt = Receipt.objects.create(
        user=user,
        image=image_file,
        scanned_text=scanned_text,
        predicted_category=predicted_category,
        predicted_amount=predicted_amount,
        date_scanned=timezone.now(),
        processed=True
    )
    transaction = Transaction.objects.create(
        user=user,
        transaction_type="EXPENSE",
        amount=predicted_amount,
        category=predicted_category,
        description="Auto-created from receipt scan",
        date=timezone.now(),
        source="receipt"
    )
    return JsonResponse({
        "message": "Receipt processed, classified, and saved successfully!",
        "receipt": {
            "id": receipt.id,
            "scanned_text": receipt.scanned_text,
            "predicted_category": receipt.predicted_category,
            "predicted_amount": float(receipt.predicted_amount),
            "date_scanned": receipt.date_scanned.isoformat()
        },
        "transaction": {
            "id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "amount": float(transaction.amount),
            "category": transaction.category,
            "description": transaction.description,
            "date": transaction.date.isoformat(),
            "source": transaction.source
        }
    })
