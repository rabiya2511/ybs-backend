from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage, ChatFeedback


# ══════════════════════════════════════════════
# POST /api/ai-assistant/chat/
# Send a message, get AI response
# ══════════════════════════════════════════════
class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        session_id = request.data.get('session_id')

        if not message:
            return Response({
                'success': False,
                'message': 'message is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if session_id:
            session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=message[:50]
            )

        # Save user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=message
        )

        # Generate placeholder AI response (real LLM integration can replace this)
        ai_response_text = self.generate_response(message)

        ai_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=ai_response_text
        )

        session.save()  # bump updated_at

        return Response({
            'success': True,
            'data': {
                'session_id': str(session.id),
                'message_id': str(ai_message.id),
                'response': ai_response_text,
            }
        }, status=status.HTTP_201_CREATED)

    def generate_response(self, message):
        # Placeholder logic — replace with real AI integration later
        return f"I received your message: \"{message}\". This is a placeholder response from YBS AI Assistant."


# ══════════════════════════════════════════════
# GET /api/ai-assistant/history/
# Get chat history for a session
# ══════════════════════════════════════════════
class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get('session_id')

        if not session_id:
            return Response({
                'success': False,
                'message': 'session_id query parameter is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
        messages = session.messages.all()

        data = [{
            'id': str(m.id),
            'role': m.role,
            'content': m.content,
            'created_at': m.created_at,
        } for m in messages]

        return Response({
            'success': True,
            'session_id': str(session.id),
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/ai-assistant/sessions/
# List all chat sessions for the user
# ══════════════════════════════════════════════
class ChatSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user)

        data = []
        for s in sessions:
            last_message = s.messages.last()
            data.append({
                'id': str(s.id),
                'title': s.title,
                'last_message': last_message.content[:100] if last_message else '',
                'created_at': s.created_at,
                'updated_at': s.updated_at,
            })

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# DELETE /api/ai-assistant/session/<id>/
# Delete a chat session
# ══════════════════════════════════════════════
class ChatSessionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        session = get_object_or_404(ChatSession, pk=pk, user=request.user)
        session.delete()
        return Response({
            'success': True,
            'message': 'Chat session deleted successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/ai-assistant/feedback/
# Submit feedback on an AI response
# ══════════════════════════════════════════════
class ChatFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message_id = request.data.get('message_id')
        is_helpful = request.data.get('is_helpful')
        comment = request.data.get('comment', '')

        if message_id is None or is_helpful is None:
            return Response({
                'success': False,
                'message': 'message_id and is_helpful are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        message = get_object_or_404(ChatMessage, pk=message_id)

        feedback = ChatFeedback.objects.create(
            message=message,
            user=request.user,
            is_helpful=is_helpful,
            comment=comment,
        )

        return Response({
            'success': True,
            'message': 'Feedback submitted successfully.',
            'data': {
                'id': str(feedback.id),
                'is_helpful': feedback.is_helpful,
            }
        }, status=status.HTTP_201_CREATED)