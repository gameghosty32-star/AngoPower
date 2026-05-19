from django.contrib import admin

from .models import Category, Ticket, Message


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('author', 'content', 'created_at')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('pk', 'subject', 'customer', 'category', 'priority', 'status', 'assigned_to', 'created_at')
    list_filter = ('priority', 'status', 'category')
    search_fields = ('subject', 'customer__meter_number', 'customer__user__username')
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'created_at')
    readonly_fields = ('ticket', 'author', 'content', 'created_at')
