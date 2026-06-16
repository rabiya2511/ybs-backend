from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'name', 'phone', 'role', 'status', 'is_verified', 'created_at']
    list_filter = ['role', 'status', 'is_verified']
    search_fields = ['email', 'name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Login Info', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'company_name', 'gstin', 'pan')}),
        ('Role & Status', {'fields': ('role', 'status', 'is_verified', 'referral_code')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'password1', 'password2', 'role', 'status'),
        }),
    )

admin.site.register(User, CustomUserAdmin)