from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError

# Create your views here.

def index(request):
    return HttpResponse("Hello")