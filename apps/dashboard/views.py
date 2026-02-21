from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from services.finance_service import (
    fleet_total_revenue,
    fleet_total_operational_cost,
    fleet_total_profit,
    active_vehicles,
    vehicles_in_maintenance,
    active_trips,
    fuel_cost_this_month,
)


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

    if request.user.role != request.user.Role.FLEET_MANAGER:
        raise PermissionDenied("You are not authorized to view this dashboard.")

    context = {
        "total_revenue": fleet_total_revenue(),
        "total_operational_cost": fleet_total_operational_cost(),
        "total_profit": fleet_total_profit(),
        "active_vehicles": active_vehicles(),
        "vehicles_in_maintenance": vehicles_in_maintenance(),
        "active_trips": active_trips(),
        "fuel_cost_this_month": fuel_cost_this_month(),
    }

    return render(request, "dashboard/fleet.html", context)