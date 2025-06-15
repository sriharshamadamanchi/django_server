from rest_framework.routers import DefaultRouter

from api.fund_manager.views import FundManagerViewSet
from api.institute.views import InstituteViewSet
from api.portfolio.views import PortfolioViewSet
from api.stock.views import StockViewSet

router = DefaultRouter()
router.register(r'institute', InstituteViewSet, basename='institute')
router.register(r'fund-manager', FundManagerViewSet, basename='fundmanager')
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')
router.register(r'stock', StockViewSet, basename='stock')

urlpatterns = router.urls
