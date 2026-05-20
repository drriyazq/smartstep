from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"profiles", views.ProfileViewSet, basename="me-profiles")
router.register(r"progress", views.TaskProgressViewSet, basename="me-progress")
router.register(r"custom-tasks", views.CustomTaskViewSet, basename="me-custom-tasks")
router.register(r"custom-rewards", views.CustomRewardViewSet, basename="me-custom-rewards")
router.register(r"reward-usage", views.RewardUsageViewSet, basename="me-reward-usage")
router.register(r"masteries", views.EarnedMasteryViewSet, basename="me-masteries")
router.register(r"session", views.SessionItemViewSet, basename="me-session")

urlpatterns = [
    path("state/", views.BulkStateView.as_view(), name="me-state"),
    path("wipe/", views.WipeView.as_view(), name="me-wipe"),
    path("", include(router.urls)),
]
