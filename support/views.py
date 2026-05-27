from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from django.utils import timezone

from customers.models import Customer
from .models import Category, Ticket, Message
from . import services


def _get_customer(user):
    return get_object_or_404(Customer, user=user)


@login_required
def ticket_list(request):
    customer = _get_customer(request.user)
    tickets = customer.tickets.select_related('category').all()
    return render(request, 'support/ticket_list.html', {
        'customer': customer,
        'tickets': tickets,
    })


@login_required
def ticket_detail(request, pk):
    customer = _get_customer(request.user)
    ticket = get_object_or_404(
        Ticket.objects.prefetch_related(
            models.Prefetch('messages', queryset=Message.objects.select_related('author'))
        ),
        pk=pk, customer=customer,
    )
    sla_ok = services.check_sla_compliance(ticket)
    messages_qs = ticket.messages.all()
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                ticket=ticket,
                author=request.user,
                content=content,
            )
            messages.success(request, 'Mensagem adicionada ao ticket.')
        return redirect('support:ticket_detail', pk=ticket.pk)
    return render(request, 'support/ticket_detail.html', {
        'customer': customer,
        'ticket': ticket,
        'messages': messages_qs,
        'sla_ok': sla_ok,
    })


@login_required
def ticket_create(request):
    customer = _get_customer(request.user)
    categories = Category.objects.filter(is_active=True)
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        priority = request.POST.get('priority', 'medium')
        if subject and description:
            category = Category.objects.filter(pk=category_id).first() if category_id else None
            ticket = services.create_ticket_with_notification(
                customer=customer,
                subject=subject,
                description=description,
                category=category,
                priority=priority,
            )
            messages.success(request, f'Ticket #{ticket.pk} criado com sucesso! Protocolo: {ticket.protocol}')
            return redirect('support:ticket_detail', pk=ticket.pk)
        else:
            messages.error(request, 'Assunto e descrição são obrigatórios.')
    return render(request, 'support/ticket_create.html', {
        'customer': customer,
        'categories': categories,
    })


@login_required
def ticket_search(request):
    q = request.GET.get('q', '').strip()
    tickets = Ticket.objects.none()
    if q:
        tickets = Ticket.objects.filter(
            models.Q(protocol__icontains=q) |
            models.Q(subject__icontains=q)
        ).select_related('customer__user', 'category')
        if not request.user.user_type in ('operator', 'admin'):
            customer = _get_customer(request.user)
            tickets = tickets.filter(customer=customer)
    return render(request, 'support/ticket_list.html', {
        'tickets': tickets,
        'search_query': q,
    })


@user_passes_test(lambda u: u.user_type in ('operator', 'admin'))
def operator_dashboard_view(request):
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    sort = request.GET.get('sort', '-created_at')

    tickets = services.get_tickets_for_operator(
        search=search,
        status=status_filter,
        priority=priority_filter,
        category_id=category_filter,
        sort=sort,
    )
    categories = Category.objects.filter(is_active=True)

    return render(request, 'support/operator_dashboard.html', {
        'tickets': tickets,
        'categories': categories,
        'search': search,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'sort': sort,
        'now': timezone.now(),
    })
