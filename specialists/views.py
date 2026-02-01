from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from specialists.models import SpecialistRequest
from specialists.serializers import (SpecialistRequestCreateSerializer,SpecialistRequestSerializer,)


class SpecialistRequestMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sr = SpecialistRequest.objects.filter(user=request.user).first()
        if not sr:
            return Response({"detail": "No specialist request found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(SpecialistRequestSerializer(sr).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SpecialistRequestCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        sr = serializer.save()
        return Response(SpecialistRequestSerializer(sr).data, status=status.HTTP_201_CREATED)
