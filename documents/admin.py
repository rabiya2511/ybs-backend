from django.contrib import admin
from .models import Folder, Document

class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'parent', 'created_at']
    search_fields = ['name', 'created_by__email']

class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_type', 'folder', 'uploaded_by', 'created_at']
    list_filter = ['file_type']
    search_fields = ['name', 'uploaded_by__email']

admin.site.register(Folder, FolderAdmin)
admin.site.register(Document, DocumentAdmin)