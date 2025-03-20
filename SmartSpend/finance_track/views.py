from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
import requests
from SmartSpend.settings import REVOLUT_API_KEY

# Create your views here.

def frontpage(request):
    return render(request, "dashboard.html")

def test(request):
    return HttpResponse()




# Use the sandbox URL for testing; switch to production as needed.
API_BASE_URL = "https://sandbox-b2b.revolut.com/api/1.0/"
api_key =  REVOLUT_API_KEY
 # Replace with your actual API key

# Set up headers with your authorization token.
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Example: Fetch account information
endpoint = f"{API_BASE_URL}accounts"
response = requests.get(endpoint, headers=headers)

if response.ok:
    accounts = response.json()
    print("Account details:", accounts)
else:
    print("Error:", response.status_code, response.text)