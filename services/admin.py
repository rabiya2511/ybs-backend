from django.contrib import admin
from .models import Service, Package

class PackageInline(admin.TabularInline):
    model = Package
    extra = 1  # shows 1 empty form to add package directly

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'starting_price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    inlines = [PackageInline]  # shows packages inside service page

admin.site.register(Service, ServiceAdmin)
admin.site.register(Package)