from rest_framework import serializers
from tasks.models import Task


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "service",
            "contact_name",
            "contact_phone",
            "address",
            "latitude",
            "longitude",
            "note",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    service_title = serializers.CharField(source="service.title", read_only=True)
    specialist_display = serializers.CharField(source="specialist.full_name", read_only=True)
    customer_display = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "service",
            "service_title",
            "customer",
            "customer_display",
            "specialist",
            "specialist_display",
            "status",
            "status_display",
            "contact_name",
            "contact_phone",
            "address",
            "latitude",
            "longitude",
            "note",
            "created_at",
        )
        read_only_fields = fields
