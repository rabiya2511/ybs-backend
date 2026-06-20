from django.urls import path
from .views import (
    BillListCreateView,
    BillDetailView,
    BillApproveView,
)

urlpatterns = [
    path('', BillListCreateView.as_view()),
    path('<uuid:pk>/', BillDetailView.as_view()),
    path('approve/', BillApproveView.as_view()),
]