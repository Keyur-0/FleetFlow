from django.contrib import admin
from .models import WorkItem, ActivityLog


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
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

    autocomplete_fields = (
        "created_by",
    )

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("work_item", "action", "performed_by", "timestamp")
    list_filter = ("timestamp",)
    ordering = ("-timestamp",)