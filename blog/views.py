from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, CommentValidateSerializer

class PostViewSet(ModelViewSet):
    queryset = Post.objects.annotate(
        comments_count=Count('comments')
    )      
    serializer_class = PostSerializer  
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.filter(is_published=True).annotate(
            comments_count=Count('comments')
        )

    def get_serializer_class(self):
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user:
            raise PermissionDenied("You are not the owner!")
        serializer.save()


    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        if request.method == 'GET':
            comments = Comment.objects.filter(post_id=pk, is_approved=True)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        if request.method == 'POST':
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required!")

            comment = Comment.objects.create(
                post_id=pk,
                author=request.user,
                body=request.data.get('body')
            )
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user:
            raise PermissionDenied("You are not the owner!")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("You are not the owner!")
        instance.delete()