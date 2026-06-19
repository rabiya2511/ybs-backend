from django.db import models
import uuid
from authentication.models import User
from orders.models import Order

class ProjectStatus(models.TextChoices):
    QUEUED = 'Queued', 'Queued'
    ACTIVE = 'Active', 'Active'
    REVIEW = 'Review', 'Review'
    DONE = 'Done', 'Done'
    ON_HOLD = 'On Hold', 'On Hold'
    CANCELLED = 'Cancelled', 'Cancelled'

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='project')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    assigned_provider = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='provider_projects'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.QUEUED
    )
    progress = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.client.name}"


class Milestone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], default='pending')
    order = models.IntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - {self.title}"


class ProjectDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='project_documents/')
    is_deliverable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} - {self.name}"