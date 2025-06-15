from django.db import models

from api.fund_manager.models import FundManager


class Portfolio(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # Optional field
    fund_manager = models.ForeignKey(
        FundManager,
        on_delete=models.CASCADE,
        related_name="portfolios")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.fund_manager.user.username})"
