import uuid
from django.conf import settings
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class TeamMembership(models.Model):
    ROLE_CHOICES = [("member", "Member"), ("manager", "Manager")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team_memberships")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    class Meta:
        unique_together = ("user", "team")
    def __str__(self):
        return f"{self.user} — {self.team} ({self.role})"

class WorkItem(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"), ("in_progress", "In progress"),
        ("blocked", "Blocked"), ("resolved", "Resolved"),
    ]
    PRIORITY_CHOICES = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")]
    title = models.CharField(max_length=180)
    description = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="work_items")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_work_items")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_work_items")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    due_date = models.DateField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    request_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["team", "status"]),
            models.Index(fields=["assignee", "status"]),
        ]
    def __str__(self):
        return self.title

class Comment(models.Model):
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    body = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["created_at"]

class ActivityLog(models.Model):
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name="activities")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=80)
    details = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["work_item", "-created_at"])]
