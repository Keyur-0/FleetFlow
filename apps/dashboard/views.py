from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.http import JsonResponse
import json
from services.finance_service import (
    fleet_total_revenue,
    fleet_total_operational_cost,
    fleet_total_profit,
    fuel_cost_this_month,
    active_fleet,
    maintenance_alerts,
    utilization_rate,
    pending_cargo,
)
from apps.workflow.models import Vehicle, FuelLog, MaintenanceLog, WorkItem
"""
Fleet dashboard view for FleetFlow.

Displays aggregated KPIs including revenue,
operational costs, profit, vehicle activity,
maintenance alerts, and trip metrics.

Access restricted to Fleet Managers only.
Business logic is delegated to the finance service layer.
"""

@login_required
def fleet_dashboard(request):

    if not request.user.is_manager:
        raise PermissionDenied("You are not authorized to view this dashboard.")

    context = {
        "active_fleet": active_fleet(),
        "maintenance_alerts": maintenance_alerts(),
        "utilization_rate": utilization_rate(),
        "pending_cargo": pending_cargo(),
        "total_revenue": fleet_total_revenue(),
        "total_operational_cost": fleet_total_operational_cost(),
        "total_profit": fleet_total_profit(),
        "fuel_cost_this_month": fuel_cost_this_month(),
    }

    return render(request, "dashboard/fleet.html", context)

@login_required
def financial_analytics(request):

    # RBAC
    if request.user.role not in [
        request.user.Role.FLEET_MANAGER,
        request.user.Role.FINANCIAL_ANALYST,
    ]:
        raise PermissionDenied

    vehicles = Vehicle.objects.all()

    total_revenue = WorkItem.objects.aggregate(
        total=Sum("revenue")
    )["total"] or 0

    total_fuel_cost = FuelLog.objects.aggregate(
        total=Sum("cost")
    )["total"] or 0

    total_maintenance_cost = MaintenanceLog.objects.aggregate(
        total=Sum("cost")
    )["total"] or 0

    total_operational_cost = sum(
        v.total_operational_cost() for v in vehicles
    )

    total_profit = total_revenue - total_operational_cost

    profit_margin = 0
    if total_revenue > 0:
        profit_margin = round((total_profit / total_revenue) * 100, 2)

    context = {
        "vehicles": vehicles,
        "total_revenue": total_revenue,
        "total_operational_cost": total_operational_cost,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
        "total_fuel_cost": total_fuel_cost,
        "total_maintenance_cost": total_maintenance_cost,
    }

    return render(request, "dashboard/financial_analytics.html", context)

@login_required
def operational_reports(request):

    if request.user.role not in [
        request.user.Role.FLEET_MANAGER,
        request.user.Role.FINANCIAL_ANALYST,
    ]:
        raise PermissionDenied

    # Monthly Revenue
    revenue_data = (
        WorkItem.objects
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("revenue"))
        .order_by("month")
    )

    # Monthly Fuel Cost
    fuel_data = (
        FuelLog.objects
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("cost"))
        .order_by("month")
    )

    # Monthly Maintenance Cost
    maintenance_data = (
        MaintenanceLog.objects
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("cost"))
        .order_by("month")
    )

    vehicles = Vehicle.objects.all()

    vehicle_costs = sorted(
        vehicles,
        key=lambda v: v.total_operational_cost(),
        reverse=True
    )[:5]

    vehicle_labels = [v.name for v in vehicle_costs]
    # vehicle_values = [v.total_operational_cost() for v in vehicle_costs]
    vehicle_values = [float(v.total_operational_cost()) for v in vehicle_costs]

    context = {
        "revenue_data": json.dumps(list(revenue_data), default=str),
        "fuel_data": json.dumps(list(fuel_data), default=str),
        "maintenance_data": json.dumps(list(maintenance_data), default=str),
        "vehicle_labels": json.dumps(vehicle_labels),
        "vehicle_values": json.dumps(vehicle_values),
    }

    return render(request, "dashboard/reports.html", context)