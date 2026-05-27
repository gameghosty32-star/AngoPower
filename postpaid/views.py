from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from customers.models import Customer
from billing_app.models import Invoice
from customers.views import _get_customer
from .models import PostpaidContract
from .forms import InspectionRequestForm, SystemSuggestionForm
from . import services


@login_required
def dashboard(request):
    customer = _get_customer(request.user)
    try:
        contract = customer.postpaid_contract
        if contract.status != 'active':
            return redirect('postpaid:contract_pending')
    except PostpaidContract.DoesNotExist:
        return redirect('postpaid:activate')
    invoices = services.get_outstanding_invoices(customer.pk)
    total_debt = services.calculate_debt(customer.pk)
    consumption = services.get_consumption_data(customer.pk)
    return render(request, 'postpaid/dashboard.html', {
        'customer': customer,
        'invoices': invoices,
        'total_debt': total_debt,
        'consumption': consumption,
    })


@login_required
def activate(request):
    customer = _get_customer(request.user)
    try:
        contract = customer.postpaid_contract
        if contract.status == 'active':
            return redirect('postpaid:dashboard')
        return redirect('postpaid:contract_pending')
    except PostpaidContract.DoesNotExist:
        pass
    return render(request, 'postpaid/activate.html', {
        'customer': customer,
    })


@login_required
def request_inspection_view(request):
    customer = _get_customer(request.user)
    if request.method == 'POST':
        form = InspectionRequestForm(request.POST)
        if form.is_valid():
            services.create_contract(
                customer=customer,
                activation_method='inspection',
                inspection_notes=form.cleaned_data['inspection_notes'],
            )
            messages.success(request, 'Pedido de vistoria enviado com sucesso! Aguarde a aprovação.')
            return redirect('postpaid:contract_pending')
    else:
        form = InspectionRequestForm()
    return render(request, 'postpaid/request_inspection.html', {
        'customer': customer,
        'form': form,
    })


@login_required
def system_suggestion_view(request):
    customer = _get_customer(request.user)
    suggested_amount = None
    if request.method == 'POST':
        form = SystemSuggestionForm(request.POST)
        if form.is_valid():
            appliances = form.cleaned_data['appliances']
            is_commercial = form.cleaned_data['is_commercial']
            services.create_contract(
                customer=customer,
                activation_method='system_suggestion',
                appliances=appliances,
                is_commercial=is_commercial,
            )
            messages.success(request, 'Contrato submetido com sucesso! Aguarde a aprovação.')
            return redirect('postpaid:contract_pending')
    else:
        form = SystemSuggestionForm()
    return render(request, 'postpaid/system_suggestion.html', {
        'customer': customer,
        'form': form,
        'suggested_amount': suggested_amount,
    })


@login_required
def contract_pending(request):
    customer = _get_customer(request.user)
    try:
        contract = customer.postpaid_contract
    except PostpaidContract.DoesNotExist:
        return redirect('postpaid:activate')
    return render(request, 'postpaid/contract_pending.html', {
        'customer': customer,
        'contract': contract,
    })


@user_passes_test(lambda u: u.user_type in ('operator', 'admin'))
def admin_approve_contract_view(request):
    contracts = services.get_pending_contracts()
    if request.method == 'POST':
        contract_id = request.POST.get('contract_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        contract = get_object_or_404(PostpaidContract, pk=contract_id)
        if action == 'approve':
            services.approve_contract(contract_id, notes)
            messages.success(request, f'Contract {contract.customer.meter_number} approved.')
        elif action == 'reject':
            services.reject_contract(contract_id, notes)
            messages.success(request, f'Contract {contract.customer.meter_number} rejected.')
        return redirect('postpaid:admin_approve')
    return render(request, 'postpaid/admin_approve.html', {
        'contracts': contracts,
    })


@login_required
def invoice_list(request):
    customer = _get_customer(request.user)
    invoices = customer.invoices.all()
    return render(request, 'postpaid/invoice_list.html', {
        'customer': customer,
        'invoices': invoices,
    })


@login_required
def invoice_detail(request, pk):
    customer = _get_customer(request.user)
    invoice = get_object_or_404(
        Invoice.objects.prefetch_related('transactions'),
        pk=pk, customer=customer,
    )
    transactions = invoice.transactions.all()
    remaining = float(invoice.amount - (invoice.paid_amount or 0))
    return render(request, 'postpaid/invoice_detail.html', {
        'customer': customer,
        'invoice': invoice,
        'transactions': transactions,
        'remaining': remaining,
    })


@login_required
def pay_invoice_view(request, pk):
    customer = _get_customer(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, customer=customer)
    remaining = float(invoice.amount - (invoice.paid_amount or 0))
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            if amount <= 0:
                raise ValueError('Amount must be positive')
            if amount > remaining:
                raise ValueError('Amount exceeds remaining balance')
            return redirect(f"{reverse('payment_gateways:select', kwargs={'context_key': 'pay_invoice', 'context_value': invoice.pk})}?amount={amount}")
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
    return render(request, 'postpaid/pay_invoice.html', {
        'customer': customer,
        'invoice': invoice,
        'remaining': remaining,
    })


@login_required
def consumption_history(request):
    customer = _get_customer(request.user)
    data = services.get_consumption_data(customer.pk)
    return render(request, 'postpaid/consumption_history.html', {
        'customer': customer,
        **data,
    })
