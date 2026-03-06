from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, CommentValidateSerializer
from common.permissions import IsModerator
import requests
from django.utils import timezone
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import OauthCodeSerializer

User = get_user_model()

class GoogleLoginAPIView(CreateAPIView):
    serializer_class = OauthCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]

        # Обмен code на access_token
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.environ.get("GOOGLE_CLIENT_URI"),
                "grant_type": "authorization_code",
            }
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            return Response({"error": "Invalid access_token!"})

        # Получение данных пользователя
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        email = user_info.get("email")
        first_name = user_info.get("given_name")
        last_name = user_info.get("family_name")

        # Создать или обновить пользователя
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.registration_source = "google"
        else:
            user.is_active = True
        user.last_login = timezone.now()
        user.save()

        # Возвращаем JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })


class PostViewSet(ModelViewSet):  
    queryset = Post.objects.filter(is_published=True).annotate(
        comments_count=Count("comments")
    ) 
    serializer_class = PostSerializer  
    permission_classes = [permissions.IsAuthenticatedOrReadOnly | IsModerator]
    
    
    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = Post.objects.create(
            author=request.user,
            title=serializer.validated_data.get("title"),
            body=serializer.validated_data.get("body"),
            is_published=serializer.validated_data.get("is_published", False),
        )

        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        post = self.get_object()

        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied("You are not the owner!")

        serializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(PostSerializer(post).data)
    

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()

        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied("You are not the owner!")

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'GET':
            comments = Comment.objects.filter(post_id=pk, is_approved=True)
            return Response(CommentSerializer(comments, many=True).data)
        if request.method == 'POST':
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required!")
            serializer = CommentValidateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = Comment.objects.create(
                post_id=pk,
                author=request.user,
                body=serializer.validated_data['body']
            )
            return Response(CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED)
        
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly | IsModerator]
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Comment.objects.all()
        return Comment.objects.filter(is_approved=True)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()

        if comment.author != request.user and not request.user.is_staff:
            raise PermissionDenied("You are not the owner!")

        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(CommentSerializer(comment).data)


    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()

        if comment.author != request.user and not request.user.is_staff:
            raise PermissionDenied("You are not the owner!")

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

