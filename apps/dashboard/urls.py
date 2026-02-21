from django.urls import path
from .views import financial_analytics, fleet_dashboard, operational_reports

urlpatterns = [
    path("", fleet_dashboard, name="dashboard"),
    path("financials/", financial_analytics, name="financial_analytics"),
    path("reports/", operational_reports, name="operational_reports"),
]