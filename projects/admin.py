from django.contrib import admin
from .models import Project, Milestone, ProjectDocument

class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0

class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'status', 'progress', 'expected_completion_date']
    list_filter = ['status']
    search_fields = ['title', 'client__email']
    inlines = [MilestoneInline, ProjectDocumentInline]

admin.site.register(Project, ProjectAdmin)
admin.site.register(Milestone)
admin.site.register(ProjectDocument)