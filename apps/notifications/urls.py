from django.urls import path

from .views import (
    NotificationDetailView,
    NotificationListCreateView,
    NotificationRetryView,
)

urlpatterns = [
    path("", NotificationListCreateView.as_view(), name="notification-list-create"),
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
    path("<int:pk>/retry/", NotificationRetryView.as_view(), name="notification-retry"),
]