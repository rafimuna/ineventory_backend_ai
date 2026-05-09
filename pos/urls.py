from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentMethodViewSet, OrderViewSet, DailyReportViewSet

router = DefaultRouter()
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reports/daily', DailyReportViewSet, basename='daily-report')

urlpatterns = [
    path('', include(router.urls)),
]