from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .models import CustomUser
from .serializers import UserCreateSerializer, UserAuthSerializer, ConfirmSerializer
from users.services import save_confirmation_code
from common.redis_client import redis_client
from django.contrib.auth import authenticate
from rest_framework.decorators import action 
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import CustomTokenObtainPairSerializer
from users.tasks import generate_report, send_welcome_email

class UserViewSet(viewsets.ViewSet):
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() 
        generate_report.delay(user.id)
        code = save_confirmation_code(user.email)
        send_welcome_email.delay(user.email)
        return Response(
            {"user_id": user.id, "confirm_code": code},
        status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def confirm_user(self, request):
        serializer = ConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        code = serializer.validated_data['code']
        key = f"confirm_code:{user.email}"
        redis_code = redis_client.get(key)
        if not redis_code:
            return Response({"error": "Код истек"}, status=400)
        if redis_code != code:
            return Response({"error": "Неверный код"}, status=400)
        user.is_active = True
        user.save()
        redis_client.delete(key)
        return Response({"message": "User confirmed"})


    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_model().objects.filter(email=serializer.validated_data['email']).first()
        if not user or not user.check_password(serializer.validated_data['password']):
            return Response({"error": "Invalid credentials"}, status=401)
        if not user.is_active:
            return Response({"error": "User not confirmed"}, status=401)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

