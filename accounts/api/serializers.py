from collections import OrderedDict

from django.contrib.auth.models import User
from django.urls import reverse_lazy
from rest_framework import serializers
from rest_framework.fields import ImageField, URLField
from rest_framework.relations import HyperlinkedIdentityField, PKOnlyObject


class UserSerializer(serializers.ModelSerializer):
    avatar = ImageField(source='profile.avatar')
    profile_view = URLField(source='profile.get_absolute_url')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar', 'profile_view',)
        read_only_fields = ('id',)


class HyperlinkedUserSerializer(serializers.HyperlinkedModelSerializer):
    avatar = ImageField(source='profile.avatar')
    profile_view = HyperlinkedIdentityField(view_name='guest-profile')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar', 'profile_view',)
        read_only_fields = ('id',)