from django.urls import path
from .views import trip_management, driver_management, maintenance_management, close_maintenance, fuel_management

urlpatterns = [
    path("", trip_management, name="trip-management"),
    path("drivers/", driver_management, name="driver-management"),
    path("maintenance/", maintenance_management, name="maintenance_management"),
    path("maintenance/<int:pk>/close/", close_maintenance, name="close_maintenance"),
    path("fuel/", fuel_management, name="fuel_management"),
]