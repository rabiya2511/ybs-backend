from django.urls import path
from .views import (
    ProviderDashboardView,
    MyTasksView,
    AcceptTaskView,
    RejectTaskView,
    StartTaskView,
    CompleteTaskView,
    UploadTaskFileView,
    MyEarningsView,
    MyPaymentsHistoryView,
)

urlpatterns = [
    # GET  /api/provider-portal/dashboard/
    path('dashboard/', ProviderDashboardView.as_view(), name='provider-dashboard'),

    # GET  /api/provider-portal/tasks/
    path('tasks/', MyTasksView.as_view(), name='provider-tasks'),

    # POST /api/provider-portal/tasks/<id>/accept/
    path('tasks/<uuid:pk>/accept/', AcceptTaskView.as_view(), name='provider-accept-task'),

    # POST /api/provider-portal/tasks/<id>/reject/
    path('tasks/<uuid:pk>/reject/', RejectTaskView.as_view(), name='provider-reject-task'),

    # POST /api/provider-portal/tasks/<id>/start/
    path('tasks/<uuid:pk>/start/', StartTaskView.as_view(), name='provider-start-task'),

    # POST /api/provider-portal/tasks/<id>/complete/
    path('tasks/<uuid:pk>/complete/', CompleteTaskView.as_view(), name='provider-complete-task'),

    # POST /api/provider-portal/tasks/<id>/upload/
    path('tasks/<uuid:pk>/upload/', UploadTaskFileView.as_view(), name='provider-upload-file'),

    # GET  /api/provider-portal/earnings/
    path('earnings/', MyEarningsView.as_view(), name='provider-earnings'),

    # GET  /api/provider-portal/payments/
    path('payments/', MyPaymentsHistoryView.as_view(), name='provider-payments'),
]