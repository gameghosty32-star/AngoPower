from django.db import models

from customers.models import Customer


class PostpaidContract(models.Model):
    class ActivationMethod(models.TextChoices):
        INSPECTION = 'inspection', 'Solicitar Vistoria'
        SYSTEM_SUGGESTION = 'system_suggestion', 'Sugestão do Sistema'

    class Status(models.TextChoices):
        PENDING_INSPECTION = 'pending_inspection', 'Aguardando Vistoria'
        PENDING_APPROVAL = 'pending_approval', 'Aguardando Aprovação'
        ACTIVE = 'active', 'Activo'
        REJECTED = 'rejected', 'Rejeitado'

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='postpaid_contract',
    )
    monthly_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    activation_method = models.CharField(
        max_length=30,
        choices=ActivationMethod.choices,
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_INSPECTION,
        db_index=True,
    )
    appliances = models.JSONField(default=list, blank=True)
    is_commercial = models.BooleanField(default=False)
    inspection_notes = models.TextField(blank=True, default='')
    admin_approval_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Postpaid Contract'
        verbose_name_plural = 'Postpaid Contracts'

    def __str__(self):
        return f"Contract {self.customer.meter_number} - {self.get_status_display()}"
