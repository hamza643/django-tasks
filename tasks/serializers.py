from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "priority", "due_date", "done", "owner"]
        read_only_fields = ["owner"]