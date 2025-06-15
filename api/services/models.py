from django.db import models

from api.portfolio.models import Portfolio


class HistoricalStockData(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="historical_data")
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    # Consider DecimalField for precision if needed
    adjusted_close = models.FloatField()

    class Meta:
        unique_together = ('portfolio', 'symbol', 'date')
        ordering = ['date']  # Good for fetching ordered data

    def __str__(self):
        return f"{self.portfolio.name} - {self.symbol} - {self.date}: {self.adjusted_close}"
