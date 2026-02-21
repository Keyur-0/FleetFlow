from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import TripCreateForm, MaintenanceForm, FuelLogForm
from .models import WorkItem, Vehicle, Driver, MaintenanceLog, FuelLog
from django.utils import timezone

from django.db.models import Sum

"""
Workflow views for FleetFlow.

Handles vehicle management, trip dispatching,
maintenance logging, and operational workflows.
"""

@login_required
def trip_management(request):

    if not request.user.is_dispatcher and not request.user.is_manager:
        raise PermissionDenied("Access denied.")

    trips = WorkItem.objects.select_related(
        "vehicle", "driver"
    ).order_by("-created_at")

    if request.method == "POST":
        form = TripCreateForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.created_by = request.user
            trip.status = WorkItem.TripStatus.DISPATCHED
            trip.save()

            # Update vehicle status
            vehicle = trip.vehicle
            vehicle.status = Vehicle.Status.ON_TRIP
            vehicle.save()

            return redirect("trip-management")
    else:
        form = TripCreateForm()

    return render(
        request,
        "workflow/trip_management.html",
        {"trips": trips, "form": form},
    )

@login_required
def driver_management(request):

    if not request.user.is_manager:
        raise PermissionDenied("Only managers can access driver management.")

    drivers = Driver.objects.select_related("user").all()

    return render(
        request,
        "workflow/driver_management.html",
        {"drivers": drivers},
    )


@login_required
def maintenance_management(request):

    # RBAC
    if request.user.role not in [
        request.user.Role.FLEET_MANAGER,
        request.user.Role.SAFETY_OFFICER,
    ]:
        raise PermissionDenied

    if request.method == "POST":
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save()

            # Move vehicle to IN_SHOP
            maintenance.vehicle.status = Vehicle.Status.IN_SHOP
            maintenance.vehicle.save()

            return redirect("maintenance_management")
    else:
        form = MaintenanceForm()

    maintenances = MaintenanceLog.objects.select_related("vehicle").all()

    context = {
        "maintenances": maintenances,
        "form": form,
    }

    return render(request, "maintenance/maintenance_management.html", context)


@login_required
def close_maintenance(request, pk):

    if request.user.role not in [
        request.user.Role.FLEET_MANAGER,
        request.user.Role.SAFETY_OFFICER,
    ]:
        raise PermissionDenied

    maintenance = get_object_or_404(MaintenanceLog, pk=pk)

    maintenance.status = MaintenanceLog.Status.CLOSED
    maintenance.closed_at = timezone.now()
    maintenance.save()

    # Return vehicle to AVAILABLE
    vehicle = maintenance.vehicle
    vehicle.status = Vehicle.Status.AVAILABLE
    vehicle.save()

    return redirect("maintenance_management")


@login_required
def fuel_management(request):

    # RBAC
    if request.user.role not in [
        request.user.Role.FLEET_MANAGER,
        request.user.Role.DISPATCHER,
        request.user.Role.FINANCIAL_ANALYST,
    ]:
        raise PermissionDenied

    if request.method == "POST":
        form = FuelLogForm(request.POST)
        if form.is_valid():
            form.save()  # model already updates odometer
            return redirect("fuel_management")
    else:
        form = FuelLogForm()

    fuel_logs = FuelLog.objects.select_related("vehicle", "trip").all()

    total_fuel_cost = fuel_logs.aggregate(
        total=Sum("cost")
    )["total"] or 0

    context = {
        "fuel_logs": fuel_logs,
        "form": form,
        "total_fuel_cost": total_fuel_cost,
    }

    return render(request, "fuel/fuel_management.html", context)