from rest_framework import serializers
from .models import Bill

class BillSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            'id', 'bill_number', 'title', 'description',
            'amount', 'gst_amount', 'total_amount',
            'category', 'status', 'vendor_name', 'vendor_email',
            'bill_date', 'due_date', 'paid_at',
            'attachment', 'notes',
            'created_by', 'created_by_name',
            'approved_by', 'approved_by_name',
            'approved_at', 'created_at', 'updated_at',
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.name if obj.approved_by else None


class BillCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = [
            'title', 'description', 'amount', 'gst_amount',
            'category', 'vendor_name', 'vendor_email',
            'bill_date', 'due_date', 'notes'
        ]