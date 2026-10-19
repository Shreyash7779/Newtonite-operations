import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.contrib.auth.models import User
from operations.models import Team, TeamMembership, WorkItem, Comment, ActivityLog

demo, _ = User.objects.get_or_create(username="demo", defaults={"first_name": "Alex", "email": "demo@example.com"})
demo.set_password("Newtonite123!")
demo.save()
manager, _ = User.objects.get_or_create(username="manager", defaults={"first_name": "Morgan"})
manager.set_password("Newtonite123!")
manager.save()
support, _ = Team.objects.get_or_create(name="Customer Support", defaults={"description": "Customer-facing operations"})
engineering, _ = Team.objects.get_or_create(name="Engineering", defaults={"description": "Product and platform"})
for user in [demo, manager]:
    TeamMembership.objects.get_or_create(user=user, team=support, defaults={"role": "manager" if user == manager else "member"})
TeamMembership.objects.get_or_create(user=manager, team=engineering, defaults={"role": "manager"})
examples = [
    ("Investigate failed payment", "Customer reports that a payment failed but the amount was deducted. Confirm transaction status and coordinate a resolution.", support, "urgent", "open", demo),
    ("Review onboarding email", "Check the latest onboarding email copy and confirm links work as expected.", support, "medium", "in_progress", manager),
    ("Investigate API latency", "Review elevated response times in the customer API and identify the likely cause.", engineering, "high", "blocked", manager),
    ("Update support knowledge base", "Document the revised refund investigation steps for the support team.", support, "low", "resolved", demo),
]
for title, description, team, priority, status, assignee in examples:
    item, created = WorkItem.objects.get_or_create(title=title, defaults={
        "description": description, "team": team, "created_by": manager,
        "assignee": assignee, "priority": priority, "status": status,
    })
    if created:
        ActivityLog.objects.create(work_item=item, actor=manager, action="created", details="Demo work item created")
        if status == "resolved":
            Comment.objects.create(work_item=item, author=demo, body="Completed and documented the outcome.")
print("Demo data ready.")
print("Login: demo / Newtonite123!")
print("Manager login: manager / Newtonite123!")
