from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Authentication APIs
    path('api/auth/', include('authentication.urls')),

    # Services & Packages APIs
    path('api/services/', include('services.urls')),

    # Orders APIs
    path('api/orders/', include('orders.urls')),

    # Payments APIs
    path('api/payments/', include('payments.urls')),

    # Notifications APIs
    path('api/notifications/', include('notifications.urls')),

    # Checkout APIs
    path('api/checkout/', include('checkout.urls')),

    # Accounting APIs
    path('api/accounting/', include('accounting.urls')),

    # Projects APIs
    path('api/projects/', include('projects.urls')),

    # Providers APIs
    path('api/providers/', include('providers.urls')),
    #Tasks APIs
    path('api/tasks/', include('tasks.urls')),
    # Clients APIs
    path('api/clients/', include('clients.urls')),
    # Provider Portal APIs
    path('api/provider-portal/', include('provider_portal.urls')),
    # Referrals APIs
    path('api/referrals/', include('referrals.urls')),  
    # Documents APIs
    path('api/documents/', include('documents.urls')),
    # Expenses APIs
    path('api/expenses/', include('expenses.urls')),
    # Site Settings APIs
    path('api/settings/', include('site_settings.urls')),
    path('api/bills/', include('bills.urls')),
    # Dashboards APIs
    path('api/dashboard/', include('dashboards.urls')),
]

# Serve uploaded files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)