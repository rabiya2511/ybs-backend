from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name  = serializers.SerializerMethodField()
    order_number     = serializers.SerializerMethodField()
    is_overdue       = serializers.SerializerMethodField()

    class Meta:
        model  = Task
        fields = [
            'id', 'task_number', 'title', 'description',
            'order', 'order_number',
            'assigned_to', 'assigned_to_name',
            'created_by', 'created_by_name',
            'priority', 'status',
            'due_date', 'started_at', 'completed_at', 'rejected_at',
            'rejection_reason', 'completion_notes',
            'is_overdue', 'created_at', 'updated_at',
        ]

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.name if obj.assigned_to else None

    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else None

    def get_order_number(self, obj):
        return obj.order.order_number if obj.order else None

    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.due_date and obj.status not in ('Completed',):
            return obj.due_date < timezone.now().date()
        return False


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Task
        fields = ['title', 'description', 'order', 'priority', 'due_date']