from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class WorkItem(models.Model):

    class TripStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        DISPATCHED = "DISPATCHED", "Dispatched"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    title = models.CharField(max_length=255)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=TripStatus.choices,
        default=TripStatus.DRAFT,
        db_index=True,
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_work_items",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_work_items",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.status == self.TripStatus.COMPLETED and not self.assigned_to:
            raise ValidationError("Cannot complete a work item without assignment.")

    def __str__(self):
        return f"{self.title} ({self.status})"
    

class ActivityLog(models.Model):
    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.CASCADE,
        related_name="activity_logs"
    )
    action = models.CharField(max_length=255)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.performed_by}"