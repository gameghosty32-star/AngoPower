from django.urls import path

from . import views

app_name = 'payment_gateways'

urlpatterns = [
    path('', views.gateway_list, name='list'),
    path('select/<str:context_key>/<str:context_value>/', views.gateway_select, name='select'),
    path('process/<str:gateway_code>/<str:context_key>/<str:context_value>/', views.gateway_process, name='process'),
]
