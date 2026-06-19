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
    # notifications APIs
    path('api/notifications/', include('notifications.urls')),
    # Checkout APIs
     path('api/checkout/', include('checkout.urls')), 
    # Accounting APIs
    path('api/accounting/', include('accounting.urls')),
    # Projects APIs
    path('api/projects/', include('projects.urls')),
]

# Serve uploaded files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)