from django.urls import path
from . import views
from .views import process_receipt
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('homepage/', views.homepage, name='homepage'),
    path('transactions/', views.transactions_page, name='transactions_page'),
    path('receipt_detail/', views.receipt_detail, name='receipt_detail'),
    path('receipt_results/', views.receipt_results, name='receipt_results'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('connect_truelayer/', views.connect_truelayer, name='connect_truelayer'),
    path('truelayer/callback/', views.truelayer_callback, name='truelayer_callback'),
    path("receipt/<int:receipt_id>/process/", process_receipt, name="process_receipt"),
    path('upload-receipt/', views.upload_receipt, name='upload_receipt'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='finance_track/login.html'), name='login', next_page='finance_track/dashboard.html'),
    path('logout/', auth_views.LogoutView.as_view(next_page='finance_track/homepage.html'), name='logout'),
]
