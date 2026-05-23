from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "status", "scheduled_time", "retry_count", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "user__email")
    readonly_fields = ("created_at", "updated_at", "sent_at")