from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserCreateSerializer, UserAuthSerializer, ConfirmSerializer
from .models import ConfirmCode
import random
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny

class UserViewSet(viewsets.ViewSet):
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        code = str(random.randint(100000, 999999))
        ConfirmCode.objects.create(user=user, code=code)
        return Response({"user_id": user.id, "confirm_code": code}, status=status.HTTP_201_CREATED)

    def confirm_user(self, request):
        serializer = ConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        try:
            confirm = ConfirmCode.objects.get(code=code)
        except ConfirmCode.DoesNotExist:
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        user = confirm.user
        user.is_active = True
        user.save()
        confirm.delete()
        return Response({"message": "User confirmed"})

    def login(self, request):
        serializer = UserAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"error": "User not confirmed"}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
