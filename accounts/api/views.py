from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from accounts.api.serializers import HyperlinkedUserSerializer
from general.consts import OBJECT_STATUS_ACTIVE


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = HyperlinkedUserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filter_fields = ('profile__friends',)
    search_fields = ('username', 'first_name', 'last_name')
