from rest_framework import serializers
from rest_framework.fields import URLField, CharField

from chat.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    author_profile_view = URLField(source='author.profile.get_absolute_url')
    author_name = CharField(source='author.username')

    class Meta:
        model = ChatMessage
        fields = ('id', 'text', 'author', 'is_read', 'chat', 'author_name', 'author_profile_view')
        read_only_fields = ('id',)