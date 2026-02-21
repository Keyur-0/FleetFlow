from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum

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

    # 🔥 NEW FIELDS

    vehicle = models.ForeignKey(
        "Vehicle",
        on_delete=models.PROTECT,
        related_name="trips",
        null=True,
        blank=True,
    )

    driver = models.ForeignKey(
        "Driver",
        on_delete=models.PROTECT,
        related_name="trips",
        null=True,
        blank=True,
    )

    cargo_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cargo weight in kg"
    )

    start_odometer = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    end_odometer = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
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

    # ========================
    # Financial Aggregations
    # ========================

    def total_fuel_cost(self):
        return self.fuel_logs.aggregate(
            total=Sum("cost")
        )["total"] or 0

    def total_maintenance_cost(self):
        return self.maintenance_logs.aggregate(
            total=Sum("cost")
        )["total"] or 0

    def total_operational_cost(self):
        return (
            self.total_fuel_cost()
            + self.total_maintenance_cost()
            + self.acquisition_cost
        )

    def total_distance(self):
        return self.odometer_current

    def cost_per_km(self):
        if self.total_distance() == 0:
            return 0
        return self.total_operational_cost() / self.total_distance()
    
    # ========================
    # Revenue & Profit
    # ========================

    def total_revenue(self):
        return self.trips.aggregate(
            total=Sum("revenue")
        )["total"] or 0

    def total_profit(self):
        return self.total_revenue() - self.total_operational_cost()

    def profit_per_km(self):
        if self.total_distance() == 0:
            return 0
        return self.total_profit() / self.total_distance()

class Driver(models.Model):

    class Status(models.TextChoices):
        ON_DUTY = "ON_DUTY", "On Duty"
        OFF_DUTY = "OFF_DUTY", "Off Duty"
        SUSPENDED = "SUSPENDED", "Suspended"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    license_expiry = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ON_DUTY,
        db_index=True
    )

    def is_license_valid(self):
        from datetime import date
        return self.license_expiry >= date.today()

    def __str__(self):
        return f"{self.user.username} (Driver)"

class MaintenanceLog(models.Model):

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="maintenance_logs",
    )

    description = models.TextField()

    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Maintenance cost"
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.status == self.Status.OPEN:
            active_exists = MaintenanceLog.objects.filter(
                vehicle=self.vehicle,
                status=self.Status.OPEN
            ).exclude(id=self.id).exists()

            if active_exists:
                raise ValidationError(
                    "Vehicle already has an active maintenance record."
                )

    def close(self):
        self.status = self.Status.CLOSED
        self.closed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.vehicle} - {self.status}"
    

class FuelLog(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="fuel_logs",
    )

    trip = models.ForeignKey(
        WorkItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fuel_logs",
    )

    liters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Fuel quantity in liters"
    )

    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Fuel cost"
    )

    odometer_reading = models.PositiveIntegerField(
        help_text="Vehicle odometer at time of refueling"
    )

    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["vehicle", "date"]),
        ]

    def clean(self):
        if self.odometer_reading < self.vehicle.odometer_current:
            raise ValidationError(
                "Odometer reading cannot be less than vehicle's current odometer."
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # <-- THIS is missing
        super().save(*args, **kwargs)

        # Update vehicle odometer after successful save
        if self.odometer_reading > self.vehicle.odometer_current:
            self.vehicle.odometer_current = self.odometer_reading
            self.vehicle.save()
            
    def __str__(self):
        return f"{self.vehicle} - {self.liters}L"
    

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