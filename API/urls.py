# scanner/urls.py
from django.urls import path
from .views import CBCReportView

urlpatterns = [
    path('upload/', CBCReportView.as_view(), name='cbc-report-upload'),
]
