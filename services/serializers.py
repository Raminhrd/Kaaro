from rest_framework import serializers
from services.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    service_type_display = serializers.CharField(source="get_service_type_display", read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "title",
            "service_type",
            "service_type_display",
            "description",
            "base_duration_minutes",
            "is_active",
        )
        read_only_fields = fields