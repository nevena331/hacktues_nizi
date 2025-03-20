from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontpage),
    path('test/', views.test),
    path('truelayer/callback/', views.truelayer_callback, name='truelayer_callback'),
]