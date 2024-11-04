from django.urls import path
from .views import SalesSummaryView, SalesVisualizationView, DownloadGraphView

urlpatterns = [
    path('sales/summary/', SalesSummaryView.as_view(), name='sales-summary'),
    path('sales/visualize/', SalesVisualizationView.as_view(), name='sales-visualization'),
    path('download-graph/', DownloadGraphView.as_view(), name='download_graph'),
]
