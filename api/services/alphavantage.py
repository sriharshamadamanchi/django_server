import os
from datetime import datetime

import requests
from django.core.cache import cache

from api.services.models import HistoricalStockData


def get_cached_live_price(symbol):
    cache_key = f"live_price:{symbol}"
    if (cached := cache.get(cache_key)) is not None:
        return float(cached)

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        price_str = res.json().get("Global Quote", {}).get("05. price")
        if price_str:
            price = float(price_str)
            cache.set(cache_key, price, timeout=3600)
            return price
    except Exception as e:
        print(f"Live price error for {symbol}: {e}")
    return None


def fetch_and_store_historical(stock):
    symbol = stock.symbol
    portfolio = stock.portfolio
    cache_key = f"hist_data:fetched:{symbol}"

    if cache.get(cache_key):
        return True

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}"

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json().get("Time Series (Daily)", {})

        for date_str, values in data.items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            price = float(values.get("5. adjusted close", 0))

            HistoricalStockData.objects.update_or_create(
                portfolio=portfolio,
                symbol=symbol,
                date=date_obj,
                defaults={"adjusted_close": price}
            )

        cache.set(cache_key, True, timeout=43200)  # 12 hours
        return True

    except Exception as e:
        print(f"Hist fetch error for {symbol}: {e}")
        return False
