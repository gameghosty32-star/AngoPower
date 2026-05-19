from django.db import models

from customers.models import Customer
from billing_app.models import Invoice


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        PAYMENT = 'payment', 'Payment'
        CREDIT = 'credit', 'Credit'
        REFUND = 'refund', 'Refund'
        ADJUSTMENT = 'adjustment', 'Adjustment'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_type', 'status']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.customer.meter_number} ({self.get_status_display()})"
