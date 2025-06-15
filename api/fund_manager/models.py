from django.contrib.auth.models import User
from django.db import models

from api.institute.models import Institute


class FundManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institute = models.ForeignKey(
        Institute,
        on_delete=models.CASCADE,
        related_name="fund_managers")

    def __str__(self):
        return self.user.username
