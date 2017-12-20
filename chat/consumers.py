import json

from channels.auth import channel_session_user_from_http, channel_session_user
from channels.channel import Group
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.utils.html import escape

from accounts.api.serializers import UserSerializer
from chat.models import ChatMessage, Chat


@channel_session_user_from_http
def chat_connect(message, pk=0):
    message.reply_channel.send({"accept": True})
    Group('chat-{}'.format(pk)).add(message.reply_channel)


@channel_session_user
def chat_message(message, pk=0):
    data = json.loads(message.content['text'])

    chat = Chat.objects.get(pk=pk)
    print(chat)
    print(chat.pk)

    if data['type'] == 'got_message':
        chat.messages.exclude(author=message.user).update(is_read=True)
    elif data['type'] == 'message':
        ChatMessage.objects.create(
            chat=chat,
            text=escape(data['text']),
            author=message.user
        )
        serializer = UserSerializer(message.user)
        sender = serializer.data
        Group('chat-{}'.format(pk)).send({'text': json.dumps({'message': data['text'],
                                            'sender': sender})})


@channel_session_user
def chat_disconnect(message, pk=0):
    Group('chat-{}'.format(pk)).discard(message.reply_channel)