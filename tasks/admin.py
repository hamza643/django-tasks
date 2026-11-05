from django.contrib import admin

from .models import Task


@admin.action(description="Mark selected tasks as done")
def mark_done(modeladmin, request, queryset):
    queryset.update(done=True)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "priority", "due_date", "done", "created_at")
    list_filter = ("done", "priority")
    search_fields = ("title", "description")
    list_editable = ("done",)
    ordering = ["-created_at"]
    actions = [mark_done]