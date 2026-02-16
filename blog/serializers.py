from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Post, Comment
from django.contrib.auth.models import User

class PostSerializer(serializers.ModelSerializer):
    title = serializers.CharField(min_length=2)
    body = serializers.CharField(min_length=5)
    author = serializers.ReadOnlyField(source='author.username')
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('author',)



class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = 'id post author body created_at updated_at is_approved'.split()


class CommentValidateSerializer(serializers.Serializer):
    body = serializers.CharField(min_length=2)
    
    