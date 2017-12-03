from django.contrib.auth.models import User
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from accounts.api.serializers import HyperlinkedUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = HyperlinkedUserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'first_name', 'last_name')
