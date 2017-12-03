import json

from channels.auth import channel_session_user_from_http, channel_session_user
from channels.channel import Group
from django.contrib.auth.models import User
from django.forms import model_to_dict

from accounts.api.serializers import UserSerializer
from chat.models import ChatMessage, Chat


@channel_session_user_from_http
def chat_connect(message, pk=0):
    message.reply_channel.send({"accept": True})
    Group('chat-{}'.format(pk)).add(message.reply_channel)


@channel_session_user
def chat_message(message, pk=0):
    ChatMessage.objects.create(
        chat=Chat.objects.get(pk=pk),
        text=message.content['text'],
        author=message.user
    )
    serializer = UserSerializer(message.user)
    sender = serializer.data
    Group('chat-{}'.format(pk)).send({'text': json.dumps({'message': message.content['text'],
                                            'sender': sender})})


@channel_session_user
def chat_disconnect(message, pk=0):
    Group('chat-{}'.format(pk)).discard(message.reply_channel)