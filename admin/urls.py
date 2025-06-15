"""
URL configuration for admin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from api.auth.views import LoginAPIView, LogoutAPIView
from api.institute.models import Institute
from api.portfolio.models import FundManager, Portfolio
from api.portfolio.views import AnalyzePortfolioAPIView, PortfolioRiskAPIView

from api.stock.models import Stock

admin.site.register(Institute)
admin.site.register(FundManager)
admin.site.register(Portfolio)
admin.site.register(Stock)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path("api/login/", LoginAPIView.as_view(), name="login"),
    path("api/logout/", LogoutAPIView.as_view(), name="logout"),
    path('api/portfolio/<int:portfolio_id>/analyze/', AnalyzePortfolioAPIView.as_view(), name='analyze-portfolio'),
    path("api/portfolio/<int:portfolio_id>/risk/", PortfolioRiskAPIView.as_view(), name="portfolio-risk")
]
