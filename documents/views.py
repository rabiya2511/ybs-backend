from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from .models import Folder, Document

# ══════════════════════════════════════════════
# POST /api/documents/upload/
# ══════════════════════════════════════════════
class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        name = request.data.get('name', file.name if file else 'Document')
        folder_id = request.data.get('folder_id')

        if not file:
            return Response({
                'success': False,
                'message': 'No file provided.'
            }, status=status.HTTP_400_BAD_REQUEST)

        folder = None
        if folder_id:
            folder = get_object_or_404(Folder, pk=folder_id)

        file_extension = file.name.split('.')[-1].lower() if '.' in file.name else ''

        document = Document.objects.create(
            name=name,
            file=file,
            file_size=file.size,
            file_type=file_extension,
            folder=folder,
            uploaded_by=request.user,
        )

        return Response({
            'success': True,
            'message': 'Document uploaded successfully.',
            'data': {
                'id': str(document.id),
                'name': document.name,
                'file_url': request.build_absolute_uri(document.file.url),
                'file_size': document.file_size,
                'file_type': document.file_type,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/documents/
# ══════════════════════════════════════════════
class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(uploaded_by=request.user)

        folder_id = request.query_params.get('folder_id')
        if folder_id:
            documents = documents.filter(folder__id=folder_id)

        data = [{
            'id': str(d.id),
            'name': d.name,
            'file_url': request.build_absolute_uri(d.file.url),
            'file_size': d.file_size,
            'file_type': d.file_type,
            'folder': d.folder.name if d.folder else None,
            'created_at': d.created_at,
        } for d in documents]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/documents/<id>/
# ══════════════════════════════════════════════
class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk)

        return Response({
            'success': True,
            'data': {
                'id': str(document.id),
                'name': document.name,
                'file_url': request.build_absolute_uri(document.file.url),
                'file_size': document.file_size,
                'file_type': document.file_type,
                'folder': document.folder.name if document.folder else None,
                'uploaded_by': document.uploaded_by.name if document.uploaded_by else None,
                'created_at': document.created_at,
            }
        })

    def delete(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        document.file.delete(save=False)
        document.delete()
        return Response({
            'success': True,
            'message': 'Document deleted successfully.'
        })


# ══════════════════════════════════════════════
# GET /api/documents/download/<id>/
# ══════════════════════════════════════════════
class DocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        try:
            return FileResponse(
                document.file.open('rb'),
                as_attachment=True,
                filename=document.name
            )
        except FileNotFoundError:
            return Response({
                'success': False,
                'message': 'File not found on server.'
            }, status=status.HTTP_404_NOT_FOUND)


# ══════════════════════════════════════════════
# POST /api/documents/folder/
# ══════════════════════════════════════════════
class FolderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name')
        parent_id = request.data.get('parent_id')

        if not name:
            return Response({
                'success': False,
                'message': 'name is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        parent = None
        if parent_id:
            parent = get_object_or_404(Folder, pk=parent_id)

        folder = Folder.objects.create(
            name=name,
            parent=parent,
            created_by=request.user,
        )

        return Response({
            'success': True,
            'message': f'Folder "{folder.name}" created successfully.',
            'data': {
                'id': str(folder.id),
                'name': folder.name,
                'parent': str(parent.id) if parent else None,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/documents/folders/
# ══════════════════════════════════════════════
class FolderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        folders = Folder.objects.filter(created_by=request.user)

        parent_id = request.query_params.get('parent_id')
        if parent_id:
            folders = folders.filter(parent__id=parent_id)
        else:
            folders = folders.filter(parent__isnull=True)

        data = [{
            'id': str(f.id),
            'name': f.name,
            'parent': str(f.parent.id) if f.parent else None,
            'subfolder_count': f.subfolders.count(),
            'document_count': f.documents.count(),
            'created_at': f.created_at,
        } for f in folders]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })