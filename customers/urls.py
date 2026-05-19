from django.urls import path

from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('balance/', views.check_balance, name='balance'),
    path('recharge/', views.request_recharge, name='recharge'),
    path('transactions/', views.transaction_history, name='transactions'),
]
