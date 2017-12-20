from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from chat.api.serializers import ChatMessageSerializer
from chat.models import ChatMessage
from general.consts import OBJECT_STATUS_ACTIVE


class ChatMessagesListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.filter(status=OBJECT_STATUS_ACTIVE).order_by('-id')
    pagination_class = LimitOffsetPagination
    filter_backend = (DjangoFilterBackend,)
    filter_fields = ('chat',)
