from django.urls import path
from .views import StockAdjustView, StockLogListView, DemandForecastView

urlpatterns = [
    path('adjust/', StockAdjustView.as_view(), name='stock-adjust'),
    path('logs/', StockLogListView.as_view(), name='stock-logs'),
    path('forecast/<int:product_id>/', DemandForecastView.as_view(), name='demand-forecast'),
]
