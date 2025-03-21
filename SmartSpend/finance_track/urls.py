from django.urls import path
from . import views
from .views import process_receipt
from django.contrib.auth import views as auth_views

app_name = 'finance_track'

urlpatterns = [
    path('', views.homepage),
    path('dashboard/', views.dashboard),
    path('transactions/', views.transactions),
    path('receipt_detail/', views.receipt_detail),
    path('receipt_results/', views.receipt_results),
    path('add_expense/', views.add_expense),
    path('auth/', views.auth),
    path('connect_truelayer/', views.connect_truelayer, name='connect_truelayer'),
    path('truelayer/callback/', views.truelayer_callback, name='truelayer_callback'),
    path("receipt/<int:receipt_id>/process/", process_receipt, name="process_receipt"),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='finance_track/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts/login/'), name='logout'),
    path('transactions/', views.transaction_list, name='transaction_list'),
]
