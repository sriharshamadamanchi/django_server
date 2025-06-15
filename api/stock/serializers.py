from rest_framework import serializers

from api.stock.models import Stock


class StockSerializer(serializers.ModelSerializer):
    total_value = serializers.SerializerMethodField()
    live_price = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            'id', 'portfolio', 'symbol', 'name',
            'quantity', 'price', 'created_at',
            'total_value', 'live_price',
        ]
        read_only_fields = ['created_at', 'total_value', 'live_price']

    def get_total_value(self, obj):
        return obj.get_total_value()

    def get_live_price(self, obj):
        return obj.get_live_price()
