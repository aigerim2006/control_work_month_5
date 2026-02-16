from django.urls import path
from .views import UserViewSet

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
]
