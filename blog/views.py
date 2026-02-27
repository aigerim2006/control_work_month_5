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

class PostViewSet(ModelViewSet):   
    serializer_class = PostSerializer  
    permission_classes = [permissions.IsAuthenticatedOrReadOnly | IsModerator]
    def get_queryset(self):
        return Post.objects.filter(is_published=True).annotate(
            comments_count=Count('comments')
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You are not the owner!")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You are not the owner!")
        instance.delete()

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
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
            return Response(CommentSerializer(comment).data)
        
class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly | IsModerator]
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Comment.objects.all()
        return Comment.objects.filter(is_approved=True)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You are not the owner!")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You are not the owner!")
        instance.delete()
    
