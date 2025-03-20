from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontpage),
    path('test/', views.test)
]