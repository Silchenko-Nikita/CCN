from django.contrib.auth.models import User
from django.urls import reverse_lazy
from rest_framework import serializers
from rest_framework.fields import ImageField, URLField
from rest_framework.relations import HyperlinkedIdentityField


class UserSerializer(serializers.HyperlinkedModelSerializer):
    avatar = ImageField(source='profile.avatar')
    profile_view = HyperlinkedIdentityField(view_name='guest-profile')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar', 'profile_view',)
        read_only_fields = ('id',)