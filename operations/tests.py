from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Team, TeamMembership, WorkItem, ActivityLog

class OperationsTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Support")
        self.user = User.objects.create_user(username="alex", password="SafePass123!")
        TeamMembership.objects.create(user=self.user, team=self.team, role="manager")
        self.item = WorkItem.objects.create(
            title="Payment issue", description="Investigate a failed payment",
            team=self.team, created_by=self.user, priority="high"
        )
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
    def test_user_can_see_dashboard(self):
        self.client.login(username="alex", password="SafePass123!")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment issue")
    def test_claim_assigns_task(self):
        self.client.login(username="alex", password="SafePass123!")
        response = self.client.post(reverse("task_claim", args=[self.item.pk]))
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.assignee, self.user)
        self.assertTrue(ActivityLog.objects.filter(work_item=self.item, action="claimed").exists())
    def test_user_cannot_access_other_team_task(self):
        other = Team.objects.create(name="Finance")
        item = WorkItem.objects.create(title="Private finance task", description="Restricted", team=other, created_by=self.user)
        self.client.login(username="alex", password="SafePass123!")
        response = self.client.get(reverse("task_detail", args=[item.pk]))
        self.assertEqual(response.status_code, 404)

    def test_stale_edit_is_rejected(self):
        self.client.login(username="alex", password="SafePass123!")
        response = self.client.post(reverse("task_edit", args=[self.item.pk]), {
            "version": "0",
            "title": "Overwritten stale title",
            "description": "Stale form content",
            "team": str(self.team.pk),
            "assignee": "",
            "priority": "high",
            "status": "open",
            "due_date": "",
        })
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, "Payment issue")
        self.assertEqual(self.item.version, 1)

    def test_member_cannot_edit_another_users_task(self):
        member = User.objects.create_user(username="sam", password="SafePass123!")
        TeamMembership.objects.create(user=member, team=self.team, role="member")
        self.client.login(username="sam", password="SafePass123!")
        response = self.client.get(reverse("task_edit", args=[self.item.pk]))
        self.assertEqual(response.status_code, 403)

    def test_api_returns_json(self):
        self.client.login(username="alex", password="SafePass123!")
        response = self.client.get(reverse("api_tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
