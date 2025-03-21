from django.urls import path
from . import views
from .views import process_receipt

urlpatterns = [
    path('', views.frontpage),
    path('connect_truelayer/', views.connect_truelayer, name='connect_truelayer'),
    path('truelayer/callback/', views.truelayer_callback, name='truelayer_callback'),
    path("receipt/<int:receipt_id>/process/", process_receipt, name="process_receipt"),
]