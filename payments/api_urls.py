from django.urls import path

from . import api_views

urlpatterns = [
    path('customers/', api_views.CustomerListAPI.as_view(), name='api_customer_list'),
    path('customers/<int:pk>/', api_views.CustomerDetailAPI.as_view(), name='api_customer_detail'),
    path('invoices/', api_views.InvoiceListAPI.as_view(), name='api_invoice_list'),
    path('transactions/', api_views.TransactionListAPI.as_view(), name='api_transaction_list'),
    path('recharge/', api_views.RechargeAPI.as_view(), name='api_recharge'),
    path('pay-invoice/', api_views.PayInvoiceAPI.as_view(), name='api_pay_invoice'),
]
