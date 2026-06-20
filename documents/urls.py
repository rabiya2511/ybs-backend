from django.urls import path
from .views import (
    DocumentUploadView,
    DocumentListView,
    DocumentDetailView,
    DocumentDownloadView,
    FolderCreateView,
    FolderListView,
)

urlpatterns = [
    # Documents
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('', DocumentListView.as_view(), name='document-list'),
    path('<uuid:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('download/<uuid:pk>/', DocumentDownloadView.as_view(), name='document-download'),

    # Folders
    path('folder/', FolderCreateView.as_view(), name='folder-create'),
    path('folders/', FolderListView.as_view(), name='folder-list'),
]