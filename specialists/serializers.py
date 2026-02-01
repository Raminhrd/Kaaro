from rest_framework import serializers
from specialists.models import SpecialistRequest, SpecialistProfile


class SpecialistRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistRequest
        fields = ("note",)

    def create(self, validated_data):
        user = self.context["request"].user

        sr, created = SpecialistRequest.objects.get_or_create(user=user)
        if not created and sr.status != SpecialistRequest.Status.PENDING:
            raise serializers.ValidationError("Your specialist request has already been reviewed.")

        sr.note = validated_data.get("note", sr.note)
        sr.save(update_fields=["note"])
        return sr


class SpecialistRequestSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SpecialistRequest
        fields = ("id", "status", "status_display", "note", "created_at", "reviewed_at")
        read_only_fields = fields


class SpecialistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistProfile
        fields = ("national_code", "bio", "city", "is_verified", "created_at")
        read_only_fields = ("is_verified", "created_at")
