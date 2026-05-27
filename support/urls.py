from django.urls import path

from . import views

app_name = 'support'

urlpatterns = [
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/search/', views.ticket_search, name='ticket_search'),
    path('operator/', views.operator_dashboard_view, name='operator_dashboard'),
]
