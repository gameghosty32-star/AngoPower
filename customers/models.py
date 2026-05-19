from django.db import models

from users.models import CustomUser


class Customer(models.Model):
    class CustomerType(models.TextChoices):
        PREPAID = 'prepaid', 'Prepaid'
        POSTPAID = 'postpaid', 'Postpaid'

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='customer_profile',
    )
    customer_type = models.CharField(
        max_length=10,
        choices=CustomerType.choices,
        default=CustomerType.PREPAID,
    )
    meter_number = models.CharField(
        max_length=50,
        unique=True,
    )
    current_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    debt = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.user.username} - {self.meter_number}"
