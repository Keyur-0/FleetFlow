from django.db.models import Sum, Count
from django.utils import timezone
from apps.workflow.models import Vehicle, WorkItem, FuelLog, MaintenanceLog


def fleet_total_revenue():
    return WorkItem.objects.aggregate(
        total=Sum("revenue")
    )["total"] or 0


def fleet_total_operational_cost():
    fuel_cost = FuelLog.objects.aggregate(
        total=Sum("cost")
    )["total"] or 0

    maintenance_cost = MaintenanceLog.objects.aggregate(
        total=Sum("cost")
    )["total"] or 0

    acquisition_cost = Vehicle.objects.aggregate(
        total=Sum("acquisition_cost")
    )["total"] or 0

    return fuel_cost + maintenance_cost + acquisition_cost


def fleet_total_profit():
    return fleet_total_revenue() - fleet_total_operational_cost()


def active_vehicles():
    return Vehicle.objects.filter(is_retired=False).count()


def vehicles_in_maintenance():
    return MaintenanceLog.objects.filter(
        status=MaintenanceLog.Status.OPEN
    ).count()


def active_trips():
    return WorkItem.objects.filter(
        status__in=[
            WorkItem.TripStatus.DISPATCHED,
            WorkItem.TripStatus.IN_PROGRESS,
        ]
    ).count()


def fuel_cost_this_month():
    now = timezone.now()
    return FuelLog.objects.filter(
        date__year=now.year,
        date__month=now.month
    ).aggregate(total=Sum("cost"))["total"] or 0