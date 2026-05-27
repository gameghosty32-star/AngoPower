from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse

from customers.models import Customer
from .models import Invoice
from .invoice_generator import InvoiceGenerator


@login_required
def invoice_list(request):
    return redirect('postpaid:invoice_list')


@login_required
def invoice_detail(request, pk):
    return redirect('postpaid:invoice_detail', pk=pk)


@login_required
def pay_invoice_view(request, pk):
    return redirect('postpaid:pay_invoice', pk=pk)


@login_required
def consumption_history(request):
    return redirect('postpaid:consumption')


@login_required
def download_invoice_pdf(request, pk):
    customer = get_object_or_404(Customer, user=request.user)
    invoice = get_object_or_404(Invoice, pk=pk, customer=customer)
    remaining = float(invoice.amount - (invoice.paid_amount or 0))
    pdf = InvoiceGenerator.generate_pdf(
        invoice,
        'billing_app/invoices/invoice_payment_receipt.html',
        context={'remaining': remaining},
    )
    return HttpResponse(pdf.getvalue(), content_type='application/pdf')
