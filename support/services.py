from datetime import timedelta

from django.utils import timezone
from django.db.models import Q

from .models import Ticket, Category, Message
from notifications.models import Notification


def check_sla_compliance(ticket):
    if not ticket.sla_deadline:
        return True
    return timezone.now() <= ticket.sla_deadline


def escalate_ticket(ticket):
    ticket.priority = 'urgent'
    ticket.save(update_fields=['priority'])
    Notification.objects.create(
        user=ticket.customer.user,
        type='ticket',
        title='Ticket Escalado',
        message=f'O ticket #{ticket.pk} ({ticket.subject}) foi escalado para prioridade urgente.',
        link=f'/support/tickets/{ticket.pk}/',
    )


def calculate_sla_deadline(category):
    if category and category.sla_hours:
        return timezone.now() + timedelta(hours=category.sla_hours)
    return timezone.now() + timedelta(hours=48)


def get_auto_reply(category):
    auto_replies = {
        'avaria-tecnica': 'Informamos que a sua solicitação de avaria técnica foi registada. Um técnico será enviado ao local dentro do SLA de 4 horas.',
        'problema-de-faturacao': 'O seu problema de faturação foi registado. A nossa equipa de facturação irá analisar o caso dentro de 24 horas.',
        'recarga-nao-creditada': 'A sua reclamação de recarga não creditada foi registada. Iremos verificar o sistema e regularizar dentro de 2 horas.',
        'pedido-de-ligacao': 'O seu pedido de ligação foi registado. Entraremos em contacto para agendar a visita técnica.',
        'denuncia-fraude': 'A sua denúncia foi registada e será tratada com confidencialidade pela equipa de segurança.',
    }
    if category:
        return auto_replies.get(category.slug, '')
    return ''


def get_tickets_for_operator(search='', status='', priority='', category_id='', sort='-created_at'):
    tickets = Ticket.objects.select_related('customer__user', 'category').all()
    if search:
        tickets = tickets.filter(
            Q(protocol__icontains=search) |
            Q(subject__icontains=search) |
            Q(customer__meter_number__icontains=search) |
            Q(customer__user__username__icontains=search)
        )
    if status:
        tickets = tickets.filter(status=status)
    if priority:
        tickets = tickets.filter(priority=priority)
    if category_id:
        tickets = tickets.filter(category_id=category_id)
    if sort.startswith('-'):
        tickets = tickets.order_by(sort)
    else:
        tickets = tickets.order_by(sort)
    return tickets


def create_ticket_with_notification(customer, subject, description, category=None, priority='medium'):
    sla_deadline = calculate_sla_deadline(category)
    ticket = Ticket.objects.create(
        customer=customer,
        subject=subject,
        description=description,
        category=category,
        priority=priority,
        sla_deadline=sla_deadline,
    )
    Message.objects.create(
        ticket=ticket,
        author=customer.user,
        content=description,
    )
    Notification.objects.create(
        user=customer.user,
        type='ticket',
        title=f'Ticket #{ticket.pk} - Protocolo {ticket.protocol}',
        message=f'Ticket criado com sucesso. Protocolo: {ticket.protocol}. Assunto: {subject}',
        link=f'/support/tickets/{ticket.pk}/',
    )
    auto_reply = get_auto_reply(category)
    if auto_reply:
        Message.objects.create(
            ticket=ticket,
            author=customer.user,
            content=auto_reply,
        )
    return ticket
