from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'meter_number', 'customer_type', 'current_balance', 'debt')
    list_filter = ('customer_type',)
    search_fields = ('meter_number', 'user__username', 'user__email')
