from django.urls import path

from . import views

app_name = 'postpaid'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('activate/', views.activate, name='activate'),
    path('activate/request-inspection/', views.request_inspection_view, name='request_inspection'),
    path('activate/system-suggestion/', views.system_suggestion_view, name='system_suggestion'),
    path('activate/pending/', views.contract_pending, name='contract_pending'),
    path('admin/approve/', views.admin_approve_contract_view, name='admin_approve'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/pay/', views.pay_invoice_view, name='pay_invoice'),
    path('consumption/', views.consumption_history, name='consumption'),
    path('debt/pdf/', views.debt_pdf, name='debt_pdf'),
]
