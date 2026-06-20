from django.urls import path
from .views import (
    ExpenseListCreateView,
    ExpenseDetailView,
)

urlpatterns = [
    path('', ExpenseListCreateView.as_view()),        # GET list, POST create
    path('<uuid:pk>/', ExpenseDetailView.as_view()),  # GET, PUT, DELETE
]