from django.urls import path
from .views import fleet_dashboard

urlpatterns = [
    path("", fleet_dashboard, name="fleet-dashboard"),
]