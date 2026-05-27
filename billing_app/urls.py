from django.urls import path

from . import views

app_name = 'billing'

urlpatterns = [
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/pay/', views.pay_invoice_view, name='pay_invoice'),
    path('invoices/<int:pk>/pdf/', views.download_invoice_pdf, name='invoice_pdf'),
    path('consumption/', views.consumption_history, name='consumption'),
]
