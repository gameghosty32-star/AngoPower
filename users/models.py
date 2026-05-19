from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class UserType(models.TextChoices):
        CLIENT = 'client', 'Client'
        OPERATOR = 'operator', 'Operator'
        ADMIN = 'admin', 'Admin'

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
    )

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
