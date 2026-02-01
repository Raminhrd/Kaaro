from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import normalize_phone_number
from users.models import SpecialistRequest

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(trim_whitespace=True)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data["phone_number"],
            password=validated_data["password"],
        )
        return user
    
    
class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(trim_whitespace=True)

    def validate_phone_number(self, value):
        return normalize_phone_number(value)


class OTPLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(trim_whitespace=True)
    otp = serializers.CharField(max_length=6, min_length=4)

    def validate_phone_number(self, value):
        return normalize_phone_number(value)

class UserInfoSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", allow_null=True)
    
    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "status",
            "role",
            "is_phone_verified",
        )