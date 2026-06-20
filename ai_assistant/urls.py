from django.urls import path
from .views import (
    ChatView,
    ChatHistoryView,
    ChatSessionListView,
    ChatSessionDeleteView,
    ChatFeedbackView,
)

urlpatterns = [
    path('chat/', ChatView.as_view(), name='ai-chat'),
    path('history/', ChatHistoryView.as_view(), name='ai-chat-history'),
    path('sessions/', ChatSessionListView.as_view(), name='ai-chat-sessions'),
    path('session/<uuid:pk>/', ChatSessionDeleteView.as_view(), name='ai-chat-session-delete'),
    path('feedback/', ChatFeedbackView.as_view(), name='ai-chat-feedback'),
]