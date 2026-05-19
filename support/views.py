from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.db import models

from customers.models import Customer
from .models import Category, Ticket, Message


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
    messages_qs = ticket.messages.all()
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                ticket=ticket,
                author=request.user,
                content=content,
            )
            messages.success(request, 'Message added to ticket.')
        return redirect('support:ticket_detail', pk=ticket.pk)
    return render(request, 'support/ticket_detail.html', {
        'customer': customer,
        'ticket': ticket,
        'messages': messages_qs,
    })


@login_required
def ticket_create(request):
    customer = _get_customer(request.user)
    categories = Category.objects.all()
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        priority = request.POST.get('priority', 'medium')
        if subject and description:
            ticket = Ticket.objects.create(
                customer=customer,
                subject=subject,
                description=description,
                category_id=category_id or None,
                priority=priority,
                status='open',
            )
            Message.objects.create(
                ticket=ticket,
                author=request.user,
                content=description,
            )
            messages.success(request, 'Ticket created successfully.')
            return redirect('support:ticket_detail', pk=ticket.pk)
        else:
            messages.error(request, 'Subject and description are required.')
    return render(request, 'support/ticket_create.html', {
        'customer': customer,
        'categories': categories,
    })
