from apps.workflow.models import Vehicle, WorkItem, FuelLog
from django.db.models import Sum
from django.utils import timezone


# ==========================================================
# Financial Aggregations
# ==========================================================

def fleet_total_revenue():
    return WorkItem.objects.aggregate(
        total=Sum("revenue")
    )["total"] or 0


def fleet_total_operational_cost():
    total = 0
    for vehicle in Vehicle.objects.all():
        total += vehicle.total_operational_cost()
    return total


def fleet_total_profit():
    return fleet_total_revenue() - fleet_total_operational_cost()


def fuel_cost_this_month():
    now = timezone.now()
    return FuelLog.objects.filter(
        date__year=now.year,
        date__month=now.month
    ).aggregate(
        total=Sum("cost")
    )["total"] or 0


# ==========================================================
# Fleet State KPIs (Command Center)
# ==========================================================

def active_fleet():
    return Vehicle.objects.filter(
        status=Vehicle.Status.ON_TRIP
    ).count()


def maintenance_alerts():
    return Vehicle.objects.filter(
        status=Vehicle.Status.IN_SHOP
    ).count()


def total_active_vehicles():
    return Vehicle.objects.exclude(
        status=Vehicle.Status.RETIRED
    ).count()


def utilization_rate():
    total = total_active_vehicles()
    active = active_fleet()

    if total == 0:
        return 0

    return round((active / total) * 100, 2)


def pending_cargo():
    return WorkItem.objects.filter(
        status=WorkItem.TripStatus.DRAFT
    ).count()