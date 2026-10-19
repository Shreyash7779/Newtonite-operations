from django.contrib import admin
from .models import Team, TeamMembership, WorkItem, Comment, ActivityLog
admin.site.register(Team)
admin.site.register(TeamMembership)
admin.site.register(WorkItem)
admin.site.register(Comment)
admin.site.register(ActivityLog)
