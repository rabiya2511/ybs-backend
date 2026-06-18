from rest_framework import serializers
from .models import Service, Package


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            'id',
            'name',
            'tagline',
            'price',
            'billing_period',
            'features',
            'is_recommended',
            'is_active',
            'sort_order',
        ]


class ServiceSerializer(serializers.ModelSerializer):
    packages = PackageSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'category',
            'description',
            'icon',
            'starting_price',
            'is_active',
            'packages',
            'created_at',
        ]


class ServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'name',
            'category',
            'description',
            'icon',
            'starting_price',
            'is_active',
        ]


class PackageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            'service',
            'name',
            'tagline',
            'price',
            'billing_period',
            'features',
            'is_recommended',
            'is_active',
            'sort_order',
        ]