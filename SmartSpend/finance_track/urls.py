from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontpage),
    path('test/', views.test),
    path('connect_truelayer/', views.connect_truelayer, name='connect_truelayer'),
]