from django.contrib import admin
from .models import Provider, ProviderRating, ProviderPayout

class ProviderAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'role', 'availability_status',
        'total_orders_completed', 'avg_rating', 'is_active'
    ]
    list_filter = ['role', 'availability_status', 'is_active']
    search_fields = ['user__name', 'user__email']

class ProviderRatingAdmin(admin.ModelAdmin):
    list_display = ['provider', 'order', 'rating', 'created_at']
    list_filter = ['rating']

class ProviderPayoutAdmin(admin.ModelAdmin):
    list_display = ['provider', 'amount', 'status', 'paid_at']
    list_filter = ['status']

admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderRating, ProviderRatingAdmin)
admin.site.register(ProviderPayout, ProviderPayoutAdmin)