from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache

from users.serializers import SignUpSerializer, OTPRequestSerializer, OTPLoginSerializer, UserInfoSerializer, SpecialistRequestAdminDecisionSerializer, SpecialistRequestSerializer, SpecialistRequestCreateSerializer
from users.utils import set_tokens_on_cookie, generate_otp
from users.tasks import send_otp_sms
from users.defaults import OTP_EXPIRY_SECONDS
from users.models import SpecialistRequest
from users.permission import IsAdminUser

User = get_user_model()

class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TypeError as e:
            raise InvalidToken(e.args[0])
        
        output = serializer.validated_data
        response = Response(output, status=status.HTTP_200_OK)
        set_tokens_on_cookie(response, output["access"], output["refresh"])
        
        return response
    

class SignUpView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        output = {"access": str(refresh.access_token), "refresh": str(refresh)}
        response = Response(output, status=status.HTTP_201_CREATED)
        set_tokens_on_cookie(response, output["access"], output["refresh"])

        return response
    

class OTPRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        
        # TODO: check if OTP exists for this phone, raise Error

        otp = generate_otp()
        cache.set(f"otp_{phone}", otp, timeout=OTP_EXPIRY_SECONDS)
        send_otp_sms.delay(phone, otp)

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class OTPLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data['phone_number']
        incoming_otp = serializer.validated_data['otp']
        cached_otp = cache.get(f"otp_{phone}")
        
        if not cached_otp or str(cached_otp) != str(incoming_otp):
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
             return Response({"error": "User not found. Sign up first."}, status=status.HTTP_404_NOT_FOUND)

        user.is_phone_verified = True
        user.save(update_fields=("is_phone_verified",))
        
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_str = str(refresh)
        
        cache.delete(f"otp_{phone}")

        response = Response({"access": access, "refresh": refresh_str}, status=status.HTTP_200_OK)
        set_tokens_on_cookie(response, access, refresh_str)
        
        return response
    

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = (
            User.objects.select_related("specialist_request").only(
                "id", "phone_number", "first_name", "last_name",
                "status", "is_phone_verified", "role",
                "specialist_request__status", "specialist_request__created_at",)
            .get(id=request.user.id))
        return Response(UserInfoSerializer(user).data)