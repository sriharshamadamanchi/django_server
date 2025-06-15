from django.db import models

from api.services.alphavantage import get_cached_live_price, fetch_and_store_historical


class Stock(models.Model):
    portfolio = models.ForeignKey(
        "Portfolio",
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    def get_total_value(self):
        """
        Returns: Total value using manual price or live price.
        """
        unit_price = self.price or self.get_live_price()
        return (unit_price or 0) * self.quantity

    def get_live_price(self):
        return get_cached_live_price(self.symbol)

    def fetch_and_store_historical_data(self):
        return fetch_and_store_historical(self)
