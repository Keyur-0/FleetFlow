from django.core.exceptions import ValidationError
from apps.workflow.models import WorkItem, ActivityLog

ALLOWED_TRANSITIONS = {
    WorkItem.TripStatus.DRAFT: [
        WorkItem.TripStatus.DISPATCHED,
        WorkItem.TripStatus.CANCELLED,
    ],
    WorkItem.TripStatus.DISPATCHED: [
        WorkItem.TripStatus.IN_PROGRESS,
        WorkItem.TripStatus.CANCELLED,
    ],
    WorkItem.TripStatus.IN_PROGRESS: [
        WorkItem.TripStatus.COMPLETED,
        WorkItem.TripStatus.CANCELLED,
    ],
    WorkItem.TripStatus.COMPLETED: [],
    WorkItem.TripStatus.CANCELLED: [],
}


def transition(work_item, new_status, user):
    current_status = work_item.status

    # Structural validation
    if new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise ValidationError(f"Cannot transition from {current_status} to {new_status}.")

    # DISPATCH VALIDATIONS
    if new_status == WorkItem.TripStatus.DISPATCHED:

        if not user.is_dispatcher and not user.is_manager:
            raise ValidationError("Only Dispatcher or Fleet Manager can dispatch trips.")

        if not work_item.vehicle:
            raise ValidationError("Vehicle must be selected.")

        if not work_item.driver:
            raise ValidationError("Driver must be selected.")

        vehicle_active_trip = WorkItem.objects.filter(
            vehicle=work_item.vehicle,
            status__in=[
                WorkItem.TripStatus.DISPATCHED,
                WorkItem.TripStatus.IN_PROGRESS,
            ],
        ).exclude(id=work_item.id).exists()

        if vehicle_active_trip:
            raise ValidationError("Vehicle already assigned to an active trip.")

        # Prevent overlapping driver assignment
        driver_active_trip = WorkItem.objects.filter(
            driver=work_item.driver,
            status__in=[
                WorkItem.TripStatus.DISPATCHED,
                WorkItem.TripStatus.IN_PROGRESS,
            ],
        ).exclude(id=work_item.id).exists()

        if driver_active_trip:
            raise ValidationError(
                "Driver already assigned to an active trip."
            )

        # Capacity validation
        if (
            work_item.cargo_weight
            and work_item.vehicle.max_capacity
            and work_item.cargo_weight > work_item.vehicle.max_capacity
        ):
            raise ValidationError("Cargo exceeds vehicle capacity.")

    # IN_PROGRESS → Only assigned driver
    if new_status == WorkItem.TripStatus.IN_PROGRESS:
        if not work_item.driver or user != work_item.driver.user:
            raise ValidationError(
                "Only the assigned driver can start the trip."
            )

    # COMPLETED → Only assigned driver
    if new_status == WorkItem.TripStatus.COMPLETED:
        if not work_item.driver or user != work_item.driver.user:
            raise ValidationError(
                "Only the assigned driver can complete the trip."
            )

    # Apply transition
    work_item.status = new_status
    work_item.full_clean()
    work_item.save()

    ActivityLog.objects.create(
        work_item=work_item,
        action=f"Status changed to {new_status}",
        performed_by=user,
    )

    return work_item