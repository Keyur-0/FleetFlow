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

    #Structural transition validation
    if new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise ValidationError(f"Cannot transition from {current_status} to {new_status}.")

    # DISPATCHED → Only Dispatcher or Fleet Manager
    if new_status == WorkItem.TripStatus.DISPATCHED:
        if not user.is_dispatcher and not user.is_manager:
            raise ValidationError(
                "Only Dispatcher or Fleet Manager can dispatch trips."
            )

        if not work_item.driver:
            raise ValidationError("Must select a driver before dispatching.")

        if not work_item.vehicle:
            raise ValidationError("Must select a vehicle before dispatching.")

    # IN_PROGRESS → Only assigned driver
    if new_status == WorkItem.TripStatus.IN_PROGRESS:
        if user != work_item.driver:
            raise ValidationError(
                "Only the assigned driver can start the trip."
            )

    # COMPLETED → Only assigned driver
    if new_status == WorkItem.TripStatus.COMPLETED:
        if user != work_item.driver:
            raise ValidationError(
                "Only the assigned driver can complete the trip."
            )

    work_item.status = new_status
    work_item.full_clean()
    work_item.save()

    ActivityLog.objects.create(
        work_item=work_item,
        action=f"Status changed to {new_status}",
        performed_by=user,
    )

    return work_item