from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import UserViewSet
from users.views import CustomTokenObtainPairView


user_list = UserViewSet.as_view({
    'post': 'create'
})
user_confirm = UserViewSet.as_view({
    'post': 'confirm_user'
})
user_login = UserViewSet.as_view({
    'post': 'login'
})

urlpatterns = [
    path('registration/', user_list, name='user-registration'),
    path('confirm/', user_confirm, name='user-confirm'),
    path('authorization/', user_login, name='user-login'),

    path("api/v1/jwt/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
