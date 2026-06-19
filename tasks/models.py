import uuid
from django.db import models
from authentication.models import User
from orders.models import Order

class TaskPriority(models.TextChoices):
    LOW    = 'Low', 'Low'
    MEDIUM = 'Medium', 'Medium'
    HIGH   = 'High', 'High'
    URGENT = 'Urgent', 'Urgent'

class TaskStatus(models.TextChoices):
    UNASSIGNED = 'Unassigned', 'Unassigned'
    ASSIGNED   = 'Assigned', 'Assigned'
    ACCEPTED   = 'Accepted', 'Accepted'
    REJECTED   = 'Rejected', 'Rejected'
    IN_PROGRESS = 'In Progress', 'In Progress'
    COMPLETED  = 'Completed', 'Completed'
    OVERDUE    = 'Overdue', 'Overdue'

class Task(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_number = models.CharField(max_length=20, unique=True, blank=True)

    # Relations
    order       = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')

    # Details
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority    = models.CharField(max_length=10, choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    status      = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.UNASSIGNED)

    # Dates
    due_date        = models.DateField(null=True, blank=True)
    started_at      = models.DateTimeField(null=True, blank=True)
    completed_at    = models.DateTimeField(null=True, blank=True)
    rejected_at     = models.DateTimeField(null=True, blank=True)

    # Notes
    rejection_reason    = models.TextField(blank=True, null=True)
    completion_notes    = models.TextField(blank=True, null=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.task_number:
            last = Task.objects.order_by('-created_at').first()
            if last and last.task_number:
                try:
                    num = int(last.task_number.split('-')[2]) + 1
                except:
                    num = 1
            else:
                num = 1
            self.task_number = f"YBS-TASK-{str(num).zfill(4)}"
        super().save(*args, **kwargs)