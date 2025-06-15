import pandas as pd
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.fund_manager.models import FundManager
from api.portfolio.models import Portfolio
from api.portfolio.serializers import PortfolioSerializer

from rest_framework.views import APIView
from django.utils.timezone import now

from api.portfolio.utils.riskanalysis import perform_risk_analysis, calculate_risk_measures, calculate_portfolio_risk
from api.services.models import HistoricalStockData


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            fund_manager = FundManager.objects.get(user=self.request.user)
            return Portfolio.objects.filter(fund_manager=fund_manager)
        except FundManager.DoesNotExist:
            return Portfolio.objects.none()

    def perform_create(self, serializer):
        try:
            fund_manager = FundManager.objects.get(user=self.request.user)
            serializer.save(fund_manager=fund_manager)
        except FundManager.DoesNotExist:
            raise serializers.ValidationError("No FundManager associated with this user.")

class AnalyzePortfolioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        portfolio = get_object_or_404(
            Portfolio, id=portfolio_id, fund_manager__user=request.user
        )
        stocks = portfolio.stocks.all()

        stock_data = []
        total_value = 0
        stock_symbols = []

        for stock in stocks:
            manual_price = stock.price
            try:
                live_price = stock.get_live_price()
            except Exception as e:
                print(f"⚠️ Error fetching live price for {stock.symbol}: {e}")
                live_price = None

            price = manual_price or live_price
            if price is not None:
                stock_total = price * stock.quantity
                total_value += stock_total
                stock_symbols.append(stock.symbol)

                stock_data.append({
                    'name': stock.name,
                    'symbol': stock.symbol,
                    'quantity': stock.quantity,
                    'manual_price': float(manual_price) if manual_price else None,
                    'live_price': float(live_price) if live_price else None,
                    'total_value': float(stock_total),
                })

        historical_qs = HistoricalStockData.objects.filter(
            portfolio=portfolio).order_by("date")

        if not historical_qs.exists():
            return Response({
                "message": "No historical data available for this portfolio.",
                "stock_data": stock_data,
                "total_value": float(total_value),
                "historical_data": {},
                "risk_measures": {},
                "portfolio_analysis": {},
                "portfolio_value": [],
                "timestamp": int(now().timestamp())
            }, status=status.HTTP_200_OK)

        df = pd.DataFrame.from_records(historical_qs.values("date", "symbol", "adjusted_close"))
        if df.empty:
            return Response({"message": "Historical data exists but is empty."}, status=200)

        pivot_df = df.pivot(index='date', columns='symbol', values='adjusted_close').dropna()
        available_symbols = pivot_df.columns.tolist()
        filtered_symbols = [s for s in stock_symbols if s in available_symbols]

        if not filtered_symbols:
            return Response({"message": "None of the stocks have valid historical data."}, status=200)

        historical_data = {
            symbol: {
                "dates": df[df["symbol"] == symbol]["date"].astype(str).tolist(),
                "prices": df[df["symbol"] == symbol]["adjusted_close"].tolist()
            } for symbol in filtered_symbols
        }

        X = pivot_df[filtered_symbols].pct_change().dropna()
        if X.empty:
            return Response({"message": "Not enough historical data to compute returns."}, status=200)

        portfolio_analysis = perform_risk_analysis(X)
        risk_measures = calculate_risk_measures(X, filtered_symbols)

        if not portfolio_analysis:
            return Response({"message": "Portfolio optimization failed due to insufficient data."}, status=200)

        portfolio_values = (pivot_df[filtered_symbols] * pd.Series({
            stock.symbol: stock.quantity for stock in stocks if stock.symbol in filtered_symbols
        })).sum(axis=1)

        portfolio_value_json = portfolio_values.reset_index()
        portfolio_value_json["date"] = portfolio_value_json["date"].astype(str)
        portfolio_value_json.columns = ["x", "y"]
        portfolio_value_json = portfolio_value_json.to_dict(orient="records")

        return Response({
            "portfolio": {
                "id": portfolio.id,
                "name": portfolio.name,
            },
            "stock_data": stock_data,
            "total_value": float(total_value),
            "historical_data": historical_data,
            "portfolio_analysis": {
                "mean_variance": portfolio_analysis.get("mean_variance", {}),
                "cvar": portfolio_analysis.get("cvar", {}),
                "erc": portfolio_analysis.get("erc", {}),
            },
            "risk_measures": risk_measures,
            "portfolio_value": portfolio_value_json,
            "timestamp": int(now().timestamp())
        }, status=status.HTTP_200_OK)

class PortfolioRiskAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        portfolio = get_object_or_404(
            Portfolio,
            id=portfolio_id,
            fund_manager__user=request.user
        )

        stocks = portfolio.stocks.all()

        historical_prices_qs = HistoricalStockData.objects.filter(
            portfolio=portfolio
        ).order_by("date")

        if not historical_prices_qs.exists():
            return Response(
                {"detail": "No historical data available to calculate portfolio risk."},
                status=status.HTTP_404_NOT_FOUND
            )

        df = pd.DataFrame.from_records(
            historical_prices_qs.values("date", "symbol", "adjusted_close")
        )

        price_data = df.pivot(
            index="date", columns="symbol", values="adjusted_close"
        ).ffill()

        available_symbols = price_data.columns.tolist()
        valid_stocks = [stock for stock in stocks if stock.symbol in available_symbols]

        if not valid_stocks:
            return Response(
                {"detail": "No valid stocks with historical data for risk calculation."},
                status=status.HTTP_404_NOT_FOUND
            )

        X = price_data[available_symbols].pct_change().dropna()
        if X.empty:
            return Response(
                {"detail": "Not enough historical data to compute returns."},
                status=status.HTTP_400_BAD_REQUEST
            )

        portfolio_weights = {
            stock.symbol: 1 / len(available_symbols) for stock in valid_stocks
        }

        try:
            portfolio_risk_measures = calculate_portfolio_risk(X, portfolio_weights)
        except Exception as e:
            return Response(
                {"detail": f"Risk calculation error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        stock_quantities = {
            stock.symbol: stock.quantity for stock in valid_stocks
        }

        portfolio_values = (price_data[available_symbols] * pd.Series(stock_quantities)).sum(axis=1)

        portfolio_value_json = portfolio_values.reset_index()
        portfolio_value_json["date"] = portfolio_value_json["date"].astype(str)
        portfolio_value_json.columns = ["x", "y"]
        portfolio_value_json = portfolio_value_json.to_dict(orient="records")

        return Response({
            "portfolio_id": portfolio.id,
            "risk_measures": portfolio_risk_measures,
            "portfolio_value": portfolio_value_json
        })