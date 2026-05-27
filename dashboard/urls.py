from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('invoices/', views.invoice_list_admin, name='invoice_list_admin'),
    path('agent/', views.agent_dashboard, name='agent'),
    path('agent/ticket/<int:pk>/', views.agent_ticket_detail, name='agent_ticket_detail'),
    path('settings/', views.settings_view, name='settings'),
]
