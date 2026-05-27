from datetime import date
from django.core.management.base import BaseCommand

from billing_app.models import Invoice
from billing_app.invoice_generator import InvoiceGenerator


class Command(BaseCommand):
    help = 'Generate cut warnings for overdue invoices'

    def handle(self, *args, **options):
        today = date.today()
        invoices = Invoice.objects.filter(
            due_date__lt=today,
            status='issued',
        )
        count = 0
        for invoice in invoices:
            invoice.status = 'overdue'
            invoice.save(update_fields=['status'])
            pdf = InvoiceGenerator.generate_due_notice(invoice)
            InvoiceGenerator.create_notification(
                invoice, 'invoice',
                f'Corte de energia - Fatura {invoice.invoice_number}',
                f'A sua fatura {invoice.invoice_number} está vencida. Regularize o pagamento para evitar o corte.',
                link=f'/billing/{invoice.pk}/',
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Generated {count} overdue notices'))
