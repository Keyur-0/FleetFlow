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

    # Check if transition is allowed structurally
    if new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise ValidationError(
            f"Cannot transition from {current_status} to {new_status}."
        )

    # Role-based rules
    if new_status == WorkItem.TripStatus.DISPATCHED:
        if user.role != "ADMIN":
            raise ValidationError("Only Admin can assign work items.")

        if not work_item.assigned_to:
            raise ValidationError("Must select staff before assigning.")

    if new_status == WorkItem.TripStatus.IN_PROGRESS:
        if user != work_item.assigned_to:
            raise ValidationError("Only assigned staff can start work.")

    if new_status == WorkItem.TripStatus.COMPLETED:
        if user != work_item.assigned_to:
            raise ValidationError("Only assigned staff can complete work.")

    # Apply transition
    work_item.status = new_status
    work_item.full_clean()
    work_item.save()

    # Log activity
    ActivityLog.objects.create(
        work_item=work_item,
        action=f"Status changed to {new_status}",
        performed_by=user,
    )

    return work_item