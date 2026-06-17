from rest_framework import serializers
from .models import Order, OrderDocument
from authentication.models import User
from services.models import Service, Package

class OrderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDocument
        fields = [
            'id',
            'name',
            'file',
            'is_deliverable',
            'uploaded_by',
            'created_at',
        ]

class OrderSerializer(serializers.ModelSerializer):
    # Show names instead of just IDs
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    documents = OrderDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'client',
            'client_name',
            'client_email',
            'service',
            'service_name',
            'package',
            'package_name',
            'provider',
            'provider_name',
            'base_amount',
            'gst_amount',
            'discount',
            'total_paid',
            'payment_method',
            'razorpay_order_id',
            'razorpay_payment_id',
            'status',
            'milestones',
            'business_name',
            'business_type',
            'business_category',
            'number_of_directors',
            'internal_notes',
            'expected_completion_date',
            'documents',
            'created_at',
            'updated_at',
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    # Used when client creates an order
    class Meta:
        model = Order
        fields = [
            'service',
            'package',
            'payment_method',
            'business_name',
            'business_type',
            'business_category',
            'number_of_directors',
            'razorpay_order_id',
            'razorpay_payment_id',
        ]

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    # Used by admin to update order status
    class Meta:
        model = Order
        fields = ['status', 'internal_notes', 'expected_completion_date']

class MilestoneUpdateSerializer(serializers.Serializer):
    # Used by admin to update a single milestone
    index = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['pending', 'active', 'completed'])