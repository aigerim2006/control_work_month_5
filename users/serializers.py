from rest_framework import serializers
from .models import CustomUser, ConfirmCode
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "phone_number", "password")


    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError("User with this email already exists")
        return value
    
    def create(self, validated_data):
        return CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone_number=validated_data.get("phone_number")
        )

class UserAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ConfirmSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(min_length=6, max_length=6)
    def validate(self, attrs):
        user_id = attrs.get('user_id')
        code = attrs.get('code')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("User does not exist")

        try:
            confirmation = ConfirmCode.objects.get(user=user)
        except ConfirmCode.DoesNotExist:
            raise ValidationError("Confirmation code not found")

        if confirmation.code != code:
            raise ValidationError("Invalid confirmation code")

        attrs['user'] = user
        return attrs
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["user_id"] = user.id
        token["birthdate"] = user.birthdate.isoformat() if user.birthdate else None  # <-- добавили birthdate
        return token