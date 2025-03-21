from django.urls import path, include
from . import views
from .views import process_receipt
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage),
    path('dashboard/', views.dashboard),
    path('transactions/', views.transactions_view),
    path('receipt_detail/', views.receipt_detail),
    path('receipt_results/', views.receipt_results),
    path('add_expense/', views.add_expense),
    path('auth/', views.auth),
    path('connect_truelayer/', views.connect_truelayer, name='connect_truelayer'),
    path('truelayer/callback/', views.truelayer_callback, name='truelayer_callback'),
    path("receipt/<int:receipt_id>/process/", process_receipt, name="process_receipt"),
    path('accounts/', include('finance_track.urls')),
]