from django.contrib import admin
from .models import Notification, ComplianceDeadline

class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'title', 'notification_type',
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'body']
    ordering = ['-created_at']

class ComplianceDeadlineAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'company_name',
        'category', 'due_date', 'is_completed'
    ]
    list_filter = ['category', 'is_completed']
    search_fields = ['title', 'user__email', 'company_name']
    ordering = ['due_date']

admin.site.register(Notification, NotificationAdmin)
admin.site.register(ComplianceDeadline, ComplianceDeadlineAdmin)