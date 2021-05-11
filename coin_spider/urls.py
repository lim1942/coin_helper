from django.urls import path
from coin_spider.views import DataExportView

urlpatterns = [
    path('data_export', DataExportView.as_view()),
]