from django.db import models

from users.models import CustomUser


class Notification(models.Model):
    class Type(models.TextChoices):
        RECHARGE = 'recharge', 'Recharge Confirmed'
        INVOICE = 'invoice', 'Invoice Alert'
        TICKET = 'ticket', 'Ticket Update'
        PAYMENT = 'payment', 'Payment Confirmed'
        SYSTEM = 'system', 'System Notification'

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, default='')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"
