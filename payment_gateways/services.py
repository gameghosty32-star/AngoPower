import random
import uuid

from .models import PaymentGateway, GatewayTransaction


def _simulate_gateway_response(gateway_code, amount, phone):
    success = random.random() > 0.1
    reference = f"{gateway_code.upper()}-{uuid.uuid4().hex[:10].upper()}"
    return {
        'success': success,
        'reference': reference,
        'message': 'Transaction completed successfully' if success else 'Transaction failed',
    }


def process_multicaixa_express(amount, phone):
    return _simulate_gateway_response('multicaixa', amount, phone)


def process_paypay(amount, phone):
    return _simulate_gateway_response('paypay', amount, phone)


def process_unitel_money(amount, phone):
    return _simulate_gateway_response('unitel', amount, phone)


def process_afrimoney(amount, phone):
    return _simulate_gateway_response('afrimoney', amount, phone)


GATEWAY_PROCESSORS = {
    'multicaixa_express': process_multicaixa_express,
    'paypay': process_paypay,
    'unitel_money': process_unitel_money,
    'afrimoney': process_afrimoney,
}


def process_gateway_payment(gateway_code, amount, phone=''):
    processor = GATEWAY_PROCESSORS.get(gateway_code)
    if not processor:
        raise ValueError(f'Unknown gateway: {gateway_code}')
    return processor(amount, phone)


def get_active_gateways():
    return PaymentGateway.objects.filter(is_active=True)


def create_gateway_transaction(gateway, transaction, gateway_reference, status, response_data):
    return GatewayTransaction.objects.create(
        gateway=gateway,
        transaction=transaction,
        gateway_reference=gateway_reference,
        status=status,
        response_data=response_data,
    )
