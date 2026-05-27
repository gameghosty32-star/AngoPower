import io
from decimal import Decimal
from datetime import date

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors

from notifications.models import Notification


class InvoiceGenerator:

    @staticmethod
    def _build_pdf(invoice, title, subtitle, amount_label, amount, extra_rows=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                topMargin=2*cm, bottomMargin=2*cm,
                                leftMargin=2*cm, rightMargin=2*cm)
        styles = getSampleStyleSheet()
        style_h = ParagraphStyle('Header', parent=styles['Heading1'], textColor=HexColor('#E30613'), spaceAfter=6)
        style_sub = ParagraphStyle('Sub', parent=styles['Normal'], textColor=colors.grey, spaceAfter=20)
        style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)
        style_amount = ParagraphStyle('Amount', parent=styles['Heading1'], fontSize=28, textColor=HexColor('#E30613'), alignment=1, spaceBefore=12, spaceAfter=12)

        elements = []
        elements.append(Paragraph(title, style_h))
        elements.append(Paragraph(subtitle, style_sub))
        elements.append(HRFlowable(width="100%", thickness=2, color=HexColor('#E30613')))
        elements.append(Spacer(1, 0.5*cm))

        data = [
            ['Cliente', invoice.customer.user.get_full_name() or invoice.customer.user.username],
            ['Nº do Medidor', invoice.customer.meter_number],
        ]
        if invoice.invoice_number:
            data.append(['Documento', invoice.invoice_number])
        if hasattr(invoice, 'issue_date') and invoice.issue_date:
            data.append(['Data de Emissão', invoice.issue_date.strftime('%d/%m/%Y')])
        if hasattr(invoice, 'due_date') and invoice.due_date:
            data.append(['Data de Vencimento', invoice.due_date.strftime('%d/%m/%Y')])
        if extra_rows:
            data.extend(extra_rows)

        table = Table(data, colWidths=[5*cm, 10*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 1*cm))

        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(amount_label, style_normal))
        elements.append(Paragraph(f'{amount:.2f} Kz', style_amount))

        elements.append(Spacer(1, 1.5*cm))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        elements.append(Paragraph('ENDE Platform - Angola', ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1, spaceBefore=6)))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_due_notice(invoice):
        remaining = float(invoice.amount - (invoice.paid_amount or 0))
        return InvoiceGenerator._build_pdf(
            invoice,
            'ENDE Platform',
            'Aviso de Vencimento - Fatura',
            'Valor a Pagar',
            remaining,
            extra_rows=[['Valor Total', f'{invoice.amount:.2f} Kz']],
        )

    @staticmethod
    def generate_payment_receipt(invoice):
        return InvoiceGenerator._build_pdf(
            invoice,
            'ENDE Platform',
            'Recibo de Pagamento',
            'Total Pago',
            float(invoice.paid_amount or 0),
            extra_rows=[
                ['Valor Total', f'{invoice.amount:.2f} Kz'],
                ['Valor Pago', f'{invoice.paid_amount:.2f} Kz'],
            ],
        )

    @staticmethod
    def generate_recharge_receipt(customer, amount, transaction_id):
        fake_invoice = type('obj', (object,), {
            'invoice_number': f'RCP-{transaction_id[:8]}',
            'customer': customer,
            'amount': Decimal(str(amount)),
            'paid_amount': Decimal(str(amount)),
            'status': 'paid',
            'issue_date': date.today(),
            'due_date': None,
        })()
        return InvoiceGenerator._build_pdf(
            fake_invoice,
            'ENDE Platform',
            'Recibo de Recarga',
            'Valor Recarregado',
            float(amount),
            extra_rows=[
                ['Transacção', transaction_id],
                ['Saldo Actual', f'{customer.current_balance:.2f} Kz'],
            ],
        )

    @staticmethod
    def generate_pdf(invoice, template_name=None, context=None):
        return InvoiceGenerator.generate_payment_receipt(invoice)

    @staticmethod
    def send_email(invoice, recipient_email, pdf_buffer, subject=None, body=None):
        if not subject:
            subject = f'ENDE Platform - Documento {invoice.invoice_number}'
        if not body:
            body = f'Prezado(a) {invoice.customer.user.get_full_name() or invoice.customer.user.username},\n\nSegue em anexo o documento {invoice.invoice_number}.'
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach(f'documento_{invoice.invoice_number}.pdf', pdf_buffer.getvalue(), 'application/pdf')
        email.send()

    @staticmethod
    def create_notification(invoice, ntype, title, message, link=''):
        Notification.objects.create(
            user=invoice.customer.user,
            type=ntype,
            title=title,
            message=message,
            link=link,
        )
