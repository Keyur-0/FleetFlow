from django.contrib import admin
from .models import (
    Vehicle,
    WorkItem,
    Driver,
    MaintenanceLog,
    FuelLog,
    ActivityLog,
)


# ==========================
# Vehicle Admin
# ==========================

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "license_plate",
        "vehicle_type",
        "status",
        "odometer_current",
    )
    list_filter = ("vehicle_type", "status")
    search_fields = ("name", "license_plate")
    ordering = ("-created_at",)


# ==========================
# WorkItem Admin
# ==========================

@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "vehicle",
        "driver",
        "created_by",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("created_by",)


# ==========================
# Other Models
# ==========================

admin.site.register(Driver)
admin.site.register(MaintenanceLog)
admin.site.register(FuelLog)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("work_item", "action", "performed_by", "timestamp")
    list_filter = ("timestamp",)
    ordering = ("-timestamp",)