from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="operations/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    path("tasks/<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:pk>/claim/", views.task_claim, name="task_claim"),
    path("api/tasks/", views.api_tasks, name="api_tasks"),
]
