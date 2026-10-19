from django import forms
from django.contrib.auth.models import User
from .models import WorkItem, Comment, Team

class WorkItemForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = ["title", "description", "team", "assignee", "priority", "status", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Investigate failed payment"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "What happened and what needs to be done?"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            team_ids = user.team_memberships.values_list("team_id", flat=True)
            self.fields["team"].queryset = Team.objects.filter(id__in=team_ids)
            self.fields["assignee"].queryset = User.objects.filter(team_memberships__team_id__in=team_ids).distinct().order_by("username")
        else:
            self.fields["team"].queryset = Team.objects.all()
            self.fields["assignee"].queryset = User.objects.all().order_by("username")
        self.fields["assignee"].required = False
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "input")

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a useful update…", "class": "input"})}
