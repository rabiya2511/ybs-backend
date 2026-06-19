from django.urls import path
from .views import (
    ProjectListView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectUpdateView,
    ProjectCompleteView,
    MilestoneListView,
    MilestoneCreateView,
    MilestoneUpdateView,
    ProjectDocumentListView,
    ProjectDocumentUploadView,
)

urlpatterns = [
    # ── Project Routes ─────────────────────────────
    # List client projects / Admin create project
    path('', ProjectListView.as_view(), name='project-list'),
    path('create/', ProjectCreateView.as_view(), name='project-create'),
    path('<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<uuid:pk>/update/', ProjectUpdateView.as_view(), name='project-update'),
    path('<uuid:pk>/complete/', ProjectCompleteView.as_view(), name='project-complete'),

    # ── Milestone Routes ───────────────────────────
    path('milestones/', MilestoneListView.as_view(), name='milestone-list'),
    path('milestones/create/', MilestoneCreateView.as_view(), name='milestone-create'),
    path('milestones/<uuid:pk>/update/', MilestoneUpdateView.as_view(), name='milestone-update'),

    # ── Document Routes ────────────────────────────
    path('<uuid:pk>/documents/', ProjectDocumentListView.as_view(), name='project-documents'),
    path('<uuid:pk>/documents/upload/', ProjectDocumentUploadView.as_view(), name='project-document-upload'),
]