from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'amount',
            'category', 'status', 'expense_date',
            'receipt', 'notes',
            'created_by', 'created_by_name',
            'approved_by', 'approved_by_name',
            'approved_at', 'created_at', 'updated_at',
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.name if obj.approved_by else None


class ExpenseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['title', 'description', 'amount', 'category', 'expense_date', 'notes']