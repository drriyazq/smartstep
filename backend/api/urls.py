from django.urls import path

from . import views

urlpatterns = [
    path("auth/dev-token/", views.dev_token, name="auth-dev-token"),
    path("auth/firebase/", views.firebase_auth, name="auth-firebase"),
    path("auth/otp/send/", views.send_otp, name="auth-otp-send"),
    path("auth/otp/verify/", views.verify_otp, name="auth-otp-verify"),
    path("tasks/", views.task_list, name="task-list"),
    path("rewards/", views.reward_list, name="reward-list"),
    path("notifications/active/", views.active_notifications, name="active-notifications"),
    path("telemetry/task-completion/", views.record_task_completion, name="task-completion"),
]
