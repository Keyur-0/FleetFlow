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

    title = models.CharField(max_length=255)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=TripStatus.choices,
        default=TripStatus.DRAFT,
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_work_items",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
        models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"
    

class Vehicle(models.Model):

    class VehicleType(models.TextChoices):
        TRUCK = "TRUCK", "Truck"
        VAN = "VAN", "Van"
        BIKE = "BIKE", "Bike"

    name = models.CharField(max_length=100)

    license_plate = models.CharField(
        max_length=20,
        unique=True,
    )

    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        db_index=True,
    )

    max_capacity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Maximum cargo capacity in kg"
    )

    acquisition_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Initial purchase cost"
    )

    odometer_current = models.PositiveIntegerField()
    is_retired = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.license_plate})"


class Driver(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
    )

    license_expiry = models.DateField()

    safety_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        help_text="Driver safety score (0-100)",
    )

    is_suspended = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.username} (Driver)"


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