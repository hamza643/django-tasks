from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    PRIORITY_CHOICES = [(1, "Low"), (2, "Medium"), (3, "High")]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    due_date = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title