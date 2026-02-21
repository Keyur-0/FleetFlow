from django.contrib import admin
from .models import WorkItem, ActivityLog


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "priority",
        "created_by",
        "assigned_to",
        "created_at",
    )
    list_filter = ("status", "priority", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    autocomplete_fields = ("created_by", "assigned_to")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("work_item", "action", "performed_by", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("action",)