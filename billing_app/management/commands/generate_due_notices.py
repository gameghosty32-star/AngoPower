from datetime import date, timedelta
from django.core.management.base import BaseCommand

from billing_app.models import Invoice
from billing_app.invoice_generator import InvoiceGenerator


class Command(BaseCommand):
    help = 'Generate due notices for invoices due in 3 days'

    def handle(self, *args, **options):
        target_date = date.today() + timedelta(days=3)
        invoices = Invoice.objects.filter(
            due_date=target_date,
            status='issued',
        )
        count = 0
        for invoice in invoices:
            pdf = InvoiceGenerator.generate_due_notice(invoice)
            InvoiceGenerator.create_notification(
                invoice, 'invoice',
                f'Fatura {invoice.invoice_number} a vencer',
                f'A sua fatura {invoice.invoice_number} de {invoice.amount}Kz vence em 3 dias.',
                link=f'/billing/{invoice.pk}/',
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Generated {count} due notices'))
