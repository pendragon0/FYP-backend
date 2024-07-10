# scanner/urls.py
from django.urls import path
from .views import CBCReportView, UserReportView

urlpatterns = [
    path('upload/', CBCReportView.as_view(), name='cbc-report-upload'),
    path('user-reports/<str:email>/', UserReportView.as_view(), name='user_reports'),

]
