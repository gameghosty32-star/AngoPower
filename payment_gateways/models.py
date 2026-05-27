from django.db import models

from payments.models import Transaction


class PaymentGateway(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    logo = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'

    def __str__(self):
        return self.name


class GatewayTransaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    gateway = models.ForeignKey(
        PaymentGateway,
        on_delete=models.CASCADE,
        related_name='gateway_transactions',
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='gateway_transaction',
    )
    gateway_reference = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    response_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Gateway Transaction'
        verbose_name_plural = 'Gateway Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.gateway.code}:{self.transaction.transaction_id} ({self.get_status_display()})"
