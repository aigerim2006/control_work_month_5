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

