from rest_framework import serializers

from api.portfolio.models import Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'description', 'fund_manager', 'created_at']
        read_only_fields = ['created_at']
