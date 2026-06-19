from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    TaskAssignView,
    TaskReassignView,
    TaskCompleteView,
    TaskRejectView,
    TaskUnassignedView,
    TaskOverdueView,
)

urlpatterns = [
    path('', TaskListCreateView.as_view()),           # GET list, POST create
    path('<uuid:pk>/', TaskDetailView.as_view()),      # GET, PUT, DELETE
    path('assign/', TaskAssignView.as_view()),         # POST assign
    path('reassign/', TaskReassignView.as_view()),     # POST reassign
    path('complete/', TaskCompleteView.as_view()),     # POST complete
    path('reject/', TaskRejectView.as_view()),         # POST reject
    path('unassigned/', TaskUnassignedView.as_view()), # GET unassigned
    path('overdue/', TaskOverdueView.as_view()),       # GET overdue
]