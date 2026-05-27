from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone

from customers.models import Customer
from billing_app.models import Invoice
from payments.models import Transaction
from support.models import Ticket, Category, Message
from postpaid.models import PostpaidContract


@login_required
def login_redirect(request):
    if request.user.user_type == 'admin':
        return redirect('dashboard:admin')
    elif request.user.user_type == 'operator':
        return redirect('dashboard:agent')
    return redirect('customers:dashboard')


def _admin_or_operator(user):
    return user.user_type in ('admin', 'operator')


@login_required
@user_passes_test(_admin_or_operator)
def admin_dashboard(request):
    total_customers = Customer.objects.count()
    prepaid_count = Customer.objects.filter(customer_type='prepaid').count()
    postpaid_count = Customer.objects.filter(customer_type='postpaid').count()
    total_revenue = Transaction.objects.filter(
        status='completed', transaction_type='payment'
    ).aggregate(total=Sum('amount'))['total'] or 0
    open_tickets = Ticket.objects.filter(status__in=('open', 'in_progress')).count()
    pending_contracts = PostpaidContract.objects.filter(status='pending').count()
    recent_tickets = Ticket.objects.select_related('customer__user', 'category').order_by('-created_at')[:5]
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_customers': total_customers,
        'prepaid_count': prepaid_count,
        'postpaid_count': postpaid_count,
        'total_revenue': total_revenue,
        'open_tickets': open_tickets,
        'pending_contracts': pending_contracts,
        'recent_tickets': recent_tickets,
    })


@login_required
@user_passes_test(_admin_or_operator)
def customer_list(request):
    q = request.GET.get('q', '')
    customers = Customer.objects.select_related('user').all()
    if q:
        customers = customers.filter(
            Q(user__username__icontains=q) |
            Q(meter_number__icontains=q) |
            Q(user__email__icontains=q) |
            Q(phone__icontains=q)
        )
    return render(request, 'dashboard/customer_list.html', {
        'customers': customers,
        'q': q,
    })


@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.meter_number = request.POST.get('meter_number', customer.meter_number)
        customer.customer_type = request.POST.get('customer_type', customer.customer_type)
        customer.current_balance = request.POST.get('current_balance', customer.current_balance)
        customer.debt = request.POST.get('debt', customer.debt)
        customer.phone = request.POST.get('phone', customer.phone)
        customer.address = request.POST.get('address', customer.address)
        customer.province = request.POST.get('province', customer.province)
        customer.municipio = request.POST.get('municipio', customer.municipio)
        customer.save()
        messages.success(request, f'Cliente {customer.meter_number} actualizado.')
        return redirect('dashboard:customer_list')
    return render(request, 'dashboard/customer_edit.html', {'customer': customer})


@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    meter = customer.meter_number
    customer.user.delete()
    customer.delete()
    messages.success(request, f'Cliente {meter} removido.')
    return redirect('dashboard:customer_list')


@login_required
@user_passes_test(_admin_or_operator)
def invoice_list_admin(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    invoices = Invoice.objects.select_related('customer__user').all()
    if q:
        invoices = invoices.filter(
            Q(invoice_number__icontains=q) |
            Q(customer__meter_number__icontains=q) |
            Q(customer__user__username__icontains=q)
        )
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    return render(request, 'dashboard/invoice_list.html', {
        'invoices': invoices,
        'q': q,
        'status_filter': status_filter,
    })


@login_required
@user_passes_test(_admin_or_operator)
def agent_dashboard(request):
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    sort = request.GET.get('sort', '-created_at')
    tickets = Ticket.objects.select_related('customer__user', 'category').all()
    if search:
        tickets = tickets.filter(
            Q(protocol__icontains=search) |
            Q(subject__icontains=search) |
            Q(customer__meter_number__icontains=search) |
            Q(customer__user__username__icontains=search)
        )
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category_id=category_filter)
    valid_sorts = ['created_at', '-created_at', 'priority', '-priority', 'status', '-status']
    if sort in valid_sorts:
        tickets = tickets.order_by(sort)
    else:
        tickets = tickets.order_by('-created_at')
    categories = Category.objects.filter(is_active=True)
    status_counts = {
        'open': Ticket.objects.filter(status='open').count(),
        'in_progress': Ticket.objects.filter(status='in_progress').count(),
        'resolved': Ticket.objects.filter(status='resolved').count(),
        'closed': Ticket.objects.filter(status='closed').count(),
    }
    return render(request, 'dashboard/agent_dashboard.html', {
        'tickets': tickets,
        'categories': categories,
        'search': search,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'sort': sort,
        'now': timezone.now(),
        'status_counts': status_counts,
    })


@login_required
@user_passes_test(_admin_or_operator)
def agent_ticket_detail(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.prefetch_related('messages__author'),
        pk=pk,
    )
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_message':
            content = request.POST.get('content', '').strip()
            if content:
                Message.objects.create(
                    ticket=ticket,
                    author=request.user,
                    content=content,
                )
                messages.success(request, 'Resposta adicionada ao ticket.')
        elif action == 'change_status':
            new_status = request.POST.get('status', '')
            if new_status in dict(Ticket.Status.choices):
                ticket.status = new_status
                ticket.save(update_fields=['status'])
                messages.success(request, f'Status alterado para {ticket.get_status_display()}.')
        elif action == 'change_priority':
            new_priority = request.POST.get('priority', '')
            if new_priority in dict(Ticket.Priority.choices):
                ticket.priority = new_priority
                ticket.save(update_fields=['priority'])
                messages.success(request, f'Prioridade alterada para {ticket.get_priority_display()}.')
        return redirect('dashboard:agent_ticket_detail', pk=ticket.pk)
    return render(request, 'dashboard/agent_ticket_detail.html', {
        'ticket': ticket,
        'messages': ticket.messages.all(),
        'now': timezone.now(),
    })


@login_required
def settings_view(request):
    themes = [
        ('red', 'Vermelho ENDE', '#E30613', 'bi-droplet'),
        ('black', 'Preto', '#1a1a1a', 'bi-moon'),
        ('white', 'Branco', '#ffffff', 'bi-sun'),
        ('purple', 'Roxo Neon', '#a855f7', 'bi-stars'),
    ]
    return render(request, 'dashboard/settings.html', {'themes': themes})
