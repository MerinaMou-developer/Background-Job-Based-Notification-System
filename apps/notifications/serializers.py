from django.utils import timezone
from rest_framework import serializers

from .models import Notification

MAX_RETRIES = 3


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("title", "message", "scheduled_time")

    def validate_scheduled_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        return Notification.objects.create(
            user=user,
            status=Notification.Status.SCHEDULED,
            **validated_data,
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "message",
            "scheduled_time",
            "status",
            "retry_count",
            "last_error",
            "sent_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields