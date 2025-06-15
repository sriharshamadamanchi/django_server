from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.portfolio.models import Portfolio
from api.stock.models import Stock
from api.stock.serializers import StockSerializer


class StockViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        portfolio_id = self.request.query_params.get("portfolio")

        queryset = Stock.objects.filter(portfolio__fund_manager__user=user)

        if portfolio_id:
            queryset = queryset.filter(portfolio_id=portfolio_id)

        return queryset

    def create(self, request, *args, **kwargs):
        portfolio_id = request.data.get("portfolio")
        symbol = request.data.get("symbol")
        name = request.data.get("name")
        quantity = int(request.data.get("quantity", 0))
        price = request.data.get("price")

        portfolio = get_object_or_404(
            Portfolio,
            id=portfolio_id,
            fund_manager__user=request.user
        )

        existing_stock = portfolio.stocks.filter(symbol=symbol).first()

        if existing_stock:
            price_decimal = Decimal(price) if price else Decimal('0')
            existing_price = existing_stock.price or Decimal('0')

            total_quantity = existing_stock.quantity + quantity

            weighted_price = (
                                     existing_price * existing_stock.quantity +
                                     price_decimal * quantity
                             ) / total_quantity if price else existing_stock.price

            existing_stock.quantity = total_quantity
            existing_stock.price = weighted_price
            existing_stock.name = name or existing_stock.name
            existing_stock.save()

            serializer = self.get_serializer(existing_stock)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stock = serializer.save(portfolio=portfolio)
        stock.fetch_and_store_historical_data()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

