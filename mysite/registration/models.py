from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(max_length=25, blank=True, null=True)
    confirmation = models.BooleanField(default=False)

    def __str__(self):
        return self.email
