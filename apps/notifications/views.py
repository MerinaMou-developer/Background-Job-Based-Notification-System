from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import (
    MAX_RETRIES,
    NotificationCreateSerializer,
    NotificationSerializer,
)


class NotificationListCreateView(generics.ListCreateAPIView):
  # list + create for /api/v1/notifications/

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        notification = serializer.save()
        # TODO (Celery): enqueue send task with eta=notification.scheduled_time
        # from .tasks import send_notification
        # send_notification.apply_async(args=[notification.id], eta=notification.scheduled_time)


class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationRetryView(APIView):
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user,
        )

        if notification.status == Notification.Status.PERMANENTLY_FAILED:
            return Response(
                {"detail": "Notification is permanently failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if notification.status != Notification.Status.FAILED:
            return Response(
                {"detail": "Only failed notifications can be retried."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if notification.retry_count >= MAX_RETRIES:
            notification.status = Notification.Status.PERMANENTLY_FAILED
            notification.save(update_fields=["status", "updated_at"])
            return Response(
                {"detail": "Maximum retry limit reached."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification.status = Notification.Status.SCHEDULED
        notification.last_error = ""
        notification.save(update_fields=["status", "last_error", "updated_at"])

        # TODO (Celery): re-enqueue task
        # send_notification.apply_async(args=[notification.id], eta=notification.scheduled_time)

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )