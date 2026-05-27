from django.contrib import admin

from .models import PaymentGateway, GatewayTransaction


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(GatewayTransaction)
class GatewayTransactionAdmin(admin.ModelAdmin):
    list_display = ('gateway', 'transaction', 'gateway_reference', 'status', 'created_at')
    list_filter = ('status', 'gateway')
    search_fields = ('gateway_reference', 'transaction__transaction_id')
