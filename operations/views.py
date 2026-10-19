import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from .models import WorkItem, Team, TeamMembership, Comment, ActivityLog
from .forms import WorkItemForm, CommentForm

def home(request):
    return redirect("dashboard" if request.user.is_authenticated else "login")

def user_team_ids(user):
    if user.is_superuser:
        return Team.objects.values_list("id", flat=True)
    return user.team_memberships.values_list("team_id", flat=True)

def visible_items(user):
    return WorkItem.objects.select_related("team", "assignee", "created_by").filter(team_id__in=user_team_ids(user))

@login_required
def dashboard(request):
    qs = visible_items(request.user)
    context = {
        "total": qs.count(),
        "open_count": qs.filter(status="open").count(),
        "progress_count": qs.filter(status="in_progress").count(),
        "blocked_count": qs.filter(status="blocked").count(),
        "urgent_items": qs.filter(priority="urgent").exclude(status="resolved")[:5],
        "recent_items": qs[:8],
    }
    return render(request, "operations/dashboard.html", context)

@login_required
def task_list(request):
    qs = visible_items(request.user)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    team = request.GET.get("team", "")
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(assignee__username__icontains=query))
    if status in dict(WorkItem.STATUS_CHOICES):
        qs = qs.filter(status=status)
    if priority in dict(WorkItem.PRIORITY_CHOICES):
        qs = qs.filter(priority=priority)
    if team.isdigit():
        qs = qs.filter(team_id=team)
    qs = qs[:100]
    return render(request, "operations/task_list.html", {
        "items": qs, "query": query, "status": status, "priority": priority,
        "team_filter": team, "teams": Team.objects.filter(id__in=user_team_ids(request.user)),
        "statuses": WorkItem.STATUS_CHOICES, "priorities": WorkItem.PRIORITY_CHOICES,
    })

@login_required
def task_create(request):
    if request.method == "POST":
        form = WorkItemForm(request.POST, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            if item.team_id not in list(user_team_ids(request.user)):
                return HttpResponseForbidden("You do not have access to this team.")
            item.created_by = request.user
            item.save()
            ActivityLog.objects.create(work_item=item, actor=request.user, action="created", details="Work item created")
            messages.success(request, "Task created successfully.")
            return redirect("task_detail", pk=item.pk)
    else:
        form = WorkItemForm(user=request.user)
    return render(request, "operations/task_form.html", {"form": form, "heading": "Create a task"})

@login_required
def task_detail(request, pk):
    item = get_object_or_404(visible_items(request.user), pk=pk)
    comment_form = CommentForm()
    if request.method == "POST" and "add_comment" in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.work_item = item
            comment.author = request.user
            comment.save()
            ActivityLog.objects.create(work_item=item, actor=request.user, action="commented", details="Added a comment")
            messages.success(request, "Comment added.")
            return redirect("task_detail", pk=pk)
    return render(request, "operations/task_detail.html", {"item": item, "comment_form": comment_form})

@login_required
def task_edit(request, pk):
    item = get_object_or_404(visible_items(request.user), pk=pk)
    membership = request.user.team_memberships.filter(team=item.team).first()
    if not (request.user.is_superuser or request.user == item.created_by or (membership and membership.role == "manager")):
        return HttpResponseForbidden("Only the creator, team manager, or administrator can edit this task.")
    if request.method == "POST":
        submitted_version = request.POST.get("version", "")
        form = WorkItemForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                locked = WorkItem.objects.select_for_update().get(pk=item.pk)
                if str(locked.version) != str(submitted_version):
                    messages.error(request, "This task changed since you opened it. Review the latest version and try again.")
                    return redirect("task_detail", pk=pk)
                before = {"status": locked.status, "priority": locked.priority, "assignee": locked.assignee_id}
                updated = form.save(commit=False)
                updated.version = locked.version + 1
                updated.save()
                changes = []
                for field, label in [("status", "status"), ("priority", "priority"), ("assignee", "assignee")]:
                    current = getattr(updated, field)
                    old = before[field]
                    new = current.pk if field == "assignee" and current else (current if field != "assignee" else None)
                    if old != new:
                        changes.append(f"{label} changed")
                ActivityLog.objects.create(work_item=updated, actor=request.user, action="updated", details=", ".join(changes) or "Task details updated")
            messages.success(request, "Task updated.")
            return redirect("task_detail", pk=pk)
    else:
        form = WorkItemForm(instance=item, user=request.user)
    return render(request, "operations/task_form.html", {"form": form, "heading": "Edit task", "item": item})

@login_required
@require_POST
def task_claim(request, pk):
    item = get_object_or_404(visible_items(request.user), pk=pk)
    # Conditional update makes the claim atomic: only one request can claim an unassigned task.
    changed = WorkItem.objects.filter(pk=item.pk, assignee__isnull=True, status__in=["open", "in_progress"]).update(
        assignee=request.user, version=item.version + 1
    )
    if changed:
        ActivityLog.objects.create(work_item=item, actor=request.user, action="claimed", details=f"Claimed by {request.user.username}")
        messages.success(request, "Task assigned to you.")
    else:
        messages.error(request, "This task has already been claimed or is no longer available.")
    return redirect("task_detail", pk=pk)

@login_required
@require_GET
def api_tasks(request):
    qs = visible_items(request.user)
    status = request.GET.get("status", "")
    if status in dict(WorkItem.STATUS_CHOICES):
        qs = qs.filter(status=status)
    data = [{
        "id": item.id, "title": item.title, "status": item.status,
        "priority": item.priority, "team": item.team.name,
        "assignee": item.assignee.username if item.assignee else None,
        "version": item.version, "updated_at": item.updated_at.isoformat(),
    } for item in qs[:100]]
    return JsonResponse({"count": len(data), "results": data})
