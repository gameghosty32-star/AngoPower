from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin'),
    path('agent/', views.agent_dashboard, name='agent'),
    path('agent/ticket/<int:pk>/', views.agent_ticket_detail, name='agent_ticket_detail'),
]
